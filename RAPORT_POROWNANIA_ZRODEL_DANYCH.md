# 📊 RAPORT PORÓWNAWCZY ŹRÓDEŁ DANYCH - PRODUKCJA ENERGII W POLSCE

**Data raportu:** 26 stycznia 2026  
**Analizowane źródła:**
- Plik CSV: `electricity_production_entsoe_all (2).csv`
- API ENTSO-E (pobierane na żywo przez system)
- API PSE (pobierane na żywo przez system)

---

## 1. ANALIZA PLIKU CSV

### 1.1. Podstawowe informacje
- **Liczba rekordów:** 139,673
- **Liczba kolumn:** 17
- **Rozmiar w pamięci:** 33.30 MB
- **Zakres czasowy:** 2 stycznia 2015 - 26 stycznia 2026 (11.1 lat)
- **Częstotliwość danych:** 15-minutowa (nie godzinowa jak początkowo sądzono!)

### 1.2. Struktura danych

#### Kolumny czasowe:
- `date` - data lokalna (Europe/Warsaw) w formacie DD.MM.YYYY HH:MM
- `date_utc` - data UTC w formacie DD.MM.YYYY HH:MM

#### Źródła energii (14 typów):
1. `hard_coal` - Węgiel kamienny
2. `coal-derived` - Produkty węglowe
3. `lignite` - Węgiel brunatny
4. `gas` - Gaz
5. `oil` - Ropa/olej
6. `biomass` - Biomasa
7. `wind_onshore` - Wiatr lądowy
8. `solar` - Fotowoltaika
9. `hydro_pumped_storage` - Magazyny pompowe
10. `hydro_run-of-river_and_poundage` - Woda przepływowa
11. `hydro_water_reservoir` - Woda zbiornikowa
12. `other` - Inne
13. `other_renewable` - Inne odnawialne

### 1.3. Brakujące wartości
- **other_renewable:** 59.3% brakujących danych
- **other:** 59.3% brakujących danych
- **solar:** 33.1% brakujących danych (brak danych przed ~2019 rokiem)
- **oil:** 3.2% brakujących danych

### 1.4. Statystyki produkcji (średnia za 11 lat)

| Źródło | Średnia [MW] | Min [MW] | Max [MW] | Suma [MWh] |
|--------|-------------|----------|----------|------------|
| Węgiel kamienny | 7,568.70 | 2,744.82 | 15,381.00 | 1,057,142,458 |
| Węgiel brunatny | 4,269.66 | 902.87 | 7,878.00 | 596,356,026 |
| Gaz | 1,575.72 | 61.00 | 4,585.03 | 220,085,767 |
| Wiatr | 2,090.95 | 8.00 | 9,835.79 | 292,049,193 |
| Fotowoltaika | 1,660.23 | 0.00 | 13,729.94 | 155,197,003 |
| Biomasa | 258.56 | 0.00 | 454.64 | 36,114,011 |

### 1.5. Ciągłość czasowa

#### Duplikaty:
✅ **Brak duplikatów** - każdy timestamp jest unikalny

#### Luki czasowe:
⚠️ **Wykryto 56,890 luk w danych**

Większość luk to:
- **Zmiany czasu DST (Daylight Saving Time)** - 10 przypadków (2015-2024)
  - Każdego roku w ostatnią niedzielę marca brakuje godziny 2:00-3:00
  - Przykład: `2015-03-29 03:00:00: luka 2 godziny`
  
- **Inne luki** - wymagają dalszej analizy

⚠️ **Uwaga:** Pozostałe ~56,880 luk sugeruje, że dane mogły być uzupełniane różnymi metodami lub pochodzą z wielu źródeł.

---

## 2. PORÓWNANIE Z DANYMI API ENTSO-E

### 2.1. Zakres porównania
- **Okres testowy:** 27 grudnia 2025 - 26 stycznia 2026 (31 dni)
- **Wspólnych pomiarów:** 2,941 (godzinowych)
- **Metoda:** Agregacja danych 15-minutowych do godzinowych (średnia z 4 pomiarów)

### 2.2. Wyniki porównania źródeł energii

#### ✅ ŹRÓDŁA ZGODNE (różnice < 10 MW, korelacja > 0.99)

| Źródło | Średnia różnica | Max różnica | Korelacja |
|--------|-----------------|-------------|-----------|
| **Węgiel kamienny** | -0.03 MW | 834.01 MW | 0.9972 |
| **Węgiel brunatny** | -0.01 MW | 575.55 MW | 0.9970 |
| **Biomasa** | 0.00 MW | 75.67 MW | 0.9983 |
| **Wiatr lądowy** | 0.01 MW | 1,294.80 MW | 0.9991 |
| **Fotowoltaika** | 0.10 MW | 1,155.54 MW | 0.9923 |

**Interpretacja:** Te źródła wykazują bardzo wysoką zgodność. Maksymalne różnice występują w okresach przejściowych (np. zmiany mocy w ciągu godziny), co jest normalne przy agregacji danych 15-minutowych do godzinowych.

