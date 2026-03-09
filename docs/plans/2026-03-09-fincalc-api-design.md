# FinCalc API — Design Document
**Date:** 2026-03-09
**Status:** Approved
**Owner:** Claude (claude-sonnet-4-6)
**Budget:** $5–30/month
**Runway:** 12 months

---

## Overview

A comprehensive financial calculator REST API deployed on a cheap VPS and listed on the RapidAPI marketplace. Pure computation — no database, no external API dependencies, near-zero marginal cost per request. RapidAPI handles billing, authentication, rate limiting, and customer discovery. Revenue funds AI compute improvements.

---

## Product

**Name:** FinCalc API
**Tagline:** Financial calculation endpoints for developers. Skip the math.

### Endpoints (v1)

| Endpoint | Description |
|---|---|
| `GET /amortize` | Full amortization schedule for a loan |
| `GET /compound-interest` | Savings/investment projections |
| `GET /roi` | Return on investment |
| `GET /npv` | Net present value |
| `GET /irr` | Internal rate of return |
| `GET /break-even` | Break-even analysis |
| `GET /depreciation` | Straight-line & declining balance |
| `GET /mortgage` | Monthly payment + total cost of loan |

All endpoints return JSON. All inputs via query params. Stateless — no data stored.

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│              RapidAPI Marketplace                │
│  (billing, auth, rate limiting, discovery)       │
└──────────────────────┬──────────────────────────┘
                       │ HTTPS (X-RapidAPI-Key)
┌──────────────────────▼──────────────────────────┐
│  Hetzner CX11 VPS (~$4.15/mo)                   │
│  ┌──────────┐    ┌──────────────────────────┐   │
│  │  Nginx   │───▶│  FastAPI + Uvicorn       │   │
│  │ (SSL/TLS)│    │  8 calculation endpoints │   │
│  └──────────┘    └──────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### Stack

- **Language:** Python 3.12
- **Framework:** FastAPI (auto-generates OpenAPI spec for RapidAPI)
- **Server:** Uvicorn (async ASGI)
- **Reverse proxy:** Nginx + Let's Encrypt (free SSL)
- **Containerization:** Docker Compose
- **Hosting:** Hetzner CX11 (~$4.15/mo)
- **Domain:** ~$10–15/year
- **Database:** None (pure computation)
- **Payments:** RapidAPI built-in billing

---

## Pricing

| Plan | Price | Requests/day | Target |
|---|---|---|---|
| Free | $0 | 50 | Evaluation, hobby |
| Basic | $9.99/mo | 1,000 | Indie devs, startups |
| Pro | $29.99/mo | 10,000 | Growing products |
| Ultra | $99.99/mo | Unlimited | Enterprise |

---

## Revenue Projections

| Month | Subscribers | Gross/mo | Net (−20% RapidAPI) | Running total |
|---|---|---|---|---|
| 3 | 3 Basic, 1 Pro | ~$60 | ~$48 | ~$100 |
| 6 | 7 Basic, 3 Pro, 1 Ultra | ~$260 | ~$208 | ~$700 |
| 12 | 15 Basic, 8 Pro, 3 Ultra | ~$640 | ~$512 | ~$3,400 |

Monthly infrastructure cost: ~$5. Net margin at scale: ~97%.

---

## Launch Plan

### Week 1
- Deploy API to Hetzner VPS
- Publish RapidAPI listing (full description, code examples in Python/JS/PHP/Ruby/Java)
- Create public GitHub repo with README and usage examples
- Post "Show HN: FinCalc API — 8 financial calculation endpoints for developers"
- Post on ProductHunt

### Month 1
- Publish 3 tutorials on Dev.to:
  1. *"Add loan amortization to your app in 10 lines of code"*
  2. *"Mortgage calculator API: skip the math, ship the feature"*
  3. *"NPV and IRR for non-quants: a developer's guide"*
- Post in /r/webdev, /r/fintech, /r/SideProject

### Month 2–12 (Ongoing, Automated)
- Monitor RapidAPI reviews and usage patterns
- Add 1–2 new endpoints per quarter based on demand
- Each new endpoint = new blog post = new discovery surface
- No paid advertising — organic only

---

## Success Criteria

- **Month 3:** First paying subscriber
- **Month 6:** $200+/mo net revenue
- **Month 12:** $500+/mo net revenue, 25+ active subscribers

---

## What the User Needs to Do (One-Time Setup)

1. Create account at hetzner.com, provision CX11 VPS
2. Purchase domain (e.g. `fincalcapi.com`)
3. Create account at rapidapi.com/provider
4. Point domain DNS to VPS IP
5. Provide VPS SSH credentials so deployment can run

After that: nothing.
