# 📋 Komendy i Instrukcje Użycia

## 🚀 Szybki Start

### 1. Instalacja zależności
```bash
# Opcja 1: Używając skryptu run.sh
./run.sh install

# Opcja 2: Bezpośrednio pip
pip install -r requirements.txt
```

### 2. Test połączenia z API
```bash
./run.sh test
```

---

## 🎯 Podstawowe Komendy

### Interfejs Interaktywny (najłatwiejszy)
```bash
# Uruchom menu interaktywne
./run.sh interactive

# lub krócej:
./run.sh i

# lub bezpośrednio:
python3 src/pse_energy_interactive.py
```

---

## 📊 Analiza Danych

### 1. Suma produkcji dla okresu
```bash
# Przez skrypt run.sh (zalecane)
./run.sh suma 2026-01-01 2026-01-31

# Bezpośrednio
python3 scripts/quick.py suma 2026-01-01 2026-01-31

# Z pełnymi danymi (PSE + ENTSO-E) - wymaga klucza API
python3 scripts/quick.py suma 2026-01-01 2026-01-31 --full

# Przykłady:
./run.sh suma 2025-12-01 2025-12-31  # Cały grudzień 2025
./run.sh suma 2026-01-01 2026-01-16  # Od początku stycznia do dziś
```

**Tryb --full pobiera dodatkowo z ENTSO-E:**
- Węgiel kamienny i brunatny
- Gaz
- Wodę, Biomasę, Magazyny energii

**Konfiguracja ENTSO-E:** Zobacz `docs/ENTSOE_API_SETUP.md`

### 2. Miesięczne sumy
```bash
# Przez skrypt run.sh (zalecane)
./run.sh miesieczne 2020 2026

# Bezpośrednio
python3 scripts/quick.py miesieczne 2020 2026

# Przykłady:
./run.sh miesieczne 2024 2026    # Ostatnie 3 lata
./run.sh miesieczne 2020 2020    # Tylko rok 2020
```

### 3. Szereg czasowy (z agregacją)
```bash
# Przez skrypt run.sh (zalecane)
./run.sh szereg 2026-01-01 2026-01-31 1D

# Bezpośrednio
python3 scripts/quick.py szereg 2026-01-01 2026-01-31 1D

# Dostępne agregacje:
./run.sh szereg 2026-01-01 2026-01-31 1h  # Co godzinę (można również 1H)
./run.sh szereg 2026-01-01 2026-01-31 1D  # Co dzień
./run.sh szereg 2026-01-01 2026-01-31 1W  # Co tydzień
./run.sh szereg 2026-01-01 2026-01-31 1M  # Co miesiąc
```

---

## 📚 Przykłady i Dokumentacja

### Uruchomienie przykładów
```bash
# Przez skrypt run.sh
./run.sh examples

# Bezpośrednio
python3 scripts/examples.py
```

### Jupyter Notebook
```bash
# Przez skrypt run.sh
./run.sh notebook

# Bezpośrednio
jupyter notebook analiza_pse.ipynb
```

---

## 🔧 Zaawansowane Użycie

### Bezpośrednie wywołanie Python
```python
# W terminalu Python lub w skrypcie
from src.pse_energy_scraper import PSEEnergyDataFetcher, EnergyDataAnalyzer

# Pobranie danych
fetcher = PSEEnergyDataFetcher()
df = fetcher.fetch_data("2026-01-01", "2026-01-31")

# Analiza
analyzer = EnergyDataAnalyzer(df)
wyniki = analyzer.sum_period()
print(wyniki)
```

### Eksport danych
```python
# Zapisanie do CSV (format europejski: separator ; i dziesiętny ,)
analyzer.export_to_csv("wyniki/dane_styczen.csv")

# Zapisanie do JSON
analyzer.export_to_json("wyniki/dane_styczen.json")
```

**Uwaga**: Wszystkie pliki CSV używają **europejskiego formatu**:
- Separator kolumn: `;` (średnik)
- Separator dziesiętny: `,` (przecinek)
- Kodowanie: UTF-8 z BOM

---

## 📁 Struktura Projektu

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
├── run.sh                           # Główny skrypt uruchamiający
├── COMMANDS.md                      # Ten plik - lista komend
├── README.md                        # Dokumentacja główna
└── requirements.txt                 # Zależności Python
```

---

## 💡 Przydatne Wskazówki

### 1. Uprawnienia do wykonania
Jeśli `run.sh` nie uruchamia się:
```bash
chmod +x run.sh
./run.sh
```

### 2. Pomoc
```bash
# Wyświetl pomoc dla run.sh
./run.sh help

# Lub po prostu:
./run.sh
```

### 3. Szybkie skróty
```bash
./run.sh i         # interactive
./run.sh s         # suma
./run.sh m         # miesieczne
./run.sh e         # examples
./run.sh nb        # notebook
```

---

## 🐛 Rozwiązywanie Problemów

### Błąd: "Python 3 nie jest zainstalowany"
```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip

# macOS
brew install python3
```

### Błąd: "No module named 'pandas'"
```bash
./run.sh install
```

### Błąd: "API nie odpowiada"
```bash
# Sprawdź połączenie
./run.sh test

# Sprawdź czy strona PSE działa
curl -I https://api.raporty.pse.pl/api/his-wlk-cal
```

### Brak danych dla wybranego okresu
- API PSE czasami ma opóźnienia w dostarczaniu danych
- Sprawdź czy data jest poprawna (YYYY-MM-DD)
- Spróbuj wcześniejszego okresu

---

## 📞 Więcej Informacji

- **README.md** - Pełna dokumentacja projektu
- **docs/API_EXAMPLES.md** - Przykłady użycia API
- **docs/QUICK_START.md** - Przewodnik dla początkujących
- **docs/NOTATKI_TECHNICZNE.md** - Szczegóły techniczne

---

## 🎓 Przykładowe Scenariusze

### Scenariusz 1: Analiza bieżącego miesiąca
```bash
# 1. Pobierz dane dla stycznia 2026
./run.sh suma 2026-01-01 2026-01-16

# 2. Zobacz dzienny rozkład
./run.sh szereg 2026-01-01 2026-01-16 1D
```

### Scenariusz 2: Porównanie rok do roku
```bash
# 1. Pobierz miesięczne sumy
./run.sh miesieczne 2020 2026

# 2. Otwórz notebook do wizualizacji
./run.sh notebook
```

### Scenariusz 3: Eksport danych do CSV
```bash
# 1. Uruchom interfejs interaktywny
./run.sh interactive

# 2. Wybierz opcję 3 (Szereg czasowy)
# 3. Podaj daty i agregację
# 4. Dane zostaną zapisane w folderze wyniki/
```

---

**Ostatnia aktualizacja:** 16 stycznia 2026
