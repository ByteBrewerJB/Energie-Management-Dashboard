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

## Implementatie in Portainer (Aanbevolen)

Voor een eenvoudige en beheerde implementatie kunt u deze applicatie als een "Stack" in Portainer draaien.

1.  **Navigeer naar Stacks:** Log in op uw Portainer-instantie en ga naar "Stacks" in het menu.
2.  **Voeg een nieuwe Stack toe:** Klik op "Add stack".
3.  **Configureer de Stack:**
    *   **Name:** Geef uw stack een naam (bijv. `joulejournal`).
    *   **Repository:** Selecteer "Repository" als de bouwmethode.
    *   **Repository URL:** Plak de URL van deze GitHub repository.
    *   **Compose path:** Zorg ervoor dat het pad is ingesteld op `docker-compose.yml`.
4.  **Omgevingsvariabelen (Environment Variables):**
    Voeg de volgende omgevingsvariabelen toe. Deze zijn essentieel voor de databaseverbinding. Klik op "Add environment variable" voor elke variabele.
    *   `POSTGRES_USER`: De gebruikersnaam voor uw database (bijv. `joule`).
    *   `POSTGRES_PASSWORD`: Een sterk wachtwoord voor de databasegebruiker.
    *   `POSTGRES_DB`: De naam van de database (bijv. `joulejournal`).
5.  **Implementeer de Stack:** Klik op "Deploy the stack" en wacht tot Portainer de images heeft gebouwd en de containers heeft gestart.
6.  **Database Setup:** De database migraties en het seeden van de data gebeurt nu automatisch wanneer de `backend` container start.
7.  **Bekijk de Applicatie:** Uw applicatie is nu beschikbaar op de hostnaam van uw Portainer-server op poort 8000 (bijv. `http://<uw-server-ip>:8000`).

## Lokale Installatie en Opstarten

Volg deze stappen om de applicatie lokaal op te zetten en te draaien.

1.  **Clone de Repository**
    ```bash
    git clone <repository_url>
    cd joulejournal-project
    ```

2.  **Maak een `.env` bestand**
    Maak een bestand met de naam `.env` in de root van het project en voeg de volgende variabelen toe:
    ```
    POSTGRES_USER=joule
    POSTGRES_PASSWORD=eensterkwachtwoord
    POSTGRES_DB=joulejournal
    ```

3.  **Bouw en Start de Applicatie**
    Dit commando bouwt de Docker-image voor de backend en start alle services (backend en database) die zijn gedefinieerd in `docker-compose.yml`.
    ```bash
    docker-compose up --build
    ```
    *Wacht tot de output aangeeft dat de Uvicorn-server draait.*

4.  **Database Setup**
    De database migraties en het seeden van de data gebeurt nu automatisch wanneer de `backend` container start. U hoeft geen aparte commando's meer uit te voeren.

5.  **Bekijk de Applicatie**
    Zodra de backend draait, is de applicatie volledig ingesteld.
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
