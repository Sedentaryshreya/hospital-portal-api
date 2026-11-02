# Incoming Ambulance APIs - API Contract

## Overview
Two endpoints that let hospital staff see ambulances heading to their hospital.
All data in this project is synthetic (fake) test data.

## Authentication (assumption)
No login system exists in this standalone module. The hospital is identified
by a required header:

    X-Hospital-Id: <integer>

In the real platform this would come from the logged-in user's session.

## 1. List incoming ambulances
`GET /api/hospital/incoming-ambulances`

### Query parameters
| Name | Type | Default | Description |
|---|---|---|---|
| status | DISPATCHED / EN_ROUTE / NEARBY | none | Filter by ambulance status |
| arrival_from | datetime | none | Expected arrival on or after this time |
| arrival_to | datetime | none | Expected arrival on or before this time |
| page | integer >= 1 | 1 | Page number |
| limit | integer 1-100 | 10 | Items per page |

### Rules
- Only bookings of the hospital in `X-Hospital-Id` are returned.
- "Incoming" means status DISPATCHED, EN_ROUTE or NEARBY (ARRIVED and CANCELLED are excluded).
- Sorted by expected arrival (earliest first), then by id. Records without an ETA come last.

### Example request
    GET /api/hospital/incoming-ambulances?page=1&limit=10
    X-Hospital-Id: 1

### Example response (200)
```json
{
  "data": [
    {
      "bookingId": "BK-1001",
      "emergencyType": "Cardiac",
      "ambulanceStatus": "EN_ROUTE",
      "expectedArrival": "2026-11-02T08:29:51.710933"
    },
    {
      "bookingId": "BK-1003",
      "emergencyType": "Stroke",
      "ambulanceStatus": "NEARBY",
      "expectedArrival": null
    }
  ],
  "page": 1,
  "limit": 10,
  "total": 2
}
```

## 2. Get one incoming ambulance
`GET /api/hospital/incoming-ambulances/{id}`

### Example response (200)
```json
{
  "bookingId": "BK-1001",
  "emergencyType": "Cardiac",
  "ambulanceStatus": "EN_ROUTE",
  "expectedArrival": "2026-11-02T08:29:51.710933"
}
```

## Error responses
| Situation | Status |
|---|---|
| Missing X-Hospital-Id header | 422 |
| Invalid status value | 422 |
| page < 1, limit < 1 or limit > 100 | 422 |
| Invalid date format | 422 |
| arrival_to earlier than arrival_from | 400 |
| Unknown id | 404 |
| id belongs to another hospital | 404 |
| No matching records | 200 with `"data": []` |

## Field mapping
| API field | Database column |
|---|---|
| bookingId | bookings.booking_code |
| emergencyType | bookings.emergency_type |
| ambulanceStatus | bookings.ambulance_status |
| expectedArrival | bookings.expected_arrival (nullable) |

## Assumptions and gaps
- No shared schema was available, so the `hospitals` and `bookings` tables are my own design. Fields need to be agreed with Archit before integration with the main platform.
- Hospital identification uses a header instead of real authentication.
- "Incoming" statuses (DISPATCHED, EN_ROUTE, NEARBY) are my assumption and need confirmation.
- ETA is stored as an expected arrival time and can be null when unavailable.
- Another hospital's record returns 404 (not 403) so its existence is not revealed.