"""Krótka glosa z TBESH i TBESG. Bierzemy kolumnę Gloss, nie hasła objęte cudzym prawem."""

from __future__ import annotations

import re
from pathlib import Path

_WIERSZ = re.compile(r"^[HG]\d")
_LEMAT = re.compile(r"^([HG]\d+)[A-Z]*$")


class Leksykon:
    def __init__(self, katalog: Path):
        self._po_d: dict[str, str] = {}
        self._po_e: dict[str, str] = {}
        for sciezka in sorted(katalog.glob("TBES*.txt")):
            self._wczytaj(sciezka)

    def _wczytaj(self, sciezka: Path) -> None:
        for wiersz in sciezka.read_text(encoding="utf-8").splitlines():
            if not _WIERSZ.match(wiersz):
                continue
            kolumny = wiersz.split("\t")
            if len(kolumny) < 7:
                continue
            e_strong = kolumny[0].strip()
            d_strong = kolumny[1].strip().split()[0]
            glosa = kolumny[6].strip()
            self._po_d.setdefault(d_strong, glosa)
            self._po_e.setdefault(e_strong, glosa)

    def glosa(self, lemma: str) -> str:
        if lemma in self._po_d:
            return self._po_d[lemma]
        trafienie = _LEMAT.match(lemma)
        if trafienie and trafienie.group(1) in self._po_e:
            return self._po_e[trafienie.group(1)]
        return ""
