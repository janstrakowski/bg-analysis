"""Rejestr ksiąg. Jedno źródło skrótów, kodów STEP i incipitów."""

from __future__ import annotations

import json

from narzedzia.sciezki import SCHEMAT
from narzedzia.tekst import zloz


def wczytaj() -> list[dict]:
    return json.loads((SCHEMAT / "ksiegi.json").read_text(encoding="utf-8"))


def po_kodzie(ksiegi: list[dict] | None = None) -> dict[str, dict]:
    dane = wczytaj() if ksiegi is None else ksiegi
    return {ksiega["kod"]: ksiega for ksiega in dane}


def po_skrocie(ksiegi: list[dict] | None = None) -> dict[str, dict]:
    dane = wczytaj() if ksiegi is None else ksiegi
    return {zloz(ksiega["skrot"]): ksiega for ksiega in dane}


def numer_ksiegi(ksiegi: list[dict], kod: str) -> int:
    for indeks, ksiega in enumerate(ksiegi, start=1):
        if ksiega["kod"] == kod:
            return indeks
    raise KeyError(kod)
