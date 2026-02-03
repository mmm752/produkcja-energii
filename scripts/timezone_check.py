#!/usr/bin/env python3
"""
Skrypt do weryfikacji synchronizacji czasowej między danymi PSE i ENTSO-E.
Porównuje szczyt produkcji fotowoltaicznej (PV) z obu źródeł.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pandas as pd
from datetime import datetime, timedelta
from pse_energy_scraper import PSEEnergyDataFetcher
from entsoe_data_fetcher import ENTSOEDataFetcher


def analyze_timezone_sync():
    """Analizuje synchronizację czasową PSE vs ENTSO-E."""
    
    print("=" * 80)
    print("🕐 ANALIZA SYNCHRONIZACJI CZASOWEJ: PSE vs ENTSO-E")
    print("=" * 80)
    print()
    
    # Wybierz ostatni pełny słoneczny dzień (3 dni wstecz dla pewności)
    target_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
    
    print(f"📅 Analizowany dzień: {target_date}")
    print()
    
    # 1. Pobierz dane z PSE
    print("=" * 80)
    print("1️⃣  DANE PSE (Polskie Sieci Elektroenergetyczne)")
    print("=" * 80)
    
    pse_fetcher = PSEEnergyDataFetcher()
    df_pse = pse_fetcher.fetch_data(target_date, target_date)
    
    if df_pse is None or df_pse.empty:
        print("❌ Brak danych PSE - sprawdź połączenie lub wybierz inny dzień")
        return
    
    print(f"✓ Pobrano {len(df_pse)} rekordów z PSE")
    print()
    
    # Znajdź szczyt produkcji PV w PSE
    pv_col_pse = 'Sumaryczna generacja źródeł fotowoltaicznych [MW]'
    
    if pv_col_pse in df_pse.columns and 'Data' in df_pse.columns:
        df_pse['Data_parsed'] = pd.to_datetime(df_pse['Data'])
        pse_max_idx = df_pse[pv_col_pse].idxmax()
        pse_max_value = df_pse.loc[pse_max_idx, pv_col_pse]
        pse_max_time = df_pse.loc[pse_max_idx, 'Data_parsed']
        
        print(f"📊 PSE - Szczyt produkcji PV:")
        print(f"   • Wartość: {pse_max_value:.2f} MW")
        print(f"   • Czas:    {pse_max_time}")
        print(f"   • Format:  {pse_max_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Pokaż kontekst czasowy
        print(f"📌 PSE - Zakres czasowy danych:")
        print(f"   • Pierwszy rekord: {df_pse['Data_parsed'].min()}")
        print(f"   • Ostatni rekord:  {df_pse['Data_parsed'].max()}")
        print(f"   • Liczba próbek:   {len(df_pse)}")
        print()
    else:
        print("⚠️  Brak kolumny PV lub Data w danych PSE")
        print(f"Dostępne kolumny: {df_pse.columns.tolist()}")
        return
    
    # 2. Pobierz dane z ENTSO-E
    print("=" * 80)
    print("2️⃣  DANE ENTSO-E (Transparency Platform)")
    print("=" * 80)
    
    try:
        entsoe_fetcher = ENTSOEDataFetcher()
        df_entsoe = entsoe_fetcher.fetch_generation_data(target_date, target_date)
        
        if df_entsoe is None or df_entsoe.empty:
            print("❌ Brak danych ENTSO-E - sprawdź klucz API lub dostępność danych")
            return
        
        print(f"✓ Pobrano {len(df_entsoe)} rekordów z ENTSO-E")
        print()
        
        # Znajdź szczyt produkcji PV w ENTSO-E
        pv_col_entsoe = 'Słońce [MW]'
        
        if pv_col_entsoe in df_entsoe.columns and 'Data' in df_entsoe.columns:
            df_entsoe['Data_parsed'] = pd.to_datetime(df_entsoe['Data'])
            entsoe_max_idx = df_entsoe[pv_col_entsoe].idxmax()
            entsoe_max_value = df_entsoe.loc[entsoe_max_idx, pv_col_entsoe]
            entsoe_max_time = df_entsoe.loc[entsoe_max_idx, 'Data_parsed']
            
            print(f"📊 ENTSO-E - Szczyt produkcji PV:")
            print(f"   • Wartość: {entsoe_max_value:.2f} MW")
            print(f"   • Czas:    {entsoe_max_time}")
            print(f"   • Format:  {entsoe_max_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Sprawdź czy ma timezone info
            if entsoe_max_time.tzinfo is not None:
                print(f"   • Strefa:  {entsoe_max_time.tzinfo}")
            else:
                print(f"   • Strefa:  (brak info - prawdopodobnie lokalny czas)")
            print()
            
            # Pokaż kontekst czasowy
            print(f"📌 ENTSO-E - Zakres czasowy danych:")
            print(f"   • Pierwszy rekord: {df_entsoe['Data_parsed'].min()}")
            print(f"   • Ostatni rekord:  {df_entsoe['Data_parsed'].max()}")
            print(f"   • Liczba próbek:   {len(df_entsoe)}")
            print()
            
        else:
            print("⚠️  Brak kolumny PV lub Data w danych ENTSO-E")
            print(f"Dostępne kolumny: {df_entsoe.columns.tolist()}")
            return
            
    except ValueError as e:
        print(f"❌ Błąd inicjalizacji ENTSO-E: {e}")
        print()
        print("💡 Aby korzystać z ENTSO-E:")
        print("   1. Zarejestruj się na https://transparency.entsoe.eu/")
        print("   2. Wygeneruj klucz API")
        print("   3. Dodaj do pliku .env: ENTSOE_API_KEY=twoj_klucz")
        return
    except Exception as e:
        print(f"❌ Błąd pobierania danych ENTSO-E: {e}")
        return
    
    # 3. Porównanie
    print("=" * 80)
    print("3️⃣  PORÓWNANIE I WERDYKT")
    print("=" * 80)
    print()
    
    # Różnica wartości
    value_diff = abs(pse_max_value - entsoe_max_value)
    value_diff_pct = (value_diff / pse_max_value) * 100 if pse_max_value > 0 else 0
    
    print(f"🔍 Porównanie wartości szczytowej:")
    print(f"   • PSE:     {pse_max_value:.2f} MW")
    print(f"   • ENTSO-E: {entsoe_max_value:.2f} MW")
    print(f"   • Różnica: {value_diff:.2f} MW ({value_diff_pct:.2f}%)")
    
    if value_diff_pct < 5:
        print(f"   ✓ Wartości są bardzo zbliżone - to ten sam dataset!")
    elif value_diff_pct < 10:
        print(f"   ⚠️  Wartości różnią się nieznacznie")
    else:
        print(f"   ❌ Wartości znacząco się różnią - może to być inny typ pomiaru")
    print()
    
    # Różnica czasu
    # Usuń timezone info jeśli istnieje dla porównania
    pse_time_naive = pse_max_time.replace(tzinfo=None) if pse_max_time.tzinfo else pse_max_time
    entsoe_time_naive = entsoe_max_time.replace(tzinfo=None) if entsoe_max_time.tzinfo else entsoe_max_time
    
    time_diff = (entsoe_time_naive - pse_time_naive).total_seconds() / 3600  # różnica w godzinach
    
    print(f"🕐 Porównanie czasu wystąpienia szczytu:")
    print(f"   • PSE:     {pse_time_naive.strftime('%H:%M')}")
    print(f"   • ENTSO-E: {entsoe_time_naive.strftime('%H:%M')}")
    print(f"   • Różnica: {time_diff:+.2f} godz ({abs(time_diff) * 60:.0f} min)")
    print()
    
    # Werdykt
    print("=" * 80)
    print("📋 WERDYKT KOŃCOWY")
    print("=" * 80)
    print()
    
    if abs(time_diff) < 0.5:  # Mniej niż 30 minut różnicy
        print("✅ DANE SĄ ZSYNCHRONIZOWANE CZASOWO")
        print()
        print("🎯 Wnioski:")
        print("   • PSE i ENTSO-E pokazują ten sam czas (lokalny polski)")
        print("   • Szczyt PV występuje o tej samej godzinie w obu źródłach")
        print("   • Nie jest wymagana korekta strefy czasowej")
        print("   • Oba serwisy używają czasu Europe/Warsaw (CET/CEST)")
        print()
        print("📌 Dla użytkownika:")
        print("   → Patrząc na dane z ENTSO-E widzisz TEN SAM CZAS co w Polsce")
        print("   → NIE musisz uwzględniać poprawki na strefę czasową")
        
    elif abs(time_diff) >= 0.9 and abs(time_diff) <= 1.1:  # Około 1 godziny
        print("⚠️  WYKRYTO PRZESUNIĘCIE CZASOWE: ~1 GODZINA")
        print()
        print("🎯 Wnioski:")
        print("   • ENTSO-E pokazuje czas UTC (bez korekty)")
        print("   • PSE używa czasu lokalnego Europe/Warsaw (CET = UTC+1)")
        print(f"   • ENTSO-E szczyt: {entsoe_time_naive.strftime('%H:%M')} UTC")
        print(f"   • PSE szczyt:     {pse_time_naive.strftime('%H:%M')} CET")
        print()
        print("📌 Dla użytkownika:")
        print("   → Dane z ENTSO-E są w UTC - musisz dodać +1h (zima) lub +2h (lato)")
        print("   → Aby zobaczyć polski czas, zastosuj konwersję UTC → Europe/Warsaw")
        
    elif abs(time_diff) >= 1.9 and abs(time_diff) <= 2.1:  # Około 2 godziny
        print("⚠️  WYKRYTO PRZESUNIĘCIE CZASOWE: ~2 GODZINY")
        print()
        print("🎯 Wnioski:")
        print("   • ENTSO-E pokazuje czas UTC (bez korekty)")
        print("   • PSE używa czasu lokalnego Europe/Warsaw (CEST = UTC+2, czas letni)")
        print(f"   • ENTSO-E szczyt: {entsoe_time_naive.strftime('%H:%M')} UTC")
        print(f"   • PSE szczyt:     {pse_time_naive.strftime('%H:%M')} CEST")
        print()
        print("📌 Dla użytkownika:")
        print("   → Dane z ENTSO-E są w UTC - musisz dodać +2h (czas letni)")
        print("   → Aby zobaczyć polski czas, zastosuj konwersję UTC → Europe/Warsaw")
        
    else:
        print(f"❓ WYKRYTO NIESTANDARDOWĄ RÓŻNICĘ: {time_diff:+.2f} godz")
        print()
        print("🎯 Możliwe przyczyny:")
        print("   • Różna rozdzielczość czasowa pomiarów")
        print("   • Artefakt związany z interpolacją danych")
        print("   • Szczyt może być 'rozmazany' w jednym ze źródeł")
        print()
        print(f"📊 Sprawdź ręcznie dane wokół godziny {pse_time_naive.strftime('%H:%M')}")
    
    print()
    print("=" * 80)
    
    # Dodatkowa analiza - pokaż kilka rekordów wokół szczytu
    print()
    print("📈 SZCZEGÓŁY - Rekordy wokół szczytu PSE:")
    print("-" * 80)
    
    pse_context = df_pse.iloc[max(0, pse_max_idx-3):min(len(df_pse), pse_max_idx+4)]
    print(pse_context[['Data', pv_col_pse]].to_string(index=False))
    
    print()
    print("📈 SZCZEGÓŁY - Rekordy wokół szczytu ENTSO-E:")
    print("-" * 80)
    
    entsoe_context = df_entsoe.iloc[max(0, entsoe_max_idx-3):min(len(df_entsoe), entsoe_max_idx+4)]
    print(entsoe_context[['Data', pv_col_entsoe]].to_string(index=False))
    
    print()


if __name__ == "__main__":
    try:
        analyze_timezone_sync()
    except KeyboardInterrupt:
        print("\n\n⚠️  Przerwano przez użytkownika")
    except Exception as e:
        print(f"\n❌ Błąd: {e}")
        import traceback
        traceback.print_exc()
