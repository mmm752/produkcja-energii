#!/usr/bin/env python3
"""
Moduł łączący dane z PSE i ENTSO-E w jeden kompleksowy analizator.
"""

import pandas as pd
from typing import Optional
from datetime import datetime
import json

from pse_energy_scraper import PSEEnergyDataFetcher, EnergyDataAnalyzer
from entsoe_data_fetcher import ENTSOEDataFetcher


class CombinedEnergyDataFetcher:
    """Klasa łącząca dane z PSE i ENTSO-E."""
    
    def __init__(self, entsoe_api_key: Optional[str] = None):
        """
        Inicjalizacja fetcher'a łączącego oba źródła danych.
        
        Args:
            entsoe_api_key: Klucz API ENTSO-E (opcjonalny, może być w .env)
        """
        self.pse_fetcher = PSEEnergyDataFetcher()
        
        try:
            self.entsoe_fetcher = ENTSOEDataFetcher(api_key=entsoe_api_key)
            self.entsoe_available = True
        except ValueError as e:
            print(f"⚠️  ENTSO-E nie jest dostępne: {e}")
            self.entsoe_available = False
    
    def fetch_combined_data(self, date_from: str, date_to: str) -> Optional[pd.DataFrame]:
        """
        Pobiera i łączy dane z PSE i ENTSO-E.
        
        Args:
            date_from: Data początkowa w formacie YYYY-MM-DD
            date_to: Data końcowa w formacie YYYY-MM-DD
            
        Returns:
            DataFrame z połączonymi danymi lub None w przypadku błędu
        """
        print("=" * 70)
        print(f"📊 Pobieranie danych dla okresu {date_from} - {date_to}")
        print("=" * 70)
        print()
        
        # Pobierz dane z PSE
        print("🔌 PSE - Dane rynkowe...")
        df_pse = self.pse_fetcher.fetch_data(date_from, date_to)
        
        if df_pse is None or df_pse.empty:
            print("⚠️  Brak danych z PSE")
            return None
        
        # Pobierz dane z ENTSO-E (jeśli dostępne)
        df_entsoe = None
        if self.entsoe_available:
            print()
            print("⚡ ENTSO-E - Dane o produkcji...")
            df_entsoe = self.entsoe_fetcher.fetch_generation_data(date_from, date_to)
        
        # Połącz dane
        if df_entsoe is not None and not df_entsoe.empty:
            print()
            print("🔗 Łączenie danych PSE + ENTSO-E...")
            
            # Upewnij się że oba DataFrame mają kolumnę Data jako index
            if 'Data' not in df_pse.index.names:
                if 'Data' in df_pse.columns:
                    df_pse.set_index('Data', inplace=True)
            
            if 'Data' not in df_entsoe.index.names:
                if 'Data' in df_entsoe.columns:
                    df_entsoe.set_index('Data', inplace=True)
            
            # Usuń informacje o strefie czasowej jeśli istnieją (aby uniknąć konfliktów)
            if df_pse.index.tz is not None:
                df_pse.index = df_pse.index.tz_localize(None)
            if df_entsoe.index.tz is not None:
                df_entsoe.index = df_entsoe.index.tz_localize(None)
            
            # Merge po indeksie czasowym (inner join - tylko wspólne timestampy)
            # To daje 95 pomiarów (00:15-23:45) dla pojedynczego dnia
            df_combined = pd.merge(
                df_pse,
                df_entsoe,
                left_index=True,
                right_index=True,
                how='inner',
                suffixes=('_PSE', '_ENTSOE')
            )
            
            # Nie wypełniaj NaN zerami - zostaw jako NaN aby średnia była poprawna
            df_combined.reset_index(inplace=True)
            
            # Przetwarzanie dat
            df_combined['Data'] = pd.to_datetime(df_combined['Data'])
            
            # Inner join już dał nam tylko wspólne timestampy (00:15-23:45 dla pojedynczego dnia)
            # Nie potrzebujemy dodatkowego filtrowania
            
            print(f"✓ Połączono {len(df_combined)} rekordów")
            
            return df_combined
        else:
            print()
            print("⚠️  Używam tylko danych PSE")
            return df_pse


