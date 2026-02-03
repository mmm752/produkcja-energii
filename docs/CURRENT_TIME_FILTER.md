# 🕐 Automatyczne filtrowanie do ostatniego rzeczywistego pomiaru

## Problem

API PSE zwraca **dane za cały dzień**, ale ostatnie pomiary mogą być **prognostyczne**, nie rzeczywiste.

### Przykład

**Dzisiaj**: 2026-02-03, godzina **12:20** (zegar)
**Ostatnia aktualizacja PSE**: **11:45** (opóźnienie ~35 minut)

**API zwraca**:
```
00:00 → 145 MW  ✅ Rzeczywisty pomiar
00:15 → 146 MW  ✅ Rzeczywisty pomiar
...
11:30 → 289 MW  ✅ Rzeczywisty pomiar
11:45 → 290 MW  ✅ Rzeczywisty pomiar (ostatni rzeczywisty)
12:00 → 291 MW  ❌ Prognoza! (PSE jeszcze nie opublikowało)
12:15 → 292 MW  ❌ Prognoza!
...
23:45 → 340 MW  ❌ Prognoza!
```

**Problem**: Dane po 11:45 to **prognozy/wypełniacze**, nie rzeczywiste pomiary!

## Rozwiązanie (od wersji 1.4.1)

Kod **automatycznie filtruje** dane do ostatniego rzeczywistego pomiaru z API.

### Jak działa

1. **Sprawdza czy to bieżący dzień** - jeśli nie, zwraca wszystkie dane
2. **Dodaje bufor 15 minut** - PSE publikuje z opóźnieniem
3. **Filtruje** - pozostawia tylko pomiary do (teraz - 15 min)
4. **Informuje** - pokazuje ile pomiarów odfiltrowano

```python
# Automatyczne filtrowanie w tle
df = fetcher.fetch_data("2026-02-03", "2026-02-03")

# Wynik: tylko dane do 12:15 (ostatni pomiar przed 12:18)
```

### Efekt

**PRZED** filtrowaniem:
```
Okres:              2026-02-03 00:00 - 2026-02-03 23:45
Liczba pomiarów:    96  ❌ zawiera prognozy
```

**PO** filtrowaniu:
```
Okres:              2026-02-03 00:00 - 2026-02-03 11:45
Liczba pomiarów:    48  ✅ tylko rzeczywiste dane
ℹ️  Odfiltrowano 48 przyszłościowych pomiarów (ostatni rzeczywisty pomiar: 2026-02-03 11:45)
```

## Szczegóły implementacji

### 1. Wykrywanie bieżącego dnia

```python
today = datetime.now().date()
has_today = any(d == today for d in df_dates)

if not has_today:
    return df  # Dane historyczne - zwróć wszystko
```

### 2. Filtrowanie z buforem

```python
# Bufor 15 minut - PSE publikuje z opóźnieniem
cutoff_time = now - timedelta(minutes=15)
df_filtered = df[df['Data'] <= cutoff_time]
```

### 3. Sprawdzanie czy dane są świeże

```python
time_diff = (now - last_timestamp).total_seconds() / 3600

if time_diff > 2:
    return df  # Dane starsze niż 2h - zwróć wszystko
```

## Dlaczego bufor 15 minut?

PSE **nie publikuje danych w czasie rzeczywistym**:
- Dane muszą być zebrane z całej sieci
- Weryfikacja i walidacja
- Opóźnienie publikacji: **~30-45 minut**

**Przykład**:
- Teraz: 12:20
- Ostatni pomiar PSE: 11:45
- Bufor: -15 min
- Granica odcięcia: 12:05
- Wynik: dane do 11:45 ✅

## Kiedy działa?

### ✅ Działa dla:
- **Bieżącego dnia** (dzisiaj)
- Zapytań zawierających dzisiejszą datę
- Danych z API PSE i combined (PSE + ENTSO-E)

### ❌ NIE działa dla:
- **Danych historycznych** (wczoraj, zeszły miesiąc, itp.)
- Dat z przeszłości - zwraca wszystkie dane
- To jest zamierzone! Dla danych historycznych chcemy mieć cały dzień

## Przykłady

### Przykład 1: Pobieranie dzisiejszych danych

**Dzisiaj**: 2026-02-03, godz. 14:30 (zegar)
**Ostatnia aktualizacja PSE**: ~13:55 (opóźnienie ~35 min)

```bash
./run.sh suma 2026-02-03 2026-02-03
```

