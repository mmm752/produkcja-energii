# 🔄 Jak zaktualizować kod na innym komputerze

## Szybka instrukcja

Jeśli używasz tego projektu na innym komputerze i chcesz otrzymać najnowsze poprawki:

### Krok 1: Sprawdź czy masz najnowszą wersję
```bash
cd /ścieżka/do/produkcja-energii
git log --oneline -1
```

**Najnowsza wersja:** `5237862 Naprawa filtrowania danych do bieżącego czasu`  
**Data:** 2026-02-03

### Krok 2: Zaktualizuj kod
```bash
git pull origin main
```

### Krok 3: Zrestartuj uruchomione procesy

**WAŻNE!** Jeśli masz uruchomiony interfejs interaktywny:
1. Zakończ go (Ctrl+C lub opcja 0)
2. Uruchom ponownie: `./run.sh i`

**Dlaczego?** Python ładuje kod do pamięci przy starcie. Stary proces używa starej wersji kodu nawet po `git pull`.

---

## Co zostało naprawione w najnowszej wersji?

### Problem
- Błąd `NoneType has no attribute empty` przy pobieraniu danych za dzisiejszy dzień
- Funkcja `_filter_future_data()` zwracała `None` zamiast odfiltrowanych danych
- Interfejs interaktywny crashował dla dat zawierających dzień bieżący

### Rozwiązanie
- Dodano brakujący `return df_filtered` w funkcji filtrowania
- Filtrowanie do ostatniego rzeczywistego pomiaru PSE działa poprawnie
- Automatyczne usuwanie danych prognostycznych/przyszłych

### Testy
- ✅ Pojedynczy dzień (2026-02-03): 47 rekordów do 11:30
- ✅ Wczoraj + dziś (2026-02-02 do 03): 142 rekordy (96+46)
- ✅ Trzy dni historyczne (2026-01-01 do 03): 288 rekordów pełnych

---

## Szczegółowa instrukcja dla początkujących

### 1. Otwórz terminal/konsolę

**Windows (Git Bash lub WSL):**
```bash
cd C:/Users/TwojeImie/projekty/produkcja-energii
```

**macOS/Linux:**
```bash
cd ~/projekty/produkcja-energii
```

### 2. Sprawdź status
```bash
git status
```

**Jeśli widzisz:**
```
On branch main
Your branch is behind 'origin/main' by X commits
```
→ Masz starą wersję, przejdź do kroku 3

**Jeśli widzisz:**
```
On branch main
Your branch is up to date with 'origin/main'
```
→ Masz najnowszą wersję ✅

### 3. Pobierz aktualizacje
```bash
git pull origin main
```

**Jeśli widzisz błąd:**
```
error: Your local changes to the following files would be overwritten by merge:
```

**Rozwiązanie:**
```bash
# Opcja A: Zachowaj swoje zmiany
git stash
git pull origin main
git stash pop

# Opcja B: Odrzuć swoje zmiany (UWAGA: straty!)
git reset --hard origin/main
```

### 4. Sprawdź czy aktualizacja się powiodła
```bash
git log --oneline -3
```

Powinno pokazać:
```
5237862 Naprawa filtrowania danych do bieżącego czasu
ada41a7 (poprzedni commit)
...
```

### 5. Zrestartuj aplikację

**Jeśli masz uruchomiony interfejs interaktywny:**
1. Naciśnij `Ctrl+C` lub wybierz opcję `0. Wyjście`
2. Uruchom ponownie:
   ```bash
   ./run.sh i
   ```

**Jeśli używasz Jupyter Notebook:**
1. Kernel → Restart & Clear Output
2. Uruchom ponownie komórki

### 6. Test
```bash
./run.sh i
# Wybierz: 1 (Suma)
# Data: 3.2.2026 do 3.2.2026
```

**Powinno zadziałać** bez błędu `NoneType`! ✅

---

## Co sprawdzić po aktualizacji?

