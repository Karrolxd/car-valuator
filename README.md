# Car Valuator — Wyceniarka samochodów

Aplikacja webowa przewidująca rynkową cenę używanego samochodu
na podstawie ogłoszeń z Otomoto.

## Stack

- **Frontend:** Next.js 16.2.6, React 19.2.5, TypeScript, Tailwind CSS
- **Backend:** FastAPI 0.129.x, Python 3.12, PostgreSQL, SQLAlchemy 2.0.50
- **ML:** scikit-learn 1.8.0, XGBoost 3.2.0, pandas 3.0.3
- **Scraping:** curl_cffi, Playwright (fallback)
- **Deploy:** Vercel (frontend) + Railway (backend + DB)
## Struktura

```
car-valuator/
├── frontend/   # Next.js → Vercel
├── backend/    # FastAPI + scraper + ML → Railway
└── docker-compose.yml
```

## Uruchomienie lokalne

> Dokumentacja zostanie uzupełniona w ticket #036.
 