#!/usr/bin/env python3
"""
Przykłady użycia biblioteki PSE Energy Scraper
"""

import sys
import os

# Dodaj ścieżkę do src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pse_energy_scraper import PSEEnergyDataFetcher, EnergyDataAnalyzer
from datetime import datetime, timedelta
import json


def przyklad_1_suma_miesiac():
    """Przykład 1: Suma dla stycznia 2026"""
    print("\n" + "="*70)
    print("PRZYKŁAD 1: Suma produkcji dla stycznia 2026")
    print("="*70 + "\n")
    
    fetcher = PSEEnergyDataFetcher()
    df = fetcher.fetch_data("2026-01-01", "2026-01-31")
    
    if df is None or df.empty:
        df = fetcher.generate_sample_data("2026-01-01", "2026-01-31")
    
    analyzer = EnergyDataAnalyzer(df)
    wyniki = analyzer.sum_period()
    
    print(f"Produkcja wiatrowa: {wyniki.get('wiatr_MWh', 0):,.0f} MWh")
    print(f"Produkcja fotowoltaiczna: {wyniki.get('fotowoltaika_MWh', 0):,.0f} MWh")
    print(f"Łączna produkcja OZE: {wyniki.get('wiatr_MWh', 0) + wyniki.get('fotowoltaika_MWh', 0):,.0f} MWh")


def przyklad_2_porownanie_miesiecy():
    """Przykład 2: Porównanie produkcji w różnych miesiącach"""
    print("\n" + "="*70)
    print("PRZYKŁAD 2: Porównanie miesięcy (styczeń vs luty 2026)")
    print("="*70 + "\n")
    
    fetcher = PSEEnergyDataFetcher()
    
    # Styczeń
    df_styczen = fetcher.fetch_data("2026-01-01", "2026-01-31")
    if df_styczen is None or df_styczen.empty:
        df_styczen = fetcher.generate_sample_data("2026-01-01", "2026-01-31")
    
    analyzer_styczen = EnergyDataAnalyzer(df_styczen)
    styczen = analyzer_styczen.sum_period()
    
    # Luty
    df_luty = fetcher.fetch_data("2026-02-01", "2026-02-28")
    if df_luty is None or df_luty.empty:
        df_luty = fetcher.generate_sample_data("2026-02-01", "2026-02-28")
    
    analyzer_luty = EnergyDataAnalyzer(df_luty)
    luty = analyzer_luty.sum_period()
    
    print("┌─────────────────┬──────────────┬──────────────┬──────────────┐")
    print("│ Miesiąc         │ Wiatr [MWh]  │ PV [MWh]     │ Razem [MWh]  │")
    print("├─────────────────┼──────────────┼──────────────┼──────────────┤")
    print(f"│ Styczeń 2026    │ {styczen.get('wiatr_MWh', 0):>12,.0f} │ {styczen.get('fotowoltaika_MWh', 0):>12,.0f} │ {styczen.get('wiatr_MWh', 0) + styczen.get('fotowoltaika_MWh', 0):>12,.0f} │")
    print(f"│ Luty 2026       │ {luty.get('wiatr_MWh', 0):>12,.0f} │ {luty.get('fotowoltaika_MWh', 0):>12,.0f} │ {luty.get('wiatr_MWh', 0) + luty.get('fotowoltaika_MWh', 0):>12,.0f} │")
    print("└─────────────────┴──────────────┴──────────────┴──────────────┘")


def przyklad_3_szereg_godzinowy():
    """Przykład 3: Szereg czasowy z agregacją godzinową dla wybranego dnia"""
    print("\n" + "="*70)
    print("PRZYKŁAD 3: Godzinowa produkcja dla 1 stycznia 2026")
    print("="*70 + "\n")
    
    fetcher = PSEEnergyDataFetcher()
    df = fetcher.fetch_data("2026-01-01", "2026-01-02")
    
    if df is None or df.empty:
        df = fetcher.generate_sample_data("2026-01-01", "2026-01-02")
    
    analyzer = EnergyDataAnalyzer(df)
    szereg_godzinowy = analyzer.get_time_series('1H')
    
    # Pokaż tylko pierwsze 24 godziny (1 dzień)
    print(szereg_godzinowy.head(24).to_string())


