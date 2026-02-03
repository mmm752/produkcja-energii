#!/bin/bash
# Skrypt z komendami do uruchamiania różnych funkcji projektu PSE
# Użycie: ./run.sh [komenda] [argumenty]

set -e

# Kolory dla lepszej czytelności
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funkcja wyświetlająca pomoc
show_help() {
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}PSE - Skrypt do analizy produkcji energii${NC}                    ${BLUE}║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Dostępne komendy:${NC}"
    echo ""
    echo "  ${GREEN}./run.sh interactive${NC}"
    echo "      Uruchamia interaktywny interfejs (menu)"
    echo ""
    echo "  ${GREEN}./run.sh suma <data_od> <data_do>${NC}"
    echo "      Oblicza sumę produkcji dla podanego okresu"
    echo "      Przykład: ./run.sh suma 2026-01-01 2026-01-31"
    echo ""
    echo "  ${GREEN}./run.sh miesieczne <rok_od> <rok_do>${NC}"
    echo "      Generuje miesięczne sumy dla podanych lat"
    echo "      Przykład: ./run.sh miesieczne 2020 2026"
    echo ""
    echo "  ${GREEN}./run.sh szereg <data_od> <data_do> <agregacja>${NC}"
    echo "      Tworzy szereg czasowy z wybraną agregacją (1H/1D/1W/1M)"
    echo "      Przykład: ./run.sh szereg 2026-01-01 2026-01-31 1D"
    echo ""
    echo "  ${GREEN}./run.sh examples${NC}"
    echo "      Uruchamia przykładowe analizy"
    echo ""
    echo "  ${GREEN}./run.sh notebook${NC}"
    echo "      Otwiera Jupyter Notebook z analizą"
    echo ""
    echo "  ${GREEN}./run.sh install${NC}"
    echo "      Instaluje wymagane pakiety Python"
    echo ""
    echo "  ${GREEN}./run.sh test${NC}"
    echo "      Testuje połączenie z API PSE"
    echo ""
    echo "  ${GREEN}./run.sh setup${NC}"
    echo "      Konfiguruje klucz API ENTSO-E (dla trybu --full)"
    echo ""
}

# Sprawdź czy Python jest zainstalowany
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${YELLOW}⚠️  Python 3 nie jest zainstalowany!${NC}"
        exit 1
    fi
}

# Instalacja zależności
install_deps() {
    echo -e "${GREEN}📦 Instalacja zależności...${NC}"
    python3 -m pip install -r requirements.txt
    echo -e "${GREEN}✅ Zależności zainstalowane!${NC}"
}

# Test API
test_api() {
    echo -e "${GREEN}🔍 Testowanie API PSE...${NC}"
    python3 -c "
from src.pse_energy_scraper import PSEEnergyDataFetcher
from datetime import datetime, timedelta
fetcher = PSEEnergyDataFetcher()
end_date = datetime.now()
start_date = end_date - timedelta(days=1)
df = fetcher.fetch_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
if df is not None and not df.empty:
    print('✅ API działa poprawnie! Pobrano', len(df), 'rekordów')
else:
    print('⚠️  Brak danych z API')
"
}

# Konfiguracja ENTSO-E API
setup_entsoe() {
    echo -e "${GREEN}🔑 Konfiguracja ENTSO-E API${NC}"
    echo ""
    echo "Aby używać trybu --full z pełnymi danymi, potrzebujesz klucza API z:"
    echo "https://transparency.entsoe.eu/"
    echo ""
    echo "Jak zdobyć klucz:"
    echo "1. Zarejestruj się na stronie ENTSO-E"
    echo "2. Zaloguj się i przejdź do 'Account Settings'"
    echo "3. W sekcji 'Web API' kliknij 'Generate API key'"
    echo "4. Skopiuj wygenerowany klucz"
    echo ""
    
    if [ -f .env ]; then
        echo -e "${YELLOW}⚠️  Plik .env już istnieje.${NC}"
        read -p "Czy chcesz go nadpisać? (t/N): " overwrite
        if [ "$overwrite" != "t" ] && [ "$overwrite" != "T" ]; then
            echo "Anulowano."
            return
        fi
    fi
    
    read -p "Podaj swój klucz ENTSO-E API (lub Enter aby pominąć): " api_key
    
    if [ -z "$api_key" ]; then
        echo "Pominięto konfigurację ENTSO-E."
        echo "Możesz ręcznie skopiować .env.example na .env i wpisać klucz."
        return
    fi
    
    echo "ENTSOE_API_KEY=$api_key" > .env
    echo -e "${GREEN}✅ Klucz API został zapisany w pliku .env${NC}"
    echo "Możesz teraz używać opcji --full w komendach"
    echo "lub pełnych danych w trybie interaktywnym"
}

# Główna logika
case "$1" in
    interactive|i)
        check_python
        echo -e "${GREEN}🚀 Uruchamianie interfejsu interaktywnego...${NC}"
        python3 src/pse_energy_interactive.py
        ;;
    suma|s)
        check_python
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo -e "${YELLOW}⚠️  Użycie: ./run.sh suma <data_od> <data_do>${NC}"
            echo "Przykład: ./run.sh suma 2026-01-01 2026-01-31"
            exit 1
        fi
        python3 scripts/quick.py suma "$2" "$3"
        ;;
    miesieczne|m)
        check_python
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo -e "${YELLOW}⚠️  Użycie: ./run.sh miesieczne <rok_od> <rok_do>${NC}"
            echo "Przykład: ./run.sh miesieczne 2020 2026"
            exit 1
        fi
        python3 scripts/quick.py miesieczne "$2" "$3"
        ;;
    szereg|series)
        check_python
        if [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
            echo -e "${YELLOW}⚠️  Użycie: ./run.sh szereg <data_od> <data_do> <agregacja>${NC}"
            echo "Agregacja: 1H (godzinowa), 1D (dzienna), 1W (tygodniowa), 1M (miesięczna)"
            echo "Przykład: ./run.sh szereg 2026-01-01 2026-01-31 1D"
            exit 1
        fi
        python3 scripts/quick.py szereg "$2" "$3" "$4"
        ;;
    examples|e)
        check_python
        echo -e "${GREEN}📚 Uruchamianie przykładów...${NC}"
        python3 scripts/examples.py
        ;;
    notebook|nb|jupyter)
        check_python
        echo -e "${GREEN}📓 Otwieranie Jupyter Notebook...${NC}"
        if command -v jupyter &> /dev/null; then
            jupyter notebook analiza_pse.ipynb
        else
            echo -e "${YELLOW}⚠️  Jupyter nie jest zainstalowany. Instaluję...${NC}"
            pip install jupyter
            jupyter notebook analiza_pse.ipynb
        fi
        ;;
    install)
        install_deps
        ;;
    test)
        check_python
        test_api
        ;;
    setup)
        setup_entsoe
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        echo -e "${YELLOW}⚠️  Nieznana komenda: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
