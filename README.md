# PSE + ENTSO-E - System pobierania danych o produkcji energii

Kompleksowy system do pobierania i analizowania danych o produkcji energii w Polsce z dwóch źródeł:
- **PSE** - dane rynkowe (API PSE v2)
- **ENTSO-E** - szczegółowe dane o produkcji wg. typu źródła (Transparency Platform)

## 🎯 Funkcjonalności

- ✅ Pobieranie danych co 15 minut dla wybranego okresu
- ✅ **Dane z PSE**: wiatr, fotowoltaika, zapotrzebowanie, saldo wymiany
- ✅ **Dane z ENTSO-E**: węgiel, gaz, woda, biomasa, magazyny energii
- ✅ Sumowanie produkcji w MWh dla dowolnego zakresu dat
- ✅ Generowanie miesięcznych sum od 2020 do teraz
- ✅ Tworzenie szeregów czasowych z różną agregacją
- ✅ Eksport danych do CSV i JSON
- ✅ Interaktywny interfejs użytkownika

## 📊 Dostępne dane

### Z PSE API (dane rynkowe - zawsze dostępne):
- **Sumaryczna generacja źródeł wiatrowych [MW]**
- **Sumaryczna generacja źródeł fotowoltaicznych [MW]**
- **Zapotrzebowanie na moc [MW]**
- **Krajowe saldo wymiany międzysystemowej [MW]**

### Z ENTSO-E API (szczegółowa produkcja wg. źródła - wymaga klucza API):
- **Węgiel kamienny [MW]** (Fossil Hard coal)
- **Węgiel brunatny [MW]** (Fossil Brown coal/Lignite)
- **Gaz [MW]** (Fossil Gas)
- **Wiatr lądowy [MW]** (Wind Onshore)
- **Słońce [MW]** (Solar)
- **Woda [MW]** (suma: Hydro Run-of-river + Hydro Water Reservoir)
- **Magazyny energii [MW]** (Energy storage)
- **Biomasa [MW]** (Biomass)

Dane z obu źródeł są pobierane z interwałem 15-minutowym.

## 🔐 Konfiguracja API ENTSO-E (opcjonalne)

Aby pobierać szczegółowe dane z ENTSO-E:

1. Zarejestruj się na https://transparency.entsoe.eu/
2. Pobierz klucz API (Account Settings -> Web API Security Token)
3. Skopiuj plik `.env.example` jako `.env`:
   ```bash
   cp .env.example .env
   ```
4. Wklej klucz API do pliku `.env`:
   ```
   ENTSOE_API_KEY=twój_klucz_api_tutaj
   ```

**📖 Szczegółowa instrukcja**: Zobacz [docs/ENTSOE_API_SETUP.md](docs/ENTSOE_API_SETUP.md)

**⚠️  Bez klucza ENTSO-E** system będzie działał z ograniczonymi danymi (tylko PSE).
**👥 Udostępnianie innym**: Zobacz [docs/INSTALACJA_DLA_INNYCH.md](docs/INSTALACJA_DLA_INNYCH.md) - jak przygotować repozytorium do udostępnienia zespołowi.
## � Struktura Projektu

```
produkcja-energii/
├── src/                              # Główne moduły
│   ├── pse_energy_scraper.py        # Moduł PSE - dane rynkowe
│   ├── entsoe_data_fetcher.py       # Moduł ENTSO-E - dane produkcji
│   ├── combined_energy_data.py      # Łączenie PSE + ENTSO-E
│   └── pse_energy_interactive.py    # Interfejs interaktywny
├── scripts/                          # Skrypty pomocnicze
│   ├── quick.py                     # Szybkie komendy
│   └── examples.py                  # Przykłady użycia
├── docs/                             # Dokumentacja
│   ├── API_EXAMPLES.md              # Przykłady API
│   ├── ENTSOE_API_SETUP.md          # Konfiguracja ENTSO-E ⭐
│   ├── INSTALACJA_DLA_INNYCH.md     # Jak udostępnić repozytorium ⭐
│   ├── QUICK_START.md               # Szybki start
│   ├── NOTATKI_TECHNICZNE.md        # Notatki techniczne
│   └── CHANGELOG.md                 # Historia zmian
├── wyniki/                           # Wygenerowane pliki
├── .env.example                      # Szablon dla klucza API
├── analiza_pse.ipynb                # Jupyter Notebook
├── run.sh                           # Główny skrypt uruchamiający ⭐
├── COMMANDS.md                      # Lista wszystkich komend ⭐
├── README.md                        # Ten plik
└── requirements.txt                 # Zależności Python
```

