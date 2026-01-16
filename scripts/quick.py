#!/usr/bin/env python3
"""
Skrypt pomocniczy - szybkie uruchomienie najczęstszych operacji
Użycie:
    python scripts/quick.py suma 2026-01-01 2026-01-31
    python scripts/quick.py miesieczne 2020 2026
    python scripts/quick.py szereg 2026-01-01 2026-01-31 1D
"""

import sys
import os

# Dodaj ścieżkę do src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pse_energy_scraper import PSEEnergyDataFetcher, EnergyDataAnalyzer
import json


def suma_okresu(data_od, data_do):
    """Szybkie policzenie sumy dla okresu."""
    print(f"📊 Pobieranie danych dla okresu {data_od} do {data_do}...\n")
    
    fetcher = PSEEnergyDataFetcher()
    df = fetcher.fetch_data(data_od, data_do)
    
    if df is None or df.empty:
        print("⚠️  Brak danych\n")
        return
    
    analyzer = EnergyDataAnalyzer(df)
    wyniki = analyzer.sum_period()
    
    # Sprawdź czy są błędy
    if 'błąd' in wyniki:
        print(f"⚠️  {wyniki['błąd']}\n")
        return
    
    print("📈 SUMA:")
    print("─" * 50)
    print(f"Okres:              {wyniki.get('okres_od')} - {wyniki.get('okres_do')}")
    print(f"Liczba pomiarów:    {wyniki.get('liczba_pomiarów', 0)}")
    print()
    print("WIATR:")
    print(f"  Suma MW:          {wyniki.get('wiatr_suma_MW', 0):,.2f} MW")
    print(f"  Energia:          {wyniki.get('wiatr_MWh', 0):,.2f} MWh")
    print(f"  Średnia:          {wyniki.get('wiatr_średnia_MW', 0):,.2f} MW")
    print()
    print("FOTOWOLTAIKA:")
    print(f"  Suma MW:          {wyniki.get('fotowoltaika_suma_MW', 0):,.2f} MW")
    print(f"  Energia:          {wyniki.get('fotowoltaika_MWh', 0):,.2f} MWh")
    print(f"  Średnia:          {wyniki.get('fotowoltaika_średnia_MW', 0):,.2f} MW")
    print()
    print("RAZEM:")
    print(f"  Suma MW:          {wyniki.get('wiatr_suma_MW', 0) + wyniki.get('fotowoltaika_suma_MW', 0):,.2f} MW")
    print(f"  Energia:          {wyniki.get('wiatr_MWh', 0) + wyniki.get('fotowoltaika_MWh', 0):,.2f} MWh")



def miesieczne_sumy(rok_od, rok_do):
    """Miesięczne sumy dla podanych lat."""
    print(f"📊 Miesięczne sumy dla lat {rok_od}-{rok_do}...\n")
    
    fetcher = PSEEnergyDataFetcher()
    df = fetcher.fetch_data(f"{rok_od}-01-01", f"{rok_do}-12-31")
    
    if df is None or df.empty:
        print("⚠️  Używam przykładowych danych\n")
        # Dla demo - tylko ostatni rok
        df = fetcher.generate_sample_data(f"{rok_do}-01-01", f"{rok_do}-12-31")
    
    analyzer = EnergyDataAnalyzer(df)
    miesieczne = analyzer.monthly_sums(int(rok_od), int(rok_do))
    
    print("📈 MIESIĘCZNE SUMY:")
    print("─" * 50)
    print(miesieczne.to_string())
    
    # Zapisz do CSV
    import os
    os.makedirs('wyniki', exist_ok=True)
    filename = f"wyniki/miesieczne_{rok_od}_{rok_do}.csv"
    miesieczne.to_csv(filename, sep=';', decimal=',', encoding='utf-8-sig')
    print(f"\n💾 Zapisano: {filename}")


def szereg_czasowy(data_od, data_do, agregacja='1D'):
    """Szereg czasowy z wybraną agregacją."""
    print(f"📊 Szereg czasowy dla okresu {data_od} do {data_do} (agregacja: {agregacja})...\n")
    
    fetcher = PSEEnergyDataFetcher()
    df = fetcher.fetch_data(data_od, data_do)
    
    if df is None or df.empty:
        print("⚠️  Używam przykładowych danych\n")
        df = fetcher.generate_sample_data(data_od, data_do)
    
    analyzer = EnergyDataAnalyzer(df)
    szereg = analyzer.get_time_series(agregacja)
    
    print("📈 SZEREG CZASOWY (pierwsze 20 rekordów):")
    print("─" * 50)
    print(szereg.head(20).to_string())
    
    # Zapisz do CSV
    import os
    os.makedirs('wyniki', exist_ok=True)
    filename = f"wyniki/szereg_{data_od}_{data_do}_{agregacja}.csv"
    szereg.to_csv(filename, sep=';', decimal=',', encoding='utf-8-sig')
    print(f"\n💾 Zapisano: {filename}")


def pomoc():
    """Wyświetl pomoc."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║  PSE Energy Quick - Szybki dostęp do danych PSE                  ║
╚══════════════════════════════════════════════════════════════════╝

UŻYCIE:

  Suma dla okresu:
    python quick.py suma <data_od> <data_do>
    
    Przykład:
    python quick.py suma 2026-01-01 2026-01-31

  ────────────────────────────────────────────────────────────────

  Miesięczne sumy:
    python quick.py miesieczne <rok_od> <rok_do>
    
    Przykład:
    python quick.py miesieczne 2020 2026

  ────────────────────────────────────────────────────────────────

  Szereg czasowy:
    python quick.py szereg <data_od> <data_do> [agregacja]
    
    Agregacja: 1H (godzinowa), 1D (dzienna), 1W (tygodniowa), 1M (miesięczna)
    
    Przykład:
    python quick.py szereg 2026-01-01 2026-01-31 1D
    python quick.py szereg 2026-01-01 2026-12-31 1W

  ────────────────────────────────────────────────────────────────

FORMAT DAT:
  - YYYY-MM-DD (np. 2026-01-15)
  - DD.MM.YYYY (np. 15.01.2026)

WYNIKI:
  - Automatycznie zapisywane do plików CSV/JSON
  - Nazwy plików zawierają datę i typ analizy

""")


def main():
    """Główna funkcja."""
    if len(sys.argv) < 2:
        pomoc()
        return
    
    komenda = sys.argv[1].lower()
    
    try:
        if komenda == 'suma':
            if len(sys.argv) < 4:
                print("❌ Błąd: Brakuje parametrów")
                print("Użycie: python quick.py suma <data_od> <data_do>")
                return
            suma_okresu(sys.argv[2], sys.argv[3])
        
        elif komenda == 'miesieczne' or komenda == 'miesięczne':
            if len(sys.argv) < 4:
                print("❌ Błąd: Brakuje parametrów")
                print("Użycie: python quick.py miesieczne <rok_od> <rok_do>")
                return
            miesieczne_sumy(sys.argv[2], sys.argv[3])
        
        elif komenda == 'szereg':
            if len(sys.argv) < 4:
                print("❌ Błąd: Brakuje parametrów")
                print("Użycie: python quick.py szereg <data_od> <data_do> [agregacja]")
                return
            agregacja = sys.argv[4] if len(sys.argv) > 4 else '1D'
            szereg_czasowy(sys.argv[2], sys.argv[3], agregacja)
        
        elif komenda in ['help', 'pomoc', '-h', '--help']:
            pomoc()
        
        else:
            print(f"❌ Nieznana komenda: {komenda}")
            pomoc()
    
    except Exception as e:
        print(f"❌ Błąd: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
