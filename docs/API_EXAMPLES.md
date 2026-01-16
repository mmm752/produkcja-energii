# Przykłady zapytań do API PSE

## Base URL
```
https://api.raporty.pse.pl/api/his-wlk-cal
```

## 1. Pobierz ostatnie 100 rekordów
```bash
curl 'https://api.raporty.pse.pl/api/his-wlk-cal'
```

## 2. Pobierz dane dla konkretnego dnia
```bash
curl 'https://api.raporty.pse.pl/api/his-wlk-cal?$filter=business_date%20eq%20%272024-06-14%27'
```

## 3. Pobierz dane dla zakresu dat
```bash
curl 'https://api.raporty.pse.pl/api/his-wlk-cal?$filter=business_date%20ge%20%272024-06-14%27%20and%20business_date%20le%20%272024-06-15%27'
```

## 4. Sortowanie wyników
```bash
curl 'https://api.raporty.pse.pl/api/his-wlk-cal?$filter=business_date%20eq%20%272024-06-14%27&$orderby=dtime%20desc'
```

## 5. Python - requests
```python
import requests

url = 'https://api.raporty.pse.pl/api/his-wlk-cal'
params = {
    '$filter': "business_date eq '2024-06-14'"
}

response = requests.get(url, params=params)
data = response.json()

print(f"Pobrano {len(data['value'])} rekordów")

# Przykładowy rekord
first_record = data['value'][0]
print(f"Wiatr: {first_record['wi']} MW")
print(f"PV: {first_record['pv']} MW")
print(f"Data: {first_record['dtime']}")
```

## 6. Wybór konkretnych pól (select)
```bash
curl 'https://api.raporty.pse.pl/api/his-wlk-cal?$filter=business_date%20eq%20%272024-06-14%27&$select=dtime,wi,pv,demand'
```

## Kluczowe pola w odpowiedzi

| Pole | Opis | Typ |
|------|------|-----|
| `wi` | Moc wiatrowa | float [MW] |
| `pv` | Moc fotowoltaiczna | float [MW] |
| `dtime` | Data i czas (lokalny) | string |
| `business_date` | Data biznesowa | string (YYYY-MM-DD) |
| `demand` | Zapotrzebowanie | float [MW] |
| `period` | Okres 15-minutowy | string |
| `jg` | Generacja jednostek jrwa | float [MW] |

## OData Operators

### Porównanie
- `eq` - równe
- `ne` - różne
- `gt` - większe
- `ge` - większe lub równe
- `lt` - mniejsze
- `le` - mniejsze lub równe

### Logiczne
- `and` - i
- `or` - lub
- `not` - nie

### Funkcje
- `contains(field, 'value')` - zawiera
- `startswith(field, 'value')` - zaczyna się od
- `endswith(field, 'value')` - kończy się na

## Przykłady zaawansowane

### Filtrowanie po godzinie
```bash
# Wszystkie rekordy z godziny 12:00
curl 'https://api.raporty.pse.pl/api/his-wlk-cal?$filter=business_date%20eq%20%272024-06-14%27%20and%20contains(period,%27%2012:%27)'
```

### Wysokie obciążenie (demand > 15000 MW)
```bash
curl 'https://api.raporty.pse.pl/api/his-wlk-cal?$filter=business_date%20eq%20%272024-06-14%27%20and%20demand%20gt%2015000'
```

### Sortowanie i limit
```bash
curl 'https://api.raporty.pse.pl/api/his-wlk-cal?$filter=business_date%20eq%20%272024-06-14%27&$orderby=wi%20desc&$top=10'
```

## Odpowiedzi API

### Sukces (200 OK)
```json
{
  "value": [
    {
      "jg": 12132.16,
      "pv": 0.0,
      "wi": 299.813,
      "dtime": "2024-06-14 00:15:00",
      "demand": 16296.632,
      "period": "00:00 - 00:15",
      "business_date": "2024-06-14"
    }
  ]
}
```

### Błąd (400 Bad Request)
```json
{
  "error": {
    "code": "BadRequest",
    "message": "Invalid Query Parameter: dateFrom",
    "status": 400
  }
}
```

## Rate Limiting

Obecnie API nie ma oficjalnych limitów, ale zaleca się:
- Maksymalnie 10 requestów na sekundę
- Dla dużych zakresów dat - pobieranie dzień po dniu
- Używanie cache dla często pobieranych danych

## Inne endpointy PSE API v2

- `/gen-jw` - Generacja jednostek wytwórczych
- `/kse-load` - Obciążenie KSE
- `/energy-prices` - Ceny energii
- `/przeplywy-mocy` - Przepływy mocy
- i wiele innych...

Pełna dokumentacja: https://api.raporty.pse.pl
