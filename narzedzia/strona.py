"""Statyczna strona. Szablony tylko wstawiają gotowe zestawienia."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from narzedzia.nawigacja import Nawigacja
from narzedzia.rejestr import wczytaj
from narzedzia.sciezki import DOCS
from narzedzia.statystyki import policz, wedlug_werdyktu
from narzedzia.tekst import zloz
from narzedzia.wiernosc import ETYKIETY, WERDYKTY
from narzedzia.zapis import iteruj_analizy

SZABLONY = Path(__file__).resolve().parent / "szablony"


def _wersety(liczba: int) -> str:
    if liczba == 1:
        return "1 werset"
    koncowka = liczba % 10
    setka = liczba % 100
    if koncowka in (2, 3, 4) and setka not in (12, 13, 14):
        return f"{liczba} wersety"
    return f"{liczba} wersetów"


def srodowisko() -> Environment:
    srodowisko_szablonow = Environment(
        loader=FileSystemLoader(SZABLONY),
        autoescape=select_autoescape(["html"]),
    )
    srodowisko_szablonow.filters["wersety"] = _wersety
    return srodowisko_szablonow


def _widok_powiazania(rekord: dict) -> list[dict]:
    polskie = [token["t"] for token in rekord["tokeny_bg"]]
    zrodlo = [token["t"] for token in rekord["zrodlo"]["tokeny"]]
    grupy = []
    for grupa in rekord["powiazanie"]:
        grupy.append(
            {
                "rola": grupa["rola"],
                "bg": [polskie[indeks] for indeks in grupa["bg"]],
                "zrodlo_slowa": [zrodlo[indeks] for indeks in grupa["zrodlo"]],
                "uwaga": grupa.get("uwaga", ""),
            }
        )
    return grupy


def _skok_js(ksiegi: list[dict]) -> str:
    dane = [{"kod": ksiega["kod"], "klucz": zloz(ksiega["skrot"])} for ksiega in ksiegi]
    return """const KSIEGI = %s;

function zloz(tekst) {
  return tekst.toLowerCase().normalize("NFD").replace(/\\p{M}/gu, "").replaceAll("y", "i").replaceAll("ſ", "s").replaceAll("ƺ", "sz");
}

function dopelnij(liczba, szerokosc) {
  return String(liczba).padStart(szerokosc, "0");
}

function znajdz(tekst) {
  const linia = tekst.trim();
  let trafienie = linia.match(/^(\\d{2}-[a-z]+)\\s+(\\d+):(\\d+)$/i);
  if (trafienie) {
    return "w/" + trafienie[1].toLowerCase() + "/" + dopelnij(trafienie[2], 2) + "/" + dopelnij(trafienie[3], 3) + ".html";
  }
  trafienie = linia.match(/^(\\d{2}-[a-z]+)\\s+(\\d+)$/i);
  if (trafienie) {
    return "k/" + trafienie[1].toLowerCase() + "/" + dopelnij(trafienie[2], 2) + ".html";
  }
  trafienie = linia.match(/^(\\d{2}-[a-z]+)$/i);
  if (trafienie) {
    return "k/" + trafienie[1].toLowerCase() + "/index.html";
  }
  const zwarte = zloz(linia.replace(/\\s+/g, ""));
  const skroty = KSIEGI.slice().sort((a, b) => b.klucz.length - a.klucz.length);
  for (const ksiega of skroty) {
    if (!zwarte.startsWith(ksiega.klucz)) continue;
    const reszta = zwarte.slice(ksiega.klucz.length);
    if (!reszta) return "k/" + ksiega.kod + "/index.html";
    trafienie = reszta.match(/^(\\d+)[,:](\\d+)$/);
    if (trafienie) {
      return "w/" + ksiega.kod + "/" + dopelnij(trafienie[1], 2) + "/" + dopelnij(trafienie[2], 3) + ".html";
    }
    trafienie = reszta.match(/^(\\d+)$/);
    if (trafienie) return "k/" + ksiega.kod + "/" + dopelnij(trafienie[1], 2) + ".html";
    return null;
  }
  return null;
}

