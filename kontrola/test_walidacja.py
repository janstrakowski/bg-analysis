import json

from narzedzia.walidacja import sprawdz
from narzedzia.wiernosc import WERDYKTY
from narzedzia.sciezki import SCHEMAT


def _werset():
    return {
        "schemat": "1.0.0",
        "id": "01-gen.1.1",
        "adres": {"wydanie": "1879", "ksiega": "01-gen", "rozdzial": 1, "werset": 1},
        "tekst_bg": "Alfa beta.",
        "tokeny_bg": [{"i": 0, "t": "Alfa"}, {"i": 1, "t": "beta"}],
        "zrodlo": {
            "wydanie": "MT",
            "jezyk": "hbo",
            "adres": "Gen.1.1",
            "adres_hebrajski": "Gen.1.1",
            "adres_angielski": "Gen.1.1",
            "rozjazd_numeracji": False,
            "tokeny": [
                {"i": 0, "t": "א", "lemma": "H1", "morph": "H", "glosa": "a", "leksykon": "", "id": "Gen.1.1#01", "jezyk": "hbo"},
                {"i": 1, "t": "ב", "lemma": "H2", "morph": "H", "glosa": "b", "leksykon": "", "id": "Gen.1.1#02", "jezyk": "hbo"},
            ],
        },
        "powiazanie": [
            {"rola": "przeklad", "bg": [0], "zrodlo": [0], "uwaga": "a"},
            {"rola": "przeklad", "bg": [1], "zrodlo": [1], "uwaga": "b"},
        ],
        "wiernosc": {"werdykt": "wierny", "uzasadnienie": "Słowa się pokrywają.", "tokeny_bg": [], "tokeny_zrodla": []},
        "twierdzenia": [{"rodzaj": "stwierdzenie", "tekst": "Pokrycie jest pełne.", "tokeny_bg": [0, 1], "tokeny_zrodla": [0, 1]}],
        "propozycje_terminow": [],
        "paralele": [],
    }


def test_schemat_ma_te_same_werdykty():
    schemat = json.loads((SCHEMAT / "werset.schema.json").read_text(encoding="utf-8"))
    assert tuple(schemat["properties"]["wiernosc"]["properties"]["werdykt"]["enum"]) == WERDYKTY


def test_pelne_pokrycie_przechodzi():
    assert sprawdz(_werset()) == []


def test_brak_slowa_polskiego_odrzuca():
    rekord = _werset()
    rekord["powiazanie"].pop()
    bledy = sprawdz(rekord)
    assert any("polskie" in blad for blad in bledy)


def test_wierny_przy_opuszczeniu_odrzuca():
    rekord = _werset()
    rekord["powiazanie"] = [
        {"rola": "przeklad", "bg": [0, 1], "zrodlo": [0], "uwaga": "a"},
        {"rola": "opuszczenie", "bg": [], "zrodlo": [1], "uwaga": "b"},
    ]
    rekord["wiernosc"]["werdykt"] = "wierny"
    bledy = sprawdz(rekord)
    assert any("wierny" in blad for blad in bledy)


def test_nieoddane_bez_wskazania_tokenu_odrzuca():
    rekord = _werset()
    rekord["powiazanie"] = [
        {"rola": "przeklad", "bg": [0], "zrodlo": [0], "uwaga": "a"},
        {"rola": "opuszczenie", "bg": [], "zrodlo": [1], "uwaga": "b"},
        {"rola": "dopelnienie", "bg": [1], "zrodlo": [], "uwaga": "dodane"},
    ]
    rekord["wiernosc"] = {
        "werdykt": "nieoddane",
        "uzasadnienie": "Słowo źródła zniknęło.",
        "tokeny_bg": [],
        "tokeny_zrodla": [],
    }
    bledy = sprawdz(rekord)
    assert any("wskazać" in blad for blad in bledy)
