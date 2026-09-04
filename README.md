# PrioraMarket Intelligence

> A Market Intelligence platform for the UAE used car market.

PrioraMarket transforms thousands of marketplace listings into structured market intelligence, helping buyers, sellers, dealers, and analysts understand the automotive market through clean data and actionable analytics—not by browsing listings.

---

## Vision

Most automotive marketplaces answer:

> "What cars are for sale?"

PrioraMarket answers:

> "What is happening in the market?"

The platform continuously ingests marketplace listings, normalizes vehicle data, builds a canonical vehicle catalog, and exposes analytics through a dashboard-first experience.

---

## Current Features

### Data Platform

- Marketplace ingestion pipeline
- Canonical vehicle normalization
- Replayable data processing
- Canonical backfill
- Vehicle Reference Catalog
- Versioned normalization engine

### Market Analytics

- Market Snapshot Dashboard
- Active Listings
- Median Price
- Typical Price Range
- Inventory Change
- Price Drops
- Cascading vehicle filters
- Catalog-based display names

---

## Architecture

```
Marketplace

        │

        ▼

Python Scraper
(Ingestion)

        │

        ▼

Canonicalization Engine

        │

        ▼

PostgreSQL

        │

        ▼

NestJS Analytics API

        │

        ▼

Next.js Dashboard
```

---

## Tech Stack

### Scraper

- Python
- PostgreSQL
- BeautifulSoup
- Requests
- CSV Reference Catalog

### Backend

- NestJS
- Prisma
- PostgreSQL
- TypeScript

### Frontend

- Next.js
- React
- TanStack Query
- Tailwind CSS

---

## Project Structure

```
scrapper/
    Data ingestion
    Canonicalization
    Replay
    Vehicle Reference Catalog

backend/
    Analytics API
    Read-only services

frontend/
    Dashboard
    Market analytics
```

---

## Design Principles

- Dashboard-first experience
- Read-only analytics backend
- Clean Architecture
- Domain-Driven Design
- Canonical data model
- No marketplace normalization outside the scraper
- Vehicle Reference Catalog as the single source of truth
- Incremental feature development using Specification-Driven Development

---

## Roadmap

### ✅ Completed

- Data ingestion
- Canonicalization
- Vehicle Reference Catalog
- Replay
- Canonical Backfill
- Market Snapshot Dashboard

### 🚧 Planned

- Market Trends
- Vehicle Valuation
- Benchmark Analytics
- AI Market Insights

---

## Development

### Backend

```bash
cd backend

npm install

npm run start:dev
```

### Frontend

```bash
cd frontend

npm install

npm run dev
```

### Scraper

```bash
cd scrapper

python -m src.ingestion.runner scrape
```

---

## Testing

Backend

```bash
npm test
```

Frontend

```bash
npm test
```

Python

```bash
pytest
```

---

## Philosophy

PrioraMarket is **not an automotive marketplace**.

It is a **Market Intelligence Platform** built to answer questions like:

- Is inventory growing or shrinking?
- What is the typical market price?
- Which models are becoming more active?
- How is the market changing over time?

The focus is analytics first, listings second.

---

## License

MIT