#### ⚠️ ŹRÓDŁA Z RÓŻNICAMI

##### 1. **Gaz**
- Średnia różnica: 0.02 MW (nieznaczna!)
- Maksymalna różnica: 793.72 MW
- Korelacja: **0.9879** (poniżej progu 0.99)
- **Przykłady największych różnic:**
  - `2026-01-05 16:00`: CSV=4,010 MW, API=3,595 MW (różnica 415 MW)
  - `2026-01-06 09:00`: CSV=4,547 MW, API=4,148 MW (różnica 398 MW)

**Możliwa przyczyna:** Różnice w klasyfikacji źródeł gazowych lub opóźnienia w raportowaniu danych.

##### 2. **Magazyny pompowe (hydro_pumped_storage)** ⚠️⚠️⚠️
- Średnia różnica: **-146.62 MW** (duża!)
- Maksymalna różnica: 1,050.95 MW
- Korelacja: **0.3740** (BARDZO NISKA!)
- **Przykłady największych różnic:**
  - `2026-01-20 15:00`: CSV=741 MW, API=191 MW (różnica 549 MW)
  - `2026-01-12 13:00`: CSV=550 MW, API=141 MW (różnica 409 MW)

**KRYTYCZNA ROZBIEŻNOŚĆ!** 
- Bardzo niska korelacja sugeruje **fundamentalną różnicę w metodologii**
- Możliwe przyczyny:
  - CSV może zawierać pompowanie + generację, API tylko jedno z nich
  - Różne klasyfikacje elektrowni szczytowo-pompowych
  - Błędne dane w jednym ze źródeł

##### 3. **Woda przepływowa (hydro_run-of-river)**
- Średnia różnica: 3.99 MW
- Maksymalna różnica: 102.17 MW
- Korelacja: **0.9143** (poniżej progu)
- **Największa różnica:** `2025-12-28 16:00`: CSV=136 MW, API=34 MW (102 MW różnicy)

**Możliwa przyczyna:** Różnice w klasyfikacji elektrowni wodnych (przepływowe vs zbiornikowe).

##### 4. **Woda zbiornikowa (hydro_water_reservoir)**
- Średnia różnica: 14.06 MW
- Maksymalna różnica: 110.26 MW
- Korelacja: **0.9733** (poniżej progu)
- Średnia różnica %: **194.39%** (bardzo wysoka ze względu na małe wartości bezwzględne)

**Możliwa przyczyna:** Podobnie jak wyżej - klasyfikacja elektrowni.

---

## 3. PORÓWNANIE Z DANYMI API PSE

### 3.1. Ograniczenia
⚠️ **Brak możliwości bezpośredniego porównania**

**Powód:** 
- PSE API dostarcza głównie dane rynkowe: `Zapotrzebowanie na moc`, `Saldo wymiany międzysystemowej`
- PSE ma kolumny `Sumaryczna generacja źródeł wiatrowych/fotowoltaicznych`, ale używają innych nazw
- Plik CSV zawiera dane ENTSO-E o wszystkich źródłach produkcji

**Kolumny w PSE:**
- `Sumaryczna generacja źródeł fotowoltaicznych [MW]`
- `Sumaryczna generacja źródeł wiatrowych [MW]`
- `Zapotrzebowanie na moc [MW]`
- `Krajowe saldo wymiany międzysystemowej [MW]`

**Wniosek:** PSE i ENTSO-E to **komplementarne źródła danych**, nie konkurencyjne.

---

## 4. KLUCZOWE WNIOSKI

### 4.1. Zgodność danych
✅ **Bardzo wysoka zgodność** dla większości źródeł:
- Węgiel (kamienny i brunatny): **99.7% korelacji**
- Wiatr: **99.9% korelacji**
- Biomasa: **99.8% korelacji**
- Fotowoltaika: **99.2% korelacji**

### 4.2. Rozbieżności wymagające uwagi

#### 🔴 **KRYTYCZNE:**
1. **Magazyny pompowe** - fundamentalna różnica w metodologii (korelacja 37%)
   - Wymaga wyjaśnienia źródła danych CSV
   - Możliwe, że CSV zawiera sumę pompowania i generacji

#### 🟡 **ŚREDNIE:**
2. **Woda przepływowa/zbiornikowa** - różnice w klasyfikacji elektrowni
   - Może wymagać weryfikacji kategoryzacji w źródle CSV

3. **Gaz** - niewielkie różnice czasowe (opóźnienia w raportowaniu?)
   - Różnica średnia bliska 0, ale korelacja 98.8%

### 4.3. Źródło pliku CSV

**Charakterystyka:**
- Dane z ENTSO-E, ale **nie identyczne** z aktualnym API
- Możliwe scenariusze:
  1. **Historyczny eksport** z ENTSO-E z innych lat
  2. **Inna metoda agregacji** danych (CSV może używać innej formuły niż obecne API)
  3. **Wersja wstępna/skorygowana** danych (ENTSO-E czasem publikuje korekty)
  4. **Inne źródło** podające się za ENTSO-E

