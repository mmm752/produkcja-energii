# PSE - Skrypt do pobierania danych o produkcji energii

Skrypt do pobierania i analizowania danych o produkcji energii wiatrowej i fotowoltaicznej z portalu PSE.

**Źródło danych**: Oficjalne API PSE v2 (https://api.raporty.pse.pl/api/his-wlk-cal)

## 🎯 Funkcjonalności

- ✅ Pobieranie danych co 15 minut dla wybranego okresu
- ✅ Sumowanie produkcji w MWh dla dowolnego zakresu dat
- ✅ Generowanie miesięcznych sum od 2020 do teraz
- ✅ Tworzenie szeregów czasowych z różną agregacją (godzinową, dzienną, tygodniową, miesięczną)
- ✅ Eksport danych do CSV i JSON
- ✅ Interaktywny interfejs użytkownika

## 📊 Dane

Skrypt pobiera następujące dane:
- **Sumaryczna generacja źródeł wiatrowych [MW]**
- **Sumaryczna generacja źródeł fotowoltaicznych [MW]**

Dane są dostępne z interwałem 15-minutowym.

## � Struktura Projektu

```
produkcja-energii/
├── src/                              # Główne moduły
│   ├── pse_energy_scraper.py        # Główny moduł do pobierania danych
│   └── pse_energy_interactive.py    # Interfejs interaktywny
├── scripts/                          # Skrypty pomocnicze
│   ├── quick.py                     # Szybkie komendy
│   └── examples.py                  # Przykłady użycia
├── docs/                             # Dokumentacja
│   ├── API_EXAMPLES.md              # Przykłady API
│   ├── QUICK_START.md               # Szybki start
│   ├── NOTATKI_TECHNICZNE.md        # Notatki techniczne
│   └── CHANGELOG.md                 # Historia zmian
├── wyniki/                           # Wygenerowane pliki
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
- `1H` - co godzinę
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

## 📚 Struktura kodu

- `pse_energy_scraper.py` - główny moduł z klasami do pobierania i analizy danych
- `pse_energy_interactive.py` - interaktywny interfejs użytkownika z menu
- `quick.py` - szybki interfejs wiersza poleceń
- `examples.py` - przykłady użycia programistycznego
- `requirements.txt` - zależności Python

## 🛠️ Rozwój

Aby dostosować skrypt do rzeczywistego API PSE:

1. Zbadaj dokładną strukturę API używając narzędzi deweloperskich przeglądarki na stronie PSE
2. Zaktualizuj metody w klasie `PSEEnergyDataFetcher`
3. Dostosuj parsowanie danych w metodzie `_parse_data()`

## 📝 Licencja

Projekt stworzony do analizy publicznych danych PSE.