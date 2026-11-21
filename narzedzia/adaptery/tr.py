"""Textus Receptus wycięty z TAGNT. Słowa bez znacznika TR nie wchodzą do paczki.

Gdy TR ma inne słowo niż tekst główny wiersza, STEPBible zostawia je w kolumnie
wariantów znaczeniowych („… in: TR”). Takie słowo wchodzi do paczki zamiast
brzmienia tekstu krytycznego. Przesunięcie szyku oznaczone przy wydaniu
(„TR«3”) zostaje w numerze pozycji, bez przestawiania tokenu.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

_ADRES = re.compile(
    r"^(?P<ksiega>[1-3]?[A-Za-z]+)\.(?P<roz>\d+)\.(?P<wer>\d+)#(?P<nr>\d+)="
)
_STRONG = re.compile(r"(G\d+[A-Z]?)")
_GRAMATYKA = re.compile(r"(G\d+[A-Z]?)=([A-Za-z0-9-]+)")
_WARIANT = re.compile(
    r"^(?P<pow>.+?)\s+\([^)]*\)\s+(?P<glosa>.*?)\s+-\s+(?P<gram>.+)$"
)

_PRZYIMKI = {
    "ανα", "αντι", "απο", "απ", "δια", "δι", "εις", "εκ", "εξ", "εν", "επι", "επ",
    "κατα", "κατ", "μετα", "μετ", "μεθ", "παρα", "παρ", "περι", "προ", "προς",
    "συν", "υπερ", "υπο", "υπ", "υφ", "χωρις",
}
_RODZAJNIKI = {
    "ο", "η", "το", "του", "της", "τω", "τη", "τον", "την", "οι", "αι", "τα",
    "των", "τοις", "ταις", "τους", "τας",
}
_ZAIMKI = {
    "αυτος", "αυτου", "αυτης", "αυτω", "αυτην", "αυτον", "αυτοι", "αυτων", "αυτοις",
    "αυτους", "αυτας", "αυτο", "μου", "σου", "ημων", "υμων", "εμου", "εμε", "με",
    "σε", "ημιν", "υμιν", "ημας", "υμας", "μοι", "σοι",
}


def czy_tr(wydania: str) -> bool:
    return "TR" in wydania.split("+")


def _czy_tr_z_przesunieciem(wydania: str) -> bool:
    for czesc in wydania.strip().split("+"):
        nazwa = czesc.split("«")[0].split("»")[0]
        if nazwa == "TR":
            return True
    return False


def _powierzchnia(pole: str) -> str:
    slowo = pole.split(" (", 1)[0].strip()
    return slowo.strip(".,;:··¶")


def _bez_akcentu(slowo: str) -> str:
    tekst = unicodedata.normalize("NFD", slowo.lower())
    return "".join(znak for znak in tekst if unicodedata.category(znak) != "Mn")


def _zgodnosc(slowo: str, morph: str) -> int:
    klasa = morph.split("-", 1)[0]
    golo = _bez_akcentu(slowo)
    if klasa == "PREP" and golo in _PRZYIMKI:
        return 5
    if klasa == "T" and golo in _RODZAJNIKI:
        return 5
    if klasa in {"P", "F"} and golo in _ZAIMKI:
        return 4
    if klasa == "V" and not golo in _PRZYIMKI | _RODZAJNIKI | _ZAIMKI:
        return 2
    if klasa in {"N", "A", "R", "D", "ADV"} and golo not in _PRZYIMKI | _RODZAJNIKI:
        return 1
    return 0


def _przypisz(slowa: list[str], pary: list[tuple[str, str]]) -> list[tuple[str, str]]:
    wolne = set(range(len(pary)))
    wynik: list[tuple[str, str] | None] = [None] * len(slowa)
    oceny = [
        (_zgodnosc(slowo, pary[j][1]), -i, -j, i, j)
        for i, slowo in enumerate(slowa)
        for j in range(len(pary))
    ]
    for _ocena, _i, _j, i, j in sorted(oceny, reverse=True):
        if wynik[i] is not None or j not in wolne:
            continue
        wynik[i] = pary[j]
        wolne.remove(j)
    for i, para in enumerate(wynik):
        if para is None:
            wynik[i] = pary[min(i, len(pary) - 1)] if pary else ("", "")
    return wynik  # type: ignore[return-value]


def _glowa(pary: list[tuple[str, str]]) -> tuple[str, str]:
    for lemma, morph in reversed(pary):
        if not morph.startswith("PREP"):
            return lemma, morph
    if pary:
        return pary[-1]
    return "", ""


def tokeny_wariantu_tr(pole: str) -> list[dict] | None:
    """Tokeny TR z kolumny wariantów. None, gdy TR nie ma tu osobnego brzmienia."""
    if not pole or "TR" not in pole:
        return None
    cialo = None
    for czesc in pole.split("¦"):
        czesc = czesc.strip()
        if " in: " not in czesc:
            continue
        opis, wydania = czesc.rsplit(" in: ", 1)
        if _czy_tr_z_przesunieciem(wydania):
            cialo = opis.strip()
            break
    if cialo is None:
        return None
    trafienie = _WARIANT.match(cialo)
    if not trafienie:
        return None
    slowa = [_powierzchnia(slowo) for slowo in trafienie.group("pow").split()]
    slowa = [slowo for slowo in slowa if slowo]
    pary = _GRAMATYKA.findall(trafienie.group("gram"))
    glosa = trafienie.group("glosa").strip()
    if not slowa:
        return None
    if len(slowa) == 1:
        lemma, morph = _glowa(pary)
        return [{"t": slowa[0], "lemma": lemma, "forma": slowa[0], "morph": morph, "glosa": glosa}]
    przypisane = _przypisz(slowa, pary)
    tokeny = []
    for slowo, (lemma, morph) in zip(slowa, przypisane, strict=True):
        tokeny.append({"t": slowo, "lemma": lemma, "forma": slowo, "morph": morph, "glosa": glosa})
    return tokeny


class TextusReceptus:
    wydanie = "TR"

    def __init__(self, katalog: Path):
        self._wersety: dict[tuple[str, int, int], list[dict]] = {}
        for sciezka in sorted(katalog.glob("TAGNT*.txt")):
            self._wczytaj(sciezka)

    def _wczytaj(self, sciezka: Path) -> None:
        for wiersz in sciezka.read_text(encoding="utf-8").splitlines():
            kolumny = wiersz.split("\t")
            trafienie = _ADRES.match(kolumny[0]) if kolumny else None
            if not trafienie or len(kolumny) < 6:
                continue
            ksiega = trafienie.group("ksiega")
            rozdzial = int(trafienie.group("roz"))
            werset = int(trafienie.group("wer"))
            numer = int(trafienie.group("nr"))
            podstawa = f"{ksiega}.{rozdzial}.{werset}#{trafienie.group('nr')}"
            wariant = None if czy_tr(kolumny[5]) else tokeny_wariantu_tr(kolumny[6] if len(kolumny) > 6 else "")
            if wariant:
                odczyty = wariant
            elif czy_tr(kolumny[5]):
                strong = _STRONG.search(kolumny[3])
                forma = kolumny[4].split("=", 1)[0].strip()
                morph = kolumny[3].split("=", 1)[1].strip() if "=" in kolumny[3] else kolumny[3].strip()
                odczyty = [
                    {
                        "t": _powierzchnia(kolumny[1]),
                        "lemma": strong.group(1) if strong else "",
                        "forma": forma,
                        "morph": morph,
                        "glosa": kolumny[2].strip(),
                    }
                ]
            else:
                continue
            for przesuniecie, odczyt in enumerate(odczyty):
                self._wersety.setdefault((ksiega, rozdzial, werset), []).append(
                    {
                        **odczyt,
                        "id": podstawa if przesuniecie == 0 else f"{podstawa}{chr(ord('b') + przesuniecie - 1)}",
                        "jezyk": "grc",
                        "_nr": numer + przesuniecie / 100,
                    }
                )

    def werset(self, ksiega_step: str, rozdzial: int, werset: int) -> dict:
        tokeny = self._wersety.get((ksiega_step, rozdzial, werset))
        if not tokeny:
            raise KeyError(f"Brak Textus Receptus {ksiega_step} {rozdzial}:{werset}")
        uporzadkowane = sorted(tokeny, key=lambda token: token["_nr"])
        oczyszczone = []
        for indeks, token in enumerate(uporzadkowane):
            oczyszczone.append({klucz: wartosc for klucz, wartosc in token.items() if klucz != "_nr"} | {"i": indeks})
        adres = f"{ksiega_step}.{rozdzial}.{werset}"
        return {
            "wydanie": self.wydanie,
            "jezyk": "grc",
            "adres": adres,
            "adres_hebrajski": None,
            "adres_angielski": adres,
            "tokeny": oczyszczone,
        }