## 🚀 Instalacja

1. Zainstaluj wymagane biblioteki:
```bash
# Używając skryptu run.sh (zalecane)
./run.sh install

# Lub bezpośrednio
pip install -r requirements.txt
```

## 📖 Użycie

### ⚡ Najszybszy sposób - przez run.sh (ZALECANE)

Użyj wygodnego skryptu `run.sh` który automatyzuje wszystkie operacje:

```bash
# Interfejs interaktywny (menu)
./run.sh interactive

# Suma dla okresu
./run.sh suma 2026-01-01 2026-01-31

# Miesięczne sumy
./run.sh miesieczne 2020 2026

# Szereg czasowy (dzienny)
./run.sh szereg 2026-01-01 2026-01-31 1D

# Przykłady
./run.sh examples

# Pomoc
./run.sh help
```

**📋 Pełna lista komend:** Zobacz [COMMANDS.md](COMMANDS.md)

### Alternatywnie - bezpośrednie wywołanie

#### Quick - Szybki dostęp

```bash
# Suma dla okresu
python3 scripts/quick.py suma 2026-01-01 2026-01-31

# Miesięczne sumy
python3 scripts/quick.py miesieczne 2020 2026

# Szereg czasowy (dzienny)
python3 scripts/quick.py szereg 2026-01-01 2026-01-31 1D
```

#### Wersja interaktywna

```bash
python3 src/pse_energy_interactive.py
```

Pojawi się menu z opcjami:
1. **Suma dla wybranego okresu** - podajesz zakres dat i otrzymujesz sumaryczną produkcję
2. **Miesięczne sumy od 2020 do teraz** - generuje miesięczne sumy dla wybranych lat
3. **Szereg czasowy** - tworzy szereg z wybraną agregacją (godzinową/dzienną/tygodniową/miesięczną)
4. **Pełna analiza** - wykonuje wszystkie analizy i eksportuje dane

#### Przykłady w Pythonie

```bash
python3 scripts/examples.py
```

Pokazuje 5 różnych przykładów użycia biblioteki programistycznie.

## 💡 Przykłady użycia

### Przykład 1: Suma dla stycznia 2026

```bash
./run.sh suma 2026-01-01 2026-01-31
```

Wynik:
```
WIATR:
  Suma MW:          5,342,981.86 MW
  Energia:          1,335,745.47 MWh
  Średnia:          3,550.15 MW

FOTOWOLTAIKA:
  Suma MW:          899,346.61 MW
  Energia:          224,836.65 MWh
  Średnia:          597.57 MW

RAZEM:
  Suma MW:          6,242,328.47 MW
  Energia:          1,560,582.12 MWh
```

### Przykład 2: Miesięczne sumy 2020-2026

```bash
./run.sh miesieczne 2020 2026
```

### Przykład 3: Dzienny szereg czasowy

```bash
./run.sh szereg 2026-01-01 2026-01-31 1D
```

## 📁 Pliki wyjściowe

Skrypt generuje następujące pliki w folderze `wyniki/`:

- `dane_surowe.csv` - surowe dane z PSE (co 15 min)
- `sumy_miesieczne.csv` - miesięczne sumy produkcji w MWh
- `szereg_czasowy_*.csv` - szereg czasowy z wybraną agregacją

