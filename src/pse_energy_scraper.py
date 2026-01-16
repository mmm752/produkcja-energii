#!/usr/bin/env python3
"""
Skrypt do pobierania i analizowania danych o produkcji energii wiatrowej i fotowoltaicznej z PSE.
Dane źródłowe: https://raporty.pse.pl/report/his-wlk-cal
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import Optional, Tuple
import sys


class PSEEnergyDataFetcher:
    """Klasa do pobierania danych o produkcji energii z PSE."""
    
    BASE_URL = "https://api.raporty.pse.pl/api"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        })
    
    def fetch_data(self, date_from: str, date_to: str) -> Optional[pd.DataFrame]:
        """
        Pobiera dane z PSE dla podanego zakresu dat.
        
        Args:
            date_from: Data początkowa w formacie YYYY-MM-DD
            date_to: Data końcowa w formacie YYYY-MM-DD
            
        Returns:
            DataFrame z danymi lub None w przypadku błędu
        """
        try:
            # Oblicz liczbę dni
            from datetime import datetime, timedelta
            start_date = datetime.strptime(date_from, '%Y-%m-%d')
            end_date = datetime.strptime(date_to, '%Y-%m-%d')
            days_diff = (end_date - start_date).days + 1
            
            # Dla długich okresów, pobieraj dane dzień po dniu
            if days_diff > 7:
                print(f"📥 Pobieranie danych dla {days_diff} dni...")
                all_dfs = []
                
                current_date = start_date
                while current_date <= end_date:
                    date_str = current_date.strftime('%Y-%m-%d')
                    df_day = self._fetch_single_day(date_str)
                    
                    if df_day is not None and not df_day.empty:
                        all_dfs.append(df_day)
                    
                    current_date += timedelta(days=1)
                    
                    # Progress indicator
                    if len(all_dfs) % 10 == 0:
                        print(f"  ✓ Pobrano {len(all_dfs)} dni...")
                
                if all_dfs:
                    return pd.concat(all_dfs, ignore_index=True)
                else:
                    return None
            else:
                # Dla krótkich okresów, jeden request
                return self._fetch_date_range(date_from, date_to)
            
        except Exception as e:
            print(f"❌ Błąd podczas pobierania danych: {e}")
            return None
    
    def _fetch_single_day(self, date: str) -> Optional[pd.DataFrame]:
        """Pobiera dane dla pojedynczego dnia."""
        endpoint = f"{self.BASE_URL}/his-wlk-cal"
        odata_filter = f"business_date eq '{date}'"
        
        params = {'$filter': odata_filter}
        
        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data and 'value' in data and len(data['value']) > 0:
                    return self._parse_data(data)
        except Exception:
            pass
        
        return None
    
    def _fetch_date_range(self, date_from: str, date_to: str) -> Optional[pd.DataFrame]:
        """Pobiera dane dla zakresu dat (krótkiego okresu)."""
        endpoint = f"{self.BASE_URL}/his-wlk-cal"
        odata_filter = f"business_date ge '{date_from}' and business_date le '{date_to}'"
        
        params = {'$filter': odata_filter}
        
        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data and 'value' in data and len(data['value']) > 0:
                    return self._parse_data(data)
                else:
                    print(f"⚠️  Brak danych dla okresu {date_from} - {date_to}")
                    return None
            else:
                print(f"⚠️  Błąd API: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Błąd: {e}")
            return None
    
    def _parse_data(self, data: dict) -> pd.DataFrame:
        """Parsuje dane JSON z API do DataFrame."""
        if isinstance(data, dict) and 'value' in data:
            df = pd.DataFrame(data['value'])
            
            # Mapowanie kolumn PSE na czytelne nazwy
            df.rename(columns={
                'dtime': 'Data',
                'wi': 'Sumaryczna generacja źródeł wiatrowych [MW]',
                'pv': 'Sumaryczna generacja źródeł fotowoltaicznych [MW]'
            }, inplace=True)
            
            # Konwersja daty na datetime
            if 'Data' in df.columns:
                df['Data'] = pd.to_datetime(df['Data'])
            
            return df
        
        return pd.DataFrame()
    
    def generate_sample_data(self, date_from: str, date_to: str) -> pd.DataFrame:
        """
        Generuje przykładowe dane dla testów (gdy API nie zwraca danych).
        UWAGA: To są dane syntetyczne, nie rzeczywiste dane PSE!
        """
        print("⚠️  UWAGA: Generuję przykładowe dane do testów (brak danych z API)")
        print("   Dane są syntetyczne i służą wyłącznie do demonstracji")
        
        date_range = pd.date_range(start=date_from, end=date_to, freq='15min')
        
        import numpy as np
        # Generowanie realistycznych danych z cyklem dobowym
        hours = date_range.hour + date_range.minute / 60
        
        # Wiatr - większa produkcja w nocy i rano
        wind_base = 2000 + 1000 * np.sin((hours - 6) * np.pi / 12)
        wind_noise = np.random.normal(0, 300, len(date_range))
        wind_power = np.maximum(0, wind_base + wind_noise)
        
        # Fotowoltaika - produkcja tylko w dzień
        solar_base = np.maximum(0, 1500 * np.sin((hours - 6) * np.pi / 12))
        solar_noise = np.random.normal(0, 200, len(date_range))
        solar_power = np.maximum(0, solar_base + solar_noise)
        
        df = pd.DataFrame({
            'Data': date_range,
            'Sumaryczna generacja źródeł wiatrowych [MW]': wind_power,
            'Sumaryczna generacja źródeł fotowoltaicznych [MW]': solar_power
        })
        
        return df


class EnergyDataAnalyzer:
    """Klasa do analizy danych o produkcji energii."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._prepare_data()
    
    def _prepare_data(self):
        """Przygotowuje dane do analizy."""
        # Znajdź kolumnę z datą
        date_columns = [col for col in self.df.columns if 'data' in col.lower() or 'date' in col.lower() or 'czas' in col.lower()]
        
        if date_columns:
            self.df['Data'] = pd.to_datetime(self.df[date_columns[0]])
        elif 'Data' not in self.df.columns:
            print("⚠️  Nie znaleziono kolumny z datą")
            return
        
        self.df.set_index('Data', inplace=True)
        
        # Znajdź kolumny z danymi o wietrze i PV
        self.wind_col = self._find_column(['wiatr', 'wind'])
        self.solar_col = self._find_column(['fotowoltai', 'solar', 'pv', 'słoneczn'])
        
        if not self.wind_col:
            print("⚠️  Nie znaleziono kolumny z danymi o energii wiatrowej")
        if not self.solar_col:
            print("⚠️  Nie znaleziono kolumny z danymi o energii fotowoltaicznej")
    
    def _find_column(self, keywords: list) -> Optional[str]:
        """Znajduje kolumnę zawierającą którekolwiek ze słów kluczowych."""
        for col in self.df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in keywords):
                return col
        return None
    
    def sum_period(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> dict:
        """
        Sumuje produkcję dla podanego okresu.
        
        Args:
            date_from: Data początkowa (opcjonalna)
            date_to: Data końcowa (opcjonalna)
            
        Returns:
            Słownik z sumami dla wiatru i PV w MWh
        """
        df_filtered = self.df
        
        if date_from:
            df_filtered = df_filtered[df_filtered.index >= date_from]
        if date_to:
            df_filtered = df_filtered[df_filtered.index <= date_to]
        
        # Sprawdź czy są dane
        if df_filtered.empty:
            return {
                'błąd': 'Brak danych dla podanego okresu',
                'wiatr_MWh': 0,
                'wiatr_średnia_MW': 0,
                'fotowoltaika_MWh': 0,
                'fotowoltaika_średnia_MW': 0
            }
        
        # Dane co 15 minut, więc mnożymy przez 0.25h aby uzyskać MWh
        results = {
            'okres_od': df_filtered.index.min().strftime('%Y-%m-%d %H:%M'),
            'okres_do': df_filtered.index.max().strftime('%Y-%m-%d %H:%M'),
            'liczba_pomiarów': len(df_filtered),
        }
        
        if self.wind_col:
            wind_sum_mw = df_filtered[self.wind_col].sum()
            wind_mwh = wind_sum_mw * 0.25  # Suma MW * 0.25h = MWh (dane co 15 min)
            wind_mean_mw = df_filtered[self.wind_col].mean()
            
            results['wiatr_suma_MW'] = round(wind_sum_mw, 2)
            results['wiatr_MWh'] = round(wind_mwh, 2)
            results['wiatr_średnia_MW'] = round(wind_mean_mw, 2)
        
        if self.solar_col:
            solar_sum_mw = df_filtered[self.solar_col].sum()
            solar_mwh = solar_sum_mw * 0.25
            solar_mean_mw = df_filtered[self.solar_col].mean()
            
            results['fotowoltaika_suma_MW'] = round(solar_sum_mw, 2)
            results['fotowoltaika_MWh'] = round(solar_mwh, 2)
            results['fotowoltaika_średnia_MW'] = round(solar_mean_mw, 2)
        
        return results
    
    def monthly_sums(self, year_from: int = 2020, year_to: Optional[int] = None) -> pd.DataFrame:
        """
        Generuje miesięczne sumy produkcji.
        
        Args:
            year_from: Rok początkowy
            year_to: Rok końcowy (domyślnie bieżący)
            
        Returns:
            DataFrame z miesięcznymi sumami
        """
        if year_to is None:
            year_to = datetime.now().year
        
        df_filtered = self.df[
            (self.df.index.year >= year_from) & 
            (self.df.index.year <= year_to)
        ]
        
        # Sumy MW (bez przeliczania na MWh)
        monthly = df_filtered.resample('M').agg({
            col: 'sum' for col in [self.wind_col, self.solar_col] if col
        })
        
        monthly.index = monthly.index.to_period('M')
        monthly.columns = [f'{col}_suma_MW' for col in monthly.columns]
        
        return monthly
    
    def get_time_series(self, resample_freq: str = '1D') -> pd.DataFrame:
        """
        Generuje szereg czasowy z agregacją.
        
        Args:
            resample_freq: Częstotliwość agregacji ('1H', '1D', '1W', '1M')
            
        Returns:
            DataFrame z szeregiem czasowym
        """
        cols_to_agg = [col for col in [self.wind_col, self.solar_col] if col]
        
        if resample_freq in ['1H', 'H', '1D', 'D']:
            # Dla godzin i dni - suma z przeliczeniem na MWh
            ts = self.df[cols_to_agg].resample(resample_freq).agg(
                lambda x: x.sum() * 0.25
            )
        else:
            # Dla dłuższych okresów
            ts = self.df[cols_to_agg].resample(resample_freq).agg(
                lambda x: x.sum() * 0.25
            )
        
        # Dodaj również średnią moc
        ts_mean = self.df[cols_to_agg].resample(resample_freq).mean()
        ts_mean.columns = [f'{col}_średnia' for col in ts_mean.columns]
        
        result = pd.concat([ts, ts_mean], axis=1)
        return result


def main():
    """Główna funkcja programu."""
    
    print("=" * 70)
    print("PSE - Pobieranie danych o produkcji energii wiatrowej i fotowoltaicznej")
    print("=" * 70)
    print()
    
    # Przykład użycia
    fetcher = PSEEnergyDataFetcher()
    
    # Pobierz dane dla stycznia 2026
    print("📥 Pobieranie danych...")
    date_from = "2026-01-01"
    date_to = "2026-01-16"
    
    df = fetcher.fetch_data(date_from, date_to)
    
    # Jeśli nie udało się pobrać prawdziwych danych, użyj przykładowych
    if df is None or df.empty:
        df = fetcher.generate_sample_data(date_from, date_to)
    
    print(f"✓ Pobrano {len(df)} rekordów")
    print()
    
    # Analiza danych
    analyzer = EnergyDataAnalyzer(df)
    
    # 1. Suma dla całego okresu
    print("📊 SUMA DLA OKRESU 1.01.2026 - 16.01.2026")
    print("-" * 70)
    period_sum = analyzer.sum_period()
    for key, value in period_sum.items():
        print(f"  {key}: {value}")
    print()
    
    # 2. Miesięczne sumy (dla przykładowych danych)
    print("📊 MIESIĘCZNE SUMY")
    print("-" * 70)
    monthly = analyzer.monthly_sums(2026, 2026)
    print(monthly.to_string())
    print()
    
    # 3. Szereg czasowy - agregacja dzienna
    print("📊 SZEREG CZASOWY - AGREGACJA DZIENNA")
    print("-" * 70)
    daily_ts = analyzer.get_time_series('1D')
    print(daily_ts.head(10).to_string())
    print()
    
    # Zapis do plików
    print("💾 Zapisywanie wyników...")
    
    # CSV z surowymi danymi (format europejski: separator ; i dziesiętny ,)
    df.to_csv('dane_surowe.csv', index=True, sep=';', decimal=',', encoding='utf-8-sig')
    print("  ✓ dane_surowe.csv")
    
    # CSV z miesięcznymi sumami
    monthly.to_csv('sumy_miesieczne.csv', index=True, sep=';', decimal=',', encoding='utf-8-sig')
    print("  ✓ sumy_miesieczne.csv")
    
    # CSV z szeregiem czasowym
    daily_ts.to_csv('szereg_czasowy_dzienny.csv', index=True, sep=';', decimal=',', encoding='utf-8-sig')
    print("  ✓ szereg_czasowy_dzienny.csv")
    
    # JSON z podsumowaniem
    with open('podsumowanie.json', 'w', encoding='utf-8') as f:
        json.dump(period_sum, f, indent=2, ensure_ascii=False)
    print("  ✓ podsumowanie.json")
    
    print()
    print("=" * 70)
    print("✓ Gotowe!")
    print("=" * 70)


if __name__ == "__main__":
    main()
