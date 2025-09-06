# Energie Management Dashboard

Een standalone webapplicatie voor het monitoren, analyseren en rapporteren van energieverbruik, -opwekking, kosten en de financiële Return on Investment (ROI) van een zonnepaneleninstallatie. De applicatie draait volledig lokaal binnen Docker containers.

## Features

*   **Dashboard met Tijdreeksanalyse:** Analyseer energiegegevens over een selecteerbare periode.
*   **KPI Overzicht:** Bekijk kerncijfers zoals totale kosten, opbrengsten, en zelfvoorzienendheid.
*   **ROI Tracker:** Volg de terugverdientijd van uw investering met een duidelijke voortgangsbalk.
*   **Interactieve Grafieken:**
    *   **Energiebalans:** Een gestapelde staafgrafiek die Import, Export, Opgewekte energie en Eigen Verbruik toont.
    *   **Verbruiksuitsplitsing:** Een doughnut chart die het verbruik van het huis versus de elektrische auto's toont.
*   **Data Invoer via Webformulier:** Voer eenvoudig nieuwe maandelijkse data in via een webformulier.
*   **Backend API:** Een robuuste FastAPI-backend voor alle berekeningen.
*   **Volledig Dockerized:** De gehele applicatie (backend, database) wordt beheerd met Docker Compose voor eenvoudige setup en deployment.

## Vereisten

*   [Docker](https://www.docker.com/get-started)
*   Docker Compose (meestal inbegrepen bij Docker Desktop)

## Installatie en Opstarten

1.  **Clone de Repository**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Bouw en Start de Applicatie**
    Gebruik Docker Compose om de images te bouwen en de containers te starten. Dit zal een backend-service en een PostgreSQL database-service opstarten.
    ```bash
    docker compose up --build -d
    ```
    De `-d` vlag start de containers in de achtergrond (detached mode).

3.  **Database Migraties Uitvoeren**
    Nadat de containers zijn gestart, moet het databaseschema worden aangemaakt. Voer het volgende commando uit om de Alembic-migraties toe te passen:
    ```bash
    docker compose exec backend alembic upgrade head
    ```

4.  **Initiële Data Importeren**
    Om de applicatie te vullen met de initiële data uit de CSV-bestanden, voert u het importscript uit:
    ```bash
    docker compose exec backend python scripts/import_data.py
    ```
    *Opmerking: Zorg ervoor dat de dummy data in `scripts/data/` is bijgewerkt met uw eigen historische gegevens voordat u dit script uitvoert.*

5.  **Applicatie Benaderen**
    De applicatie is nu volledig operationeel.
    *   **Frontend Dashboard:** Open uw browser en ga naar [http://localhost:8000](http://localhost:8000)
    *   **API Documentatie (Swagger UI):** Ga naar [http://localhost:8000/docs](http://localhost:8000/docs) voor een interactief overzicht van alle API-endpoints.

## Projectstructuur

```
.
├── app/              # Backend FastAPI applicatie
│   ├── api/          # API endpoints
│   ├── crud/         # Database operaties
│   ├── db/           # Database sessie management
│   ├── models/       # SQLAlchemy datamodellen
│   └── schemas/      # Pydantic schemas
├── scripts/          # Hulpscripts (bv. data import)
├── static/           # Statische bestanden (CSS, JS)
├── templates/        # HTML templates
├── alembic/          # Database migraties
├── Dockerfile        # Docker-configuratie voor de backend
└── docker-compose.yml # Docker Compose orkestratie
```

## Stoppen van de Applicatie

Om de applicatie te stoppen, gebruikt u:
```bash
docker compose down
```
Als u ook de database-volume wilt verwijderen (LET OP: DIT VERWIJDERT ALLE DATA), gebruikt u:
```bash
docker compose down -v
```
