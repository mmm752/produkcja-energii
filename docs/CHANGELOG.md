# Historia zmian

## Wersja 1.2.0 (2026-01-16)

### 🎉 Nowe funkcje

**Reorganizacja struktury projektu:**
- ✅ Utworzono foldery: `src/`, `scripts/`, `docs/`
- ✅ Dodano skrypt `run.sh` - wygodny interfejs do wszystkich funkcji
- ✅ Utworzono `COMMANDS.md` z pełną listą komend
- ✅ Dodano `INFO.txt` - szybki przewodnik

**Format europejski CSV:**
- ✅ Separator kolumn: `;` (średnik)
- ✅ Separator dziesiętny: `,` (przecinek)
- ✅ Kodowanie: UTF-8 z BOM
- ✅ Pełna kompatybilność z polskim Excelem

### 🐛 Naprawione błędy

**Walidacja dat:**
- ✅ Dodano sprawdzanie czy data początkowa nie jest późniejsza niż końcowa
- ✅ Czytelne komunikaty błędów
- ✅ Obsługa pustego DataFrame (naprawiono błąd `NaTType does not support strftime`)

**Ulepszone wyświetlanie wyników:**
- ✅ Dodano wyświetlanie zarówno sum w MW jak i energii w MWh
- ✅ Dodano liczbę pomiarów
- ✅ Dodano wyświetlanie okresu danych
- ✅ Poprawa czytelności wyników (podział na sekcje)

---

## Wersja 1.1.0 (2026-01-16)

### 🎉 Główne zmiany

**Integracja z prawdziwym API PSE:**
- ✅ Połączenie z oficjalnym API PSE v2 (https://api.raporty.pse.pl/api/)
- ✅ Używanie endpointu `/his-wlk-cal` z filtrowaniem OData
- ✅ Automatyczne pobieranie danych dzień po dniu dla długich okresów
- ✅ Obsługa prawdziwych danych z PSE (wiatr, fotowoltaika)

**Poprawki:**
- Usunięto generowanie przykładowych danych jako domyślne zachowanie
- Zaktualizowano dokumentację z informacjami o API
- Dodano obsługę limitów API (max 100 rekordów)

**Struktura danych:**
- Mapowanie pól API: `wi` → wiatr, `pv` → fotowoltaika
- Parsowanie dat w formacie ISO
- Obsługa wszystkich dodatkowych pól z API (demand, period, etc.)

---

## Wersja 1.0.0 (2026-01-16)

### ✨ Pierwsze wydanie

**Główne funkcje:**
- ✅ Pobieranie danych o produkcji energii wiatrowej i fotowoltaicznej z PSE
- ✅ Obsługa danych 15-minutowych
- ✅ Sumowanie produkcji dla dowolnego okresu
- ✅ Generowanie miesięcznych sum
- ✅ Tworzenie szeregów czasowych z różną agregacją
- ✅ Eksport danych do CSV i JSON

**Interfejsy użytkownika:**
- 📱 `quick.py` - szybki dostęp z linii poleceń
- 🎮 `pse_energy_interactive.py` - interaktywne menu
- 🔧 `pse_energy_scraper.py` - moduł główny (API programistyczne)
- 📓 `analiza_pse.ipynb` - notebook Jupyter z wizualizacjami
- 💡 `examples.py` - 5 przykładów użycia

**Dokumentacja:**
- 📖 README.md - pełna dokumentacja
- 🚀 QUICK_START.md - szybki start
- 🔧 NOTATKI_TECHNICZNE.md - zaawansowana konfiguracja

**Funkcje techniczne:**
- Automatyczne wykrywanie kolumn w danych
- Obsługa wielu formatów dat (YYYY-MM-DD, DD.MM.YYYY, etc.)
- Przeliczanie MW → MWh z uwzględnieniem interwału 15 min
- Generowanie przykładowych danych (gdy API niedostępne)
- Wsparcie dla różnych agregacji (1H, 1D, 1W, 1M)
- Eksport do CSV z polskimi znakami (UTF-8-sig)

**Statystyki:**
- ~1500 linii kodu i dokumentacji
- 9 plików źródłowych
- 5 zależności Python

### 📋 Znane ograniczenia

- API zwraca maksymalnie ~100 rekordów na zapytanie (skrypt automatycznie dzieli na mniejsze reqesty)
- Dane dostępne z opóźnieniem (zazwyczaj kilka godzin od czasu rzeczywistego)

### 🔮 Planowane funkcje (v1.2.0)

- [ ] Cache dla pobranych danych (aby uniknąć wielokrotnych zapytań)
- [ ] Retry logic dla requestów (obsługa błędów sieci)
- [ ] Równoległe pobieranie danych (Thread Pool)
- [ ] Więcej typów wykresów w Jupyter Notebook
- [ ] Eksport do Excel
- [ ] Porównanie rok do roku
- [ ] Alerty przy niskiej produkcji
- [ ] Interfejs webowy (Flask/Streamlit)

---

## Format wersji

Projekt używa [Semantic Versioning](https://semver.org/):
- MAJOR.MINOR.PATCH
- MAJOR - niekompatybilne zmiany API
- MINOR - nowe funkcje (wstecznie kompatybilne)
- PATCH - poprawki błędów
