"""Czysta kontrola zapisu: schemat, pokrycie słów i zgodność werdyktu."""

from __future__ import annotations

import json

from jsonschema import Draft202012Validator

from narzedzia.sciezki import SCHEMAT
from narzedzia.wiernosc import sprawdz_werdykt

ROLE = {"przeklad", "dopelnienie", "opuszczenie", "zlanie", "rozbicie"}
RODZAJE = {"stwierdzenie", "hipoteza", "niepewne"}

_WALIDATOR: Draft202012Validator | None = None


def walidator() -> Draft202012Validator:
    global _WALIDATOR
    if _WALIDATOR is None:
        schemat = json.loads((SCHEMAT / "werset.schema.json").read_text(encoding="utf-8"))
        _WALIDATOR = Draft202012Validator(schemat)
    return _WALIDATOR


def _ciaglosc(tokeny: list[dict], nazwa: str) -> list[str]:
    bledy = []
    for oczekiwany, token in enumerate(tokeny):
        if token.get("i") != oczekiwany:
            bledy.append(f"{nazwa}[{oczekiwany}] ma indeks {token.get('i')}.")
        if not str(token.get("t", "")).strip():
            bledy.append(f"{nazwa}[{oczekiwany}] nie ma tekstu.")
    return bledy


def _pokrycie(rekord: dict) -> list[str]:
    bledy: list[str] = []
    widziane_bg: set[int] = set()
    widziane_zrodlo: set[int] = set()
    for numer, grupa in enumerate(rekord["powiazanie"]):
        rola = grupa["rola"]
        if rola not in ROLE:
            bledy.append(f"Grupa {numer} ma nieznaną rolę {rola}.")
            continue
        bg = list(grupa["bg"])
        zrodlo = list(grupa["zrodlo"])
        if rola == "dopelnienie" and (not bg or zrodlo):
            bledy.append(f"Grupa {numer}: dopowiedzenie obejmuje tylko słowa polskie.")
        if rola == "opuszczenie" and (not zrodlo or bg):
            bledy.append(f"Grupa {numer}: opuszczenie obejmuje tylko słowa źródła.")
        if rola in {"przeklad", "zlanie", "rozbicie"} and (not bg or not zrodlo):
            bledy.append(f"Grupa {numer}: {rola} łączy słowa polskie ze źródłem.")
        for indeks in bg:
            if indeks in widziane_bg:
                bledy.append(f"Polskie słowo {indeks} jest w dwóch grupach.")
            widziane_bg.add(indeks)
        for indeks in zrodlo:
            if indeks in widziane_zrodlo:
                bledy.append(f"Słowo źródła {indeks} jest w dwóch grupach.")
            widziane_zrodlo.add(indeks)
    oczekiwane_bg = set(range(len(rekord["tokeny_bg"])))
    oczekiwane_zrodlo = set(range(len(rekord["zrodlo"]["tokeny"])))
    if widziane_bg != oczekiwane_bg:
        brak = sorted(oczekiwane_bg - widziane_bg)
        bledy.append(f"Bez grupy zostały polskie słowa: {brak}.")
    if widziane_zrodlo != oczekiwane_zrodlo:
        brak = sorted(oczekiwane_zrodlo - widziane_zrodlo)
        bledy.append(f"Bez grupy zostały słowa źródła: {brak}.")
    return bledy


def sprawdz(rekord: dict, kursywa: set[int] | None = None) -> list[str]:
    bledy = [f"{'/'.join(map(str, blad.path))}: {blad.message}" for blad in walidator().iter_errors(rekord)]
    if bledy:
        return bledy
    bledy.extend(_ciaglosc(rekord["tokeny_bg"], "tokeny_bg"))
    bledy.extend(_ciaglosc(rekord["zrodlo"]["tokeny"], "zrodlo.tokeny"))
    for twierdzenie in rekord["twierdzenia"]:
        if twierdzenie["rodzaj"] not in RODZAJE:
            bledy.append(f"Nieznany rodzaj twierdzenia: {twierdzenie['rodzaj']}.")
    bledy.extend(_pokrycie(rekord))
    bledy.extend(sprawdz_werdykt(rekord, kursywa))
    return bledy


def sprawdz_z_paczka(rekord: dict, paczka: dict) -> list[str]:
    bledy = sprawdz(rekord, set(paczka["kursywa_1632"]))
    if rekord["tekst_bg"] != paczka["tekst_bg"]:
        bledy.append("tekst_bg nie jest wersetem wydania 1879.")
    if [token["t"] for token in rekord["tokeny_bg"]] != [token["t"] for token in paczka["tokeny_bg"]]:
        bledy.append("Tokeny polskie nie zgadzają się z paczką.")
    if [token["t"] for token in rekord["zrodlo"]["tokeny"]] != [token["t"] for token in paczka["zrodlo"]["tokeny"]]:
        bledy.append("Tokeny źródła nie zgadzają się z paczką.")
    if rekord["zrodlo"]["wydanie"] != paczka["zrodlo"]["wydanie"]:
        bledy.append("Wydanie źródła nie zgadza się z paczką.")
    return bledy