document.getElementById("skok").addEventListener("submit", (zdarzenie) => {
  zdarzenie.preventDefault();
  const cel = znajdz(document.getElementById("adres").value);
  const blad = document.getElementById("skok-blad");
  if (!cel) {
    blad.hidden = false;
    blad.textContent = "Nie ma takiego adresu. Przykład: Ps 22,17 albo 19-psa 22:17.";
    return;
  }
  blad.hidden = true;
  window.location.href = document.body.dataset.korzen + cel;
});
""" % json.dumps(dane, ensure_ascii=False)


def zbuduj(cel: Path | None = None, wydanie=None, ksiegi: list[dict] | None = None, analizy: list[dict] | None = None) -> Path:
    cel = cel or DOCS
    ksiegi = wczytaj() if ksiegi is None else ksiegi
    if wydanie is None:
        from narzedzia.adaptery.bg import BibliaGdanska
        from narzedzia.sciezki import ZRODLA

        wydanie = BibliaGdanska(ZRODLA / "biblia-druk-tekst")
    if analizy is None:
        analizy = [rekord for _sciezka, rekord in iteruj_analizy()]
    po_adresie = {(rekord["adres"]["ksiega"], rekord["adres"]["rozdzial"], rekord["adres"]["werset"]): rekord for rekord in analizy}
    pelny_kanon = wydanie.kanon()
    kanon = [(ksiega, rozdzial, werset) for ksiega, rozdzial, werset, _tekst in pelny_kanon]
    teksty = {(ksiega, rozdzial, werset): tekst for ksiega, rozdzial, werset, tekst in pelny_kanon}
    nawigacja = Nawigacja(kanon)
    stat = policz(len(kanon), analizy)
    grupy = wedlug_werdyktu(analizy)
    po_kodzie = {ksiega["kod"]: ksiega for ksiega in ksiegi}
    srodowisko_szablonow = srodowisko()
    if cel.exists():
        shutil.rmtree(cel)
    cel.mkdir(parents=True)
    shutil.copyfile(SZABLONY / "style.css", cel / "style.css")
    (cel / "skok.js").write_text(_skok_js(ksiegi), encoding="utf-8")
    (cel / ".nojekyll").write_text("", encoding="utf-8")
    (cel / "statystyki.json").write_text(json.dumps(stat, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    postep = []
    for ksiega in ksiegi:
        wlasne = [adres for adres in kanon if adres[0] == ksiega["kod"]]
        rozdzialy = []
        for numer in wydanie.rozdzialy(ksiega["kod"]):
            wersety_rozdzialu = [adres for adres in wlasne if adres[1] == numer]
            rozdzialy.append(
                {
                    "numer": numer,
                    "wersetow": len(wersety_rozdzialu),
                    "zanalizowanych": sum(1 for adres in wersety_rozdzialu if adres in po_adresie),
                }
            )
        postep.append(
            {
                **ksiega,
                "wersetow": len(wlasne),
                "zanalizowanych": sum(pozycja["zanalizowanych"] for pozycja in rozdzialy),
                "rozdzialy": rozdzialy,
            }
        )

    srodowisko_szablonow.get_template("index.html").stream(
        tytul="Analiza Biblii Gdańskiej",
        korzen="",
        stat=stat,
        etykiety=ETYKIETY,
        ksiegi=postep,
    ).dump(str(cel / "index.html"), encoding="utf-8")

    for ksiega in postep:
        katalog = cel / "k" / ksiega["kod"]
        katalog.mkdir(parents=True)
        srodowisko_szablonow.get_template("ksiega.html").stream(
            tytul=ksiega["nazwa"],
            korzen="../../",
            ksiega=ksiega,
            rozdzialy=ksiega["rozdzialy"],
        ).dump(str(katalog / "index.html"), encoding="utf-8")
        for rozdzial in ksiega["rozdzialy"]:
            wersety = []
            for numer in range(1, rozdzial["wersetow"] + 1):
                rekord = po_adresie.get((ksiega["kod"], rozdzial["numer"], numer))
                wersety.append(
                    {
                        "numer": numer,
                        "stan": ETYKIETY[rekord["wiernosc"]["werdykt"]] if rekord else "Brak analizy",
                    }
                )
            pierwszy = (ksiega["kod"], rozdzial["numer"], 1)
            sasiedzi = nawigacja.werset(*pierwszy) if pierwszy in nawigacja._pozycja else {}
            srodowisko_szablonow.get_template("rozdzial.html").stream(
                tytul=f"{ksiega['skrot']} {rozdzial['numer']}",
                korzen="../../",
                ksiega=ksiega,
                rozdzial=rozdzial["numer"],
                wersety=wersety,
                poprzedni=sasiedzi.get("poprzedni_rozdzial"),
                nastepny=sasiedzi.get("nastepny_rozdzial"),
            ).dump(str(katalog / f"{rozdzial['numer']:02d}.html"), encoding="utf-8")

    for ksiega, rozdzial, werset in kanon:
        rekord = po_adresie.get((ksiega, rozdzial, werset))
        widok = None
        if rekord:
            widok = dict(rekord)
            widok["powiazanie"] = _widok_powiazania(rekord)
        sasiedzi = nawigacja.werset(ksiega, rozdzial, werset)
        katalog = cel / "w" / ksiega / f"{rozdzial:02d}"
        katalog.mkdir(parents=True, exist_ok=True)
        opis = po_kodzie[ksiega]
        srodowisko_szablonow.get_template("werset.html").stream(
            tytul=f"{opis['skrot']} {rozdzial},{werset}",
            korzen="../../../",
            ksiega=opis,
            rozdzial=rozdzial,
            werset=werset,
            tekst=teksty[(ksiega, rozdzial, werset)],
            rekord=widok,
            etykiety=ETYKIETY,
            **sasiedzi,
        ).dump(str(katalog / f"{werset:03d}.html"), encoding="utf-8")

    katalog_werdyktow = cel / "werdykt"
    katalog_werdyktow.mkdir()
    for werdykt in WERDYKTY:
        adresy = []
        for adres in grupy[werdykt]:
            opis = po_kodzie[adres["ksiega"]]
            adresy.append({**adres, "podpis": f"{opis['skrot']} {adres['rozdzial']},{adres['werset']}"})
        srodowisko_szablonow.get_template("werdykt.html").stream(
            tytul=ETYKIETY[werdykt],
            korzen="../",
            etykieta=ETYKIETY[werdykt],
            adresy=adresy,
        ).dump(str(katalog_werdyktow / f"{werdykt}.html"), encoding="utf-8")
    return cel
