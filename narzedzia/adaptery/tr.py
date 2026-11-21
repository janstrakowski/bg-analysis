"""Textus Receptus wycięty z TAGNT. Słowa bez znacznika TR nie wchodzą do paczki."""

from __future__ import annotations

import re
from pathlib import Path

_ADRES = re.compile(
    r"^(?P<ksiega>[1-3]?[A-Za-z]+)\.(?P<roz>\d+)\.(?P<wer>\d+)#(?P<nr>\d+)="
)
_STRONG = re.compile(r"(G\d+[A-Z]?)")


def czy_tr(wydania: str) -> bool:
    return "TR" in wydania.split("+")


def _powierzchnia(pole: str) -> str:
    slowo = pole.split(" (", 1)[0].strip()
    return slowo.strip(".,;:··")


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
            if not trafienie or len(kolumny) < 6 or not czy_tr(kolumny[5]):
                continue
            ksiega = trafienie.group("ksiega")
            rozdzial = int(trafienie.group("roz"))
            werset = int(trafienie.group("wer"))
            strong = _STRONG.search(kolumny[3])
            forma = kolumny[4].split("=", 1)[0].strip()
            morph = kolumny[3].split("=", 1)[1].strip() if "=" in kolumny[3] else kolumny[3].strip()
            self._wersety.setdefault((ksiega, rozdzial, werset), []).append(
                {
                    "t": _powierzchnia(kolumny[1]),
                    "lemma": strong.group(1) if strong else "",
                    "forma": forma,
                    "morph": morph,
                    "glosa": kolumny[2].strip(),
                    "id": f"{ksiega}.{rozdzial}.{werset}#{trafienie.group('nr')}",
                    "jezyk": "grc",
                    "_nr": int(trafienie.group("nr")),
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
