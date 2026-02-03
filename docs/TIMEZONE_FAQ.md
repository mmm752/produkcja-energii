# ⏰ Strefy Czasowe: Szybkie FAQ

## ❓ Czy dane z ENTSO-E i PSE są w tym samym czasie?

**TAK** ✅ - Oba źródła pokazują czas lokalny polski (Europe/Warsaw).

## ❓ Czy muszę konwertować czasy z UTC?

**NIE** ❌ - Aplikacja robi to automatycznie za Ciebie.

## ❓ Co jeśli widzę oznaczenie `+01:00` lub `+02:00`?

To informacja, że czas jest już **przekonwertowany** na polski:
- `+01:00` = czas zimowy (CET = UTC+1)
- `+02:00` = czas letni (CEST = UTC+2)

Możesz je traktować jako normalny czas polski.

## ❓ Czy szczyt produkcji słonecznej jest o tej samej godzinie?

**TAK** ✅ - Przykład z 18 stycznia 2026:
- PSE: szczyt **11:45** = 8100.01 MW
- ENTSO-E: szczyt **11:45** = 8100.02 MW
- Różnica: **0 minut**, 0.00 MW

## ❓ Skąd to wiem?

Przeprowadziliśmy empiryczną analizę:
```bash
python3 scripts/timezone_check.py
```

Wynik: 
```
✅ DANE SĄ ZSYNCHRONIZOWANE CZASOWO
→ NIE musisz uwzględniać poprawki na strefę czasową
```

Szczegóły: [TIMEZONE_SYNC_ANALYSIS.md](TIMEZONE_SYNC_ANALYSIS.md)

## ❓ Co się dzieje "pod maską"?

1. **ENTSO-E API** zwraca dane w UTC (np. `10:45:00Z`)
2. **Kod aplikacji** automatycznie konwertuje na Europe/Warsaw
3. **Ty widzisz** już przekonwertowany czas (np. `11:45+01:00`)

Kod konwersji ([src/entsoe_data_fetcher.py](../src/entsoe_data_fetcher.py#L292)):
```python
df_pivot['Data'] = df_pivot['Data'].dt.tz_convert('Europe/Warsaw')
```

## ❓ A co z czasem letnim/zimowym?

Kod **automatycznie obsługuje** przejścia:
- CET → CEST (29 marca 2026): dodaje +2h zamiast +1h
- CEST → CET (25 października 2026): dodaje +1h zamiast +2h

Nie musisz się tym przejmować! 🎉

---

**Podsumowanie jednym zdaniem:**  
Dane PSE i ENTSO-E pokazują ten sam czas lokalny polski - bez żadnych poprawek.
