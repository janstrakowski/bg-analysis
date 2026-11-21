"""Sąsiedzi wersetu i rozdziału. Nie zna HTML."""

from __future__ import annotations


class Nawigacja:
    def __init__(self, kanon: list[tuple[str, int, int]]):
        self.kanon = kanon
        self._pozycja = {adres: indeks for indeks, adres in enumerate(kanon)}
        self._rozdzialy: dict[tuple[str, int], int] = {}
        for indeks, (ksiega, rozdzial, _werset) in enumerate(kanon):
            self._rozdzialy.setdefault((ksiega, rozdzial), indeks)

    def werset(self, ksiega: str, rozdzial: int, werset: int) -> dict:
        indeks = self._pozycja[(ksiega, rozdzial, werset)]
        return {
            "poprzedni_werset": self.kanon[indeks - 1] if indeks else None,
            "nastepny_werset": self.kanon[indeks + 1] if indeks + 1 < len(self.kanon) else None,
            "poprzedni_rozdzial": self._inny_rozdzial(indeks, -1),
            "nastepny_rozdzial": self._inny_rozdzial(indeks, 1),
        }

    def _inny_rozdzial(self, indeks: int, krok: int) -> tuple[str, int] | None:
        ksiega, rozdzial, _werset = self.kanon[indeks]
        pozycja = indeks + krok
        while 0 <= pozycja < len(self.kanon):
            inna_ksiega, inny_rozdzial, _ = self.kanon[pozycja]
            if (inna_ksiega, inny_rozdzial) != (ksiega, rozdzial):
                return inna_ksiega, inny_rozdzial
            pozycja += krok
        return None
