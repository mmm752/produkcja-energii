#!/usr/bin/env python3
"""
Skrypt pomocniczy - szybkie uruchomienie najczęstszych operacji
Użycie:
    python scripts/quick.py suma 2026-01-01 2026-01-31
    python scripts/quick.py suma 2026-01-01 2026-01-31 --full  # Z danymi ENTSO-E
    python scripts/quick.py miesieczne 2020 2026
    python scripts/quick.py szereg 2026-01-01 2026-01-31 1D
"""

import sys
import os

# Dodaj ścieżkę do src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pse_energy_scraper import PSEEnergyDataFetcher, EnergyDataAnalyzer
import json

# Spróbuj zaimportować moduły ENTSO-E (opcjonalne)
try:
    from combined_energy_data import CombinedEnergyDataFetcher, CombinedEnergyDataAnalyzer
    ENTSOE_AVAILABLE = True
except ImportError:
    ENTSOE_AVAILABLE = False


def suma_okresu(data_od, data_do, use_combined=True):
    """Szybkie policzenie sumy dla okresu."""
    print(f"📊 Pobieranie danych dla okresu {data_od} do {data_do}...\n")
    
    # Tryb combined (PSE + ENTSO-E) lub tylko PSE
    if use_combined and ENTSOE_AVAILABLE:
        try:
            fetcher = CombinedEnergyDataFetcher()
            df = fetcher.fetch_combined_data(data_od, data_do)
            analyzer_class = CombinedEnergyDataAnalyzer
            print()
        except Exception as e:
            print(f"⚠️  Błąd trybu combined: {e}")
            print("   Używam tylko danych PSE\n")
            use_combined = False
    
    if not use_combined or not ENTSOE_AVAILABLE:
        fetcher = PSEEnergyDataFetcher()
        df = fetcher.fetch_data(data_od, data_do)
        analyzer_class = EnergyDataAnalyzer
    
    if df is None or df.empty:
        print("⚠️  Brak danych\n")
        return
    
    analyzer = analyzer_class(df)
    wyniki = analyzer.sum_period()
    
    # Sprawdź czy są błędy
    if 'błąd' in wyniki:
        print(f"⚠️  {wyniki['błąd']}\n")
        return
    
    print("📈 SUMA:")
    print("─" * 50)
    print(f"Okres:              {wyniki.get('okres_od')} - {wyniki.get('okres_do')}")
    print(f"Liczba pomiarów:    {wyniki.get('liczba_pomiarów', 0)}")
    
    # Wyświetl wszystkie dostępne wskaźniki
    # Najpierw sprawdź czy to tryb combined czy podstawowy
    is_combined = 'wiatr_pse_suma_MW' in wyniki
    
    if is_combined:
        categories = {
            'WIATR (PSE)': 'wiatr_pse',
            'FOTOWOLTAIKA (PSE)': 'pv_pse',
            'ZAPOTRZEBOWANIE': 'demand',
            'SALDO WYMIANY': 'swm_total',
            'WĘGIEL KAMIENNY': 'hard_coal',
            'WĘGIEL BRUNATNY': 'lignite',
            'GAZ': 'gas',
            'WIATR (ENTSO-E)': 'wind_entsoe',
            'SŁOŃCE (ENTSO-E)': 'solar_entsoe',
            'WODA': 'hydro',
            'MAGAZYNY ENERGII': 'storage',
            'BIOMASA': 'biomass'
        }
    else:
        # Tryb podstawowy PSE
        categories = {
            'WIATR': 'wiatr',
            'FOTOWOLTAIKA': 'fotowoltaika',
            'ZAPOTRZEBOWANIE': 'zapotrzebowanie',
            'SALDO WYMIANY': 'saldo_wymiany'
        }
    
    for category_name, key_prefix in categories.items():
        suma_key = f'{key_prefix}_suma_MW'
        mwh_key = f'{key_prefix}_MWh'
        avg_key = f'{key_prefix}_średnia_MW'
        
        if suma_key in wyniki and wyniki.get(suma_key, 0) != 0:
            print()
            print(f"{category_name}:")
            print(f"  Suma MW:          {wyniki.get(suma_key, 0):,.2f} MW")
            print(f"  Energia:          {wyniki.get(mwh_key, 0):,.2f} MWh")
            print(f"  Średnia:          {wyniki.get(avg_key, 0):,.2f} MW")
    
    # Podsumowanie OZE (jeśli są dane)
    if is_combined:
        wiatr_sum = wyniki.get('wiatr_pse_suma_MW', 0)
        pv_sum = wyniki.get('pv_pse_suma_MW', 0)
        wiatr_mwh = wyniki.get('wiatr_pse_MWh', 0)
        pv_mwh = wyniki.get('pv_pse_MWh', 0)
    else:
        wiatr_sum = wyniki.get('wiatr_suma_MW', 0)
        pv_sum = wyniki.get('fotowoltaika_suma_MW', 0)
        wiatr_mwh = wyniki.get('wiatr_MWh', 0)
        pv_mwh = wyniki.get('fotowoltaika_MWh', 0)
    
    if wiatr_sum or pv_sum:
        print()
        print("RAZEM OZE (WIATR + FOTOWOLTAIKA):")
        print(f"  Suma MW:          {wiatr_sum + pv_sum:,.2f} MW")
        print(f"  Energia:          {wiatr_mwh + pv_mwh:,.2f} MWh")



