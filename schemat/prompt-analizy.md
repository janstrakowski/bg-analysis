# Kontrakt analizy jednego wersetu

Dostajesz jedną paczkę JSON z polecenia `python -m narzedzia.polecenie paczka`. Oddajesz jeden obiekt JSON zgodny z `schemat/werset.schema.json`. Nic poza tym obiektem.

Paczka jest faktem. Nie poprawiasz w niej tekstu masoreckiego ani Textus Receptus i nie oceniasz, czy źródło należałoby czytać inaczej.

Zasady zapisu:

- `tokeny_bg` i `zrodlo.tokeny` przepisz z paczki bez zmiany kolejności i pisowni.
- Każdy indeks polski i każdy indeks źródłowy należy do dokładnie jednej grupy w `powiazanie`.
- Role: `przeklad`, `dopelnienie`, `opuszczenie`, `zlanie`, `rozbicie`.
- Słowo z `kursywa_1632` ma rolę `dopelnienie`, chyba że w grupie podasz `wyjatek_kursywy`.
- Dopowiedzenie spoza kursywy wymaga pola `uzasadnienie`. Bez niego werdykt ma być `nieoddane`.
- Opuszczenie słowa źródła też daje werdykt `nieoddane`.
- `wierny` tylko wtedy, gdy nie ma dopowiedzenia ani opuszczenia.
- `sens_przesuniety` i `nieoddane` wskazują tokeny w `wiernosc.tokeny_bg` albo `wiernosc.tokeny_zrodla`.
- Każde zdanie w `twierdzenia` ma rodzaj `stwierdzenie`, `hipoteza` albo `niepewne`. `stwierdzenie` wynika z tokenów paczki. Wpływ, którego paczka nie dowodzi, jest hipotezą.
- Glosa bierze się z pola `glosa` albo `leksykon`. Nie wklejaj HALOT-u ani BDAG-u.
- Paralela z `dostepny: false` nie istnieje. Nie zgaduj jej brzmienia. O brzeskiej nie pisz, dopóki paczka jej nie poda.
- Propozycję stałego odpowiednika lematu zapisz w `propozycje_terminow` tego wersetu. Nie edytuj `schemat/terminologia.json`.
- Zapis sprawdź poleceniem `python -m narzedzia.polecenie sprawdz` i poprawiaj, aż przejdzie.