### ✅ Lista kontrolna
- [ ] `git pull` zakończył się sukcesem
- [ ] Brak komunikatów o konfliktach
- [ ] Zamknąłeś/zrestartowałeś stare procesy Python
- [ ] Test: `./run.sh i` → opcja 1 → dzisiejsza data
- [ ] Widzisz poprawnie odfiltrowane dane (np. 47 rekordów do 11:30)
- [ ] Komunikat: "Automatycznie odfiltrowano X pomiarów z przyszłości"

---

## Problemy i rozwiązania

### Problem: "Already up to date" ale kod nie działa
**Przyczyna:** Python używa starej wersji załadowanej do pamięci  
**Rozwiązanie:** Zrestartuj proces Python (`Ctrl+C` + `./run.sh i`)

### Problem: Konflikt przy `git pull`
**Przyczyna:** Zmiany lokalne konfliktują z aktualizacjami  
**Rozwiązanie:**
```bash
# Zobacz co się zmieniło
git status

# Opcja 1: Zachowaj swoje zmiany
git stash
git pull
git stash pop

# Opcja 2: Zaakceptuj zmiany z serwera
git reset --hard origin/main
```

### Problem: "Cannot pull with rebase: You have unstaged changes"
**Rozwiązanie:**
```bash
git add .
git commit -m "Moje lokalne zmiany"
git pull origin main
```

### Problem: Nadal błąd `NoneType`
**Sprawdź:**
1. Czy faktycznie pobrałeś aktualizację?
   ```bash
   git log --oneline -1
   # Powinno być: 5237862 Naprawa filtrowania...
   ```
2. Czy zrestartowałeś proces Python?
3. Która linia w pliku `pse_energy_scraper.py` ma problem?
   ```bash
   grep -n "return df_filtered" src/pse_energy_scraper.py
   # Powinno pokazać linię ~183
   ```

---

## Różnice między wersjami

### Wersja 1.4.0 (stara) → 1.4.1 (nowa)

**Zmiany w kodzie:**
| Plik | Co się zmieniło |
|------|----------------|
| `src/pse_energy_scraper.py` | Dodano `return df_filtered` w linii 183 |
| `src/pse_energy_interactive.py` | Poprawiona inicjalizacja zmiennych |
| `docs/CHANGELOG.md` | Zaktualizowano historię zmian |

**Nowe pliki:**
- `docs/CURRENT_TIME_FILTER.md` - dokumentacja filtrowania
- `docs/FAQ_LIMIT_100.md` - FAQ o limicie API
- `test_current_time_filter.py` - test demo

**Naprawione błędy:**
- ❌ Przed: Błąd `NoneType has no attribute empty`
- ✅ Po: Poprawne filtrowanie do bieżącego czasu

---

## Automatyzacja aktualizacji (dla zaawansowanych)

### Skrypt aktualizujący
Utwórz plik `update.sh`:
```bash
#!/bin/bash
echo "🔄 Aktualizacja projektu produkcja-energii"
echo ""

# 1. Przejdź do folderu
cd /ścieżka/do/produkcja-energii || exit

# 2. Sprawdź status
echo "📋 Status przed aktualizacją:"
git status

# 3. Pobierz zmiany
echo ""
echo "📥 Pobieranie zmian..."
git pull origin main

# 4. Sprawdź wynik
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Aktualizacja zakończona sukcesem!"
    echo ""
    echo "📝 Ostatnie zmiany:"
    git log --oneline -3
    echo ""
    echo "⚠️  PAMIĘTAJ: Zrestartuj uruchomione procesy Python!"
else
    echo ""
    echo "❌ Błąd podczas aktualizacji"
    echo "Sprawdź komunikaty powyżej"
fi
```

Nadaj uprawnienia:
```bash
chmod +x update.sh
```

Użycie:
```bash
./update.sh
```

---

## Kontakt

Jeśli masz problem z aktualizacją:
1. Sprawdź [COMMANDS.md](../COMMANDS.md) - sekcja "Rozwiązywanie problemów"
2. Zobacz [docs/FAQ_LIMIT_100.md](FAQ_LIMIT_100.md)
3. Otwórz issue na GitHub: https://github.com/mmm752/produkcja-energii/issues

---

**Ostatnia aktualizacja:** 3 lutego 2026  
**Wersja:** 1.4.1
