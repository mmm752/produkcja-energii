# Notatki techniczne - PSE Energy Scraper

## ✅ API PSE - Zintegrowane!

Skrypt jest już zintegrowany z oficjalnym API PSE v2:
- **Base URL**: `https://api.raporty.pse.pl/api/`
- **Endpoint**: `/his-wlk-cal`
- **Protokół**: OData v4 z filtrowaniem

### Przykłady użycia API

**Pojedynczy dzień:**
```bash
curl 'https://api.raporty.pse.pl/api/his-wlk-cal?$filter=business_date eq '2024-06-14''
```

**Zakres dat:**
```bash
curl 'https://api.raporty.pse.pl/api/his-wlk-cal?$filter=business_date ge '2024-06-14' and business_date le '2024-06-15''
```

### Struktura danych

API zwraca JSON z kluczowymi polami:
- `wi` - moc wiatrowa [MW]
- `pv` - moc fotowoltaiczna [MW]
- `dtime` - data i czas (lokalny)
- `business_date` - data biznesowa
- `period` - okres 15-minutowy

## 🔧 Zaawansowana konfiguracja

### Dostępne pola w API

Kompletna lista pól zwracanych przez API PSE:
```python
{
    'jg': 'Generacja jednostek jrwa',
    'pv': 'Fotowoltaika [MW]',
    'wi': 'Wiatr [MW]',
    'dtime': 'Data i czas (lokalny)',
    'business_date': 'Data biznesowa',
    'period': 'Okres 15-minutowy',
    'demand': 'Zapotrzebowanie [MW]',
    'jnwrb': 'Jednostki niezależne',
    # ... i wiele innych
}
```

### Ograniczenia API

1. **Limit rekordów**: API zwraca maksymalnie ~100 rekordów na zapytanie OData
   - 1 dzień = 96 pomiarów (co 15 min)
   - Problem: zapytanie o 2+ dni zwraca tylko pierwsze 100 rekordów
   - **UWAGA**: API PSE **NIE obsługuje** parametru `$top` - zwraca błąd 400!
   
2. **Rozwiązania zaimplementowane** (od wersji 2026-02-03):
   - Automatyczne pobieranie dzień po dniu dla okresów > 1 dzień
   - ~~Parametr `$top=200`~~ ❌ NIE DZIAŁA - API nie obsługuje
   - Ostrzeżenia gdy wykryto możliwy limit (≥100 rekordów)
   - Weryfikacja kompletności danych
   
3. **Opóźnienie danych**: Dane publikowane z opóźnieniem (zazwyczaj kilka godzin)

### Przykłady zapytań OData

**Filtrowanie po dacie:**
```python
$filter=business_date eq '2024-06-14'
# ✅ Działa - zwraca 96 rekordów
```

**Zakres dat:**
```python
$filter=business_date ge '2024-06-01' and business_date le '2024-06-30'
# ⚠️  UWAGA: dla >1 dnia użyj pobierania dzień po dniu!
# Zwraca tylko ~100 pierwszych rekordów
```

**Parametr $top:**
```python
$filter=business_date eq '2024-06-14'&$top=200
# ❌ NIE DZIAŁA! Błąd 400: "Invalid Query Parameter: $top"
```

**Uwaga**: Dla okresów dłuższych niż 1 dzień **zawsze** używaj metody pobierania dzień po dniu, aby uniknąć problemu z limitem 100 rekordów.

## 📊 Pełna struktura danych PSE

Przykładowy rekord z API:
## 📊 Pełna struktura danych PSE

Przykładowy rekord z API:
```json
{
  "jg": 12132.16,
  "pv": 0.0,
  "wi": 299.813,
  "jga": null,
  "jgm": -15.179,
  "jgo": null,
  "jgm1": 0.0,
  "jgm2": null,
  "jgw1": 12132.16,
  "jgw2": null,
  "dtime": "2024-06-14 00:15:00",
  "jnwrb": 3568.568,
  "swm_p": 490.833,
  "demand": 16296.632,
  "period": "00:00 - 00:15",
  "swm_np": 122.25,
  "dtime_utc": "2024-06-13 22:15:00",
  "period_utc": "22:00 - 22:15",
  "business_date": "2024-06-14",
  "publication_ts": "2025-05-14 14:26:06.069",
  "publication_ts_utc": "2025-05-14 12:26:06.069"
}
```

