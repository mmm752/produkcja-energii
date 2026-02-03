# Historia zmian

## Wersja 1.4.1 (2026-02-03)

### 🔧 Poprawki krytyczne

**Problem 1: Parametr $top powodował błąd 400**
- API PSE **nie obsługuje** parametru `$top` w zapytaniach OData
- Dodanie tego parametru powodowało błąd: `"Invalid Query Parameter: $top"`
- Rezultat: brak danych z API, kod używał przykładowych danych

**Rozwiązanie:**
- ✅ Usunięto parametr `$top` z zapytań do API PSE
- ✅ API PSE domyślnie zwraca wszystkie rekordy dla pojedynczego dnia (96)
- ✅ Dla okresów > 1 dzień zachowano pobieranie dzień po dniu (limit ~100 rekordów)
- ✅ Dane rzeczywiste działają poprawnie!

**Problem 2: Błędna obsługa braku danych w interfejsie**
- Gdy API nie zwracało danych, kod próbował użyć `len(None)`
- TypeError: object of type 'NoneType' has no len()

**Rozwiązanie:**
- ✅ Dodano inicjalizację zmiennych (df, fetcher, analyzer_class)
- ✅ Poprawiona walidacja przed użyciem len()
- ✅ Lepsze zarządzanie przełączaniem między trybami PSE/combined
- ✅ Czytelne komunikaty o błędach

### 🕐 Nowa funkcja - Filtrowanie danych do ostatniego rzeczywistego pomiaru

**Problem:**
- API PSE zwraca dane za cały dzień, nawet jeśli dzień jeszcze trwa
- Gdy teraz jest 12:20, ostatnia aktualizacja PSE była o 11:45
- API zwracało dane do 23:45 (prognozy), zamiast do 11:45 (ostatni rzeczywisty pomiar)

**Rozwiązanie:**
- ✅ Automatyczne wykrywanie ostatniego rzeczywistego pomiaru w danych
- ✅ Filtrowanie tylko do aktualnie dostępnych danych (z 15 min buforem)
- ✅ Usuwanie danych prognostycznych/przyszłościowych
- ✅ Działa tylko dla bieżącego dnia (nie wpływa na dane historyczne)
- ✅ Nie wymaga dodatkowych bibliotek (używa wbudowanych w pandas)

**Przykład:**
```
Teraz:     2026-02-03 12:20
PSE API:   ostatnia aktualizacja 11:45
Przed:     96 pomiarów (00:00 - 23:45) ❌ zawiera prognozy
Po:        48 pomiarów (00:00 - 11:45) ✅ tylko rzeczywiste dane
ℹ️  Odfiltrowano 48 przyszłościowych pomiarów (ostatni rzeczywisty pomiar: 2026-02-03 11:45)
```

**Dokumentacja:**
- ✅ Zaktualizowano COMMANDS.md - nowa sekcja o limicie 100
- ✅ Zaktualizowano NOTATKI_TECHNICZNE.md - szczegóły OData
- ✅ Dodano FAQ_LIMIT_100.md - kompletny przewodnik rozwiązywania problemu

**Pliki zmienione:**
- `src/pse_energy_scraper.py` - parametry OData i weryfikacja
- `src/pse_energy_interactive.py` - poprawiona obsługa błędów gdy brak danych API
- `docs/COMMANDS.md` - sekcja rozwiązywania problemów
- `docs/NOTATKI_TECHNICZNE.md` - ograniczenia API
- `docs/FAQ_LIMIT_100.md` - nowy dokument

---

## Wersja 1.4.0 (2026-01-19)

### 🎉 Główne zmiany - Integracja ENTSO-E

**Nowe źródło danych:**
- ✅ Dodano integrację z ENTSO-E Transparency Platform
- ✅ Nowa klasa `ENTSOEDataFetcher` do pobierania danych
- ✅ Obsługa klucza API ENTSO-E (plik .env)
- ✅ Parsowanie danych XML z ENTSO-E

**Dodatkowe wskaźniki z ENTSO-E:**
- ✅ Węgiel kamienny [MW]
- ✅ Węgiel brunatny [MW]
- ✅ Gaz [MW]
- ✅ Woda [MW] (suma: przepływowa + zbiornikowa)
- ✅ Magazyny energii [MW]
- ✅ Biomasa [MW]
- ✅ Wiatr lądowy [MW] (ENTSO-E)
- ✅ Słońce [MW] (ENTSO-E)

**Połączenie danych PSE + ENTSO-E:**
- ✅ Nowa klasa `CombinedEnergyDataFetcher`
- ✅ Nowa klasa `CombinedEnergyDataAnalyzer`
- ✅ Automatyczne łączenie danych po timestamp
- ✅ Graceful fallback do trybu PSE gdy ENTSO-E niedostępne

**Ulepszenia skryptów:**
- ✅ Flaga `--full` w quick.py dla pełnych danych
- ✅ Automatyczne wykrywanie dostępności ENTSO-E
- ✅ Wyswietlanie wszystkich dostępnych wskaźników

**Dokumentacja:**
- ✅ Nowy plik `docs/ENTSOE_API_SETUP.md` - instrukcja konfiguracji
- ✅ Plik `.env.example` dla klucza API
- ✅ Zaktualizowano README.md
- ✅ Zaktualizowano COMMANDS.md
- ✅ Dodano `.env` do `.gitignore`

**Zależności:**
- ✅ Dodano `python-dotenv>=1.0.0` do requirements.txt

---

## Wersja 1.3.0 (2026-01-19)

### 🎉 Nowe funkcje

**Rozszerzone pobieranie danych:**
- ✅ Dodano pobieranie **Zapotrzebowania na moc [MW]** (`demand`)
- ✅ Dodano pobieranie **Krajowego salda wymiany międzysystemowej [MW]** (suma `swm_p` + `swm_np`)
- ✅ Automatyczne obliczanie sumy sald równoległych i nierównoległych
- ✅ Wszystkie nowe wskaźniki dostępne we wszystkich funkcjach (suma, miesięczne, szereg czasowy)

**Ulepszenia wyświetlania:**
- ✅ Zaktualizowano skrypt `quick.py` o wyświetlanie nowych wskaźników
- ✅ Dodano sekcje "ZAPOTRZEBOWANIE" i "SALDO WYMIANY MIĘDZYSYSTEMOWEJ" w wynikach
- ✅ Interfejs interaktywny automatycznie pokazuje wszystkie dostępne wskaźniki

**Dokumentacja:**
- ✅ Zaktualizowano README.md o nowe wskaźniki
- ✅ Zaktualizowano API_EXAMPLES.md o pola `demand`, `swm_p`, `swm_np`
- ✅ Dodano generowanie przykładowych danych dla nowych wskaźników

---

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
