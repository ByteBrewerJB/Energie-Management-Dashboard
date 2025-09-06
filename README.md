# JouleJournal - Energie Management Dashboard

Een webapplicatie voor het monitoren, analyseren en rapporteren van energieverbruik, -opwekking, kosten en de financiële Return on Investment (ROI) van een zonnepaneleninstallatie.

## Features

- **Dynamisch Dashboard:** Real-time visualisatie van uw energiegegevens.
- **KPI Overzicht:** Kerncijfers voor het huidige jaar, inclusief netto kosten en zelfvoorzienendheid.
- **ROI Tracker:** Visuele voortgangsbalk die de terugverdientijd van uw investering toont.
- **Interactieve Grafieken (Chart.js):**
    - **Energiebalans:** Gestapelde staafgrafiek van Import, Export, en Eigen Verbruik.
    - **Verbruiksuitsplitsing:** Taartdiagram dat verbruik van het huis vs. elektrische auto toont.
    - **Productie vs. Forecast:** Lijngrafiek die werkelijke productie vergelijkt met de prognose.
- **Robuuste Backend API:** Gebouwd met FastAPI voor snelle en betrouwbare dataverwerking.
- **Containerized:** Volledig geconfigureerd om te draaien met Docker voor een eenvoudige en consistente setup.

## Vereisten

- [Docker](https://www.docker.com/get-started)
- Docker Compose V1 (docker-compose) of V2 (docker compose)

## Installatie en Opstarten

Volg deze stappen om de applicatie lokaal op te zetten en te draaien.

1.  **Clone de Repository**
    ```bash
    git clone <repository_url>
    cd joulejournal-project
    ```

2.  **Bouw en Start de Applicatie**
    Dit commando bouwt de Docker-image voor de backend en start alle services (backend en database) die zijn gedefinieerd in `docker-compose.yml`.
    ```bash
    docker-compose up --build
    ```
    *Wacht tot de output aangeeft dat de Uvicorn-server draait.*

3.  **Draai Database Migraties (in een nieuw terminalvenster)**
    Met de applicatie draaiend, opent u een tweede terminal. Dit commando past de database schema's toe.
    ```bash
    docker-compose exec backend alembic upgrade head
    ```

4.  **Seed de Database met Startdata (in hetzelfde nieuwe terminalvenster)**
    Dit script vult de database met initiële data voor investeringen, tarieven en metingen, zodat het dashboard direct bruikbaar is.
    ```bash
    docker-compose exec backend python scripts/seed_db.py
    ```

5.  **Bekijk de Applicatie**
    De applicatie is nu volledig ingesteld en draait.
    - **Frontend Dashboard:** Open uw browser en ga naar [http://localhost:8000](http://localhost:8000)
    - **API Documentatie (Swagger UI):** Ga naar [http://localhost:8000/docs](http://localhost:8000/docs)

## Projectstructuur

```
.
├── app/              # Backend FastAPI applicatie
├── scripts/          # Hulpscripts (seed_db.py)
├── static/           # Statische bestanden (CSS, JS)
├── templates/        # HTML templates
├── alembic/          # Database migraties
├── Dockerfile
└── docker-compose.yml
```

## Stoppen van de Applicatie

Om de containers te stoppen, druk op `Ctrl+C` in de terminal waar `docker-compose up` draait, of voer uit:
```bash
docker-compose down
```
Om ook de database-volume te verwijderen (LET OP: DIT VERWIJDERT ALLE DATA), gebruikt u:
```bash
docker-compose down -v
```
