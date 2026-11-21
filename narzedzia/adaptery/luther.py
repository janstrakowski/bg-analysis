"""Luther 1545. Submoduł getbible trzyma sumy i adresy, a tekst tylko gdy plik ma pole verses."""

from __future__ import annotations

import json
from pathlib import Path


class Luther:
    ident = "lut1545"

    def __init__(self, katalog: Path):
        self.katalog = katalog

    def werset(self, numer_ksiegi: int, rozdzial: int, werset: int) -> dict:
        sciezka = self.katalog / str(numer_ksiegi) / f"{rozdzial}.json"
        if sciezka.is_file():
            dane = json.loads(sciezka.read_text(encoding="utf-8"))
            for pozycja in dane.get("verses") or []:
                if int(pozycja.get("verse", 0)) == werset:
                    return {
                        "id": self.ident,
                        "dostepny": True,
                        "tekst": str(pozycja.get("text", "")).strip(),
                        "powod": None,
                    }
        return {
            "id": self.ident,
            "dostepny": False,
            "tekst": None,
            "powod": (
                "Submoduł getbible zapisuje dla Lutra 1545 sumy kontrolne i adres API, "
                "nie tekst wersetów."
            ),
        }
