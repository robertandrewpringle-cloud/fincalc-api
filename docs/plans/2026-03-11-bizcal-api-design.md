# BizCal API — Design Document

**Date:** 2026-03-11
**Status:** Approved
**Project:** Second income-generating API product (revenue → user savings)

---

## 1. Product Identity

**Name:** BizCal API
**Tagline:** Business days, working hours, and holiday calendars for 15 countries — one API.
**Category:** Date & Calendar Utilities
**Marketplace:** RapidAPI

### Positioning
BizCal is the companion product to FinCalc API. Where FinCalc handles financial math, BizCal handles time math for business logic — the other calculation developers constantly need but hate building themselves. Same buyer persona (backend developers building business applications), complementary product. Both eventually listed under a "FinTools" umbrella on RapidAPI.

### Key Differentiators
- Sub-national region holidays (US states, German Länder, Australian states, Canadian provinces, Indian states) — deepest coverage on RapidAPI
- Working hours + SLA deadline engine — not just day counts
- Calendar intelligence endpoints (quarter, fiscal year, Nth weekday) — one-stop toolkit
- 21 endpoints across 4 categories — most comprehensive business calendar API on the marketplace
- Zero external API dependencies — pure computation, ~97% margin

---

## 2. Endpoint Map

### `/business-days/` — 6 endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/business-days/between` | Count business days between two dates |
| GET | `/business-days/add` | Add N business days to a date |
| GET | `/business-days/subtract` | Subtract N business days from a date |
| GET | `/business-days/next` | Next business day from a given date |
| GET | `/business-days/previous` | Previous business day from a given date |
| GET | `/business-days/is-business-day` | Check if a date is a business day |

### `/working-hours/` — 3 endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/working-hours/between` | Working hours between two datetimes (timezone-aware, 9am-5pm Mon-Fri) |
| GET | `/working-hours/add` | Add N working hours to a datetime |
| GET | `/working-hours/deadline` | SLA deadline calculator — given start datetime + N hours, return expiry datetime |

### `/holidays/` — 4 endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/holidays/list` | All holidays for a country/region/year |
| GET | `/holidays/is-holiday` | Check if a date is a public holiday |
| GET | `/holidays/next` | Next upcoming holiday from a given date |
| GET | `/holidays/countries` | List all supported countries and sub-national regions |

### `/calendar/` — 8 endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/calendar/week-number` | ISO week number and year for a date |
| GET | `/calendar/quarter` | Quarter number, start/end dates, days remaining in quarter |
| GET | `/calendar/fiscal-year` | Fiscal year info with configurable start month |
| GET | `/calendar/month-boundaries` | First and last business day of a given month |
| GET | `/calendar/nth-weekday` | Nth weekday of a month (e.g. 3rd Monday of March 2026) |
| GET | `/calendar/days-until` | Days until end of week/month/quarter/year |
| GET | `/calendar/date-info` | Mega-endpoint — all calendar facts about a date in one call |

### Other
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |

### Pro-only
| Method | Path | Description |
|--------|------|-------------|
| POST | `/bulk` | Batch up to 50 date calculations in a single request |

**Total: 22 endpoints** (21 standard + 1 bulk Pro)

---

## 3. Holiday Data & Country Coverage

**Data source:** Python `holidays` library (open source, pip install, zero API cost, actively maintained)

**15 countries with sub-national regions (~200+ distinct region calendars):**

| # | Country | Regional breakdown |
|---|---------|-------------------|
| 1 | 🇺🇸 United States | All 50 states + DC |
| 2 | 🇬🇧 United Kingdom | England, Wales, Scotland, Northern Ireland |
| 3 | 🇨🇦 Canada | All 13 provinces + territories |
| 4 | 🇦🇺 Australia | All 8 states + territories |
| 5 | 🇩🇪 Germany | All 16 Länder |
| 6 | 🇫🇷 France | Metropolitan + overseas territories |
| 7 | 🇪🇸 Spain | National + 17 autonomous communities |
| 8 | 🇮🇹 Italy | National + provinces |
| 9 | 🇳🇱 Netherlands | National |
| 10 | 🇧🇷 Brazil | National + 26 states |
| 11 | 🇮🇳 India | National + 28 states |
| 12 | 🇯🇵 Japan | National |
| 13 | 🇸🇬 Singapore | National |
| 14 | 🇿🇦 South Africa | National |
| 15 | 🇳🇿 New Zealand | National + regions |

