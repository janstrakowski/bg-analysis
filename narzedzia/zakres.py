"""Zakres pracy: jeden werset, rozdział, księga albo kilka zakresów naraz."""

from __future__ import annotations

import re

from narzedzia.rejestr import po_kodzie, po_skrocie
from narzedzia.tekst import zloz

_KOD_ZAKRES = re.compile(r"^(\d+):(\d+)-(\d+)$")
_KOD_WERSET = re.compile(r"^(\d+):(\d+)$")
_KOD_ROZDZIAL = re.compile(r"^(\d+)$")
_SKROT_ZAKRES = re.compile(r"^(\d+)[,:](\d+)-(\d+)$")
_SKROT_WERSET = re.compile(r"^(\d+)[,:](\d+)$")
_SKROT_ROZDZIAL = re.compile(r"^(\d+)$")


class BladZakresu(ValueError):
    pass


def _rozwin_ksiege(kod: str, rozdzial: int | None, od: int | None, do: int | None, wydanie) -> list[tuple[str, int, int]]:
    rozdzialy = [rozdzial] if rozdzial is not None else wydanie.rozdzialy(kod)
    wynik: list[tuple[str, int, int]] = []
    for numer in rozdzialy:
        ostatni = wydanie.liczba_wersetow(kod, numer)
        poczatek = od if od is not None and numer == rozdzial else 1
        koniec = do if do is not None and numer == rozdzial else ostatni
        if poczatek < 1 or koniec > ostatni or poczatek > koniec:
            raise BladZakresu(f"Zakres {kod} {numer}:{poczatek}-{koniec} wychodzi poza rozdział ({ostatni} wersetów).")
        wynik.extend((kod, numer, werset) for werset in range(poczatek, koniec + 1))
    return wynik


def _z_kodu(tekst: str, ksiegi: dict[str, dict]) -> tuple[str, int | None, int | None, int | None] | None:
    czesci = tekst.split()
    if not czesci or czesci[0] not in ksiegi:
        return None
    kod = czesci[0]
    if len(czesci) == 1:
        return kod, None, None, None
    if len(czesci) != 2:
        raise BladZakresu(f"Nieczytelny zakres: {tekst}")
    reszta = czesci[1]
    for wzor, pola in (
        (_KOD_ZAKRES, lambda m: (int(m.group(1)), int(m.group(2)), int(m.group(3)))),
        (_KOD_WERSET, lambda m: (int(m.group(1)), int(m.group(2)), int(m.group(2)))),
        (_KOD_ROZDZIAL, lambda m: (int(m.group(1)), None, None)),
    ):
        trafienie = wzor.fullmatch(reszta)
        if trafienie:
            rozdzial, od, do = pola(trafienie)
            return kod, rozdzial, od, do
    raise BladZakresu(f"Nieczytelny zakres: {tekst}")


def _ze_skrotu(tekst: str, skroty: dict[str, dict]) -> tuple[str, int | None, int | None, int | None]:
    zwarte = zloz(tekst.replace(" ", ""))
    kandydaci = sorted(skroty, key=len, reverse=True)
    for skrot in kandydaci:
        if zwarte.startswith(skrot):
            kod = skroty[skrot]["kod"]
            reszta = zwarte[len(skrot) :]
            if not reszta:
                return kod, None, None, None
            for wzor, pola in (
                (_SKROT_ZAKRES, lambda m: (int(m.group(1)), int(m.group(2)), int(m.group(3)))),
                (_SKROT_WERSET, lambda m: (int(m.group(1)), int(m.group(2)), int(m.group(2)))),
                (_SKROT_ROZDZIAL, lambda m: (int(m.group(1)), None, None)),
            ):
                trafienie = wzor.fullmatch(reszta)
                if trafienie:
                    rozdzial, od, do = pola(trafienie)
                    return kod, rozdzial, od, do
            break
    raise BladZakresu(f"Nieczytelny zakres: {tekst}")


def rozwin(tekst: str, wydanie, ksiegi: list[dict] | None = None) -> list[tuple[str, int, int]]:
    from narzedzia.rejestr import wczytaj

    dane = wczytaj() if ksiegi is None else ksiegi
    kody = po_kodzie(dane)
    skroty = po_skrocie(dane)
    wynik: list[tuple[str, int, int]] = []
    for surowa in tekst.splitlines():
        linia = surowa.split("#", 1)[0].strip()
        if not linia:
            continue
        opis = _z_kodu(linia, kody)
        if opis is None:
            opis = _ze_skrotu(linia, skroty)
        kod, rozdzial, od, do = opis
        wynik.extend(_rozwin_ksiege(kod, rozdzial, od, do, wydanie))
    if not wynik:
        raise BladZakresu("Zakres jest pusty.")
    return wynik
