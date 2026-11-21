"""Port Biblii brzeskiej. Działa, gdy pojawi się submoduł o układzie księga/rozdział jak w BG."""

from __future__ import annotations

from pathlib import Path

from narzedzia.adaptery.bg import Wydanie


class Brzeska:
    ident = "brz"

    def __init__(self, katalog: Path):
        self.katalog = katalog
        self._wydanie = Wydanie(katalog) if katalog.is_dir() else None

    def werset(self, kod_ksiegi: str, rozdzial: int, werset: int) -> dict:
        if self._wydanie is None:
            return {
                "id": self.ident,
                "dostepny": False,
                "tekst": None,
                "powod": "Brak submodułu zrodla/brzeska.",
            }
        try:
            tekst = self._wydanie.werset(kod_ksiegi, rozdzial, werset)
        except FileNotFoundError:
            return {
                "id": self.ident,
                "dostepny": False,
                "tekst": None,
                "powod": f"Submoduł brzeskiej nie ma wersetu {kod_ksiegi} {rozdzial}:{werset}.",
            }
        return {"id": self.ident, "dostepny": True, "tekst": tekst, "powod": None}