def miesieczne_sumy(rok_od, rok_do, use_combined=True):
    """Miesięczne sumy dla podanych lat."""
    print(f"📊 Miesięczne sumy dla lat {rok_od}-{rok_do}...\n")
    
    # Tryb combined (PSE + ENTSO-E) lub tylko PSE
    if use_combined and ENTSOE_AVAILABLE:
        try:
            fetcher = CombinedEnergyDataFetcher()
            df = fetcher.fetch_combined_data(f"{rok_od}-01-01", f"{rok_do}-12-31")
            analyzer_class = CombinedEnergyDataAnalyzer
            print()
        except Exception as e:
            print(f"⚠️  Błąd trybu combined: {e}")
            print("   Używam tylko danych PSE\n")
            use_combined = False
    
    if not use_combined or not ENTSOE_AVAILABLE:
        fetcher = PSEEnergyDataFetcher()
        df = fetcher.fetch_data(f"{rok_od}-01-01", f"{rok_do}-12-31")
        analyzer_class = EnergyDataAnalyzer
    
    if df is None or df.empty:
        print("⚠️  Używam przykładowych danych\n")
        # Dla demo - tylko ostatni rok
        df = fetcher.generate_sample_data(f"{rok_do}-01-01", f"{rok_do}-12-31")
    
    analyzer = analyzer_class(df)
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


def szereg_czasowy(data_od, data_do, agregacja='1D', use_combined=True):
    """Szereg czasowy z wybraną agregacją."""
    print(f"📊 Szereg czasowy dla okresu {data_od} do {data_do} (agregacja: {agregacja})...\n")
    
    # Tryb combined (PSE + ENTSO-E) lub tylko PSE
    if use_combined and ENTSOE_AVAILABLE:
        try:
            fetcher = CombinedEnergyDataFetcher()
            df = fetcher.fetch_combined_data(data_od, data_do)
            analyzer_class = CombinedEnergyDataAnalyzer
            print()
        except Exception as e:
            print(f"⚠️  Błąd trybu combined: {e}")
            print("   Używam tylko danych PSE\n")
            use_combined = False
    
    if not use_combined or not ENTSOE_AVAILABLE:
        fetcher = PSEEnergyDataFetcher()
        df = fetcher.fetch_data(data_od, data_do)
        analyzer_class = EnergyDataAnalyzer
    
    if df is None or df.empty:
        print("⚠️  Używam przykładowych danych\n")
        df = fetcher.generate_sample_data(data_od, data_do)
    
    analyzer = analyzer_class(df)
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
║  PSE + ENTSO-E Energy Quick - Szybki dostęp do danych energii   ║
╚══════════════════════════════════════════════════════════════════╝

UŻYCIE:

  Suma dla okresu (domyślnie PSE + ENTSO-E):
    python quick.py suma <data_od> <data_do>
    
  Suma dla okresu (tylko PSE):
    python quick.py suma <data_od> <data_do> --pse-only
    
    Przykład:
    python quick.py suma 2026-01-01 2026-01-31
    python quick.py suma 2026-01-01 2026-01-31 --pse-only

  ────────────────────────────────────────────────────────────────

  Miesięczne sumy:
    python quick.py miesieczne <rok_od> <rok_do>
    
    Przykład:
    python quick.py miesieczne 2020 2026

  ────────────────────────────────────────────────────────────────

  Szereg czasowy:
    python quick.py szereg <data_od> <data_do> [agregacja]
    
    Agregacja: 1h (godzinowa), 1D (dzienna), 1W (tygodniowa), 1M (miesięczna)
    
    Przykład:
    python quick.py szereg 2026-01-01 2026-01-31 1D
    python quick.py szereg 2026-01-01 2026-12-31 1W

  ────────────────────────────────────────────────────────────────

ŹRÓDŁA DANYCH:

  Domyślnie (PSE + ENTSO-E - wymaga klucza API):
    PSE:
      - Wiatr, Fotowoltaika
      - Zapotrzebowanie
      - Saldo wymiany międzysystemowej
    
    ENTSO-E:
      - Węgiel kamienny, brunatny
      - Gaz
      - Woda, Biomasa, Magazyny energii
    
    Konfiguracja ENTSO-E: docs/ENTSOE_API_SETUP.md
  
  Flaga --pse-only: tylko dane PSE (bez ENTSO-E)

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
                print("Użycie: python quick.py suma <data_od> <data_do> [--pse-only]")
                print("  Domyślnie: PSE + ENTSO-E (pełne dane)")
                print("  --pse-only : Pobiera tylko dane PSE (bez ENTSO-E)")
                return
            
            # Sprawdź czy jest flaga --pse-only (domyślnie używamy combined)
            use_full = '--pse-only' not in sys.argv
            suma_okresu(sys.argv[2], sys.argv[3], use_combined=use_full)
        
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
