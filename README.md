# Analiza Biblii Gdańskiej

Słowo po słowie: skąd w wydaniu z 1879 roku wzięło się brzmienie wersetu. Stary Testament jest zestawiany z tekstem masoreckim, Nowy z Textus Receptus. Werdykt dotyczy przekładu.

Świeży model, który dostanie to repozytorium, ma czytać [AGENTS.md](AGENTS.md) i wykonać zapisany tam zakres. Jeden werset to jeden plik `analiza/<księga>/<rozdział>/<werset>.json`.

## Instalacja

Środowisko stawia conda, z kanału conda-forge:

```bash
conda env create -f environment.yml
conda activate bg-analiza
```

Polecenia uruchamia się z korzenia repozytorium, bez osobnej instalacji pakietu:

```bash
python -m narzedzia.polecenie paczka --zakres "01-gen 1:1"
python -m narzedzia.polecenie sprawdz analiza/01-gen/01/001.json
python -m narzedzia.polecenie status --zakres "01-gen 1"
python -m narzedzia.polecenie strona
python -m pytest kontrola
```

## Układ

- `zrodla/` — submoduły: tekst Gdański 1632 i 1879, STEPBible (tekst masorecki, Textus Receptus, glosy), kralicka, getbible (Luther 1545).
- `schemat/` — jedyny standard zapisu, rejestr ksiąg i kontrakt dla modelu.
- `narzedzia/` — paczka, walidacja, werdykt, strona.
- `analiza/` — wersety, które przeszły walidację.
- `docs/` — strona zbudowana z tych plików. Wejście pokazuje liczniki werdyktów.

Luther 1545 jest przypięty jako submoduł getbible. To repozytorium zapisuje sumy kontrolne i adres API, nie sam tekst wersetów, więc paczka oznacza go jako niedostępny, dopóki plik rozdziału nie zawiera pola `verses`. Kralicka jest w submodułie jako tekst.

Dane STEPBible są na licencji CC BY 4.0. Przy cytowaniu: Tyndale House i [STEPBible](https://www.stepbible.org), źródło [STEPBible-Data](https://stepbible.github.io/STEPBible-Data/).

## Wzorce

W `analiza/` są wersety, na których widać oba krańce skali. Rdz 1,1 jest wierny. Ps 22,17 jest nieoddany: כָּאֲרִי („jak lew”) nie ma polskiego odpowiednika, a „przebodli” nie stoi na tokenie masoreckim.