Najważniejsze pola:
- `wi` - moc wiatrowa [MW]
- `pv` - moc fotowoltaiczna [MW]
- `dtime` - data i czas lokalny
- `demand` - zapotrzebowanie na moc [MW]
- `business_date` - data biznesowa (do filtrowania)

## 🔐 Uwierzytelnianie

API PSE v2 jest publicznie dostępne i nie wymaga uwierzytelniania.

Jeśli w przyszłości pojawi się wymaganie uwierzytelniania:

```python
self.session.headers.update({
    'Authorization': 'Bearer YOUR_TOKEN',
    # lub
    'X-API-Key': 'YOUR_API_KEY'
})
```

## ⚡ Optymalizacja

### Cache dla danych
Dodaj cache aby uniknąć wielokrotnego pobierania tych samych danych:

```python
import pickle
from pathlib import Path

def fetch_data_with_cache(self, date_from: str, date_to: str):
    cache_file = Path(f"cache/{date_from}_{date_to}.pkl")
    
    if cache_file.exists():
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    
    df = self.fetch_data(date_from, date_to)
    
    cache_file.parent.mkdir(exist_ok=True)
    with open(cache_file, 'wb') as f:
        pickle.dump(df, f)
    
    return df
```

### Równoległe pobieranie
Dla długich okresów, pobieraj dane równolegle:

```python
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

def fetch_year_parallel(self, year: int):
    months = [(f"{year}-{m:02d}-01", f"{year}-{m:02d}-{self._last_day(year, m)}") 
              for m in range(1, 13)]
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        dfs = list(executor.map(lambda dates: self.fetch_data(*dates), months))
    
    return pd.concat(dfs, ignore_index=True)
```

## 🧪 Testy jednostkowe

Przykładowe testy (stwórz plik `test_pse_scraper.py`):

```python
import unittest
from pse_energy_scraper import PSEEnergyDataFetcher, EnergyDataAnalyzer

class TestPSEScraper(unittest.TestCase):
    
    def setUp(self):
        self.fetcher = PSEEnergyDataFetcher()
        self.df = self.fetcher.generate_sample_data("2026-01-01", "2026-01-02")
    
    def test_data_not_empty(self):
        self.assertIsNotNone(self.df)
        self.assertGreater(len(self.df), 0)
    
    def test_analyzer_sum(self):
        analyzer = EnergyDataAnalyzer(self.df)
        results = analyzer.sum_period()
        
        self.assertIn('wiatr_MWh', results)
        self.assertIn('fotowoltaika_MWh', results)
        self.assertGreater(results['wiatr_MWh'], 0)

if __name__ == '__main__':
    unittest.main()
```

## 📝 Rozszerzenia

### 1. Dodaj więcej źródeł energii
```python
# W klasie EnergyDataAnalyzer
self.coal_col = self._find_column(['węgiel', 'coal'])
self.gas_col = self._find_column(['gaz', 'gas'])
```

### 2. Predykcja produkcji
Użyj uczenia maszynowego do przewidywania:
```python
from sklearn.ensemble import RandomForestRegressor

def predict_next_day(self):
    # Przygotuj dane treningowe
    X = # features (godzina, dzień roku, etc.)
    y = # produkcja
    
    model = RandomForestRegressor()
    model.fit(X, y)
    
    # Predykcja
    return model.predict(X_future)
```

### 3. Alerty i monitoring
```python
def check_low_production(self, threshold_mw: float):
    """Sprawdź czy produkcja spadła poniżej progu."""
    current = self.df[self.wind_col].iloc[-1]
    
    if current < threshold_mw:
        # Wyślij alert (email, SMS, etc.)
        send_alert(f"Niska produkcja wiatrowa: {current} MW")
```

## 🌐 API Rate Limiting

Jeśli API ma ograniczenia:

```python
import time
from functools import wraps

def rate_limit(calls_per_minute=60):
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = min_interval - elapsed
            
            if wait_time > 0:
                time.sleep(wait_time)
            
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

# Użycie:
@rate_limit(calls_per_minute=30)
def fetch_data(self, date_from, date_to):
    # ...
```

## 🔍 Debugging

Włącz szczegółowe logowanie:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pse_scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# W kodzie:
logger.debug(f"Pobieranie danych: {date_from} - {date_to}")
logger.info(f"Otrzymano {len(df)} rekordów")
logger.error(f"Błąd: {str(e)}")
```
