# JouleJournal - Energie Management Dashboard

Een webapplicatie voor het monitoren, analyseren en rapporteren van energieverbruik, -opwekking, kosten en de financiële Return on Investment (ROI) van een zonnepaneleninstallatie.

## Features

- **Dynamisch Dashboard:** Real-time visualisatie van uw energiegegevens.
- **Admin Panel:** Een beveiligd admin-paneel (/admin) voor het handmatig beheren van alle data (Investments, Tariffs, en Monthly Metrics).
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

## Implementatie en Setup

Volg deze stappen om de applicatie lokaal of in Portainer op te zetten.

1.  **Clone de Repository** (indien lokaal)
    ```bash
    git clone <repository_url>
    cd joulejournal-project
    ```

2.  **Configureer Omgevingsvariabelen**
    Maak een `.env` bestand in de root van het project (voor lokale setup) of voeg de variabelen toe in Portainer.

    **Database Variabelen (verplicht):**
    ```
    POSTGRES_USER=joule
    POSTGRES_PASSWORD=eensterkwachtwoord
    POSTGRES_DB=joulejournal
    ```

    **Admin Login Variabelen (verplicht):**
    Deze credentials worden gebruikt om in te loggen op het `/admin` paneel.
    ```
    ADMIN_USER=admin
    ADMIN_PASSWORD=joulejournal_admin_pass
    ```

    **Beveiligingssleutel (optioneel maar aanbevolen):**
    Wordt gebruikt voor het ondertekenen van authenticatie tokens. Als deze niet wordt opgegeven, wordt een standaardwaarde gebruikt.
    ```
    # Genereer een sterke, willekeurige string, bijvoorbeeld met: openssl rand -hex 32
    SECRET_KEY=uw_zeer_geheime_sleutel
    ```

3.  **Bouw en Start de Applicatie**
    - **Lokaal:** Voer `docker-compose up --build` uit in de projectmap.
    - **Portainer:** Maak een nieuwe "Stack", verbind deze met uw Git repository en stel het `docker-compose.yml` pad in. Wijs de omgevingsvariabelen toe en klik op "Deploy the stack".

4.  **Database Setup**
    De database migraties worden automatisch uitgevoerd wanneer de `backend` container start. **Het seeden van data gebeurt niet meer automatisch.**

5.  **Data Invoeren**
    - Ga naar `http://<uw-server-ip>:8000/admin`.
    - Log in met de `ADMIN_USER` en `ADMIN_PASSWORD` die u heeft ingesteld.
    - Voer hier uw data in voor Investeringen, Tarieven en Maandelijkse Cijfers. Zonder data zal het dashboard leeg zijn.

6.  **Bekijk de Applicatie**
    - **Frontend Dashboard:** [http://localhost:8000](http://localhost:8000)
    - **Admin Paneel:** [http://localhost:8000/admin](http://localhost:8000/admin)
    - **API Documentatie (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)

## Projectstructuur

```
.
├── app/              # Backend FastAPI applicatie
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
