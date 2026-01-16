# 🚀 Szybki Start

## Instalacja (30 sekund)

```bash
# 1. Zainstaluj zależności
pip install -r requirements.txt

# 2. Gotowe! 
```

## Podstawowe użycie

### Opcja A: Szybkie komendy (najłatwiejsze)

```bash
# Suma za styczeń 2026
python quick.py suma 2026-01-01 2026-01-31

# Miesięczne sumy za ostatnie lata
python quick.py miesieczne 2020 2026

# Szereg czasowy (dzienny)
python quick.py szereg 2026-01-01 2026-01-31 1D
```

### Opcja B: Menu interaktywne

```bash
python pse_energy_interactive.py
```

Wybierz opcję z menu (1-4).

### Opcja C: Python (programistycznie)

```python
from pse_energy_scraper import PSEEnergyDataFetcher, EnergyDataAnalyzer

# Pobierz dane
fetcher = PSEEnergyDataFetcher()
df = fetcher.fetch_data("2026-01-01", "2026-01-31")

# Analizuj
analyzer = EnergyDataAnalyzer(df)
wyniki = analyzer.sum_period()

print(f"Produkcja wiatrowa: {wyniki['wiatr_MWh']} MWh")
```

### Opcja D: Jupyter Notebook

```bash
jupyter notebook analiza_pse.ipynb
```

## Przykładowe rezultaty

Po uruchomieniu `python quick.py suma 2026-01-01 2026-01-31`:

```
📊 Pobieranie danych dla okresu 2026-01-01 do 2026-01-31...

📈 WYNIKI:
──────────────────────────────────────────────────
okres_od                      : 2026-01-01 00:00
okres_do                      : 2026-01-31 00:00
wiatr_MWh                     : 1441973.0
wiatr_średnia_MW              : 1940.3
fotowoltaika_MWh              : 372937.0
fotowoltaika_średnia_MW       : 501.8

💾 Zapisano: suma_2026-01-01_2026-01-31.json
```

## Pliki wyjściowe

Po wykonaniu analiz otrzymasz:
- `suma_*.json` - podsumowanie w JSON
- `miesieczne_*.csv` - miesięczne sumy w CSV
- `szereg_*.csv` - szereg czasowy w CSV

## Częste problemy

**Brak danych dla wybranego okresu?**
- PSE publikuje dane z opóźnieniem
- Sprawdź czy wybrana data nie jest zbyt daleko w przeszłości lub przyszłości
- API zwraca dane dla dostępnych okresów

**Długi czas pobierania?**
- Dla okresów > 7 dni skrypt pobiera dane dzień po dniu
- To normalne zachowanie aby nie przeciążać API

## Co dalej?

- 📖 Pełna dokumentacja: [README.md](README.md)
- 🔧 Dostosowanie API: [NOTATKI_TECHNICZNE.md](NOTATKI_TECHNICZNE.md)
- 💡 Więcej przykładów: uruchom `python examples.py`
