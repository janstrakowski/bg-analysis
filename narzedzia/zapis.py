"""Odczyt i zapis plików analizy. Jeden werset to jeden plik."""

from __future__ import annotations

import json
from pathlib import Path

from narzedzia.sciezki import ANALIZA, SCHEMAT


def sciezka_wersetu(ksiega: str, rozdzial: int, werset: int, katalog: Path | None = None) -> Path:
    return (katalog or ANALIZA) / ksiega / f"{rozdzial:02d}" / f"{werset:03d}.json"


def zapisz_json(sciezka: Path, dane: dict) -> None:
    sciezka.parent.mkdir(parents=True, exist_ok=True)
    sciezka.write_text(json.dumps(dane, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def wczytaj_json(sciezka: Path) -> dict:
    return json.loads(sciezka.read_text(encoding="utf-8"))


def iteruj_analizy(katalog: Path | None = None) -> list[tuple[Path, dict]]:
    korzen = katalog or ANALIZA
    if not korzen.is_dir():
        return []
    wynik = []
    for sciezka in sorted(korzen.glob("*/*/*.json")):
        wynik.append((sciezka, wczytaj_json(sciezka)))
    return wynik


def dopisz_podzial(wpis: dict) -> None:
    sciezka = SCHEMAT / "podzial.json"
    dane = json.loads(sciezka.read_text(encoding="utf-8"))
    for istniejacy in dane["wpisy"]:
        if (
            istniejacy["ksiega"] == wpis["ksiega"]
            and istniejacy["rozdzial_bg"] == wpis["rozdzial_bg"]
            and istniejacy["werset_bg"] == wpis["werset_bg"]
        ):
            return
    dane["wpisy"].append(wpis)
    zapisz_json(sciezka, dane)