**Format CSV**: Pliki używają **europejskiego formatu CSV**:
- Separator kolumn: `;` (średnik)
- Separator dziesiętny: `,` (przecinek)
- Kodowanie: UTF-8 z BOM (otwiera się poprawnie w Excel)
- `podsumowanie.json` - podsumowanie w formacie JSON

## ⚙️ Konfiguracja

### Format dat

Skrypt akceptuje następujące formaty dat:
- `YYYY-MM-DD` (np. 2026-01-15)
- `DD.MM.YYYY` (np. 15.01.2026)
- `DD-MM-YYYY` (np. 15-01-2026)
- `YYYY/MM/DD` (np. 2026/01/15)

### Agregacja danych

Dostępne opcje agregacji:
- `1h` lub `1H` - co godzinę
- `1D` - co dzień
- `1W` - co tydzień
- `1M` - co miesiąc

## 🔧 Przeliczenia

- Dane wejściowe: moc chwilowa w MW (co 15 minut)
- Dane wyjściowe: energia w MWh
- Przelicznik: MW × 0.25h = MWh (dla danych co 15 min)

## ⚠️ Uwagi

1. **API PSE**: Skrypt używa oficjalnego API PSE v2 (https://api.raporty.pse.pl/api/his-wlk-cal)

2. **Dostępność danych**: PSE publikuje dane historyczne. Najnowsze dane są dostępne zazwyczaj z opóźnieniem kilku godzin/dni.

3. **Duże zakresy dat**: Dla okresów dłuższych niż 7 dni, skrypt automatycznie pobiera dane dzień po dniu, co może zająć więcej czasu.

4. **Automatyczne filtrowanie do ostatniego rzeczywistego pomiaru** (od wersji 1.4.1):
   - Gdy pobierasz dane za dzisiaj, kod automatycznie pokazuje **tylko rzeczywiste pomiary**
   - API PSE zwraca dane za cały dzień, ale ostatnie mogą być prognostyczne
   - Przykład: teraz jest 12:20, ale ostatnia aktualizacja PSE była o 11:45
   - Kod automatycznie odfiltruje dane po 11:45 (prognozy) i pokaże tylko rzeczywiste pomiary
   - Nie wpływa na dane historyczne (tylko bieżący dzień)

## 📚 Dokumentacja Techniczna

### Moduły aplikacji
- `pse_energy_scraper.py` - główny moduł z klasami do pobierania i analizy danych
- `pse_energy_interactive.py` - interaktywny interfejs użytkownika z menu
- `entsoe_data_fetcher.py` - moduł do pobierania danych z ENTSO-E
- `combined_energy_data.py` - łączenie danych z PSE i ENTSO-E
- `quick.py` - szybki interfejs wiersza poleceń
- `examples.py` - przykłady użycia programistycznego
- `requirements.txt` - zależności Python

### Dokumentacja dodatkowa
- [TIMEZONE_SYNC_ANALYSIS.md](docs/TIMEZONE_SYNC_ANALYSIS.md) - **Analiza synchronizacji czasowej PSE ↔ ENTSO-E**
- [ENTSOE_API_SETUP.md](docs/ENTSOE_API_SETUP.md) - Konfiguracja API ENTSO-E
- [QUICK_START.md](docs/QUICK_START.md) - Przewodnik szybkiego startu
- [API_EXAMPLES.md](docs/API_EXAMPLES.md) - Przykłady użycia API
- [NOTATKI_TECHNICZNE.md](docs/NOTATKI_TECHNICZNE.md) - Szczegóły techniczne

## 🛠️ Rozwój

Aby dostosować skrypt do rzeczywistego API PSE:

1. Zbadaj dokładną strukturę API używając narzędzi deweloperskich przeglądarki na stronie PSE
2. Zaktualizuj metody w klasie `PSEEnergyDataFetcher`
3. Dostosuj parsowanie danych w metodzie `_parse_data()`

## 📝 Licencja

Projekt stworzony do analizy publicznych danych PSE.