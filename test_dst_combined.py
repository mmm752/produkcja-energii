#!/usr/bin/env python3
"""Test pobierania i łączenia danych dla okresu z DST."""

import sys
sys.path.insert(0, '/workspaces/produkcja-energii/src')

from pse_energy_scraper import PSEEnergyDataFetcher
from entsoe_data_fetcher import ENTSOEDataFetcher
from combined_energy_data import CombinedEnergyDataFetcher
import pandas as pd

print("=" * 80)
print("TEST POBIERANIA DANYCH DLA OKRESU Z DST (2025-10-25 do 2025-10-27)")
print("=" * 80)

# Test 1: PSE pojedyncze dni
print("\n1️⃣  Test PSE - pobieranie dzień po dniu:")
print("-" * 80)
pse = PSEEnergyDataFetcher()
for date in ['2025-10-25', '2025-10-26', '2025-10-27']:
    df = pse.fetch_data(date, date)
    print(f"   {date}: {len(df)} rekordów")

# Test 2: PSE zakres 3-dniowy
print("\n2️⃣  Test PSE - zakres 3-dniowy:")
print("-" * 80)
df_pse_range = pse.fetch_data('2025-10-25', '2025-10-27')
print(f"   2025-10-25 → 2025-10-27: {len(df_pse_range)} rekordów")
print(f"   Oczekiwano: ~288 rekordów (96+96+96)")

# Test 3: ENTSO-E
print("\n3️⃣  Test ENTSO-E - zakres 3-dniowy:")
print("-" * 80)
entsoe = ENTSOEDataFetcher()
df_entsoe = entsoe.fetch_generation_data('2025-10-25', '2025-10-27')
if df_entsoe is not None:
    print(f"   2025-10-25 → 2025-10-27: {len(df_entsoe)} rekordów")
else:
    print("   ❌ Brak danych z ENTSO-E")

# Test 4: Combined
print("\n4️⃣  Test Combined - łączenie PSE + ENTSO-E:")
print("-" * 80)
combined = CombinedEnergyDataFetcher()
df_combined = combined.fetch_combined_data('2025-10-25', '2025-10-27')

if df_combined is not None:
    print(f"\n✓ Wynik: {len(df_combined)} rekordów")
    print(f"\nKolumny z ENTSO-E (przykłady):")
    entsoe_cols = [col for col in df_combined.columns if any(x in col for x in ['Węgiel', 'Gaz', 'Woda', 'Biomasa'])]
    for col in entsoe_cols[:5]:
        print(f"  - {col}")
else:
    print("❌ Brak połączonych danych")
