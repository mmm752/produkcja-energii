# 🕐 Raport: Synchronizacja Czasowa PSE ↔ ENTSO-E

## 📋 Podsumowanie Wykonawcze

**Data analizy:** 21 stycznia 2026  
**Analizowany dzień danych:** 18 stycznia 2026  
**Metoda:** Porównanie szczytów produkcji fotowoltaicznej (PV)

---

## ✅ WERDYKT

### **Dane PSE i ENTSO-E SĄ W PEŁNI ZSYNCHRONIZOWANE CZASOWO**

Użytkownik patrząc na dane z ENTSO-E widzi **ten sam czas co w Polsce** — **NIE** jest wymagana żadna poprawka na strefę czasową.

---

## 📊 Dowody Empiryczne

### Porównanie Szczytu Produkcji PV (18 stycznia 2026)

| Źródło | Wartość szczytu | Czas wystąpienia | Strefa czasowa |
|--------|----------------|------------------|----------------|
| **PSE** | 8100.01 MW | **11:45** | Europe/Warsaw (implicit) |
| **ENTSO-E** | 8100.02 MW | **11:45** | Europe/Warsaw (explicit +01:00) |
| **Różnica** | 0.00 MW (0.00%) | 0 minut | — |

### Szczegółowe Dane Wokół Szczytu

#### PSE (czas lokalny):
```
Czas          Produkcja PV
11:00:00      7629.062 MW
11:15:00      7888.548 MW
11:30:00      8027.928 MW
11:45:00      8100.012 MW  ← SZCZYT
12:00:00      7564.578 MW
12:15:00      7449.415 MW
12:30:00      7284.053 MW
```

#### ENTSO-E (czas lokalny z oznaczeniem +01:00):
```
Czas             Produkcja PV
11:00:00+01:00   7629.063 MW
11:15:00+01:00   7888.551 MW
11:30:00+01:00   8027.931 MW
11:45:00+01:00   8100.016 MW  ← SZCZYT
12:00:00+01:00   7564.577 MW
12:15:00+01:00   7449.417 MW
12:30:00+01:00   7284.057 MW
```

**Obserwacje:**
- Wartości są identyczne z dokładnością do 0.01 MW (błąd zaokrągleń)
- Czas wystąpienia szczytu: identyczny (11:45)
- To potwierdza, że to **ten sam dataset**

---

## 🔍 Analiza Techniczna

### 1. Strefa Czasowa PSE

