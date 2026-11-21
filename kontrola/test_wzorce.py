from pathlib import Path

from narzedzia.paczka import Zrodla, zbuduj
from narzedzia.statystyki import policz
from narzedzia.strona import srodowisko
from narzedzia.walidacja import sprawdz_z_paczka
from narzedzia.wiernosc import ETYKIETY, WERDYKTY
from narzedzia.zapis import iteruj_analizy

WZORCE = [
    ("01-gen", 1, 1, "wierny"),
    ("01-gen", 1, 4, "wierny_z_dopelnieniem"),
    ("43-joh", 1, 1, "wierny"),
    ("62-joh", 5, 7, "wierny"),
    ("19-psa", 22, 17, "nieoddane"),
]


def test_wzorce_przechodza_bramke():
    zrodla = Zrodla()
    rekordy = []
    for sciezka, rekord in iteruj_analizy():
        adres = rekord["adres"]
        paczka = zbuduj(zrodla, adres["ksiega"], adres["rozdzial"], adres["werset"])
        assert sprawdz_z_paczka(rekord, paczka) == [], sciezka
        rekordy.append(rekord)
    werdykty = {rekord["id"]: rekord["wiernosc"]["werdykt"] for rekord in rekordy}
    for ksiega, rozdzial, werset, oczekiwany in WZORCE:
        assert werdykty[f"{ksiega}.{rozdzial}.{werset}"] == oczekiwany
    stat = policz(31102, rekordy)
    assert stat["werdykty"]["wierny"] >= 1
    assert stat["werdykty"]["nieoddane"] >= 1
    html = srodowisko().get_template("index.html").render(
        tytul="test",
        korzen="",
        stat=stat,
        etykiety=ETYKIETY,
        ksiegi=[],
    )
    assert f">{stat['werdykty']['wierny']}<" in html
    assert f">{stat['werdykty']['nieoddane']}<" in html
    assert ETYKIETY["wierny"] in html and ETYKIETY["nieoddane"] in html
    for werdykt in WERDYKTY:
        assert f"werdykt/{werdykt}.html" in html
    assert Path("analiza/19-psa/22/017.json").is_file()
