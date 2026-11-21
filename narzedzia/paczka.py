"""Składa paczkę wersetu bez modelu, wyłącznie z przypiętych źródeł."""

from __future__ import annotations

from narzedzia.adaptery.bg import BibliaGdanska
from narzedzia.adaptery.brzeska import Brzeska
from narzedzia.adaptery.kralicka import Kralicka
from narzedzia.adaptery.leksykon import Leksykon
from narzedzia.adaptery.luther import Luther
from narzedzia.adaptery.mt import TekstMasorecki
from narzedzia.adaptery.tr import TextusReceptus
from narzedzia.rejestr import numer_ksiegi, po_kodzie, wczytaj
from narzedzia.sciezki import ZRODLA
from narzedzia.zapis import dopisz_podzial, wczytaj_json
from narzedzia.sciezki import SCHEMAT


class Zrodla:
    def __init__(self, korzen_zrodel=ZRODLA):
        self.ksiegi = wczytaj()
        self.po_kodzie = po_kodzie(self.ksiegi)
        self.bg = BibliaGdanska(korzen_zrodel / "biblia-druk-tekst")
        katalog_step = korzen_zrodel / "stepbible-data" / "Translators Amalgamated OT+NT"
        self.mt = TekstMasorecki(katalog_step)
        self.tr = TextusReceptus(katalog_step)
        self.leksykon = Leksykon(korzen_zrodel / "stepbible-data" / "Lexicons")
        self.kralicka = Kralicka(korzen_zrodel / "open-bibles" / "cze-bkr.zefania.xml")
        self.luther = Luther(korzen_zrodel / "getbible" / "luther1545")
        self.brzeska = Brzeska(korzen_zrodel / "brzeska")
        self.terminologia = wczytaj_json(SCHEMAT / "terminologia.json")


def _sasiedzi(bg: BibliaGdanska, ksiegi: list[dict], kod: str, rozdzial: int, werset: int) -> dict:
    def adres(k: str, r: int, w: int) -> dict:
        return {"ksiega": k, "rozdzial": r, "werset": w, "tekst": bg.werset(k, r, w)}

    poprzedni = None
    if werset > 1:
        poprzedni = adres(kod, rozdzial, werset - 1)
    elif rozdzial > 1 and (rozdzial - 1) in bg.rozdzialy(kod):
        poprzedni_rozdzial = rozdzial - 1
        poprzedni = adres(kod, poprzedni_rozdzial, bg.liczba_wersetow(kod, poprzedni_rozdzial))
    else:
        indeks = next(i for i, ksiega in enumerate(ksiegi) if ksiega["kod"] == kod)
        if indeks > 0:
            poprzednia = ksiegi[indeks - 1]["kod"]
            poprzedni_rozdzial = bg.rozdzialy(poprzednia)[-1]
            poprzedni = adres(poprzednia, poprzedni_rozdzial, bg.liczba_wersetow(poprzednia, poprzedni_rozdzial))

    nastepny = None
    if werset < bg.liczba_wersetow(kod, rozdzial):
        nastepny = adres(kod, rozdzial, werset + 1)
    elif (rozdzial + 1) in bg.rozdzialy(kod):
        nastepny = adres(kod, rozdzial + 1, 1)
    else:
        indeks = next(i for i, ksiega in enumerate(ksiegi) if ksiega["kod"] == kod)
        if indeks + 1 < len(ksiegi):
            nastepna = ksiegi[indeks + 1]["kod"]
            nastepny = adres(nastepna, bg.rozdzialy(nastepna)[0], 1)
    return {"poprzedni": poprzedni, "nastepny": nastepny}


def _terminy(terminologia: dict, tokeny: list[dict]) -> list[dict]:
    lematy = terminologia.get("lematy", {})
    wynik = []
    widziane = set()
    for token in tokeny:
        lemma = token["lemma"]
        if lemma in lematy and lemma not in widziane:
            widziane.add(lemma)
            wynik.append({"lemma": lemma, "odpowiedniki": lematy[lemma]["odpowiedniki"]})
    return wynik


def zbuduj(zrodla: Zrodla, ksiega: str, rozdzial: int, werset: int, zapisuj_podzial: bool = False) -> dict:
    opis = zrodla.po_kodzie[ksiega]
    tekst = zrodla.bg.tekst_i_kursywa(ksiega, rozdzial, werset)
    if opis["zrodlo"] == "MT":
        zrodlo = zrodla.mt.werset(opis["step"], rozdzial, werset)
    else:
        zrodlo = zrodla.tr.werset(opis["step"], rozdzial, werset)
    for token in zrodlo["tokeny"]:
        token["leksykon"] = zrodla.leksykon.glosa(token["lemma"])
    if zrodlo["adres_hebrajski"] and zrodlo["adres_hebrajski"] != zrodlo["adres_angielski"]:
        wpis = {
            "ksiega": ksiega,
            "rozdzial_bg": rozdzial,
            "werset_bg": werset,
            "adres_hebrajski": zrodlo["adres_hebrajski"],
            "adres_angielski": zrodlo["adres_angielski"],
        }
        zrodlo["rozjazd_numeracji"] = True
        if zapisuj_podzial:
            dopisz_podzial(wpis)
    else:
        zrodlo["rozjazd_numeracji"] = False
    numer = numer_ksiegi(zrodla.ksiegi, ksiega)
    paralele = [
        zrodla.kralicka.werset(numer, rozdzial, werset),
        zrodla.luther.werset(numer, rozdzial, werset),
        zrodla.brzeska.werset(ksiega, rozdzial, werset),
    ]
    return {
        "id": f"{ksiega}.{rozdzial}.{werset}",
        "adres": {"wydanie": "1879", "ksiega": ksiega, "rozdzial": rozdzial, "werset": werset},
        "nazwa": opis["nazwa"],
        "skrot": opis["skrot"],
        **tekst,
        "zrodlo": zrodlo,
        "sasiedzi": _sasiedzi(zrodla.bg, zrodla.ksiegi, ksiega, rozdzial, werset),
        "paralele": paralele,
        "terminologia": _terminy(zrodla.terminologia, zrodlo["tokeny"]),
    }
