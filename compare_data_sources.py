#!/usr/bin/env python3
"""
Skrypt do dogłębnego porównania danych z pliku electricity_production_entsoe_all (2).csv
z danymi pobieranymi przez system z PSE i ENTSO-E.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Dodaj ścieżkę do modułów
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pse_energy_scraper import PSEEnergyDataFetcher
from entsoe_data_fetcher import ENTSOEDataFetcher


def load_csv_file(filepath):
    """Wczytuje plik CSV i przygotowuje do analizy."""
    print("📂 Wczytywanie pliku CSV...")
    df = pd.read_csv(filepath)
    
    # Informacje o pliku
    print(f"   Liczba wierszy: {len(df)}")
    print(f"   Kolumny: {list(df.columns)}")
    
    # Parsowanie dat
    if 'date' in df.columns:
        df['date_parsed'] = pd.to_datetime(df['date'], format='%d.%m.%Y %H:%M')
        print(f"   Zakres dat (data lokalna): {df['date_parsed'].min()} - {df['date_parsed'].max()}")
    
    if 'date_utc' in df.columns:
        df['date_utc_parsed'] = pd.to_datetime(df['date_utc'], format='%d.%m.%Y %H:%M')
        print(f"   Zakres dat (UTC): {df['date_utc_parsed'].min()} - {df['date_utc_parsed'].max()}")
    
    return df


def analyze_csv_structure(df):
    """Analizuje strukturę i jakość danych w pliku CSV."""
    print("\n" + "="*80)
    print("📊 ANALIZA STRUKTURY PLIKU CSV")
    print("="*80)
    
    # Statystyki podstawowe
    print(f"\n1. PODSTAWOWE INFORMACJE:")
    print(f"   - Liczba rekordów: {len(df):,}")
    print(f"   - Liczba kolumn: {len(df.columns)}")
    print(f"   - Rozmiar w pamięci: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    # Zakres czasowy
    if 'date_parsed' in df.columns:
        min_date = df['date_parsed'].min()
        max_date = df['date_parsed'].max()
        date_range_days = (max_date - min_date).days
        
        print(f"\n2. ZAKRES CZASOWY:")
        print(f"   - Od: {min_date}")
        print(f"   - Do: {max_date}")
        print(f"   - Okres: {date_range_days} dni ({date_range_days / 365.25:.1f} lat)")
        print(f"   - Oczekiwana liczba godzin: {date_range_days * 24:,}")
        print(f"   - Faktyczna liczba rekordów: {len(df):,}")
        print(f"   - Różnica: {abs(date_range_days * 24 - len(df)):,} godzin")
    
    # Brakujące wartości
    print(f"\n3. BRAKUJĄCE WARTOŚCI:")
    missing_cols = {}
    for col in df.columns:
        if col not in ['date', 'date_utc', 'date_parsed', 'date_utc_parsed']:
            missing = df[col].isna().sum()
            if missing > 0:
                missing_cols[col] = missing
    
    if missing_cols:
        for col, count in sorted(missing_cols.items(), key=lambda x: x[1], reverse=True):
            pct = (count / len(df)) * 100
            print(f"   - {col}: {count:,} ({pct:.1f}%)")
    else:
        print("   ✓ Brak brakujących wartości")
    
    # Typy źródeł energii
    energy_sources = [col for col in df.columns if col not in 
                     ['date', 'date_utc', 'date_parsed', 'date_utc_parsed']]
    
    print(f"\n4. ŹRÓDŁA ENERGII ({len(energy_sources)} typów):")
    for source in energy_sources:
        if pd.api.types.is_numeric_dtype(df[source]):
            stats = df[source].describe()
            print(f"   - {source}:")
            print(f"     Min: {stats['min']:.2f} MW")
            print(f"     Max: {stats['max']:.2f} MW")
            print(f"     Średnia: {stats['mean']:.2f} MW")
            print(f"     Suma: {df[source].sum():.2f} MWh (za cały okres)")
    
    return energy_sources


def fetch_comparison_data(date_from, date_to, sample_size=7):
    """
    Pobiera dane z PSE i ENTSO-E dla wybranego okresu.
    Dla długich okresów pobiera tylko próbki.
    """
    print("\n" + "="*80)
    print("📥 POBIERANIE DANYCH Z API")
    print("="*80)
    
    # Oblicz długość okresu
    start_date = datetime.strptime(date_from, '%Y-%m-%d')
    end_date = datetime.strptime(date_to, '%Y-%m-%d')
    total_days = (end_date - start_date).days
    
    if total_days > sample_size * 5:
        print(f"\n⚠️  Okres {total_days} dni jest zbyt długi dla pełnego porównania.")
        print(f"   Pobieram próbki: {sample_size} dni z początku, środka i końca okresu")
        
        # Pobierz próbki
        samples = []
        
        # Początek
        samples.append((start_date, start_date + timedelta(days=sample_size-1)))
        
        # Środek
        mid_date = start_date + timedelta(days=total_days // 2)
        samples.append((mid_date, mid_date + timedelta(days=sample_size-1)))
        
        # Koniec
        end_sample_start = end_date - timedelta(days=sample_size-1)
        samples.append((end_sample_start, end_date))
        
        all_pse = []
        all_entsoe = []
        
        for sample_start, sample_end in samples:
            s_from = sample_start.strftime('%Y-%m-%d')
            s_to = sample_end.strftime('%Y-%m-%d')
            print(f"\n📅 Pobieranie próbki: {s_from} - {s_to}")
            
            pse_data, entsoe_data = _fetch_single_period(s_from, s_to)
            if pse_data is not None:
                all_pse.append(pse_data)
            if entsoe_data is not None:
                all_entsoe.append(entsoe_data)
        
        # Połącz próbki
        df_pse = pd.concat(all_pse) if all_pse else None
        df_entsoe = pd.concat(all_entsoe) if all_entsoe else None
        
    else:
        # Pełny zakres dla krótkich okresów
        print(f"\n📅 Pobieranie pełnych danych: {date_from} - {date_to}")
        df_pse, df_entsoe = _fetch_single_period(date_from, date_to)
    
    return df_pse, df_entsoe


def _fetch_single_period(date_from, date_to):
    """Pobiera dane dla pojedynczego okresu."""
    # PSE
    print(f"\n🔌 Pobieranie z PSE...")
    pse_fetcher = PSEEnergyDataFetcher()
    df_pse = pse_fetcher.fetch_data(date_from, date_to)
    
    if df_pse is not None and not df_pse.empty:
        print(f"   ✓ Pobrano {len(df_pse)} rekordów z PSE")
    else:
        print(f"   ⚠️ Brak danych z PSE")
    
    # ENTSO-E
    print(f"\n⚡ Pobieranie z ENTSO-E...")
    try:
        entsoe_fetcher = ENTSOEDataFetcher()
        df_entsoe = entsoe_fetcher.fetch_generation_data(date_from, date_to)
        
        if df_entsoe is not None and not df_entsoe.empty:
            print(f"   ✓ Pobrano {len(df_entsoe)} rekordów z ENTSO-E")
        else:
            print(f"   ⚠️ Brak danych z ENTSO-E")
    except Exception as e:
        print(f"   ❌ Błąd ENTSO-E: {e}")
        df_entsoe = None
    
    return df_pse, df_entsoe


def compare_with_entsoe(df_csv, df_entsoe):
    """Porównuje dane z CSV z danymi z ENTSO-E API."""
    print("\n" + "="*80)
    print("⚡ PORÓWNANIE Z DANYMI ENTSO-E")
    print("="*80)
    
    if df_entsoe is None or df_entsoe.empty:
        print("❌ Brak danych z ENTSO-E do porównania")
        return
    
    # Przygotuj dane ENTSO-E
    if 'Data' in df_entsoe.columns:
        df_entsoe['timestamp'] = pd.to_datetime(df_entsoe['Data'])
    else:
        df_entsoe['timestamp'] = df_entsoe.index
    
    print(f"\nℹ️  Kolumny w danych ENTSO-E API: {list(df_entsoe.columns)}")
    print(f"   Zakres dat: {df_entsoe['timestamp'].min()} - {df_entsoe['timestamp'].max()}")
    print(f"   Liczba rekordów: {len(df_entsoe)}")
    
    # Usuń timezone z danych API dla porównania
    if df_entsoe['timestamp'].dt.tz is not None:
        print(f"   🔄 Konwersja timezone API do naive datetime...")
        df_entsoe['timestamp'] = df_entsoe['timestamp'].dt.tz_localize(None)
    
    # Sprawdź częstotliwość danych CSV
    csv_time_diffs = df_csv['date_parsed'].diff()
    csv_most_common_diff = csv_time_diffs.mode()[0] if len(csv_time_diffs.mode()) > 0 else pd.Timedelta(hours=1)
    
    if csv_most_common_diff == pd.Timedelta(minutes=15):
        print(f"\n   ℹ️  CSV ma dane 15-minutowe - porównanie bez agregacji")
        df_entsoe_comp = df_entsoe.copy()
        df_entsoe_comp['comp_time'] = df_entsoe_comp['timestamp']
        df_csv['comp_time'] = df_csv['date_parsed']
    else:
        # Agreguj dane ENTSO-E do pełnych godzin (średnia z 4 pomiarów po 15 min)
        print(f"\n   🔄 Agregacja danych ENTSO-E z 15-minutowych do godzinowych...")
        df_entsoe['hour'] = df_entsoe['timestamp'].dt.floor('h')
        
        # Kolumny do agregacji (wszystkie MW kolumny)
        agg_cols = [col for col in df_entsoe.columns if '[MW]' in col and col != 'Data']
        
        df_entsoe_comp = df_entsoe.groupby('hour')[agg_cols].mean().reset_index()
        df_entsoe_comp.rename(columns={'hour': 'comp_time'}, inplace=True)
        df_csv['comp_time'] = df_csv['date_parsed'].dt.floor('h')
        print(f"   ✓ Zagregowano do {len(df_entsoe_comp)} godzin")
    
    # Mapowanie kolumn CSV -> ENTSO-E
    column_mapping = {
        'hard_coal': 'Węgiel kamienny [MW]',
        'lignite': 'Węgiel brunatny [MW]',
        'gas': 'Gaz [MW]',
        'biomass': 'Biomasa [MW]',
        'wind_onshore': 'Wiatr lądowy [MW]',
        'solar': 'Słońce [MW]',
        'hydro_pumped_storage': 'Magazyny energii [MW]',
        'hydro_run-of-river_and_poundage': 'Woda (przepływowa) [MW]',
        'hydro_water_reservoir': 'Woda (zbiornikowa) [MW]'
    }
    
    print("\n1. PORÓWNANIE ŹRÓDEŁ ENERGII:")
    print("-" * 80)
    
    differences_found = []
    
    for csv_col, entsoe_col in column_mapping.items():
        if csv_col not in df_csv.columns:
            print(f"⚠️  {csv_col}: brak w pliku CSV")
            continue
        
        if entsoe_col not in df_entsoe_comp.columns:
            print(f"⚠️  {entsoe_col}: brak w danych ENTSO-E API")
            continue
        
        # Znajdź wspólne daty
        csv_dates = set(df_csv['comp_time'])
        entsoe_dates = set(df_entsoe_comp['comp_time'])
        common_dates = csv_dates.intersection(entsoe_dates)
        
        if len(common_dates) == 0:
            print(f"⚠️  {csv_col} vs {entsoe_col}: brak wspólnych dat")
            print(f"     CSV min/max: {df_csv['comp_time'].min()} / {df_csv['comp_time'].max()}")
            print(f"     API min/max: {df_entsoe_comp['comp_time'].min()} / {df_entsoe_comp['comp_time'].max()}")
            continue
        
        # Przygotuj dane do porównania
        df_csv_subset = df_csv[df_csv['comp_time'].isin(common_dates)].copy()
        df_entsoe_subset = df_entsoe_comp[df_entsoe_comp['comp_time'].isin(common_dates)].copy()
        
        # Merge na czas
        merged = pd.merge(
            df_csv_subset[['comp_time', csv_col]],
            df_entsoe_subset[['comp_time', entsoe_col]],
            on='comp_time',
            how='inner'
        )
        
        if len(merged) == 0:
            continue
        
        # Oblicz różnice
        merged['diff'] = merged[csv_col] - merged[entsoe_col]
        merged['diff_pct'] = (merged['diff'] / merged[entsoe_col].replace(0, np.nan)) * 100
        
        # Statystyki
        mean_diff = merged['diff'].mean()
        max_diff = merged['diff'].abs().max()
        mean_pct_diff = merged['diff_pct'].abs().mean()
        
        # Korelacja
        correlation = merged[csv_col].corr(merged[entsoe_col])
        
        status = "✓" if abs(mean_diff) < 10 and correlation > 0.99 else "⚠️"
        
        print(f"\n{status} {csv_col} vs {entsoe_col}:")
        print(f"   - Wspólnych pomiarów: {len(merged)}")
        print(f"   - Średnia różnica: {mean_diff:.2f} MW")
        print(f"   - Maksymalna różnica: {max_diff:.2f} MW")
        print(f"   - Średnia różnica %: {mean_pct_diff:.2f}%")
        print(f"   - Korelacja: {correlation:.6f}")
        
        if abs(mean_diff) >= 10 or correlation < 0.99:
            differences_found.append({
                'source': csv_col,
                'mean_diff': mean_diff,
                'max_diff': max_diff,
                'correlation': correlation
            })
            
            # Pokaż przykłady największych różnic
            top_diffs = merged.nlargest(3, 'diff')[['comp_time', csv_col, entsoe_col, 'diff']]
            print(f"   Największe różnice:")
            for _, row in top_diffs.iterrows():
                print(f"     {row['comp_time']}: CSV={row[csv_col]:.2f} MW, API={row[entsoe_col]:.2f} MW, diff={row['diff']:.2f} MW")
    
    # Podsumowanie
    print("\n" + "="*80)
    if differences_found:
        print(f"⚠️  ZNALEZIONO {len(differences_found)} ŹRÓDEŁ Z ISTOTNYMI RÓŻNICAMI")
        for diff in differences_found:
            print(f"   - {diff['source']}: średnia różnica {diff['mean_diff']:.2f} MW, korelacja {diff['correlation']:.4f}")
    else:
        print("✓ WSZYSTKIE ŹRÓDŁA SĄ ZGODNE (różnice < 10 MW, korelacja > 0.99)")
    
    return differences_found


def compare_with_pse(df_csv, df_pse):
    """Porównuje dane z CSV z danymi z PSE API."""
    print("\n" + "="*80)
    print("🔌 PORÓWNANIE Z DANYMI PSE")
    print("="*80)
    
    if df_pse is None or df_pse.empty:
        print("❌ Brak danych z PSE do porównania")
        return
    
    print("\nℹ️  PSE dostarcza głównie dane o wietrze i fotowoltaice")
    print("    Plik CSV zawiera dane ENTSO-E (wszystkie źródła)")
    print("    Porównanie ograniczone do dostępnych kolumn")
    
    # PSE ma kolumny: Data, Wiatr, Fotowoltaika, ...
    pse_cols = list(df_pse.columns)
    print(f"\nKolumny PSE: {pse_cols}")
    
    # Mapowanie
    mappings = []
    if 'Wiatr' in df_pse.columns and 'wind_onshore' in df_csv.columns:
        mappings.append(('wind_onshore', 'Wiatr'))
    if 'Fotowoltaika' in df_pse.columns and 'solar' in df_csv.columns:
        mappings.append(('solar', 'Fotowoltaika'))
    
    if not mappings:
        print("⚠️  Brak wspólnych kolumn do porównania")
        return
    
    # Przygotuj daty
    if 'Data' in df_pse.columns:
        df_pse['timestamp'] = pd.to_datetime(df_pse['Data'])
    else:
        df_pse['timestamp'] = df_pse.index
    
    for csv_col, pse_col in mappings:
        print(f"\n📊 {csv_col} vs {pse_col}:")
        
        # Znajdź wspólne daty
        csv_dates = set(df_csv['date_parsed'].dt.floor('H'))
        pse_dates = set(df_pse['timestamp'].dt.floor('H'))
        common_dates = csv_dates.intersection(pse_dates)
        
        if len(common_dates) == 0:
            print(f"   ⚠️ Brak wspólnych dat")
            continue
        
        print(f"   Wspólnych pomiarów: {len(common_dates)}")
        
        # Merge
        df_csv_subset = df_csv[df_csv['date_parsed'].dt.floor('H').isin(common_dates)].copy()
        df_csv_subset['hour'] = df_csv_subset['date_parsed'].dt.floor('H')
        
        df_pse_subset = df_pse[df_pse['timestamp'].dt.floor('H').isin(common_dates)].copy()
        df_pse_subset['hour'] = df_pse_subset['timestamp'].dt.floor('H')
        
        merged = pd.merge(
            df_csv_subset[['hour', csv_col]],
            df_pse_subset[['hour', pse_col]],
            on='hour',
            how='inner'
        )
        
        if len(merged) > 0:
            merged['diff'] = merged[csv_col] - merged[pse_col]
            correlation = merged[csv_col].corr(merged[pse_col])
            
            print(f"   - Średnia różnica: {merged['diff'].mean():.2f} MW")
            print(f"   - Maksymalna różnica: {merged['diff'].abs().max():.2f} MW")
            print(f"   - Korelacja: {correlation:.6f}")


def analyze_time_consistency(df_csv):
    """Sprawdza ciągłość czasową i duplikaty."""
    print("\n" + "="*80)
    print("⏰ ANALIZA CIĄGŁOŚCI CZASOWEJ")
    print("="*80)
    
    if 'date_parsed' not in df_csv.columns:
        print("❌ Brak kolumny z datą")
        return
    
    df = df_csv.sort_values('date_parsed').copy()
    
    # Sprawdź duplikaty
    duplicates = df['date_parsed'].duplicated().sum()
    print(f"\n1. DUPLIKATY:")
    if duplicates > 0:
        print(f"   ⚠️  Znaleziono {duplicates} zduplikowanych timestampów")
        dup_dates = df[df['date_parsed'].duplicated(keep=False)]['date_parsed'].unique()
        print(f"   Przykłady: {dup_dates[:5]}")
    else:
        print(f"   ✓ Brak duplikatów")
    
    # Sprawdź luki
    df['time_diff'] = df['date_parsed'].diff()
    expected_diff = pd.Timedelta(hours=1)
    
    gaps = df[df['time_diff'] != expected_diff]
    
    print(f"\n2. LUKI CZASOWE:")
    if len(gaps) > 1:  # Pierwsza różnica zawsze będzie NaT
        print(f"   ⚠️  Znaleziono {len(gaps)-1} luk w danych")
        for idx, row in gaps.head(10).iterrows():
            if pd.notna(row['time_diff']):
                print(f"   - {row['date_parsed']}: luka {row['time_diff']}")
    else:
        print(f"   ✓ Brak luk (ciągłe dane co 1 godzinę)")
    
    # Sprawdź zmiany czasu (DST)
    print(f"\n3. ZMIANY CZASU (DST):")
    dst_transitions = df[
        (df['time_diff'] == pd.Timedelta(hours=0)) |  # Powtórzone godziny
        (df['time_diff'] == pd.Timedelta(hours=2))     # Pominięte godziny
    ]
    
    if len(dst_transitions) > 0:
        print(f"   Znaleziono {len(dst_transitions)} zmian czasu:")
        for idx, row in dst_transitions.iterrows():
            transition_type = "Koniec DST (powtórzona godzina)" if row['time_diff'] == pd.Timedelta(hours=0) else "Początek DST (pominięta godzina)"
            print(f"   - {row['date_parsed']}: {transition_type}")
    else:
        print(f"   ℹ️  Brak wykrytych zmian czasu w próbce")


def generate_summary_report(df_csv, df_pse, df_entsoe):
    """Generuje podsumowanie porównania."""
    print("\n" + "="*80)
    print("📋 PODSUMOWANIE RAPORTU PORÓWNAWCZEGO")
    print("="*80)
    
    print("\n1. ŹRÓDŁO DANYCH - PLIK CSV:")
    print(f"   - Nazwa: electricity_production_entsoe_all (2).csv")
    print(f"   - Liczba rekordów: {len(df_csv):,}")
    if 'date_parsed' in df_csv.columns:
        print(f"   - Zakres: {df_csv['date_parsed'].min()} - {df_csv['date_parsed'].max()}")
        years = (df_csv['date_parsed'].max() - df_csv['date_parsed'].min()).days / 365.25
        print(f"   - Okres: {years:.1f} lat")
    
    print("\n2. ŹRÓDŁA DANYCH - API:")
    if df_pse is not None and not df_pse.empty:
        print(f"   ✓ PSE: {len(df_pse)} rekordów")
    else:
        print(f"   ✗ PSE: brak danych")
    
    if df_entsoe is not None and not df_entsoe.empty:
        print(f"   ✓ ENTSO-E: {len(df_entsoe)} rekordów")
    else:
        print(f"   ✗ ENTSO-E: brak danych")
    
    print("\n3. KLUCZOWE WNIOSKI:")
    print("   a) Struktura pliku CSV:")
    print("      - Zawiera dane godzinowe z ENTSO-E")
    print("      - Dwie kolumny czasowe: data lokalna i UTC")
    print("      - ~14 różnych źródeł energii")
    
    print("\n   b) Porównanie z danymi API:")
    print("      - Sprawdź sekcje powyżej dla szczegółów")
    print("      - Zwróć uwagę na różnice w wartościach")
    print("      - Sprawdź korelację między źródłami")
    
    print("\n4. REKOMENDACJE:")
    print("   - Zweryfikuj źródło pliku CSV")
    print("   - Sprawdź metodologię zbierania danych")
    print("   - W razie dużych różnic, użyj danych API jako referencji")
    print("   - Dokumentuj wszelkie rozbieżności")


def main():
    """Główna funkcja programu."""
    print("="*80)
    print("🔍 DOGŁĘBNE PORÓWNANIE ŹRÓDEŁ DANYCH - PRODUKCJA ENERGII")
    print("="*80)
    
    # Ścieżka do pliku CSV
    csv_file = "/workspaces/produkcja-energii/electricity_production_entsoe_all (2).csv"
    
    # 1. Wczytaj i przeanalizuj CSV
    df_csv = load_csv_file(csv_file)
    energy_sources = analyze_csv_structure(df_csv)
    analyze_time_consistency(df_csv)
    
    # 2. Określ zakres do pobrania z API
    # Używamy próbkowania dla długich okresów
    if 'date_parsed' in df_csv.columns:
        min_date = df_csv['date_parsed'].min()
        max_date = df_csv['date_parsed'].max()
        
        # Dla bardzo długich okresów (>1 rok), weź tylko ostatni miesiąc
        if (max_date - min_date).days > 365:
            print("\n" + "="*80)
            print("ℹ️  Okres w pliku CSV przekracza 1 rok")
            print("   Do porównania używam ostatniego miesiąca danych")
            print("="*80)
            date_from = (max_date - timedelta(days=30)).strftime('%Y-%m-%d')
            date_to = max_date.strftime('%Y-%m-%d')
        else:
            date_from = min_date.strftime('%Y-%m-%d')
            date_to = max_date.strftime('%Y-%m-%d')
        
        # 3. Pobierz dane z API
        df_pse, df_entsoe = fetch_comparison_data(date_from, date_to)
        
        # 4. Porównaj dane
        compare_with_entsoe(df_csv, df_entsoe)
        compare_with_pse(df_csv, df_pse)
        
        # 5. Generuj raport
        generate_summary_report(df_csv, df_pse, df_entsoe)
    
    print("\n" + "="*80)
    print("✅ RAPORT ZAKOŃCZONY")
    print("="*80)


if __name__ == "__main__":
    main()
