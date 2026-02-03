# ❓ FAQ: Problem z limitem 100 rekordów

## Problem

**Objawy:**
- Pobieranie danych dla 2+ dni zwraca tylko 100 rekordów zamiast pełnych danych
- Okres 2026-02-02 do 2026-02-03 powinien dać 192 pomiary (2 dni × 96), ale zwraca tylko 100

## Przyczyna

**API PSE ma oficjalny limit ~100 rekordów** na pojedyncze zapytanie OData.

### Matematyka

Dane PSE publikowane są **co 15 minut**:
- **1 godzina** = 4 pomiary (00:00, 00:15, 00:30, 00:45)
- **1 dzień** = 96 pomiarów (24h × 4)
- **2 dni** = 192 pomiary ❌ **przekracza limit 100!**

## Rozwiązanie

### Wersja zaktualizowana (2026-02-03 i nowsze)

Kod **automatycznie** radzi sobie z tym problemem:

1. ✅ **Pobieranie dzień po dniu** - dla okresów > 1 dzień
2. ✅ **Parametr `$top=200`** - zabezpieczenie w zapytaniach OData
3. ✅ **Ostrzeżenia** - gdy wykryto możliwy limit API
4. ✅ **Weryfikacja** - sprawdza duplikaty i kompletność

### Sprawdź swoją wersję

```bash
# Sprawdź ostatni commit
git log --oneline -1

# Zaktualizuj do najnowszej wersji
git pull
```

### Użycie

```bash
# Najłatwiej - tryb interaktywny (zawsze działa poprawnie)
./run.sh i

# Lub bezpośrednio
./run.sh suma 2026-02-01 2026-02-03
```

**Wynik**: Powinno zwrócić wszystkie rekordy (np. 192 dla 2 dni).

## Starsze wersje kodu

Jeśli masz starszą wersję **bez tej poprawki**:

### Opcja 1: Aktualizacja (zalecane)
```bash
git pull
# lub pobierz najnowszą wersję z repozytorium
```

### Opcja 2: Manualne pobieranie dzień po dniu
```bash
# Zamiast:
./run.sh suma 2026-02-01 2026-02-03  # ❌ zwraca tylko 100

# Użyj osobno:
./run.sh suma 2026-02-01 2026-02-01  # ✅ 96 rekordów
./run.sh suma 2026-02-02 2026-02-02  # ✅ 96 rekordów  
./run.sh suma 2026-02-03 2026-02-03  # ✅ X rekordów (bieżący dzień)
```

## Techniczne szczegóły

### Jak sprawdzić czy masz problem?

Uruchom kod i obserwuj output:

#### ✅ Poprawna wersja
```
📥 Pobieranie danych dla 2 dni...
  ✓ Pobrano 2 dni...
Okres:              2026-02-02 00:00 - 2026-02-03 23:45
Liczba pomiarów:    192
```

#### ❌ Błędna wersja
```
Okres:              2026-02-02 00:00 - 2026-02-02 15:45
Liczba pomiarów:    100  # ← Problem! Powinno być 192
⚠️  OSTRZEŻENIE: Otrzymano dokładnie 100 rekordów!
```

### Zapytania OData

**Błędne** (przekracza limit):
```python
# Zapytanie o 2 dni naraz
$filter=business_date ge '2026-02-02' and business_date le '2026-02-03'
# Wynik: tylko pierwsze 100 z 192 rekordów ❌
```

**Poprawne** (dzień po dniu):
```python
# Dzień 1
$filter=business_date eq '2026-02-02'
$top=200
# Wynik: 96 rekordów ✅

# Dzień 2
$filter=business_date eq '2026-02-03'
$top=200
# Wynik: 96 rekordów ✅

# Łącznie: 192 rekordy ✅
```

## Inne komputery

**Problem**: Na innym komputerze kod działa źle.

**Rozwiązanie**:
1. Sprawdź wersję kodu (data ostatniej modyfikacji pliku `pse_energy_scraper.py`)
2. Jeśli starsze niż 2026-02-03 → zaktualizuj
3. Upewnij się że plik zawiera:
   - Linię 46: komentarz o limicie API
   - Linię 112-114: `params` z `$top=200`
   - Linię 149-151: `params` z `$top=200`

```bash
# Sprawdź obecność poprawek
grep -n "\$top" src/pse_energy_scraper.py

# Powinno zwrócić 2 linie (około 113 i 150)
```

## Wsparcie

Jeśli nadal masz problem:
1. Sprawdź [COMMANDS.md](../COMMANDS.md) - sekcja "Rozwiązywanie problemów"
2. Zobacz [NOTATKI_TECHNICZNE.md](NOTATKI_TECHNICZNE.md) - szczegóły API
3. Uruchom test: `./run.sh test`

---

**Ostatnia aktualizacja:** 3 lutego 2026
