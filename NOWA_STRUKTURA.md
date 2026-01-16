# Nowa struktura projektu PSE

## ✅ Co zostało zrobione:

### 1. Utworzone foldery:
- **src/** - Główne moduły Python (pse_energy_scraper.py, pse_energy_interactive.py)
- **scripts/** - Skrypty pomocnicze (quick.py, examples.py)
- **docs/** - Dokumentacja (API_EXAMPLES.md, QUICK_START.md, itp.)

### 2. Utworzone pliki:
- **run.sh** - Główny skrypt bash do uruchamiania wszystkich funkcji
- **COMMANDS.md** - Pełna lista komend i instrukcji użycia
- **INFO.txt** - Szybki przegląd projektu

### 3. Zaktualizowane pliki:
- **README.md** - Zaktualizowany z nową strukturą i komendami
- Wszystkie skrypty Python - poprawione importy

## 🚀 Jak używać:

### Najprostszy sposób - run.sh:
```bash
./run.sh help              # Pomoc
./run.sh interactive       # Menu interaktywne
./run.sh suma 2026-01-01 2026-01-31
./run.sh miesieczne 2020 2026
./run.sh szereg 2026-01-01 2026-01-31 1D
./run.sh examples          # Przykłady
./run.sh test              # Test API
```

### Bezpośrednie wywołanie:
```bash
python3 src/pse_energy_interactive.py
python3 scripts/quick.py suma 2026-01-01 2026-01-31
python3 scripts/examples.py
```

## 📁 Struktura:
```
produkcja-energii/
├── run.sh ⭐              # Główny skrypt
├── COMMANDS.md ⭐         # Lista komend
├── INFO.txt ⭐            # Szybki start
├── README.md              # Dokumentacja
├── src/                   # Główne moduły
│   ├── __init__.py
│   ├── pse_energy_scraper.py
│   └── pse_energy_interactive.py
├── scripts/               # Skrypty pomocnicze
│   ├── quick.py
│   └── examples.py
├── docs/                  # Dokumentacja
│   ├── API_EXAMPLES.md
│   ├── QUICK_START.md
│   ├── NOTATKI_TECHNICZNE.md
│   └── CHANGELOG.md
├── wyniki/                # Wygenerowane pliki
├── analiza_pse.ipynb      # Jupyter notebook
└── requirements.txt       # Zależności
```

## 📋 Wszystkie dostępne komendy w COMMANDS.md