def przyklad_4_eksport_json():
    """Przykład 4: Eksport danych do JSON"""
    print("\n" + "="*70)
    print("PRZYKŁAD 4: Eksport miesięcznych sum do JSON")
    print("="*70 + "\n")
    
    fetcher = PSEEnergyDataFetcher()
    df = fetcher.fetch_data("2026-01-01", "2026-03-31")
    
    if df is None or df.empty:
        df = fetcher.generate_sample_data("2026-01-01", "2026-03-31")
    
    analyzer = EnergyDataAnalyzer(df)
    miesieczne = analyzer.monthly_sums(2026, 2026)
    
    # Konwersja do słownika
    wynik = {}
    for index, row in miesieczne.iterrows():
        wynik[str(index)] = {
            'wiatr_MWh': round(row.iloc[0], 2),
            'fotowoltaika_MWh': round(row.iloc[1], 2)
        }
    
    filename = 'przyklad_miesieczne.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(wynik, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Zapisano do: {filename}")
    print("\nZawartość pliku:")
    print(json.dumps(wynik, indent=2, ensure_ascii=False))


def przyklad_5_statystyki():
    """Przykład 5: Dodatkowe statystyki"""
    print("\n" + "="*70)
    print("PRZYKŁAD 5: Statystyki produkcji dla stycznia 2026")
    print("="*70 + "\n")
    
    fetcher = PSEEnergyDataFetcher()
    df = fetcher.fetch_data("2026-01-01", "2026-01-31")
    
    if df is None or df.empty:
        df = fetcher.generate_sample_data("2026-01-01", "2026-01-31")
    
    analyzer = EnergyDataAnalyzer(df)
    
    # Podstawowe statystyki
    if analyzer.wind_col and analyzer.solar_col:
        wiatr_stats = analyzer.df[analyzer.wind_col].describe()
        pv_stats = analyzer.df[analyzer.solar_col].describe()
        
        print("Statystyki produkcji wiatrowej [MW]:")
        print(f"  Średnia:        {wiatr_stats['mean']:>10.2f} MW")
        print(f"  Minimum:        {wiatr_stats['min']:>10.2f} MW")
        print(f"  Maksimum:       {wiatr_stats['max']:>10.2f} MW")
        print(f"  Odch. std:      {wiatr_stats['std']:>10.2f} MW")
        
        print("\nStatystyki produkcji fotowoltaicznej [MW]:")
        print(f"  Średnia:        {pv_stats['mean']:>10.2f} MW")
        print(f"  Minimum:        {pv_stats['min']:>10.2f} MW")
        print(f"  Maksimum:       {pv_stats['max']:>10.2f} MW")
        print(f"  Odch. std:      {pv_stats['std']:>10.2f} MW")
        
        # Współczynnik wykorzystania
        # Zakładamy zainstalowaną moc: wiatr 10 GW, PV 20 GW
        zainstalowana_wiatr = 10000  # MW
        zainstalowana_pv = 20000     # MW
        
        wspolczynnik_wiatr = (wiatr_stats['mean'] / zainstalowana_wiatr) * 100
        wspolczynnik_pv = (pv_stats['mean'] / zainstalowana_pv) * 100
        
        print(f"\nWspółczynnik wykorzystania:")
        print(f"  Wiatr:          {wspolczynnik_wiatr:>10.1f} %")
        print(f"  Fotowoltaika:   {wspolczynnik_pv:>10.1f} %")


def main():
    """Uruchom wszystkie przykłady"""
    print("\n" + "🔋" * 35)
    print(" " * 10 + "PRZYKŁADY UŻYCIA PSE ENERGY SCRAPER")
    print("🔋" * 35)
    
    przyklad_1_suma_miesiac()
    przyklad_2_porownanie_miesiecy()
    przyklad_3_szereg_godzinowy()
    przyklad_4_eksport_json()
    przyklad_5_statystyki()
    
    print("\n" + "="*70)
    print("✓ Wszystkie przykłady zakończone!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
