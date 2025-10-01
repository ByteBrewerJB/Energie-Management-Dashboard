# JouleJournal v2

JouleJournal is een energie management platform voor huiseigenaren met zonnepanelen, thuisbatterijen en elektrische auto''s. De applicatie levert financieel inzicht, ROI-tracking en visualisaties op basis van handmatig ingevoerde maanddata.

## Belangrijkste functionaliteiten
- **Dashboard** met KPI''s, energiebalans, consumptiesplitsing en productie vs. verwachting.
- **ROI-tracker** die besparingen afzet tegen de initiële investering.
- **Maandjournaal** voor het invoeren van verbruiks-, productie- en tariefdata, inclusief laadinformatie per auto.
- **Assetbeheer** voor zonnepanelen, batterijen en elektrische auto''s.
- **JWT-authenticatie** met login, registratie en afgeschermde API-endpoints.

## Architectuur
- **Backend:** FastAPI + SQLAlchemy
- **Frontend:** Jinja2-templates, vanilla JavaScript en Chart.js
- **Database:** SQLite (development) of PostgreSQL (productie via Docker)
- **Containerisatie:** Dockerfile + docker-compose voor backend en PostgreSQL

Mappenstructuur:
```
backend/
  app/
    api/        # REST API routers
    core/       # Configuratie, security en dependencies
    db/         # Database sessie en initialisatie
    models/     # SQLAlchemy modellen
    schemas/    # Pydantic schema''s
    services/   # Aggregatielogica (dashboard & ROI)
    templates/  # Jinja2 templates
    static/     # CSS & JS assets
    main.py     # FastAPI applicatie en UI-routes
  requirements.txt
  Dockerfile
```

## Voorbereiding lokale ontwikkeling (SQLite)
1. **Virtuele omgeving** (optioneel, maar aanbevolen)
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. **Dependencies installeren**
   ```bash
   pip install -r backend/requirements.txt
   ```
3. **Omgevingsvariabelen**
   - Kopieer `backend/.env.example` naar `backend/.env` en pas waar nodig aan.
   - Standaard wordt SQLite gebruikt (`sqlite:///./joulejournal.db`).
4. **Applicatie starten**
   ```bash
   uvicorn backend.app.main:app --reload
   ```
5. Applicatie is bereikbaar via `http://localhost:5210`. De API-documentatie staat op `/docs` (vereist inloggen voor beveiligde endpoints).

## Docker (PostgreSQL + backend)
1. Kopieer `.env.example` naar `.env` wanneer je custom secrets wilt instellen.
2. Start de containers:
   ```bash
   docker-compose up --build
   ```
3. Backend draait op `http://localhost:5210`, database op poort `5544`.

## Authenticatie
- Nieuwe gebruikers kunnen zichzelf registreren via `/register` of via de API (`POST /api/auth/register`).
- Inloggen levert een JWT-token (`POST /api/auth/token`). De webinterface slaat het token op in een HttpOnly-cookie.
- Een eerste beheeraccount wordt tijdens startup aangemaakt op basis van `FIRST_SUPERUSER_EMAIL` en `FIRST_SUPERUSER_PASSWORD`.

## Data & Rapportage
- Maandjournaals worden uniek gemaakt op combinatie van gebruiker + jaar + maand.
- Autoladingen worden gekoppeld via het CarChargeJournal en meegenomen in ROI- en dashboardberekeningen.
- De ROI-voortgang combineert vermeden verbruikskosten, terugleveropbrengsten en auto-declaraties.

## Tests en vervolgstappen
- Voeg unit tests of integratietests toe (bijvoorbeeld pytest + TestClient) voor kritieke services (`services/dashboard.py`, `services/roi.py`).
- Overweeg Alembic voor database migraties wanneer het datamodel evolueert.
- Breid de UI uit met import/export functionaliteit voor maanddata en meer geavanceerde filters.

## Licentie
Dit project is geleverd als referentie-implementatie; kies een licentie die past bij jouw distributiewensen.