**Źródło danych:** [api.raporty.pse.pl/api/his-wlk-cal](https://api.raporty.pse.pl/api/his-wlk-cal)

```python
# Timestampy z API PSE (przykład):
{
  "Data": "2026-01-18 11:45:00",
  "business_date": "2026-01-18",
  "Sumaryczna generacja źródeł fotowoltaicznych [MW]": 8100.01
}
```

**Charakterystyka:**
- ✓ Dane publikowane w **czasie lokalnym** (Europe/Warsaw)
- ✓ Brak explicite oznaczenia strefy czasowej
- ✓ Rozdzielczość: 15 minut (96 pomiarów/dobę: 00:00, 00:15, ..., 23:45)
- ✓ Dotyczy obszaru Polski (KSE - Krajowy System Elektroenergetyczny)

### 2. Strefa Czasowa ENTSO-E

**Źródło danych:** [ENTSO-E Transparency Platform API](https://web-api.tp.entsoe.eu/api)

**API zwraca dane w UTC:**
```xml
<start>2026-01-18T10:45:00Z</start>
<!-- Z = UTC, czyli 11:45 CET (UTC+1) -->
```

**Konwersja w kodzie ([src/entsoe_data_fetcher.py:292](src/entsoe_data_fetcher.py#L292)):**
```python
# Linia 292-293: Konwersja UTC → Europe/Warsaw
df_pivot['Data'] = pd.to_datetime(df_pivot['Data'])
df_pivot['Data'] = df_pivot['Data'].dt.tz_convert('Europe/Warsaw')
```

**Charakterystyka:**
- ✓ API zwraca dane w **UTC** (Coordinated Universal Time)
- ✓ Kod aplikacji **automatycznie konwertuje** UTC → Europe/Warsaw
- ✓ Po konwersji timestampy mają oznaczenie `+01:00` (zima) lub `+02:00` (lato)
- ✓ Rozdzielczość: 15 minut (zgodnie z ENTSO-E standard)
- ✓ Obszar: 10YPL-AREA-----S (Polska)

### 3. Obsługa Czasu Letniego/Zimowego

**Europe/Warsaw (CET/CEST):**
- Czas zimowy (CET): UTC+1 (ostatnia niedziela października – ostatnia niedziela marca)
- Czas letni (CEST): UTC+2 (ostatnia niedziela marca – ostatnia niedziela października)

**W testowanym dniu (18 stycznia 2026):**
- Obowiązuje czas zimowy (CET = UTC+1)
- ENTSO-E: 10:45 UTC → 11:45 CET
- PSE: 11:45 CET (bezpośrednio)
- ✅ Czasy się zgadzają

**Latem sytuacja będzie analogiczna:**
- ENTSO-E: 09:45 UTC → 11:45 CEST (UTC+2)
- PSE: 11:45 CEST
- ✅ Kod automatycznie obsługuje zmianę dzięki `pytz.timezone('Europe/Warsaw')`

---

## 💻 Implementacja w Kodzie

### Moduł `combined_energy_data.py`

Synchronizacja odbywa się w [src/combined_energy_data.py:75-102](src/combined_energy_data.py#L75-L102):

```python
# Jeśli PSE nie ma tz, dodaj tz lokalną
if df_pse.index.tz is None:
    df_pse.index = df_pse.index.tz_localize(
        'Europe/Warsaw', 
        ambiguous='infer', 
        nonexistent='shift_forward'
    )

# Jeśli ENTSO-E ma inną tz, konwertuj do Europe/Warsaw
if df_entsoe.index.tz is not None:
    df_entsoe.index = df_entsoe.index.tz_convert('Europe/Warsaw')
else:
    df_entsoe.index = df_entsoe.index.tz_localize(
        'Europe/Warsaw', 
        ambiguous='infer', 
        nonexistent='shift_forward'
    )

# Po synchronizacji, usuń informację o tz dla prostoty
df_pse.index = df_pse.index.tz_localize(None)
df_entsoe.index = df_entsoe.index.tz_localize(None)
```

**Kluczowe parametry:**
- `ambiguous='infer'` - obsługuje zduplikowane godziny podczas przejścia z CEST→CET (np. 02:30 występuje 2×)
- `nonexistent='shift_forward'` - obsługuje nieistniejące godziny podczas przejścia CET→CEST (np. 02:30 nie istnieje)

---

## 📌 Odpowiedź na Pytanie Użytkownika

### Czy dane wymagają konwersji strefy czasowej?

**NIE** ❌

**Dlaczego?**

1. **ENTSO-E API zwraca dane w UTC**, ale...
2. **Kod aplikacji automatycznie konwertuje** je do czasu polskiego (Europe/Warsaw)
3. **Po tej konwersji** dane z obu źródeł pokazują ten sam czas

### Czy użytkownik musi brać poprawkę?

**NIE** ❌

**Kiedy użytkownik widzi dane:**
- Są już przekonwertowane do czasu polskiego
- Szczyt PV o 11:45 w PSE = szczyt PV o 11:45 w ENTSO-E
- Nie ma różnicy +1h czy +2h

### Co jeśli ktoś używa ENTSO-E bezpośrednio (bez tego kodu)?

**TAK** ✅ - wtedy TRZEBA uwzględnić strefę czasową

Jeśli pobierasz surowe dane z ENTSO-E API (bez tej aplikacji):
```
ENTSO-E (surowe UTC):  10:45:00Z  ← UTC
Polska (CET):          11:45:00   ← UTC+1 (zima)
Polska (CEST):         12:45:00   ← UTC+2 (lato)
```

Ale **w tej aplikacji** ta konwersja już jest zrobiona automatycznie.

---

## 🧪 Metoda Weryfikacji

### Skrypt Testowy

Utworzono skrypt [scripts/timezone_check.py](scripts/timezone_check.py), który:

1. Pobiera dane PSE dla testowego dnia
2. Pobiera dane ENTSO-E dla tego samego dnia
3. Znajduje szczyt produkcji PV w obu źródłach
4. Porównuje:
   - Wartość szczytu (MW)
   - Czas wystąpienia szczytu
   - Oblicza różnice czasowe

### Uruchomienie:
```bash
python3 scripts/timezone_check.py
```

### Wynik:
```
✅ DANE SĄ ZSYNCHRONIZOWANE CZASOWO

🎯 Wnioski:
   • PSE i ENTSO-E pokazują ten sam czas (lokalny polski)
   • Szczyt PV występuje o tej samej godzinie w obu źródłach
   • Nie jest wymagana korekta strefy czasowej
   • Oba serwisy używają czasu Europe/Warsaw (CET/CEST)

📌 Dla użytkownika:
   → Patrząc na dane z ENTSO-E widzisz TEN SAM CZAS co w Polsce
   → NIE musisz uwzględniać poprawki na strefę czasową
```

---

## 📚 Dodatkowe Informacje

### Offset UTC dla Polski

| Okres | Standard | UTC Offset | Przykład |
|-------|----------|------------|----------|
| **Zima** | CET (Central European Time) | UTC+1 | 12:00 UTC = 13:00 CET |
| **Lato** | CEST (Central European Summer Time) | UTC+2 | 12:00 UTC = 14:00 CEST |

### Zmiana czasu w 2026

- **CET → CEST:** 29 marca 2026, 02:00 → 03:00 (godzina 02:00-03:00 nie istnieje)
- **CEST → CET:** 25 października 2026, 03:00 → 02:00 (godzina 02:00-03:00 występuje 2×)

Kod obsługuje oba przypadki dzięki parametrom `ambiguous` i `nonexistent`.

---

## ✅ Wnioski Końcowe

1. **Synchronizacja czasowa jest prawidłowa** - oba źródła pokazują ten sam czas lokalny
2. **Wartości są identyczne** - różnica 0.00 MW potwierdza ten sam dataset
3. **Kod aplikacji działa poprawnie** - konwersja UTC→Europe/Warsaw jest automatyczna
4. **Użytkownik NIE musi** robić żadnych poprawek czasowych
5. **Weryfikacja możliwa** - skrypt `timezone_check.py` może być używany do testów

---

**Autor:** GitHub Copilot  
**Data:** 21 stycznia 2026  
**Status:** ✅ Zweryfikowano empirycznie
