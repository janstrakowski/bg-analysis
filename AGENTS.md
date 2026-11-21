# Zadanie

To repozytorium analizuje Biblię Gdańską z 1879 roku słowo po słowie wobec tekstu, z którego tłumaczono: tekstu masoreckiego w Starym Testamencie i Textus Receptus w Nowym. Nie oceniasz, czy to źródło należałoby czytać inaczej.

Zanim cokolwiek zapiszesz, przeczytaj `schemat/prompt-analizy.md` i `schemat/werset.schema.json`.

## Zakres

Weź zakres z polecenia użytkownika. Gdy go tam nie ma, czytaj `praca/zakres.txt` (wiele zakresów, jeden na linię). Gdy nie ma ani polecenia, ani tego pliku, nie ruszaj kanonu. Wypisz, jak podać zakres, i na tym skończ.

Przyjęte zapisy zakresu: `01-gen 1:1-5`, `01-gen 1`, `01-gen`, `62-joh 5:7`, `Ps 22,17`.

## Jedna jednostka pracy

Plik wersetu to `analiza/<ksiega>/<rozdzial>/<werset>.json`. Dwa przebiegi na rozłącznych zakresach nie zapisują tego samego pliku. Plik, który przechodzi `sprawdz`, zostaw. Nie edytuj wersetów spoza zakresu i nie edytuj `schemat/terminologia.json`.

Dla każdego wersetu zakresu bez poprawnego pliku:

1. `python -m narzedzia.polecenie paczka --zakres "01-gen 1:1"`
2. Ułóż JSON według `schemat/prompt-analizy.md`.
3. Zapisz go we właściwej ścieżce.
4. `python -m narzedzia.polecenie sprawdz analiza/01-gen/01/001.json`
5. Poprawiaj, aż polecenie przejdzie.

Stan zakresu: `python -m narzedzia.polecenie status --zakres praca/zakres.txt`.

Kartotekę lematów scala tylko osobne, jednowątkowe polecenie `python -m narzedzia.polecenie terminy`. Nie rób tego w trakcie równoległej analizy.

## Źródła

Są w `zrodla/` jako submoduły. Paczka czyta je sama. Biblia brzeska dojdzie jako `zrodla/brzeska` w układzie `ksiega/rozdzial.txt`, takim jak `1879` w `biblia-druk-tekst`. Do tej pory adapter zwraca brak tekstu.

## Strona

`python -m narzedzia.polecenie strona` buduje `docs/` z tych samych plików JSON. Nie pisz HTML wersetów ręcznie.
