"""Liczniki werdyktów. Czysta funkcja rekordów, bez HTML i bez dysku."""

from __future__ import annotations

from narzedzia.wiernosc import WERDYKTY


def policz(wersetow: int, rekordy: list[dict]) -> dict:
    werdykty = {werdykt: 0 for werdykt in WERDYKTY}
    for rekord in rekordy:
        werdykty[rekord["wiernosc"]["werdykt"]] += 1
    return {
        "wersetow": wersetow,
        "zanalizowanych": len(rekordy),
        "bez_analizy": wersetow - len(rekordy),
        "werdykty": werdykty,
    }


def wedlug_werdyktu(rekordy: list[dict]) -> dict[str, list[dict]]:
    grupy = {werdykt: [] for werdykt in WERDYKTY}
    for rekord in rekordy:
        grupy[rekord["wiernosc"]["werdykt"]].append(rekord["adres"])
    for adresy in grupy.values():
        adresy.sort(key=lambda adres: (adres["ksiega"], adres["rozdzial"], adres["werset"]))
    return grupy
