# Informacje o dniach zmiany czasu (DST) dla użytkowników

## Co to jest dzień zmiany czasu?

W Polsce dwa razy w roku zmieniamy czas:
- **Marzec** (ostatnia niedziela): zmiana na **czas letni** - zegar przestawiamy z 2:00 na 3:00
- **Październik** (ostatnia niedziela): zmiana na **czas zimowy** - zegar cofamy z 3:00 na 2:00

## Wpływ na dane energetyczne

### Zmiana na czas letni (marzec)
Godzina 2:00-3:00 **nie istnieje** - zegar przeskakuje z 1:59 na 3:00.

**Skutek dla danych:**
- Brak pomiarów z godziny 2:00, 2:15, 2:30, 2:45 (4 pomiary)
- Dzień ma **92 rekordy** zamiast standardowych 96

### Zmiana na czas zimowy (październik)
Godzina 2:00-3:00 **występuje dwa razy** - zegar cofa się z 3:00 na 2:00.

**Teoretycznie:**
- Powinno być 100 rekordów (4 dodatkowe z powtórzonej godziny)

**W praktyce (w tym systemie):**
- System usuwa niejednoznaczne timestampy
- Dzień ma **92 rekordy** zamiast 96 lub 100
- Brak pomiarów z powtórzonej godziny 2:00-2:45

## Jak system to raportuje?

Przykładowy raport dla dnia 2025-10-26:

```
⏰ DZIEŃ ZMIANY CZASU - wykryto 1 dni:
----------------------------------------------------------------------

📅 2025-10-26
   Typ zmiany: CZAS ZIMOWY (październik)
   Pomiary: 92 z 96 oczekiwanych
   Brak 4 pomiarów z powtórzonej godziny 2:00-2:45 (zegar 3→2)
   ℹ️  To normalne - nie jest błędem systemu
----------------------------------------------------------------------
```

## Czy to jest problem?

**NIE** - to normalne zachowanie!

- Utrata 4 pomiarów rocznie (1 godziny) to **0.04%** danych
- System wyraźnie oznacza te dni w raportach
- Nie wpływa to na ogólną jakość analiz
- Wszystkie pozostałe pomiary (99.96%) są kompletne

## Daty zmiany czasu w Polsce

### 2024
- Czas letni: 31 marca 2024 (niedziela)
- Czas zimowy: 27 października 2024 (niedziela)

### 2025
- Czas letni: 30 marca 2025 (niedziela)
- Czas zimowy: 26 października 2025 (niedziela)

### 2026
- Czas letni: 29 marca 2026 (niedziela)
- Czas zimowy: 25 października 2026 (niedziela)

## Co można zrobić z brakującymi danymi?

W analizach można:
1. **Pominąć** brakującą godzinę - najczęściej najlepsze rozwiązanie
2. **Interpolować** wartości z godzin sąsiednich (dla wykresów ciągłych)
3. **Oznaczyć** jako brak danych w wizualizacjach

System automatycznie wykrywa i raportuje te dni, więc zawsze wiesz kiedy i dlaczego brakuje danych.

## Techniczne szczegóły

Jeśli API PSE zwraca format "02a:" i "02b:" dla powtórzonej godziny (historyczne dane), system może zachować wszystkie 100 rekordów dla dnia zmiany zimowej. Dla przyszłych dat (prognozy) API nie zwraca tego formatu, więc system usuwa niejednoznaczne timestampy.

Zobacz również: `docs/DST_HANDLING.md` dla szczegółów technicznych implementacji.
