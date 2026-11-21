"""Wydania Biblii Gdańskiej z submodułu biblia-druk-tekst."""

from __future__ import annotations

from pathlib import Path

from narzedzia.tekst import indeksy_kursywy, tokeny


class Wydanie:
    def __init__(self, katalog: Path):
        self.katalog = katalog
        self._wiersze: dict[tuple[str, int], list[str]] = {}

    def _plik(self, ksiega: str, rozdzial: int) -> Path:
        katalog = self.katalog / ksiega
        if not katalog.is_dir():
            raise FileNotFoundError(f"Brak księgi {ksiega} w {self.katalog}")
        for sciezka in katalog.iterdir():
            if sciezka.suffix == ".txt" and sciezka.stem.isdigit() and int(sciezka.stem) == rozdzial:
                return sciezka
        raise FileNotFoundError(f"Brak rozdziału {rozdzial} w {katalog}")

    def wiersze(self, ksiega: str, rozdzial: int) -> list[str]:
        klucz = (ksiega, rozdzial)
        if klucz not in self._wiersze:
            self._wiersze[klucz] = self._plik(ksiega, rozdzial).read_text(encoding="utf-8").splitlines()
        return self._wiersze[klucz]

    def werset(self, ksiega: str, rozdzial: int, werset: int) -> str:
        wiersze = self.wiersze(ksiega, rozdzial)
        if werset < 1 or werset > len(wiersze):
            raise FileNotFoundError(f"Brak wersetu {ksiega} {rozdzial}:{werset}")
        return wiersze[werset - 1]

    def rozdzialy(self, ksiega: str) -> list[int]:
        katalog = self.katalog / ksiega
        numery = [
            int(sciezka.stem)
            for sciezka in katalog.iterdir()
            if sciezka.suffix == ".txt" and sciezka.stem.isdigit()
        ]
        return sorted(numery)

    def liczba_wersetow(self, ksiega: str, rozdzial: int) -> int:
        return len(self.wiersze(ksiega, rozdzial))


class BibliaGdanska:
    """Tekst badany to 1879. Kursywa słów dodanych jest w 1632."""

    def __init__(self, root: Path):
        self.nowe = Wydanie(root / "1879")
        self.stare = Wydanie(root / "1632")

    def werset(self, ksiega: str, rozdzial: int, werset: int) -> str:
        return self.nowe.werset(ksiega, rozdzial, werset)

    def rozdzialy(self, ksiega: str) -> list[int]:
        return self.nowe.rozdzialy(ksiega)

    def liczba_wersetow(self, ksiega: str, rozdzial: int) -> int:
        return self.nowe.liczba_wersetow(ksiega, rozdzial)

    def kanon(self) -> list[tuple[str, int, int, str]]:
        wynik: list[tuple[str, int, int, str]] = []
        for ksiega in sorted(sciezka.name for sciezka in (self.nowe.katalog).iterdir() if sciezka.is_dir()):
            for rozdzial in self.nowe.rozdzialy(ksiega):
                for numer, tekst in enumerate(self.nowe.wiersze(ksiega, rozdzial), start=1):
                    wynik.append((ksiega, rozdzial, numer, tekst))
        return wynik

    def tekst_i_kursywa(self, ksiega: str, rozdzial: int, werset: int) -> dict:
        tekst = self.nowe.werset(ksiega, rozdzial, werset)
        slowa = tokeny(tekst)
        try:
            tekst_1632 = self.stare.werset(ksiega, rozdzial, werset)
        except FileNotFoundError:
            tekst_1632 = None
            kursywa: list[int] = []
        else:
            kursywa = indeksy_kursywy(slowa, tekst_1632)
        return {
            "tekst_bg": tekst,
            "tokeny_bg": [{"i": i, "t": slowo} for i, slowo in enumerate(slowa)],
            "tekst_1632": tekst_1632,
            "kursywa_1632": kursywa,
        }
