"""Tekst masorecki z TAHOT. Wiersze spoza Leningradu i qere (X, R, samo ketiw) nie wchodzą do paczki."""

from __future__ import annotations

import re
from pathlib import Path

_ADRES = re.compile(
    r"^(?P<ksiega>[1-3]?[A-Za-z]+)\.(?P<roz>\d+)\.(?P<wer>\d+)"
    r"(?:\((?P<hroz>\d+)\.(?P<hwer>\d+)\))?#(?P<nr>\d+)=(?P<typ>[A-Za-z]+)"
)
_LEMAT = re.compile(r"\{([HA]\d+[A-Z]?)\}|[HA]\d+[A-Z]?")


def czy_mt(typ: str) -> bool:
    """L to Leningrad, Q to qere. Oba należą do tekstu masoreckiego."""
    return typ in {"L", "Q"}


def _lemat(pole: str) -> str:
    w_nawiasie = re.findall(r"\{([HA]\d+[A-Z]?)\}", pole)
    if w_nawiasie:
        return w_nawiasie[-1]
    znalezione = _LEMAT.findall(pole)
    return znalezione[-1] if znalezione else pole


def _powierzchnia(pole: str) -> str:
    return pole.split("\\", 1)[0].replace("/", "")


class TekstMasorecki:
    wydanie = "MT"

    def __init__(self, katalog: Path):
        self._wersety: dict[tuple[str, int, int], dict] = {}
        for sciezka in sorted(katalog.glob("TAHOT*.txt")):
            self._wczytaj(sciezka)

    def _wczytaj(self, sciezka: Path) -> None:
        for wiersz in sciezka.read_text(encoding="utf-8").splitlines():
            kolumny = wiersz.split("\t")
            trafienie = _ADRES.match(kolumny[0]) if kolumny else None
            if not trafienie or not czy_mt(trafienie.group("typ")):
                continue
            if len(kolumny) < 6:
                continue
            ksiega = trafienie.group("ksiega")
            rozdzial_en = int(trafienie.group("roz"))
            werset_en = int(trafienie.group("wer"))
            rozdzial = int(trafienie.group("hroz") or rozdzial_en)
            werset = int(trafienie.group("hwer") or werset_en)
            klucz = (ksiega, rozdzial, werset)
            rekord = self._wersety.setdefault(
                klucz,
                {
                    "wydanie": self.wydanie,
                    "adres": f"{ksiega}.{rozdzial}.{werset}",
                    "adres_hebrajski": f"{ksiega}.{rozdzial}.{werset}",
                    "adres_angielski": f"{ksiega}.{rozdzial_en}.{werset_en}",
                    "tokeny": [],
                },
            )
            morph = kolumny[5].strip()
            jezyk = "arc" if morph.startswith("A") else "hbo"
            rekord["tokeny"].append(
                {
                    "t": _powierzchnia(kolumny[1].strip()),
                    "lemma": _lemat(kolumny[4]),
                    "morph": morph,
                    "glosa": kolumny[3].strip(),
                    "id": f"{ksiega}.{rozdzial_en}.{werset_en}#{trafienie.group('nr')}",
                    "jezyk": jezyk,
                    "_nr": int(trafienie.group("nr")),
                }
            )

    def werset(self, ksiega_step: str, rozdzial: int, werset: int) -> dict:
        rekord = self._wersety.get((ksiega_step, rozdzial, werset))
        if rekord is None:
            raise KeyError(f"Brak tekstu masoreckiego {ksiega_step} {rozdzial}:{werset}")
        tokeny = sorted(rekord["tokeny"], key=lambda token: token["_nr"])
        jezyki = {token["jezyk"] for token in tokeny}
        if jezyki == {"arc"}:
            jezyk = "arc"
        elif "arc" in jezyki:
            jezyk = "mieszany"
        else:
            jezyk = "hbo"
        oczyszczone = []
        for indeks, token in enumerate(tokeny):
            oczyszczone.append({klucz: wartosc for klucz, wartosc in token.items() if klucz != "_nr"} | {"i": indeks})
        return {
            "wydanie": self.wydanie,
            "jezyk": jezyk,
            "adres": rekord["adres"],
            "adres_hebrajski": rekord["adres_hebrajski"],
            "adres_angielski": rekord["adres_angielski"],
            "tokeny": oczyszczone,
        }
