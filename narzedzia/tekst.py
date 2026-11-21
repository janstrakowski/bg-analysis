"""Dzielenie tekstu na słowa i złożenie pisowni 1632 do 1879."""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher

_SLOWO = re.compile(
    r"[0-9A-Za-z\u00C0-\u024F\u1E00-\u1EFF]+"
    r"(?:['’-][0-9A-Za-z\u00C0-\u024F\u1E00-\u1EFF]+)*"
)
_KURSYWA = re.compile(r"<i>(.*?)</i>", re.DOTALL)


def tokeny(tekst: str) -> list[str]:
    return _SLOWO.findall(tekst)


def zloz(tekst: str) -> str:
    """Sprowadza ortografię 1632 i 1879 do wspólnego kształtu, tylko do zrównania słów."""
    tekst = tekst.replace("ſ", "s").replace("ƺ", "sz").replace("Ʒ", "sz")
    tekst = unicodedata.normalize("NFD", tekst.lower())
    tekst = "".join(znak for znak in tekst if unicodedata.category(znak) != "Mn")
    return tekst.replace("y", "i")


def _tokeny_z_oznaczeniem(tekst: str) -> list[tuple[str, bool]]:
    wynik: list[tuple[str, bool]] = []
    pozycja = 0
    for trafienie in _KURSYWA.finditer(tekst):
        wynik.extend((slowo, False) for slowo in tokeny(tekst[pozycja : trafienie.start()]))
        wynik.extend((slowo, True) for slowo in tokeny(trafienie.group(1)))
        pozycja = trafienie.end()
    wynik.extend((slowo, False) for slowo in tokeny(tekst[pozycja:]))
    return wynik


def indeksy_kursywy(tokeny_bg: list[str], tekst_1632: str) -> list[int]:
    """Indeksy słów 1879, które w 1632 stoją w kursywie."""
    stare = _tokeny_z_oznaczeniem(tekst_1632)
    if not stare or not tokeny_bg:
        return []
    zgodnosc = SequenceMatcher(
        a=[zloz(slowo) for slowo, _ in stare],
        b=[zloz(slowo) for slowo in tokeny_bg],
        autojunk=False,
    )
    indeksy: list[int] = []
    for operacja, i1, i2, j1, j2 in zgodnosc.get_opcodes():
        if operacja != "equal":
            continue
        for i, j in zip(range(i1, i2), range(j1, j2)):
            if stare[i][1]:
                indeksy.append(j)
    return indeksy
