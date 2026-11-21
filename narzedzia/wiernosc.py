"""Werdykt wierności wynika z powiązania słów, nie z osobnego elaboratu."""

from __future__ import annotations

WERDYKTY = (
    "wierny",
    "wierny_z_dopelnieniem",
    "sens_zachowany_forma_wolna",
    "sens_przesuniety",
    "nieoddane",
)

ETYKIETY = {
    "wierny": "Wierny",
    "wierny_z_dopelnieniem": "Wierny z dopowiedzeniem",
    "sens_zachowany_forma_wolna": "Sens zachowany, forma wolna",
    "sens_przesuniety": "Sens przesunięty",
    "nieoddane": "Nieoddane",
}


def rozlicz(rekord: dict, kursywa: set[int] | None = None) -> dict:
    """Liczy dopowiedzenia, opuszczenia i dopowiedzenia bez uzasadnienia."""
    oznaczone = kursywa or set()
    dopelnienia: list[int] = []
    opuszczenia: list[int] = []
    nieuzasadnione: list[int] = []
    for grupa in rekord["powiazanie"]:
        if grupa["rola"] == "dopelnienie":
            for indeks in grupa["bg"]:
                dopelnienia.append(indeks)
                if indeks not in oznaczone and not grupa.get("uzasadnienie"):
                    nieuzasadnione.append(indeks)
        elif grupa["rola"] == "opuszczenie":
            opuszczenia.extend(grupa["zrodlo"])
    return {
        "dopelnienia": dopelnienia,
        "opuszczenia": opuszczenia,
        "nieuzasadnione": nieuzasadnione,
    }


def sprawdz_werdykt(rekord: dict, kursywa: set[int] | None = None) -> list[str]:
    bledy: list[str] = []
    wiernosc = rekord["wiernosc"]
    werdykt = wiernosc["werdykt"]
    if werdykt not in WERDYKTY:
        return [f"Nieznany werdykt: {werdykt}"]
    listy = rozlicz(rekord, kursywa)
    dopelnienia = listy["dopelnienia"]
    opuszczenia = listy["opuszczenia"]
    nieuzasadnione = listy["nieuzasadnione"]
    wskazane = list(wiernosc.get("tokeny_bg") or []) + list(wiernosc.get("tokeny_zrodla") or [])
    if werdykt == "wierny" and (dopelnienia or opuszczenia):
        bledy.append("Werdykt wierny wymaga pustych dopowiedzeń i opuszczeń.")
    if werdykt == "wierny_z_dopelnieniem":
        if opuszczenia:
            bledy.append("Werdykt wierny z dopowiedzeniem nie znosi opuszczenia treści.")
        if not dopelnienia:
            bledy.append("Werdykt wierny z dopowiedzeniem wymaga oznaczonego dopowiedzenia.")
        if nieuzasadnione:
            bledy.append("Dopowiedzenie bez kursywy 1632 albo uzasadnienia nie jest wiernym dopowiedzeniem.")
    if werdykt == "sens_zachowany_forma_wolna" and (dopelnienia or opuszczenia):
        bledy.append("Sens zachowany przy wolnej formie wymaga pełnego pokrycia, bez dopowiedzeń i opuszczeń.")
    if werdykt == "sens_przesuniety":
        if opuszczenia or nieuzasadnione:
            bledy.append("Przesunięcie sensu nie zastępuje opuszczenia ani nieuzasadnionego dopowiedzenia.")
        if not wskazane:
            bledy.append("Przesunięcie sensu musi wskazać tokeny.")
    if werdykt == "nieoddane":
        if not opuszczenia and not nieuzasadnione:
            bledy.append("Werdykt nieoddane wymaga opuszczenia treści albo dopowiedzenia bez uzasadnienia.")
        if not wskazane:
            bledy.append("Werdykt nieoddane musi wskazać tokeny.")
    for indeks in kursywa or set():
        grupy = [grupa for grupa in rekord["powiazanie"] if indeks in grupa["bg"]]
        if not grupy:
            continue
        grupa = grupy[0]
        if grupa["rola"] != "dopelnienie" and not grupa.get("wyjatek_kursywy"):
            slowo = rekord["tokeny_bg"][indeks]["t"]
            bledy.append(f"Słowo „{slowo}” jest kursywą w 1632 i ma być dopowiedzeniem.")
    return bledy