### 4.4. Obsługa zmian czasu (DST)

⚠️ **Plik CSV nie obsługuje poprawnie DST:**
- Brakuje godziny 2:00-3:00 w każdą ostatnią niedzielę marca (2015-2024)
- Brak oznaczenia powtarzających się godzin w końcu października

**Nasz system obsługuje DST poprawnie:**
- Znaczniki `_dst_marker`: 'first'/'second' dla powtarzających się godzin
- Automatyczne wykrywanie i obsługa zmian czasu

---

## 5. REKOMENDACJE

### 5.1. Dla użytkowników danych

1. **Dla analiz historycznych (2015-2025):**
   - ✅ Użyj pliku CSV dla ogólnych trendów
   - ⚠️ **NIE używaj** kolumny `hydro_pumped_storage` bez weryfikacji
   - ⚠️ Zweryfikuj okresy DST (marzec/październik każdego roku)

2. **Dla analiz bieżących (2025-2026):**
   - ✅ **Preferuj dane z API ENTSO-E** - są aktualniejsze i bardziej wiarygodne
   - ✅ Uzupełnij danymi PSE dla kontekstu rynkowego

3. **Dla raportowania:**
   - Zawsze podawaj źródło danych (`CSV historyczny` vs `API ENTSO-E`)
   - Dokumentuj metodologię agregacji danych 15-minutowych

### 5.2. Dla rozwoju systemu

1. **Priorytet wysoki:**
   - [ ] Zaimplementuj automatyczną weryfikację danych pompowych
   - [ ] Dodaj ostrzeżenia dla okresów DST w danych historycznych
   - [ ] Udokumentuj różnice między CSV a API w dokumentacji projektu

2. **Priorytet średni:**
   - [ ] Rozważ ponowne pobranie danych historycznych z API ENTSO-E (zamiast używania CSV)
   - [ ] Dodaj flagę `data_source` do wszystkich rekordów (CSV vs API)
   - [ ] Zaimplementuj system alertów dla rozbieżności > 10%

3. **Priorytet niski:**
   - [ ] Porównaj dane z innymi źródłami (np. Eurostat, IEA)
   - [ ] Automatyczna analiza trendów dla wykrywania anomalii

### 5.3. Pytania do wyjaśnienia

1. **Skąd pochodzi plik CSV?**
   - Czy to oficjalny eksport z ENTSO-E?
   - Z jakiej daty pochodzi eksport?
   - Czy dane były modyfikowane po eksporcie?

2. **Metodologia magazynów pompowych:**
   - Co dokładnie zawiera kolumna `hydro_pumped_storage` w CSV?
   - Czy to generacja, pompowanie, czy suma?

3. **Plan na przyszłość:**
   - Czy kontynuować używanie CSV dla danych historycznych?
   - Czy migrować na 100% do API?

---

## 6. PODSUMOWANIE TECHNICZNE

### 6.1. Narzędzia użyte do analizy
- **Język:** Python 3.x
- **Biblioteki:** pandas, numpy, datetime
- **Źródła danych:**
  - CSV: `electricity_production_entsoe_all (2).csv`
  - API ENTSO-E: `https://web-api.tp.entsoe.eu/api`
  - API PSE: `https://api.raporty.pse.pl/api`

### 6.2. Metoda porównania
1. Wczytanie CSV (139,673 rekordów, 11.1 lat)
2. Pobranie danych z API dla ostatniego miesiąca (2,944 rekordów 15-min)
3. Agregacja API do godzin (736 godzin)
4. Dopasowanie timestampów (usunięcie timezone)
5. Merge na wspólne daty (2,941 pomiarów)
6. Obliczenie różnic, korelacji, statystyk

### 6.3. Metryki jakości

**Progi akceptowalności:**
- ✅ Korelacja ≥ 0.99
- ✅ Średnia różnica < 10 MW
- ⚠️ Korelacja 0.90-0.99: Do weryfikacji
- ❌ Korelacja < 0.90: Krytyczne rozbieżności

**Wyniki:**
- **5/9 źródeł:** ✅ Zgodne
- **3/9 źródeł:** ⚠️ Do weryfikacji
- **1/9 źródeł:** ❌ Krytyczne (magazyny pompowe)

---

## 7. ZAŁĄCZNIKI

### Skrypt porównawczy
Pełny kod analizy dostępny w: [`compare_data_sources.py`](compare_data_sources.py)

**Uruchomienie:**
```bash
python compare_data_sources.py
```

**Wymagania:**
```
pandas
numpy
python-dotenv
requests
```

### Pliki danych
- CSV: `electricity_production_entsoe_all (2).csv` (33.3 MB)
- Wyniki systemu: `szereg_czasowy_*.csv`, `analiza_*.csv`

---

**Raport przygotowany automatycznie przez:** System analizy danych energetycznych  
**Kontakt:** [konfiguracja systemu]  
**Wersja:** 1.0  
**Licencja danych:** ENTSO-E Transparency Platform
