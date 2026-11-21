"""Porty źródeł. Adaptery je implementują, a paczka wersetu zna tylko te kształty."""

from __future__ import annotations

from typing import Protocol


class WydaniePolskie(Protocol):
    def werset(self, ksiega: str, rozdzial: int, werset: int) -> str: ...

    def rozdzialy(self, ksiega: str) -> list[int]: ...

    def liczba_wersetow(self, ksiega: str, rozdzial: int) -> int: ...

    def kanon(self) -> list[tuple[str, int, int, str]]: ...


class TekstZrodlowy(Protocol):
    wydanie: str

    def werset(self, ksiega_step: str, rozdzial: int, werset: int) -> dict: ...


class Paralela(Protocol):
    ident: str

    def werset(self, numer_ksiegi: int, rozdzial: int, werset: int) -> dict: ...


class LeksykonPort(Protocol):
    def glosa(self, lemma: str) -> str: ...