**Wynik**:
```
Okres:              2026-02-03 00:00 - 2026-02-03 13:45
Liczba pomiarów:    56
ℹ️  Odfiltrowano 40 przyszłościowych pomiarów (ostatni rzeczywisty pomiar: 2026-02-03 13:45)

Suma produkcji:
  Wiatr: 1234.56 MWh
  Fotowoltaika: 234.56 MWh
```

### Przykład 2: Zakres dat z dzisiejszym dniem

**Dzisiaj**: 2026-02-03, godz. 10:00
**Ostatnia aktualizacja PSE**: ~09:25

```bash
./run.sh suma 2026-02-01 2026-02-03
```

**Wynik**:
```
📥 Pobieranie danych dla 3 dni...
ℹ️  Odfiltrowano 58 przyszłościowych pomiarów (ostatni rzeczywisty pomiar: 2026-02-03 09:30)

Okres:              2026-02-01 00:00 - 2026-02-03 09:30
Liczba pomiarów:    230
  - 2026-02-01: 96 pomiarów (cały dzień)
  - 2026-02-02: 96 pomiarów (cały dzień)  
  - 2026-02-03: 38 pomiarów (do 09:30)
```

### Przykład 3: Dane historyczne (bez filtrowania)

```bash
./run.sh suma 2026-01-01 2026-01-01
```

**Wynik**:
```
Okres:              2026-01-01 00:00 - 2026-01-01 23:45
Liczba pomiarów:    96  ✅ cały dzień, bez filtrowania
```

## Test

Możesz przetestować funkcjonalność:

```bash
# Test demonstracyjny
python3 test_current_time_filter.py

# Rzeczywisty test z API
./run.sh i
# Wybierz opcję 1: Suma produkcji
# Podaj dzisiejszą datę jako zakres
```

## Wyłączenie filtrowania

Filtrowanie jest **zawsze aktywne** dla bieżącego dnia i nie można go wyłączyć standardowo.

Jeśli potrzebujesz danych prognostycznych/całego dnia, możesz:

### Opcja 1: Poczekaj do następnego dnia
```bash
# Jutro dane za dzisiaj będą kompletne
./run.sh suma 2026-02-03 2026-02-03  # uruchom jutro
```

### Opcja 2: Użyj API bezpośrednio
```python
from src.pse_energy_scraper import PSEEnergyDataFetcher

fetcher = PSEEnergyDataFetcher()
# Pobierz surowe dane bez filtrowania
response = fetcher.session.get(
    "https://api.raporty.pse.pl/api/his-wlk-cal",
    params={'$filter': "business_date eq '2026-02-03'", '$top': 200}
)
data = response.json()
# data['value'] zawiera wszystkie rekordy, łącznie z prognozami
```

## Rozwiązywanie problemów

### Problem: "Brak danych dla dzisiejszego dnia"

**Możliwe przyczyny**:
1. PSE jeszcze nie opublikowało danych (opóźnienie do 45 min)
2. Dzisiaj jest dopiero 00:30 - za mało pomiarów
3. Problemy z API PSE

**Rozwiązanie**:
- Poczekaj 30-60 minut
- Sprawdź dane z wczoraj: `./run.sh suma 2026-02-02 2026-02-02`
- Sprawdź czy API działa: `./run.sh test`

### Problem: "Za mało rekordów"

**Scenariusz**: Jest godz. 14:00, widzisz tylko 20 pomiarów (powinno być ~55)

**Przyczyny**:
1. PSE ma większe opóźnienie niż zwykle
2. API zwraca niepełne dane
3. Problemy techniczne po stronie PSE

**Rozwiązanie**:
```bash
# Sprawdź dokładnie jaki jest ostatni pomiar
./run.sh suma 2026-02-03 2026-02-03

# Komunikat pokaże:
# "ostatni rzeczywisty pomiar: 2026-02-03 08:45"
# Jeśli jest ~6h opóźnienie - problem po stronie PSE
```

## Zależności

Nie wymaga dodatkowych bibliotek - używa tylko wbudowanych w pandas i Python:
- `datetime` (wbudowane)
- `pandas` (już wymagane)

**Instalacja**:
```bash
./run.sh install
```

## Kod źródłowy

Funkcja: `_filter_future_data()` w [src/pse_energy_scraper.py](../src/pse_energy_scraper.py)

---

**Ostatnia aktualizacja**: 3 lutego 2026 (wersja 1.4.1)