class CombinedEnergyDataAnalyzer:
    """Klasa do analizy połączonych danych z PSE i ENTSO-E."""
    
    def __init__(self, df: pd.DataFrame):
        """
        Inicjalizacja analizatora.
        
        Args:
            df: DataFrame z połączonymi danymi
        """
        self.df = df.copy()
        self._prepare_data()
    
    def _prepare_data(self):
        """Przygotowuje dane do analizy."""
        # Znajdź kolumnę z datą
        date_columns = [col for col in self.df.columns if 'data' in col.lower() or 'date' in col.lower()]
        
        if date_columns:
            self.df['Data'] = pd.to_datetime(self.df[date_columns[0]])
        elif 'Data' not in self.df.columns:
            print("⚠️  Nie znaleziono kolumny z datą")
            return
        
        self.df.set_index('Data', inplace=True)
        
        # Znajdź dostępne kolumny
        self.available_columns = {
            'wiatr_pse': self._find_column(['sumaryczna generacja źródeł wiatrowych', 'wiatr']),
            'pv_pse': self._find_column(['sumaryczna generacja źródeł fotowoltaicznych', 'fotowoltai']),
            'demand': self._find_column(['zapotrzebowanie']),
            'swm_total': self._find_column(['krajowe saldo wymiany międzysystemowej [mw]']),
            'hard_coal': self._find_column(['węgiel kamienny']),
            'lignite': self._find_column(['węgiel brunatny']),
            'gas': self._find_column(['gaz [mw]']),
            'wind_entsoe': self._find_column(['wiatr lądowy']),
            'solar_entsoe': self._find_column(['słońce [mw]']),
            'hydro': self._find_column(['woda [mw]']),
            'storage': self._find_column(['magazyny energii']),
            'biomass': self._find_column(['biomasa'])
        }
    
    def _find_column(self, keywords: list) -> Optional[str]:
        """Znajduje kolumnę zawierającą którekolwiek ze słów kluczowych."""
        for col in self.df.columns:
            col_lower = col.lower()
            if any(keyword.lower() in col_lower for keyword in keywords):
                return col
        return None
    
    def sum_period(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> dict:
        """
        Sumuje wszystkie dostępne wskaźniki dla podanego okresu.
        
        Args:
            date_from: Data początkowa (opcjonalna)
            date_to: Data końcowa (opcjonalna)
            
        Returns:
            Słownik z sumami dla wszystkich wskaźników
        """
        df_filtered = self.df
        
        if date_from:
            df_filtered = df_filtered[df_filtered.index >= date_from]
        if date_to:
            df_filtered = df_filtered[df_filtered.index <= date_to]
        
        if df_filtered.empty:
            return {'błąd': 'Brak danych dla podanego okresu'}
        
        results = {
            'okres_od': df_filtered.index.min().strftime('%Y-%m-%d %H:%M'),
            'okres_do': df_filtered.index.max().strftime('%Y-%m-%d %H:%M'),
            'liczba_pomiarów': len(df_filtered),
        }
        
        # Dodaj sumy dla wszystkich dostępnych wskaźników
        # Dane są co 15 min, więc mnożymy przez 0.25h aby uzyskać MWh
        for name, col in self.available_columns.items():
            if col and col in df_filtered.columns:
                sum_mw = df_filtered[col].sum()
                mwh = sum_mw * 0.25
                mean_mw = df_filtered[col].mean()
                
                results[f'{name}_suma_MW'] = round(sum_mw, 2)
                results[f'{name}_MWh'] = round(mwh, 2)
                results[f'{name}_średnia_MW'] = round(mean_mw, 2)
        
        return results
    
    def get_time_series(self, resample_freq: str = '1D') -> pd.DataFrame:
        """
        Generuje szereg czasowy z agregacją dla wszystkich wskaźników.
        
        Args:
            resample_freq: Częstotliwość agregacji ('1h', '1D', '1W', '1M')
            
        Returns:
            DataFrame z szeregiem czasowym
        """
        # Pobierz wszystkie dostępne kolumny numeryczne
        cols_to_agg = [col for col in self.available_columns.values() if col and col in self.df.columns]
        
        if not cols_to_agg:
            return pd.DataFrame()
        
        # Suma z przeliczeniem na MWh
        ts = self.df[cols_to_agg].resample(resample_freq).agg(
            lambda x: x.sum() * 0.25
        )
        
        # Dodaj również średnią moc
        ts_mean = self.df[cols_to_agg].resample(resample_freq).mean()
        ts_mean.columns = [f'{col}_średnia' for col in ts_mean.columns]
        
        result = pd.concat([ts, ts_mean], axis=1)
        return result
    
    def monthly_sums(self, year_from: int, year_to: int) -> pd.DataFrame:
        """
        Generuje miesięczne sumy dla wybranych lat.
        
        Args:
            year_from: Rok początkowy
            year_to: Rok końcowy
            
        Returns:
            DataFrame z miesięcznymi sumami
        """
        # Filtruj dane dla wybranych lat
        df_filtered = self.df[
            (self.df.index.year >= year_from) & 
            (self.df.index.year <= year_to)
        ]
        
        # Pobierz wszystkie dostępne kolumny numeryczne
        cols_to_agg = [col for col in self.available_columns.values() if col and col in df_filtered.columns]
        
        if not cols_to_agg:
            return pd.DataFrame()
        
        # Grupuj po miesiącach i sumuj (konwersja MW -> MWh poprzez * 0.25)
        monthly = df_filtered[cols_to_agg].resample('1M').agg(
            lambda x: x.sum() * 0.25
        )
        
        # Formatuj kolumny z jednostkami
        monthly.columns = [f'{col}_suma_MW' for col in monthly.columns]
        
        return monthly
    
    def export_to_csv(self, filename: str):
        """Eksportuje dane do CSV (format europejski)."""
        self.df.to_csv(filename, sep=';', decimal=',', encoding='utf-8-sig')
        print(f"💾 Zapisano: {filename}")
    
    def export_to_json(self, filename: str):
        """Eksportuje dane do JSON."""
        self.df.reset_index().to_json(filename, orient='records', date_format='iso', force_ascii=False, indent=2)
        print(f"💾 Zapisano: {filename}")


def main():
    """Funkcja testowa."""
    print("=" * 70)
    print("Combined Energy Data Fetcher - Test")
    print("=" * 70)
    print()
    
    fetcher = CombinedEnergyDataFetcher()
    df = fetcher.fetch_combined_data('2025-01-15', '2025-01-15')
    
    if df is not None:
        print()
        print("📊 Dostępne kolumny:")
        print("-" * 70)
        for col in df.columns:
            print(f"  - {col}")
        
        print()
        print("📊 Przykładowe dane (pierwsze 5 rekordów):")
        print("-" * 70)
        print(df.head(5).to_string())
        
        # Analiza
        analyzer = CombinedEnergyDataAnalyzer(df)
        results = analyzer.sum_period()
        
        print()
        print("📈 Podsumowanie:")
        print("-" * 70)
        for key, value in results.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
