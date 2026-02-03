# 📦 Jak udostępnić to repozytorium innym osobom

## ✅ Co już działa bez konfiguracji

Każda osoba, która sklonuje to repozytorium, będzie mogła **natychmiast** używać:

- ✅ Pobierania danych PSE (wiatr, słońce, zapotrzebowanie, saldo)
- ✅ Wszystkich komend przez `run.sh`
- ✅ Trybu interaktywnego `./run.sh interactive`
- ✅ Generowania raportów i wykresów

**Nie wymaga żadnej konfiguracji!**

## 🔑 Co wymaga konfiguracji przez każdego użytkownika

Aby korzystać z **pełnych danych ENTSO-E** (węgiel, gaz, woda, biomasa, magazyny):

Każdy użytkownik musi:
1. Zarejestrować własne konto na https://transparency.entsoe.eu/
2. Wygenerować własny klucz API
3. Uruchomić `./run.sh setup` i wpisać swój klucz

**Dlaczego?**
- Klucze API są **osobiste** i nie mogą być udostępniane
- Każdy użytkownik musi mieć swoje konto ENTSO-E
- Twój klucz API **nie jest** i **nie powinien być** w repozytorium

## 📋 Instrukcja dla nowych użytkowników

Przekaż im ten link lub sekcję:

### Krok 1: Sklonuj repozytorium
```bash
git clone https://github.com/mmm752/produkcja-energii.git
cd produkcja-energii
```

### Krok 2: Zainstaluj zależności
```bash
./run.sh install
```

### Krok 3: Test (tylko dane PSE)
```bash
./run.sh test
./run.sh interactive
```

✅ **Na tym etapie wszystko już działa!** (tylko dane PSE)

### Krok 4: Opcjonalnie - włącz pełne dane ENTSO-E

Jeśli chcesz mieć również dane o węglu, gazie, wodzie, etc.:

```bash
./run.sh setup
# Następnie podążaj za instrukcjami na ekranie
```

Szczegółowy przewodnik: [ENTSOE_API_SETUP.md](ENTSOE_API_SETUP.md)

## 🔒 Bezpieczeństwo

### Co jest bezpieczne:
- ✅ Plik `.env.example` (szablon)
- ✅ Cały kod źródłowy
- ✅ Dokumentacja

### Co NIE MOŻE być w repozytorium:
- ❌ Plik `.env` (zawiera klucz API)
- ❌ Twój osobisty klucz ENTSO-E
- ❌ Jakiekolwiek hasła lub tokeny

### Jak to jest zabezpieczone:
- `.env` jest w `.gitignore` - nie może być przypadkowo commitowany
- `.env.example` zawiera tylko szablon, nie prawdziwy klucz
- Każdy użytkownik tworzy własny plik `.env` lokalnie

## 📝 Co powinieneś zrobić przed udostępnieniem

1. **Sprawdź `.gitignore`**
   ```bash
   cat .gitignore | grep .env
   # Powinno pokazać: .env
   ```

2. **Sprawdź co jest w repozytorium**
   ```bash
   git status
   # Upewnij się, że .env NIE jest w staged changes
   ```

3. **Dodaj README z instrukcjami**
   - README.md już zawiera sekcję "Konfiguracja API ENTSO-E"
   - Wskaż nowym użytkownikom na `docs/ENTSOE_API_SETUP.md`

4. **Przetestuj na świeżym klonie**
   ```bash
   # W innym folderze
   git clone <url_twojego_repo>
   cd produkcja-energii
   ./run.sh install
   ./run.sh test
   ```

## 💡 Wskazówki

### Dla użytkowników bez klucza ENTSO-E:
- Wszystkie komendy działają, ale z ograniczonymi danymi (tylko PSE)
- W menu interactive pojawi się informacja jak włączyć pełny tryb
- Mogą pracować bez ENTSO-E i dodać klucz później

### Dla użytkowników z kluczem ENTSO-E:
- Po skonfigurowaniu klucza wszystko działa automatycznie
- Tryb interactive automatycznie wykrywa klucz i używa pełnych danych
- Mogą używać flagi `--full` w komendach CLI

## ❓ FAQ dla nowych użytkowników

**Q: Dlaczego nie mogę pobrać danych ENTSO-E?**
A: Musisz skonfigurować swój własny klucz API. Uruchom `./run.sh setup`

**Q: Gdzie jest klucz API w repozytorium?**
A: Nigdzie! Każdy użytkownik musi mieć własny klucz. To kwestia bezpieczeństwa.

**Q: Czy mogę używać repozytorium bez klucza ENTSO-E?**
A: Tak! Dane PSE (wiatr, słońce, zapotrzebowanie) działają bez klucza.

**Q: Jak długo trwa rejestracja na ENTSO-E?**
A: Zazwyczaj kilka minut. Rejestracja jest darmowa.

**Q: Co się stanie jeśli wpisuję niewłaściwy klucz?**
A: System automatycznie przełączy się na tryb podstawowy (tylko PSE).

## 📞 Dodatkowe zasoby

- [README.md](../README.md) - Główna dokumentacja
- [ENTSOE_API_SETUP.md](ENTSOE_API_SETUP.md) - Szczegółowa instrukcja konfiguracji
- [COMMANDS.md](../COMMANDS.md) - Lista wszystkich komend
- [QUICK_START.md](QUICK_START.md) - Szybki start dla początkujących

---

**Ostatnia aktualizacja:** 20 stycznia 2026
