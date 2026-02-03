# Walidacja ciągłości danych

## Opis

Moduł `combined_energy_data` zawiera funkcje do walidacji ciągłości czasowej pobranych danych. Automatycznie sprawdza czy dla każdego dnia pobrano oczekiwaną liczbę rekordów (96 dla interwału 15-minutowego).

## Funkcje

### `validate_data_continuity(df, date_from, date_to, expected_interval_minutes=15)`

Sprawdza ciągłość czasową danych i wykrywa brakujące dni/godziny.

**Parametry:**
- `df` - DataFrame z danymi (musi mieć kolumnę 'Data')
- `date_from` - Oczekiwana data początkowa (YYYY-MM-DD)
- `date_to` - Oczekiwana data końcowa (YYYY-MM-DD)
- `expected_interval_minutes` - Oczekiwany interwał czasowy w minutach (domyślnie 15)

**Zwraca:** Słownik z informacjami:
- `is_complete` - czy dane są kompletne
- `expected_records` - oczekiwana liczba rekordów
- `actual_records` - faktyczna liczba rekordów
- `missing_records` - liczba brakujących rekordów
- `missing_days` - lista dni z niekompletnymi danymi
- `records_per_day` - liczba rekordów dla każdego dnia

### `print_data_quality_report(validation_result, save_to_file=None)`

Wyświetla raport jakości danych w czytelnym formacie.

**Parametry:**
- `validation_result` - Wynik z `validate_data_continuity()`
- `save_to_file` - Opcjonalna ścieżka do zapisania raportu w JSON

## Automatyczne użycie

Funkcje są **automatycznie wywoływane** przy pobieraniu danych przez:
- `CombinedEnergyDataFetcher.fetch_combined_data()`
- Wyświetlany jest raport po zakończeniu pobierania danych

## Przykładowy raport

```
======================================================================
📋 RAPORT JAKOŚCI DANYCH
======================================================================

Oczekiwano:     10,944 rekordów
Pobrano:        10,844 rekordów
Brakuje:        100 rekordów
Kompletność:    99.09%

Oczekiwano:     96 rekordów/dzień
Okres:          114 dni

⚠️  Wykryto 2 dni z niekompletnymi danymi:

----------------------------------------------------------------------
Data         Oczekiwano   Pobrano      Brakuje     
----------------------------------------------------------------------
2025-10-15   96           46           50          
2025-11-03   96           46           50          
----------------------------------------------------------------------
```

## Interpretacja wyników

### Kompletne dane (100%)
```
✅ Dane są kompletne!
```
Wszystkie oczekiwane rekordy zostały pobrane.

### Niekompletne dane
Raport pokazuje:
- **Które dni** mają niekompletne dane
- **Ile rekordów** brakuje dla każdego dnia
- **Łączną liczbę** brakujących rekordów

### Typowe przyczyny braków:

1. **Przejście czasu (zmiana czasu letni/zimowy)**
   - W dzień zmiany czasu zimowego → więcej rekordów (97 zamiast 96)
   - W dzień zmiany czasu letniego → mniej rekordów (95 zamiast 96)
   
2. **Problemy z API**
   - Timeout przy pobieraniu
   - API zwróciło niepełne dane
   - Brak danych w systemie źródłowym

3. **Problemy z łączeniem danych PSE + ENTSO-E**
   - Różnice w timestampach między źródłami
   - Różnice w strefach czasowych

## Ręczne użycie

```python
from src.combined_energy_data import validate_data_continuity, print_data_quality_report
import pandas as pd

# Twoje dane
df = pd.DataFrame({
    'Data': pd.date_range('2025-10-01', '2025-10-31', freq='15min')
})

# Walidacja
validation = validate_data_continuity(df, '2025-10-01', '2025-10-31')

# Raport
print_data_quality_report(validation)

# Lub zapis do pliku
print_data_quality_report(validation, save_to_file='raport_jakosc.json')
```

## Rozwiązywanie problemów

### Brakuje ~50 rekordów w jednym dniu
**Przyczyna:** Prawdopodobnie zmiana czasu (letni/zimowy)
**Rozwiązanie:** To normalne, można zignorować

### Brakuje 96 rekordów (cały dzień)
**Przyczyna:** Brak danych dla tego dnia w API
**Rozwiązanie:** Sprawdź dostępność danych w źródle

### Brakuje kilka rekordów losowo
**Przyczyna:** Luki w danych źródłowych lub problemy z API
**Rozwiązanie:** Rozważ interpolację lub uzupełnienie danych

## Zapis raportu do pliku

Raport można zapisać do pliku JSON dla późniejszej analizy:

```python
print_data_quality_report(validation, save_to_file='quality_report.json')
```

Plik zawiera pełne informacje o brakujących danych w formacie JSON.
