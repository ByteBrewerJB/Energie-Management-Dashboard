# Frontend Aanbevelingen

Dit document beschrijft de noodzakelijke aanpassingen aan de frontend (HTML-templates en JavaScript) om de vernieuwde backend-structuur te ondersteunen. De backend is nu gebaseerd op een centraal `MonthlyJournal` model, wat leidt tot een eenvoudigere en krachtigere API.

## 1. Algemene Structuur

De frontend kan worden opgesplitst in twee hoofdonderdelen:
1.  **Beheer Pagina (`admin.html`):** Voor het eenmalig instellen van installaties en auto's.
2.  **Dashboard (`index.html`):** Voor het maandelijks invoeren van het journaal en het bekijken van de resultaten.

---

## 2. Aanpassingen aan `admin.html` (Beheer Pagina)

Op deze pagina moeten formulieren en lijsten komen om de basisgegevens te beheren.

### 2.1. Zonnepanelen Installatie
*   **Doel:** De gegevens van de zonnepanelen-installatie beheren. Omdat er maar één is, is een "create" en "update" formulier voldoende.
*   **API Endpoints:** `POST /api/solar_panels` en `PUT /api/solar_panels/{id}`.
*   **Formuliervelden:**
    *   `name` (tekst, bijv. "Zonnepanelen Dak Zuid")
    *   `purchase_date` (datum)
    *   `purchase_cost_eur` (getal)
    *   `total_power_wp` (getal)

### 2.2. Batterij Installatie
*   **Doel:** De gegevens van de batterij-installatie beheren.
*   **API Endpoints:** `POST /api/batteries` en `PUT /api/batteries/{id}`.
*   **Formuliervelden:**
    *   `name` (tekst, bijv. "Thuisbatterij")
    *   `purchase_date` (datum)
    *   `purchase_cost_eur` (getal)
    *   `capacity_kwh` (getal)

### 2.3. Elektrische Auto's
*   **Doel:** Meerdere auto's kunnen toevoegen, bekijken en verwijderen.
*   **API Endpoints:** `POST /api/cars`, `GET /api/cars`, `DELETE /api/cars/{id}`.
*   **JavaScript Logica:**
    1.  Bij het laden van de pagina, roep `GET /api/cars` aan om de lijst van bestaande auto's op te halen en weer te geven.
    2.  Maak een formulier om een nieuwe auto toe te voegen.
*   **Formuliervelden:**
    *   `name` (tekst, bijv. "Tesla Model 3" of kenteken)
    *   `reimbursement_rate_eur_per_kwh` (getal, bijv. 0.21)

---

## 3. Aanpassingen aan `index.html` (Dashboard)

Dit is de hoofdpagina waar de gebruiker de meeste interactie zal hebben.

### 3.1. Het Maandjournaal Formulier
*   **Doel:** Een groot, intuïtief formulier waarmee de gebruiker alle maandelijkse gegevens in één keer kan invoeren.
*   **API Endpoint:** `POST /api/journal/`.
*   **Formuliervelden:**
    *   `year` (getal, bijv. 2024)
    *   `month` (getal, 1-12)
    *   **Netverbruik (kWh):**
        *   `grid_consumption_low_kwh`
        *   `grid_consumption_high_kwh`
        *   `grid_feed_in_low_kwh`
        *   `grid_feed_in_high_kwh`
    *   **Tarieven (€/kWh):**
        *   `consumption_price_low_eur_kwh`
        *   `consumption_price_high_eur_kwh`
        *   `feed_in_tariff_low_eur_kwh`
        *   `feed_in_tariff_high_eur_kwh`
    *   **Interne Productie & Verbruik:**
        *   `solar_production_kwh`
        *   `battery_charge_kwh`
        *   `battery_discharge_kwh`
    *   **Financieel:**
        *   `monthly_prepayment_eur` (Voorschot)
    *   **Autogebruik (Dynamisch):**
        *   De JavaScript-code moet `GET /api/cars` aanroepen en voor elke auto een inputveld genereren: `total_charged_kwh` met de `car_id`.
        *   De data voor de auto's moet als een lijst van objecten (`car_entries`) meegestuurd worden in de JSON-payload. Voorbeeld: `car_entries: [{car_id: 1, total_charged_kwh: 150.5}, {car_id: 2, total_charged_kwh: 200.0}]`.

### 3.2. Weergave van Resultaten
*   **Doel:** De resultaten van een geselecteerd maandjournaal tonen.
*   **API Endpoint:** `GET /api/journal/{year}/{month}`.
*   **JavaScript Logica:**
    1.  Voeg een selector (bijv. dropdowns voor jaar en maand) toe waarmee de gebruiker een journaal kan kiezen.
    2.  Wanneer een selectie wordt gemaakt, roep het endpoint aan.
    3.  De API retourneert een `JournalWithStatement` object. Gebruik de `financial_statement` property om de berekende resultaten weer te geven.
*   **Te Tonen Velden (uit `financial_statement`):**
    *   Totale verbruikskosten: `total_consumption_cost_eur`
    *   Totale terugleveropbrengst: `total_feed_in_revenue_eur`
    *   Netto energiekosten: `net_energy_cost_eur`
    *   Totaal gedeclareerd autogebruik: `total_car_reimbursement_eur`
    *   **Eindafrekening van de maand:** `final_settlement_eur` (dit is het belangrijkste getal: wat je netto betaalt of terugkrijgt).

---

## 4. Aanpassingen aan `static/js/main.js`

De JavaScript-code moet worden bijgewerkt om de bovenstaande logica te implementeren.

*   **Functie `loadCars()`:** Een functie die `GET /api/cars` aanroept en de resultaten gebruikt om de autolijst in `admin.html` en de dynamische velden in het journaalformulier op `index.html` te bouwen.
*   **Functie `submitJournal(event)`:** Een event handler voor het journaalformulier. Deze moet:
    1.  `event.preventDefault()` aanroepen.
    2.  Alle formulierdata verzamelen en omzetten naar de correcte JSON-structuur (zoals vereist door `MonthlyJournalCreate`). Let vooral op de `car_entries` lijst.
    3.  Een `POST` request naar `/api/journal/` sturen met de JSON-payload.
    4.  Feedback geven aan de gebruiker (succes of foutmelding).
*   **Functie `loadJournalStatement()`:** Een functie die wordt aangeroepen wanneer de gebruiker een jaar/maand selecteert. Deze moet:
    1.  De `GET` request naar `/api/journal/{year}/{month}` uitvoeren.
    2.  De response verwerken en de HTML-elementen voor de resultaten bijwerken.

Door deze aanbevelingen te volgen, kan de frontend naadloos aansluiten op de sterk verbeterde backend.
