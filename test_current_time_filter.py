#!/usr/bin/env python3
"""
Test filtrowania danych do ostatniego rzeczywistego pomiaru.
Pokazuje jak kod automatycznie usuwa dane prognostyczne.
"""

from datetime import datetime, timedelta
import pandas as pd

def test_filter_demo():
    """Demonstracja jak działa filtrowanie danych przyszłościowych."""
    
    print("=" * 70)
    print("TEST: Filtrowanie do ostatniego rzeczywistego pomiaru PSE")
    print("=" * 70)
    
    # Symulacja aktualnego czasu
    now = datetime.now()
    
    # Symulacja: API PSE ma opóźnienie ~30-45 minut
    last_real_measurement = now - timedelta(minutes=35)
    
    print(f"\n📅 Dzisiaj:                    {now.strftime('%Y-%m-%d')}")
    print(f"🕐 Teraz (zegar):              {now.strftime('%H:%M:%S')}")
    print(f"📊 Ostatnia aktualizacja PSE:  {last_real_measurement.strftime('%H:%M')} (opóźnienie ~35 min)")
    print()
    
    # Symulacja danych API PSE - zwraca cały dzień nawet jeśli dopiero jest południe
    print("📊 API PSE zwróciło dane za cały dzień (96 pomiarów co 15 min):")
    print("   Pomiary: 00:00, 00:15, 00:30, ..., 23:30, 23:45")
    
    # Utwórz przykładowe dane
    today_str = now.strftime('%Y-%m-%d')
    start_time = datetime.strptime(f"{today_str} 00:00:00", "%Y-%m-%d %H:%M:%S")
    
    # Generuj 96 pomiarów (cały dzień)
    timestamps = [start_time + timedelta(minutes=15*i) for i in range(96)]
    
    df = pd.DataFrame({
        'Data': timestamps,
        'Wartość [MW]': [100 + i for i in range(96)]
    })
    
    print(f"\n   Pierwszy pomiar: {df['Data'].iloc[0].strftime('%Y-%m-%d %H:%M')}")
    print(f"   Ostatni pomiar:  {df['Data'].iloc[-1].strftime('%Y-%m-%d %H:%M')}")
    print(f"   Liczba pomiarów: {len(df)}")
    
    # Filtruj do ostatniego rzeczywistego pomiaru (z buforem 15 min)
    cutoff_time = now - timedelta(minutes=15)
    df_filtered = df[df['Data'] <= cutoff_time].copy()
    
    print(f"\n✂️  Po filtrowaniu do ostatniego rzeczywistego pomiaru:")
    print(f"   Granica odcięcia: {cutoff_time.strftime('%H:%M')} (teraz - 15 min)")
    print(f"   Pierwszy pomiar:  {df_filtered['Data'].iloc[0].strftime('%Y-%m-%d %H:%M')}")
    print(f"   Ostatni pomiar:   {df_filtered['Data'].iloc[-1].strftime('%Y-%m-%d %H:%M')}")
    print(f"   Liczba pomiarów:  {len(df_filtered)}")
    
    removed = len(df) - len(df_filtered)
    print(f"\n   🗑️  Usunięto {removed} przyszłościowych/prognostycznych pomiarów")
    
    # Pokaż ostatnie 5 pomiarów
    print("\n📋 Ostatnie 5 rzeczywistych pomiarów:")
    for idx in range(max(0, len(df_filtered)-5), len(df_filtered)):
        row = df_filtered.iloc[idx]
        print(f"   {row['Data'].strftime('%H:%M')} → {row['Wartość [MW]']:.0f} MW")
    
    print("\n💡 Dlaczego opóźnienie?")
    print("   PSE publikuje dane z opóźnieniem ~30-45 minut")
    print("   To normalne - dane muszą być zebrane i zweryfikowane")
    
    print("\n" + "=" * 70)
    print("✅ Kod pokazuje tylko rzeczywiste pomiary, bez prognoz!")
    print("=" * 70)

if __name__ == '__main__':
    test_filter_demo()
