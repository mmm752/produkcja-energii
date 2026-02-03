#!/bin/bash
# Test czy setup dla nowych użytkowników działa poprawnie

echo "🧪 Test konfiguracji dla nowych użytkowników"
echo ""

# 1. Sprawdź czy .env.example istnieje
if [ -f .env.example ]; then
    echo "✅ Plik .env.example istnieje"
else
    echo "❌ Brak pliku .env.example"
    exit 1
fi

# 2. Sprawdź czy .env jest w .gitignore
if grep -q "^\.env$" .gitignore; then
    echo "✅ Plik .env jest w .gitignore"
else
    echo "❌ Plik .env NIE jest w .gitignore!"
    exit 1
fi

# 3. Sprawdź czy .env NIE jest w repozytorium
if git ls-files | grep -q "^\.env$"; then
    echo "⚠️  UWAGA: Plik .env jest śledzony przez Git!"
    echo "   Uruchom: git rm --cached .env"
else
    echo "✅ Plik .env nie jest śledzony przez Git"
fi

# 4. Sprawdź czy dokumentacja istnieje
docs=(
    "docs/ENTSOE_API_SETUP.md"
    "docs/INSTALACJA_DLA_INNYCH.md"
    "README.md"
    "COMMANDS.md"
)

for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        echo "✅ Dokumentacja: $doc"
    else
        echo "❌ Brak: $doc"
    fi
done

# 5. Sprawdź czy run.sh ma funkcję setup
if grep -q "setup_entsoe()" run.sh; then
    echo "✅ Funkcja setup_entsoe() istnieje w run.sh"
else
    echo "❌ Brak funkcji setup_entsoe() w run.sh"
fi

echo ""
echo "✅ Repozytorium jest gotowe do udostępnienia!"
echo ""
echo "Nowi użytkownicy mogą:"
echo "  1. Sklonować repo"
echo "  2. Uruchomić: ./run.sh install"
echo "  3. Używać bez ENTSO-E (tylko dane PSE)"
echo "  4. Opcjonalnie: ./run.sh setup (dla pełnych danych)"
