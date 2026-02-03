# Obsługa dni zmiany czasu (DST - Daylight Saving Time)

## Problem

API PSE zwraca nieprawidłowy format czasowy dla dni przejścia czasu zimowego/letniego, np.:
- **26 października 2025** (zmiana czasu: letni → zimowy)
- PSE zwraca timestampy jak: `"2025-10-26 02a:15:00"` i `"2025-10-26 02b:15:00"`
- Godzina 2:00-3:00 jest powtórzona (czas lokalny cofa się o 1h)

## Rozwiązanie

### 1. Parser dat w PSE scraper
Plik: `src/pse_energy_scraper.py`

```python
# Zastąpienie nieprawidłowego formatu PSE:
# "02a:15:00" → "02:15:00" (pierwsze przejście przez godz. 2)
# "02b:15:00" → "03:15:00" (drugie przejście - już czas zimowy)
df['Data'] = df['Data'].str.replace(r'(\d{2})a:', r'\1:', regex=True)
df['Data'] = df['Data'].str.replace(r'(\d{2})b:', lambda m: f"{int(m.group(1))+1:02d}:", regex=True)
```

### 2. Walidator ciągłości danych
Plik: `src/combined_energy_data.py`

Walidator rozpoznaje dni zmiany czasu i **nie traktuje ich jako błąd**:
- Normalny dzień: 96 rekordów (15-min interwały)
- Dzień zmiany czasu zimowego: ~100 rekordów (dodatkowa godzina)
- Dzień zmiany czasu letniego: ~92 rekordów (stracona godzina)

**Tolerancja:** 95-100 rekordów jest OK dla dni zmiany czasu.

## Daty zmiany czasu w Polsce (2025-2030)

### Czas letni → zimowy (Październik)
- **2025:** 26 października (niedziela) 3:00 → 2:00 (~100 rekordów)
- **2026:** 25 października (niedziela) 3:00 → 2:00
- **2027:** 31 października (niedziela) 3:00 → 2:00
- **2028:** 29 października (niedziela) 3:00 → 2:00
- **2029:** 28 października (niedziela) 3:00 → 2:00
- **2030:** 27 października (niedziela) 3:00 → 2:00

### Czas zimowy → letni (Marzec)
- **2026:** 29 marca (niedziela) 2:00 → 3:00 (~92 rekordy)
- **2027:** 28 marca (niedziela) 2:00 → 3:00
- **2028:** 26 marca (niedziela) 2:00 → 3:00
- **2029:** 25 marca (niedziela) 2:00 → 3:00
- **2030:** 31 marca (niedziela) 2:00 → 3:00
- **2031:** 30 marca (niedziela) 2:00 → 3:00

## Przykładowy raport walidacji

```
======================================================================
📋 RAPORT JAKOŚCI DANYCH
======================================================================

Oczekiwano:     10,944 rekordów
Pobrano:        10,948 rekordów  
Brakuje:        -4 rekordów
Kompletność:    100.04%

Oczekiwano:     96 rekordów/dzień
Okres:          114 dni

⏰ Wykryto 1 dni zmiany czasu (letni/zimowy):
   2025-10-26: 100 rekordów

✅ Dane są kompletne!
```

## Merge z ENTSO-E

Używamy **LEFT JOIN** z PSE jako głównym źródłem czasu:
- PSE: dokładniejsze timestampy (co 15 min)
- ENTSO-E: może mieć różne timestampy lub luki
- LEFT JOIN zachowuje wszystkie rekordy PSE, nawet jeśli ENTSO-E ich nie ma

## Retry mechanism

Dodano automatyczne ponowienie (3 próby) dla:
- Błędów sieciowych
- Błędów serwera (HTTP 500+)
- Z wykładniczym backoff (1s, 2s, 3s)

## Diagnostyka

Przy pobieraniu długich okresów wyświetlane są:
- Dni bez danych z PSE
- Statystyki łączenia PSE + ENTSO-E
- Procent dopasowanych rekordów

Przykład:
```
✓ Połączono 10948 rekordów
   PSE: 10948, ENTSO-E: 10945
   Wspólne timestampy: 10945
   Dopasowano ENTSO-E: 10945 / 10948 (99.97%)
```