---

## 4. Working Hours Engine

**Default schedule:** Monday–Friday, 09:00–17:00 (8 working hours/day)
**Timezone:** Caller-specified (IANA timezone string, e.g. `America/New_York`)
**Respects:** Public holidays for the specified country/region
**DST-safe:** Uses Python `zoneinfo` for correct DST handling

All working hours endpoints accept `country` and `region` parameters. If provided, public holidays are excluded from working hours calculations automatically.

---

## 5. Pricing Tiers

| Tier | Price | Requests/day | Features |
|------|-------|--------------|----------|
| Free | $0 | 50 | All standard endpoints, US + UK + AU only |
| Basic | $9.99/mo | 1,000 | All 15 countries + all regions |
| Pro | $29.99/mo | 10,000 | Everything + `/bulk` endpoint + custom fiscal year start month |
| Ultra | $99.99/mo | Unlimited | Everything + priority support |

**Free tier is country-limited** (not just rate-limited) to drive upgrades for real use cases.
**RapidAPI cut:** 20%
**Infrastructure cost:** ~$4.15/mo (Hetzner CX11, shared with or separate from FinCalc)
**Net margin:** ~97%

### Revenue Targets
- Month 6: $250+/mo net
- Month 12: $600+/mo net

---

## 6. Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 |
| Framework | FastAPI + Uvicorn |
| Holiday data | `holidays` library (pip) |
| Date/timezone math | Python `datetime` + `zoneinfo` (stdlib) |
| Reverse proxy | Nginx |
| Containers | Docker Compose |
| Hosting | Hetzner CX11 VPS (~$4.15/mo) |
| Marketplace | RapidAPI |
| SSL | Certbot (webroot via snap) |
| Deploy | `deploy.sh` (same pattern as FinCalc) |

---

## 7. Project Structure

```
api/
  main.py                        # FastAPI app, router includes
  routes/
    business_days.py             # 6 endpoints
    working_hours.py             # 3 endpoints
    holidays.py                  # 4 endpoints
    calendar.py                  # 8 endpoints
  calculators/
    business_days.py             # Pure business day logic
    working_hours.py             # Working hours engine
    holidays.py                  # Holiday lookup + country registry
    calendar.py                  # Calendar intelligence functions
docker/
  Dockerfile
  nginx.conf
docker-compose.yml
deploy.sh
tests/
  test_business_days.py
  test_working_hours.py
  test_holidays.py
  test_calendar.py
docs/
  rapidapi-listing.md
  plans/
    2026-03-11-bizcal-api-design.md
```

---

## 8. Testing Strategy

**Target: ~50 tests** (vs 33 in FinCalc)

Critical edge cases to cover:
- Business day addition crossing month/year boundaries
- Working hours spanning DST transitions (spring forward / fall back)
- Holiday falling on weekend (should not double-count)
- Cross-year fiscal year calculations
- Leap year February handling
- Nth weekday for months where it doesn't exist (e.g. 5th Monday)
- `/date-info` mega-endpoint correctness across all fields

---

## 9. Marketing Assets to Build

Same pipeline as FinCalc:
- `docs/rapidapi-listing.md` — marketplace copy
- `README.md` — GitHub public readme with code examples in Python, JS, curl
- 3 Dev.to tutorials:
  1. "Calculating Business Days in JavaScript (Using BizCal API)"
  2. "Building an SLA Deadline Tracker in Python"
  3. "Holiday-Aware Date Math for Global Applications"
- ProductHunt launch post
- Show HN post

---

## 10. Launch Steps

Same 11-step process as FinCalc:
1. Push to GitHub (new repo: `bizcal-api`)
2. Provision Hetzner CX11 VPS
3. Purchase domain (bizcalapi.com or similar)
4. Point DNS
5. SSH + run `deploy.sh`
6. Verify `/health`
7. Create RapidAPI listing
8. Set pricing tiers
9. Post Show HN
10. Post ProductHunt (Tuesday 12:01am PST)
11. Write 3 Dev.to tutorials
