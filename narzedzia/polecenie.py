"""Polecenia, które świeży model wykonuje sam: paczka, sprawdzenie, status, strona."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from narzedzia.paczka import Zrodla, zbuduj
from narzedzia.sciezki import PRACA, SCHEMAT
from narzedzia.strona import zbuduj as zbuduj_strone
from narzedzia.walidacja import sprawdz_z_paczka
from narzedzia.zakres import BladZakresu, rozwin
from narzedzia.zapis import iteruj_analizy, sciezka_wersetu, wczytaj_json, zapisz_json


def _tekst_zakresu(wartosc: str) -> str:
    sciezka = Path(wartosc)
    if sciezka.is_file():
        return sciezka.read_text(encoding="utf-8")
    return wartosc


def _zakres(zrodla: Zrodla, wartosc: str):
    return rozwin(_tekst_zakresu(wartosc), zrodla.bg, zrodla.ksiegi)


def _paczka(argumenty, zrodla: Zrodla) -> int:
    try:
        adresy = _zakres(zrodla, argumenty.zakres)
    except (BladZakresu, KeyError, FileNotFoundError) as blad:
        print(blad, file=sys.stderr)
        return 2
    paczki = [zbuduj(zrodla, *adres, zapisuj_podzial=True) for adres in adresy]
    json.dump(paczki if len(paczki) > 1 else paczki[0], sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


def _sprawdz(argumenty, zrodla: Zrodla) -> int:
    rekord = wczytaj_json(Path(argumenty.plik))
    adres = rekord["adres"]
    paczka = zbuduj(zrodla, adres["ksiega"], adres["rozdzial"], adres["werset"])
    bledy = sprawdz_z_paczka(rekord, paczka)
    if bledy:
        print("\n".join(bledy), file=sys.stderr)
        return 1
    print(f"{rekord['id']}: zgodne ze schematem i z paczką")
    return 0


def _status(argumenty, zrodla: Zrodla) -> int:
    try:
        adresy = _zakres(zrodla, argumenty.zakres)
    except (BladZakresu, KeyError, FileNotFoundError) as blad:
        print(blad, file=sys.stderr)
        return 2
    kod = 0
    for ksiega, rozdzial, werset in adresy:
        sciezka = sciezka_wersetu(ksiega, rozdzial, werset)
        adres = f"{ksiega} {rozdzial}:{werset}"
        if not sciezka.is_file():
            print(f"{adres} brak")
            continue
        try:
            rekord = wczytaj_json(sciezka)
            paczka = zbuduj(zrodla, ksiega, rozdzial, werset)
            bledy = sprawdz_z_paczka(rekord, paczka)
        except (json.JSONDecodeError, KeyError, FileNotFoundError) as blad:
            print(f"{adres} bledne: {blad}")
            kod = 1
            continue
        if bledy:
            print(f"{adres} bledne: {bledy[0]}")
            kod = 1
        else:
            print(f"{adres} gotowe")
    return kod


def _terminy(_argumenty, _zrodla: Zrodla) -> int:
    sciezka = SCHEMAT / "terminologia.json"
    dane = wczytaj_json(sciezka)
    lematy = dane.setdefault("lematy", {})
    for _plik, rekord in iteruj_analizy():
        for propozycja in rekord.get("propozycje_terminow", []):
            wpis = lematy.setdefault(propozycja["lemma"], {"odpowiedniki": [], "zrodla": []})
            if propozycja["propozycja"] not in wpis["odpowiedniki"]:
                wpis["odpowiedniki"].append(propozycja["propozycja"])
            if rekord["id"] not in wpis["zrodla"]:
                wpis["zrodla"].append(rekord["id"])
    zapisz_json(sciezka, dane)
    print(f"Kartoteka: {len(lematy)} lematów")
    return 0


def _strona(_argumenty, _zrodla: Zrodla) -> int:
    cel = zbuduj_strone()
    print(cel)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m narzedzia.polecenie")
    parser.add_argument("--zakres", help=argparse.SUPPRESS)
    podpolecenia = parser.add_subparsers(dest="polecenie", required=True)

    paczka = podpolecenia.add_parser("paczka")
    paczka.add_argument("--zakres", required=True)
    paczka.set_defaults(funkcja=_paczka)

    sprawdz = podpolecenia.add_parser("sprawdz")
    sprawdz.add_argument("plik")
    sprawdz.set_defaults(funkcja=_sprawdz)

    status = podpolecenia.add_parser("status")
    status.add_argument("--zakres", required=True)
    status.set_defaults(funkcja=_status)

    terminy = podpolecenia.add_parser("terminy")
    terminy.set_defaults(funkcja=_terminy)

    strona = podpolecenia.add_parser("strona")
    strona.set_defaults(funkcja=_strona)

    argumenty = parser.parse_args(argv)
    PRACA.mkdir(exist_ok=True)
    zrodla = None if argumenty.polecenie in {"strona", "terminy"} else Zrodla()
    return argumenty.funkcja(argumenty, zrodla)


if __name__ == "__main__":
    raise SystemExit(main())
