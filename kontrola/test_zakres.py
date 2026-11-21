import pytest

from narzedzia.adaptery.bg import BibliaGdanska
from narzedzia.rejestr import wczytaj
from narzedzia.sciezki import ZRODLA
from narzedzia.tekst import zloz
from narzedzia.zakres import rozwin


@pytest.fixture(scope="module")
def wydanie():
    return BibliaGdanska(ZRODLA / "biblia-druk-tekst")


def test_skroty_nie_zlewaja_sie():
    klucze = [zloz(ksiega["skrot"]) for ksiega in wczytaj()]
    assert len(klucze) == len(set(klucze))


def test_zakres_wersetow_i_skrotu(wydanie):
    assert rozwin("01-gen 1:1-2", wydanie) == [("01-gen", 1, 1), ("01-gen", 1, 2)]
    assert rozwin("Ps 22,17", wydanie) == [("19-psa", 22, 17)]
    assert rozwin("62-joh 5", wydanie)[0] == ("62-joh", 5, 1)
    assert len(rozwin("65-jud", wydanie)) == wydanie.liczba_wersetow("65-jud", 1)


def test_kilka_linii(wydanie):
    tekst = "01-gen 1:1\n# komentarz\n\n19-psa 22:17\n"
    assert rozwin(tekst, wydanie) == [("01-gen", 1, 1), ("19-psa", 22, 17)]
