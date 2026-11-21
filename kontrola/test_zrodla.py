import pytest

from narzedzia.adaptery.mt import czy_mt
from narzedzia.adaptery.tr import czy_tr
from narzedzia.paczka import Zrodla, zbuduj
from narzedzia.rejestr import wczytaj


def test_filtry_wydan():
    assert czy_mt("L") and czy_mt("Q")
    assert not czy_mt("X") and not czy_mt("K") and not czy_mt("R")
    assert czy_tr("TR") and czy_tr("NA28+TR+Byz")
    assert not czy_tr("NA28+NA27+SBL")


@pytest.fixture(scope="module")
def zrodla():
    return Zrodla()


def test_kazda_ksiega_ma_zrodlo_pierwszego_wersetu(zrodla):
    for ksiega in wczytaj():
        paczka = zbuduj(zrodla, ksiega["kod"], 1, 1)
        assert paczka["tekst_bg"] == ksiega["incipit"]
        assert paczka["zrodlo"]["tokeny"]
        assert paczka["zrodlo"]["wydanie"] == ksiega["zrodlo"]


def test_rdz_1_4_wykrywa_kursywe(zrodla):
    paczka = zbuduj(zrodla, "01-gen", 1, 4)
    assert paczka["tokeny_bg"][5]["t"] == "była"
    assert paczka["kursywa_1632"] == [5]


def test_psalm_22_17_zostawia_lwa_w_tekscie_masoreckim(zrodla):
    paczka = zbuduj(zrodla, "19-psa", 22, 17)
    assert paczka["zrodlo"]["adres"] == "Psa.22.17"
    assert paczka["zrodlo"]["adres_angielski"] == "Psa.22.16"
    lew = paczka["zrodlo"]["tokeny"][6]
    assert "lion" in lew["glosa"]
    assert "dug" not in lew["t"] and "dug" not in lew["glosa"]


def test_comma_jest_w_textus_receptus(zrodla):
    paczka = zbuduj(zrodla, "62-joh", 5, 7)
    lematy = [token["lemma"] for token in paczka["zrodlo"]["tokeny"]]
    assert "G3772" in lematy
    assert "G3962" in lematy
    assert all(token["jezyk"] == "grc" for token in paczka["zrodlo"]["tokeny"])


def test_mateusz_bierze_wariant_textus_receptus(zrodla):
    paczka = zbuduj(zrodla, "40-mat", 1, 18)
    lematy = [token["lemma"] for token in paczka["zrodlo"]["tokeny"]]
    powierzchnia = [token["t"] for token in paczka["zrodlo"]["tokeny"]]
    assert "G1083" in lematy
    assert "G1078" not in lematy
    assert "γέννησις" in powierzchnia
    niebo = zbuduj(zrodla, "40-mat", 5, 48)
    slowa = [token["t"] for token in niebo["zrodlo"]["tokeny"]]
    assert ["ἐν", "τοῖς", "οὐρανοῖς"] == slowa[slowa.index("ἐν") : slowa.index("ἐν") + 3]
    assert "οὐράνιος" not in slowa


def test_brzeskiej_jeszcze_nie_ma(zrodla):
    paralela = next(pozycja for pozycja in zbuduj(zrodla, "01-gen", 1, 1)["paralele"] if pozycja["id"] == "brz")
    assert paralela["dostepny"] is False
