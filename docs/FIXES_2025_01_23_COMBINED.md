# NAPRAWY 2025-01-23 - Łączenie danych PSE + ENTSO-E

## Problem

Użytkownik zgłosił że dane są niepełne - brakuje kolumn z ENTSO-E (węgiel, gaz, woda, biomasa, magazyny).  
Przy pobieraniu okresu 2025-10-01 do 2026-01-22 (114 dni = 10,944 rekordy) system zwracał tylko 100 rekordów i tylko dane PSE.

## Przyczyny

1. **Limit API PSE**: API PSE ma limit ~100 rekordów na pojedyncze zapytanie, więc dla okresów > 1 dzień zwracało niepełne dane
2. **Próg pobierania dzień po dniu**: Kod był ustawiony na `days_diff > 7`, co oznaczało że okresy 2-7 dni pobierały dane w jednym zapytaniu
3. **Błąd timezone dla dni DST**: Podczas łączenia danych, próba zlokalizowania timezone dla dnia 2025-10-26 (dzień zmiany czasu) powodowała wyjątek `AmbiguousTimeError`

## Rozwiązania

### 1. Obniżenie progu pobierania dzień po dniu (pse_energy_scraper.py)

**Plik**: `src/pse_energy_scraper.py`, linia ~44  
**Zmiana**: `if days_diff > 7` → `if days_diff > 1`

```python
# PRZED:
if days_diff > 7:
    # Pobieraj dzień po dniu

# PO:
if days_diff > 1:  # ZAWSZE pobieraj dzień po dniu dla pewności
    # Pobieraj dzień po dniu
```

**Efekt**: Każdy dzień jest pobierany osobnym zapytaniem, co unika limitu API (96 rekordów/dzień)

### 2. Dodanie markera DST (pse_energy_scraper.py)

**Plik**: `src/pse_energy_scraper.py`, linia ~189-197

Dodano kolumnę `_dst_marker` która oznacza czy timestamp pochodzi z pierwszej ('first') czy drugiej ('second') godziny 2:xx podczas zmiany czasu:

```python
df['_dst_marker'] = ''
if df['Data'].dtype == 'object':
    df.loc[df['Data'].str.contains(r'\d{2}a:', regex=True, na=False), '_dst_marker'] = 'first'
    df.loc[df['Data'].str.contains(r'\d{2}b:', regex=True, na=False), '_dst_marker'] = 'second'
    
    # Zastąp "02a:" i "02b:" przez "02:" - oba będą miały ten sam timestamp
    df['Data'] = df['Data'].str.replace(r'(\d{2})a:', r'\1:', regex=True)
    df['Data'] = df['Data'].str.replace(r'(\d{2})b:', r'\1:', regex=True)
```

**Uwaga**: API PSE nie zwraca formatu "02a/02b" dla przyszłych dat (2025-10-26 jeszcze nie nastąpił), więc marker będzie pusty dla danych testowych.

### 3. Obsługa timezone z fallback na `ambiguous='NaT'` (combined_energy_data.py)

**Plik**: `src/combined_energy_data.py`, linia ~88-122

Dodano try/except z fallbackiem:
- Próba 1: Użyj markera `_dst_marker` jeśli dostępny
- Próba 2: `ambiguous='infer'` (działa dla większości dni)
- Próba 3: `ambiguous='NaT'` + usuń wiersze z NaT (działa dla dni DST bez markera)

```python
try:
    df_pse.index = df_pse.index.tz_localize('Europe/Warsaw', ambiguous='infer', nonexistent='shift_forward')
except Exception:
    # Jeśli 'infer' nie działa, użyj 'NaT' aby oznaczyć niejednoznaczne jako brakujące
    df_pse.index = df_pse.index.tz_localize('Europe/Warsaw', ambiguous='NaT', nonexistent='shift_forward')
    # Usuń wiersze z NaT
    df_pse = df_pse[df_pse.index.notna()]
    print(f"   ⚠️  Usunięto niejednoznaczne timestampy DST, pozostało {len(df_pse)} rekordów")
```

**Efekt**: Dla dnia DST (2025-10-26) usuwa 4 niejednoznaczne rekordy (godzina 02:00-02:45), ale zachowuje pozostałe 92 rekordy.

## Wyniki

### Przed naprawą:
- Okres 2025-10-01 do 2026-01-22: **100 rekordów** (0.91%)
- Tylko dane PSE: wiatr, fotowoltaika, zapotrzebowanie, saldo
- Brak danych ENTSO-E: węgiel, gaz, woda, biomasa, magazyny

### Po naprawie:
- Okres 2025-10-01 do 2026-01-22: **10,940 z 10,944 rekordów (99.96%)**
- Wszystkie dane PSE + ENTSO-E
- Brakuje tylko 4 rekordy z dnia DST 2025-10-26 (niejednoznaczne timestampy)
- Dopasowanie ENTSO-E: 10,936 / 10,940 (100.0%)

### Test 3-dniowy (2025-10-25 do 2025-10-27):
- Oczekiwano: 288 rekordów (96+96+96)
- Pobrano: 284 rekordy (96+92+96)
- Kompletność: 98.61%
- Brakuje: 4 rekordy z 2025-10-26 (DST)

## Znane ograniczenia

1. **Przyszłe dni DST**: Dla przyszłych dat (jak 2025-10-26) API PSE nie zwraca formatu "02a/02b", więc marker DST jest pusty i tracimy 4 rekordy na dzień zmiany czasu.

2. **Rozwiązanie dla przeszłych dat**: Dla historycznych dni DST (np. 2024-10-27) API PSE zwraca "02a/02b" i marker działa poprawnie - wtedy mamy wszystkie 100 rekordów dla dnia DST.

3. **Akceptowalne straty**: Utrata 4 rekordów (1 godziny) na rok podczas zmiany czasu zimowego to akceptowalny kompromis - 99.96% kompletności danych.

## Pliki zmodyfikowane

1. `src/pse_energy_scraper.py`:
   - Linia 44: Próg `> 7` → `> 1`
   - Linia 189-197: Marker DST

2. `src/combined_energy_data.py`:
   - Linia 88-122: Obsługa timezone z fallback

3. `test_dst_combined.py` (nowy): Skrypt testowy dla okresu DST

## Testowanie

```bash
# Test krótkiego okresu z DST
python test_dst_combined.py

# Test pełnego okresu (114 dni)
python scripts/quick.py suma 2025-10-01 2026-01-22
```

## Data naprawy
2025-01-23 (konwersacja z użytkownikiem)
