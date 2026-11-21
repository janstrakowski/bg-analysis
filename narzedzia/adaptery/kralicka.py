"""Biblia kralicka z pliku Zefania w submodułie open-bibles."""

from __future__ import annotations

from pathlib import Path

from lxml import etree


class Kralicka:
    ident = "bkr"

    def __init__(self, sciezka: Path):
        self._wersety: dict[tuple[int, int, int], str] = {}
        if not sciezka.is_file():
            return
        drzewo = etree.parse(str(sciezka))
        for ksiega in drzewo.findall("BIBLEBOOK"):
            numer = int(ksiega.get("bnumber"))
            for rozdzial in ksiega.findall("CHAPTER"):
                nr_rozdzialu = int(rozdzial.get("cnumber"))
                for werset in rozdzial.findall("VERS"):
                    self._wersety[(numer, nr_rozdzialu, int(werset.get("vnumber")))] = (werset.text or "").strip()

    def werset(self, numer_ksiegi: int, rozdzial: int, werset: int) -> dict:
        tekst = self._wersety.get((numer_ksiegi, rozdzial, werset))
        if tekst is None:
            return {
                "id": self.ident,
                "dostepny": False,
                "tekst": None,
                "powod": f"Brak wersetu kralickiej {numer_ksiegi} {rozdzial}:{werset}.",
            }
        return {"id": self.ident, "dostepny": True, "tekst": tekst, "powod": None}
