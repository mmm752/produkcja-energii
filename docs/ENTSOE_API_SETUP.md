# 🔐 Jak uzyskać klucz API ENTSO-E

## 📋 Wymagania

Aby pobierać dane z ENTSO-E Transparency Platform, potrzebujesz klucza API (Security Token).

## 🚀 Kroki rejestracji

### 1. Zarejestruj się na platformie ENTSO-E

1. Odwiedź: https://transparency.entsoe.eu/
2. Kliknij **"Login"** w prawym górnym rogu
3. Wybierz **"Register"**
4. Wypełnij formularz rejestracyjny:
   - Email
   - Hasło
   - Organizacja (możesz wpisać "Personal use" jeśli używasz do celów osobistych)
   - Kraj
5. Potwierdź rejestrację przez email

### 2. Pobierz klucz API

Po zalogowaniu:

1. Kliknij na swoją nazwę użytkownika w prawym górnym rogu
2. Wybierz **"Account Settings"**
3. Znajdź sekcję **"Web API Security Token"**
4. Kliknij **"Generate Token"**
5. Skopiuj wygenerowany token (długi ciąg znaków)

⚠️  **WAŻNE**: Token jest wyświetlany tylko raz! Zapisz go w bezpiecznym miejscu.

### 3. Skonfiguruj klucz w projekcie

**Opcja A: Plik .env (zalecane)**

1. Skopiuj plik `.env.example` jako `.env`:
   ```bash
   cp .env.example .env
   ```

2. Otwórz plik `.env` i wklej swój klucz API:
   ```
   ENTSOE_API_KEY=twój_długi_klucz_api_tutaj
   ```

**Opcja B: Zmienna środowiskowa**

Ustaw zmienną środowiskową w terminalu:

```bash
# Linux/Mac
export ENTSOE_API_KEY='twój_długi_klucz_api_tutaj'

# Windows (PowerShell)
$env:ENTSOE_API_KEY="twój_długi_klucz_api_tutaj"

# Windows (CMD)
set ENTSOE_API_KEY=twój_długi_klucz_api_tutaj
```

## ✅ Testowanie połączenia

Po skonfigurowaniu klucza, przetestuj połączenie:

```bash
# Test modułu ENTSO-E
python3 src/entsoe_data_fetcher.py

# Lub przez połączony moduł
python3 src/combined_energy_data.py
```

## 📊 Jakie dane są dostępne?

Z API ENTSO-E możesz pobierać:

- **Węgiel kamienny** (Fossil Hard coal)
- **Węgiel brunatny** (Fossil Brown coal/Lignite)
- **Gaz** (Fossil Gas)
- **Wiatr lądowy** (Wind Onshore)
- **Słońce** (Solar)
- **Woda**:
  - Przepływowa (Hydro Run-of-river and poundage)
  - Zbiornikowa (Hydro Water Reservoir)
- **Magazyny energii** (Hydro Pumped Storage)
- **Biomasa** (Biomass)

## 🔒 Bezpieczeństwo

⚠️  **Nie commituj pliku `.env` do repozytorium Git!**

Plik `.env` jest już dodany do `.gitignore`, więc nie zostanie przypadkowo wysłany do repozytorium.

## ❓ Problemy?

### Błąd 401 - Unauthorized
- Sprawdź czy klucz API jest poprawny
- Upewnij się że token nie wygasł
- Zaloguj się na platformie ENTSO-E i wygeneruj nowy token

### Błąd 400 - Bad Request
- Sprawdź format dat (YYYY-MM-DD)
- Upewnij się że nie próbujesz pobrać danych z przyszłości
- Sprawdź czy wybrany obszar (Polska) ma dostępne dane

### Brak danych
- API ENTSO-E może mieć opóźnienia w publikacji danych
- Spróbuj wcześniejszego okresu (np. sprzed kilku dni)
- Nie wszystkie typy produkcji mogą być dostępne dla każdego okresu

## 📚 Dodatkowe zasoby

- **Dokumentacja API**: https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html
- **FAQ**: https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/FAQ.html
- **Status API**: https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Status.html

## 💡 Limity API

ENTSO-E API ma następujące limity:
- **400 requestów na minutę**
- **10,000 requestów dziennie**

System automatycznie zarządza requestami aby nie przekroczyć limitów.

---

**Aktualizacja**: 19 stycznia 2026
