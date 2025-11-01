# Energie-management webapp — Totale Specificatie + Self-Hosted Deploy (2025)

Deze specificatie beschrijft de functionele en technische eisen voor de energie-management webapp in combinatie met de self-hosted Docker/Portainer instructies. De inhoud weerspiegelt de volledige blauwdruk voor het systeem, gebaseerd op de meest recente 2025 datasets en infrastructuurvereisten.

## Inhoud

0. [Samenvatting & scope](#0-samenvatting--scope)
1. [Gebruikers & rollen](#1-gebruikers--rollen)
2. [Systeemoverzicht](#2-systeemoverzicht)
3. [Databronnen & entiteiten](#3-databronnen--entiteiten)
4. [Invoer (blauwe velden)](#4-invoer-blauwe-velden)
5. [Kern-berekeningen & definities](#5-kern-berekeningen--definities)
6. [Datamodel (ERD) & JSON-schemas](#6-datamodel-erd--json-schemas)
7. [API-specificatie (REST)](#7-api-specificatie-rest)
8. [UI/UX & toegankelijkheid](#8-uiux--toegankelijkheid)
9. [Validatie & business-regels](#9-validatie--business-regels)
10. [Integraties](#10-integraties)
11. [Beveiliging & privacy](#11-beveiliging--privacy)
12. [Prestaties & schaalbaarheid](#12-prestaties--schaalbaarheid)
13. [Observability & datakwaliteit](#13-observability--datakwaliteit)
14. [Teststrategie & acceptatiecriteria](#14-teststrategie--acceptatiecriteria)
15. [Import/Export (Excel mapping 2025)](#15-importexport-excel-mapping-2025)
16. [Optimalisaties (algoritmen)](#16-optimalisaties-algoritmen)
17. [Roadmap](#17-roadmap)
18. [Database-schema (DDL)](#18-database-schema-ddl)
19. [Acceptatie-checklist](#19-acceptatie-checklist)
20. [Self-Hosted Docker/Portainer](#20-self-hosted-dockerportainer)
21. [Voorbeeld Codex/LLM-prompts](#21-voorbeeld-codexllm-prompts)

---

## 0) Samenvatting & scope

* **Doel**: één webapp die **verbruik, opwek, tarieven, BTW/heffingen, CO₂-impact, investeringen** (PV/batterij/EV) en **automatisering** samenbrengt voor huishouden of MKB.
* **Datasets 2025**: maandelijkse verbruiksregels, PV-opwek per maand, tariefstructuur (vast/dynamisch), investeringsvoorstellen.
* **Resultaat**: dashboard, rapportages, RoI-modules, optimalisaties (laad/ontlaad, load-shifting), exports.
* **Bron-excel**: tabbladen zoals *Awesems 2025*, *Solar Power 2025*, *Solar Investment*.

---

## 1) Gebruikers & rollen

* **Beheerder**: alle rechten, configuratie, integraties, gebruikersbeheer.
* **Gebruiker**: eigen site(s) beheren, data inzien, exporteren, regels instellen.
* **Lezer**: alleen lezen/rapportage.
* **Installateur/Partner (optioneel)**: asset-registratie en health-checks voor toegewezen sites.
  **RBAC** resource-scoped (tenant → site → asset), **auditlog** op wijzigingen.

---

## 2) Systeemoverzicht

* **Frontend**: Web (SPA/SSR), PWA-capabel, i18n (NL/EN).
* **Backend**: REST/GraphQL API, WebSocket voor live, jobqueue voor berekening.
* **Data**: time-series DB, relationele DB (config/metadata), object storage (exports).
* **Integraties**: slimme meter/DSMR, omvormers, EV-laders (OCPP), dag-vooruit prijzen, weerdata, CO₂-intensiteit.
* **Edge-gateway (optioneel)**: lokaal verzamelen via MQTT/Modbus/OpenTherm; buffered upload.

---

## 3) Databronnen & entiteiten

* **Site** (locatie en aansluiting).
* **Meter** (import/teruglevering).
* **PV-systeem** (panelen, omvormer).
* **Batterij** (capaciteit, rendement).
* **EV-lader/EV** (vermogen, accu, vertrektijden).
* **Tariefplan** (vast/dynamisch, BTW, heffingen).
* **Tijdreeksen**: consumptie/opwek/prijs/CO₂/weer.
* **Financieel**: factuurregels, budgetten.
* **Investeringen**: voorstellen + berekende NPV/IRR/LCOS.
* **Automatisering**: regels met triggers, condities, acties.

---

## 4) Invoer (blauwe velden)

**Formaat**: `id` – label [type, eenheid] (validatie) {voorbeeld}

### 4.1 Site & aansluiting

* 🔷 `site.name` – Site naam [string] (1–100) {“Woning Rivierdijk”}
* 🔷 `site.address` – Adres [string] {“Voorbeeldstraat 12, 1234 AB Stad”}
* 🔷 `site.ean_electricity` – EAN elektriciteit [string, 18] (regex EAN)
* 🔷 `site.phases` – Aansluiting [enum: `1P`,`3P`]
* 🔷 `site.main_fuse_amps` – Hoofdzekering [int, A] (6–80) {25}
* 🔷 `site.timezone` – Tijdzone [IANA] {“Europe/Amsterdam”}
* 🔷 `site.currency` – Valuta [enum] {EUR}

### 4.2 Gebruiker

* 🔷 `account.display_name` – Naam [string] {“Jimmy”}
* 🔷 `account.email` – E-mail [email]
* 🔷 `account.locale` – Taal [enum: `nl-NL`,`en-GB`]

### 4.3 Tariefplan & BTW/Heffingen

* 🔷 `tariff.plan_name` – Tariefplan [string] {“Variabel 2025”}
* 🔷 `tariff.type` – Type [enum: `vast`,`dynamisch_day_ahead`]
* 🔷 `tariff.vat_rate` – BTW % [decimal, 0–100] {21}
* 🔷 `tariff.fix_per_month` – Vaste kosten p/m [€] {7.50}
* 🔷 `tariff.grid_fee_per_kwh` – Netwerkkosten/kWh [€/kWh]
* 🔷 `tariff.energy_tax_per_kwh` – Energiebelasting/kWh [€/kWh]
* 🔷 `tariff.feed_in_price_per_kwh` – Terugleververgoeding [€/kWh]
* 🔷 `tariff.duo_rate_enabled` – Enkel/Dubbel tarief [bool]
* 🔷 `tariff.low_rate_hours` – Laag tarief uren [cron-achtig] {“23:00–07:00 + weekend”}
* 🔷 `tariff.dynamic_source` – Bron [enum: `ENTSOE`,`EPEX`,`SupplierAPI`,`CSV`]
* 🔷 `tariff.supplier_name` – Leverancier [string]

### 4.4 Assets (PV, batterij, EV, warmtepomp)

**PV-systeem**

* 🔷 `pv.manufacturer` – Paneel merk [string]
* 🔷 `pv.panel_count` – Aantal panelen [int, 1–200]
* 🔷 `pv.panel_wp` – Wp per paneel [int] {435}
* 🔷 `pv.inverter_brand` – Omvormer [string]
* 🔷 `pv.inverter_count` – Aantal omvormers [int]
* 🔷 `pv.orientation` – Oriëntatie [enum: `Zuid`,`Oost`,`West`,`O/W`,`Z/O/W`]
* 🔷 `pv.tilt_deg` – Hellingshoek [int, °, 0–60]
* 🔷 `pv.install_date` – Installatiedatum [date]

**Batterij**

* 🔷 `battery.capacity_kwh` – Capaciteit [kWh]
* 🔷 `battery.max_charge_kw` – Max laden [kW]
* 🔷 `battery.max_discharge_kw` – Max ontladen [kW]
* 🔷 `battery.roundtrip_eff` – Rondrendement [%] {90–97}
* 🔷 `battery.min_soc` – Min SoC [%] {10}
* 🔷 `battery.max_soc` – Max SoC [%] {90}

**EV-lader/EV**

* 🔷 `evcharger.brand` – Lader merk [string]
* 🔷 `evcharger.max_kw` – Max laadvermogen [kW]
* 🔷 `ev.vehicle_battery_kwh` – EV accu [kWh]
* 🔷 `ev.preferred_departure` – Gewenst vertrektijdstip [time]
* 🔷 `ev.required_soc_at_departure` – Vereiste SoC [%]

**Warmtepomp (optioneel)**

* 🔷 `hp.brand` – Merk [string]
* 🔷 `hp.cop_nominal` – COP nominaal [decimal]
* 🔷 `hp.has_buffer` – Buffervat [bool]

### 4.5 Maanddata 2025 (match *Awesems 2025*)

Per maandrecord:

* 🔷 `m.month` – Maand [1–12]
* 🔷 `m.kwh_total` – Verbruik kWh [decimal]
* 🔷 `m.price_energy_per_kwh` – Energieprijs €/kWh **excl. BTW** [decimal]
* 🔷 `m.feed_in_kwh` – Teruglevering kWh [decimal]
* 🔷 `m.kwh_house` – Verbruik huis kWh [decimal]
* 🔷 `m.kwh_ev` – Verbruik auto kWh [decimal]
* 🔷 `m.kwh_pv_self_used` – Zelfverbruik PV kWh [decimal]
* 🔷 `m.kwh_pv_total` – Totale PV opwek kWh [decimal]
* 🔷 `m.notes` – Notities [string]
  **⚙️** `m.total_cost_ex_vat`, `m.total_cost_inc_vat`, `m.cost_breakdown` worden berekend.

### 4.6 PV-opwek 2025 (match *Solar Power 2025*)

* 🔷 `pv_2025.jan … dec` – Opwek per maand [kWh]
* 🔷 `pv_2025.annual_expected` – Jaarverwachting [kWh] (optioneel)

### 4.7 Investeringen (match *Solar Investment*)

Per voorstel:

* 🔷 `inv.supplier` – Leverancier [string]
* 🔷 `inv.panel_count` – Aantal panelen [int]
* 🔷 `inv.panel_type` – Paneel type [string]
* 🔷 `inv.total_wp` – Totaal Wp [int]
* 🔷 `inv.annual_kwh` – Jaaropbrengst [kWh]
* 🔷 `inv.inverter` – Omvormer [string]
* 🔷 `inv.total_cost_eur` – Totaalkosten [€]
* 🔷 `inv.price_per_panel_eur` – Prijs/paneel [€]
* 🔷 `inv.savings_first_year_eur` – Besparing 1e jaar [€]
* 🔷 `inv.payback_years` – Terugverdientijd [jaar]
  **⚙️** `inv.npv`, `inv.irr`, `inv.lcos` worden berekend.

### 4.8 CO₂-parameters

* 🔷 `co2.grid_intensity_source` – Bron [enum: `ENTSOE`,`Supplier`,`Manual`]
* 🔷 `co2.grid_intensity_avg` – Gem. CO₂ g/kWh [int]
* 🔷 `co2.pv_embodied_kg` – Geïncorporeerde CO₂ PV [kg/kWp] (afschrijving)
  **⚙️** CO₂ per maand/jaar wordt berekend.

### 4.9 Budget & doelen

* 🔷 `budget.monthly_eur` – Maandbudget [€]
* 🔷 `goal.self_consumption_pct` – Doel zelfverbruik [%]
* 🔷 `goal.autarky_pct` – Doel autonomie [%]

### 4.10 Automatisering

* 🔷 `rule.name` – Naam [string]
* 🔷 `rule.trigger` – Trigger [enum: `price_below`,`price_above`,`co2_below`,`time`,`soc_below`,`soc_above`]
* 🔷 `rule.condition` – Voorwaarde [expression]
* 🔷 `rule.action` – Actie [enum: `charge_battery`,`discharge_battery`,`start_ev_charge`,`stop_ev_charge`,`heat_boost`]
* 🔷 `rule.schedule_window` – Tijdvenster [time range]
* 🔷 `rule.max_cycles_per_day` – Max cycli [int]

---

## 5) Kern-berekeningen & definities

**Excl. BTW tenzij anders vermeld.**

1. **Totale kosten maand (excl. BTW)**
   `cost_ex_vat = (kwh_from_grid * (energy_price + energy_tax + grid_fee)) + fixed_monthly_fee`

2. **BTW**
   `vat_amount = cost_ex_vat * vat_rate / 100`

3. **Totale kosten (incl. BTW)**
   `cost_inc_vat = cost_ex_vat + vat_amount - feed_in_revenue_inc_vat`

4. **Terugleververgoeding**
   `feed_in_revenue_ex_vat = feed_in_kwh * feed_in_price_per_kwh`
   `feed_in_revenue_inc_vat = feed_in_revenue_ex_vat * (1 + vat_rate/100)` *(indien van toepassing)*

5. **Zelfverbruik en Autarkie**
   `self_consumption_kwh = kwh_pv_self_used`
   `self_consumption_pct = self_consumption_kwh / kwh_pv_total`
   `autarky_pct = (kwh_pv_self_used + battery_discharge_used_locally) / total_site_consumption_kwh`

6. **Batterij rondtrip**
   `usable_kwh = capacity_kwh * (max_soc - min_soc) / 100`
   `roundtrip_loss = charged_kwh * (1 - roundtrip_eff/100)`

7. **CO₂**
   `co2_month = (grid_kwh * co2_grid_intensity) - (export_kwh * co2_grid_intensity)`
   *(optioneel: embodied PV uitsmeren over levensduur)*

8. **Dynamisch tarief (day-ahead)**
   Per uur: `cost_hour = consumption_hour_kwh * (price_hour + taxes + grid_fee)`
   Maand = som van uren.

9. **RoI**
   `simple_payback = total_cost / annual_savings`
   `NPV` met discontovoet `r`, horizon `n` (15–25 jaar).
   `IRR` iteratief.
   `LCOS = (capex + opex_pv) / lifetime_kwh`

---

## 6) Datamodel (ERD) & JSON-schemas

**ERD (tekstueel)**

* **Tenant** 1—N **Site**
* **Site** 1—N **Asset** (`meter`,`pv`,`battery`,`evcharger`,`heatpump`)
* **Site** 1—N **TariffPlan** 1—N **TariffPeriod**
* **Site** 1—N **Reading** (time-series: `import`,`export`,`pv`,`battery_charge`,`battery_discharge`,`ev`)
* **Site** 1—N **PricePoint** (uurtarieven)
* **Site** 1—N **MonthlySummary**
* **Site** 1—N **InvestmentProposal**
* **Site** 1—N **AutomationRule**
* **AuditLog** op mutaties

**Voorbeeld `MonthlySummary`**

```json
{
  "id": "uuid",
  "siteId": "uuid",
  "year": 2025,
  "month": 1,
  "kwh": {
    "import": 524.06,
    "export": 120.0,
    "pv_total": 714.5,
    "pv_self_used": 400.0,
    "ev": 180.0,
    "house": 344.0
  },
  "cost": {
    "exVat": 163.41,
    "vat": 34.32,
    "incVat": 197.73,
    "feedInExVat": 18.00,
    "feedInIncVat": 21.78
  },
  "co2": {
    "gridIntensity_g_per_kwh": 280,
    "net_kg": 113.5
  },
  "createdAt": "2025-02-01T10:00:00Z"
}
```

**Voorbeeld `InvestmentProposal`**

```json
{
  "id": "uuid",
  "siteId": "uuid",
  "supplier": "DoWatt 15",
  "panelCount": 15,
  "panelType": "JA Solar 430W",
  "totalWp": 6525,
  "annualKwh": 6397,
  "inverter": "Growatt",
  "totalCostEur": 5900,
  "pricePerPanelEur": 393.33,
  "savingsFirstYearEur": 2139.70,
  "paybackYears": 2.76,
  "metrics": { "npv": 7120.0, "irr": 0.23, "lcos": 0.06 }
}
```

---

## 7) API-specificatie (REST)

**Auth**: OAuth2/OIDC, scopes per rol; JSON overal; idempotente PUT; ETag/If-Match.

* `POST /sites` 🔷 maak site
* `GET /sites/{id}`
* `PUT /sites/{id}` 🔷 update met **site** velden
* `POST /sites/{id}/assets` 🔷 asset registreren
* `GET /sites/{id}/readings?from=…&to=…&type=…`
* `POST /sites/{id}/readings:batch` 🔷 upload tijdreeks (CSV/JSON)
* `GET /sites/{id}/prices?from=…&to=…`
* `POST /sites/{id}/tariffs` 🔷 tariefplan aanmaken
* `GET /sites/{id}/monthly-summaries?year=2025`
* `POST /sites/{id}/investments` 🔷 voorstel opslaan
* `POST /sites/{id}/optimize` (payload: doelen, constraints)
* `GET /sites/{id}/reports/monthly?year=2025&format=pdf|xlsx`
* **Realtime**: `GET /ws` WebSocket voor live prijzen/SOC/acties
* **Webhooks**: `POST {callback}` bij rule-trigger, factuur gereed, etc.

---

## 8) UI/UX & toegankelijkheid

* **Dashboard**: kaarten *Kosten maand*, *Verbruik vs Opwek*, *PV prestatie*, *Batterij-SoC*, *CO₂ footprint*, *Budget t.o.v. realisatie*.
* **Grafieken**: dag/maand/jaar; stapelgrafiek (huis/EV/batterij), prijs-lijn; uurlijk bij dynamisch tarief.
* **Formulieren (blauw)**: Site & Tarief wizard; Maanddata 2025 bulk; Investeringen; CO₂-instellingen; Automatisering.
* **Stijlafspraak voor blauwe velden**:

  * CSS `.field--blue { background:#E6F0FF; border:1px solid #6AA0FF }` + 🔷-icoon in label.
* **Toegankelijkheid**: WCAG 2.2 AA, ARIA labels, toetsenbord-navigatie.
* **PWA**: offline read-only; achtergrond sync voor metingen.

---

## 9) Validatie & business-regels

* kWh-waarden ≥ 0; somdelen ≤ totaal.
* BTW 0–100%.
* Dubbel tarief: low/high uurblokken niet overlappen.
* Dynamische prijsreeks: exact 24 of 24×n per dag; DST-veilig.
* Batterij: `min_soc < max_soc`; vermogens ≤ aansluiting (per fase).
* Tariefplan: perioden mogen niet overlappen.

---

## 10) Integraties

* **DSMR P1**: kwartier/uurwaarden.
* **Omvormers**: Enphase/SMA/SolarEdge/Fronius.
* **EV-laden**: OCPP 1.6/2.0.1 sessies + smart charging.
* **Weer/irradiatie**: PV-verwachting; COP-inschatting warmtepomp.
* **Prijzen**: ENTSO-E/EPEX of leverancier APIs; onbalansprijzen.
* **Home Assistant**: MQTT topics → `readings` + device registry.

---

## 11) Beveiliging & privacy

* TLS 1.3, HSTS; opslag-encryptie (AES-256); secrets in vault.
* RBAC/ABAC per site; auditlog met oude/nieuwe waarden.
* DPIA-vriendelijk: dataminimalisatie, bewaartermijnen, recht op verwijdering.
* Rate-limiting, brute-force bescherming, reCAPTCHA op publieke endpoints.

---

## 12) Prestaties & schaalbaarheid

* Time-series DB (TimescaleDB/Influx) voor uurdata.
* Aggregaties via jobqueue; near-real-time.
* Paginatie, server-side filtering; compressie (gzip/br).
* Backpressure op ingest (tenant/site limieten).

---

## 13) Observability & datakwaliteit

* Metrics: ingest-lag, jobduur, p95 API-latency, error-ratio’s.
* Structured logging + trace-ids (OpenTelemetry).
* Data-kwaliteit: ontbrekende uren detecteren; outliers; reconciliatie maandtotalen vs factuur.

---

## 14) Teststrategie & acceptatiecriteria

* **Unit**: kosten/BTW/teruglevering; tijdzone/DST.
* **Integratie**: prijsimport, Excel-import, OCPP-sessies.
* **E2E**: “invoer `m.kwh_total` → dashboard update incl. BTW ≤ 1 min.”
* **Load**: 1 jaar uurlijks × 3 assets × 10k sites; backlog < 5 min.

---

## 15) Import/Export (Excel mapping 2025)

* **Import Excel** (`/imports/excel`):

  * *Awesems 2025* → `MonthlyInput[year=2025]`:
    `month,kwh_total,price_energy_per_kwh,kwh_ev,kwh_pv_total,kwh_pv_self_used,kwh_house,feed_in_kwh,notes`.
  * *Solar Power 2025* → `PVMonthly[year=2025]{jan..dec}`.
  * *Solar Investment* → `InvestmentProposal[]`.
* **Validatie**: rij/kolom + foutmelding; ontbrekende maanden aanvullen (null).
* **Export**: CSV/XLSX per maand/jaar; PDF-rapport met grafieken.

---

## 16) Optimalisaties (algoritmen)

* **Load shifting**: plan laden/ontladen bij laagste uurprijs binnen venster, onder zekeringlimiet.
* **Peak-shaving**: bewaak 1/3-fase limieten; ontladen bij piek.
* **Self-consumption max**: plan verbruik bij PV-piek.
* **CO₂-optimalisatie**: gewogen doel `kosten` vs `CO₂` via α (0–1).
* **Planner-API**: integer programming/heuristics; constraints: `power ≤ fuse * phase_count`, `soc_min/max`, `schedule_window`.

---

## 17) Roadmap

1. **v1**: Handmatige invoer (🔷), dashboard, statische tarieven, PV-tab, export.
2. **v1.1**: Dynamische prijzen + uurweergave + budgetalerts.
3. **v1.2**: Integratie Home Assistant/DSMR; auto-ingest.
4. **v1.3**: Batterij/EV planning, regels, webhooks.
5. **v2**: Investeringen uitgebreid (NPV/IRR), scenario’s, CO₂-boekhouding.
6. **v2.1**: Multi-site, partnerportaal.

---

## 18) Database-schema (DDL — schets)

```sql
create table site (
  id uuid primary key, tenant_id uuid, name text, address text,
  ean_electricity text, phases text, main_fuse_amps int,
  timezone text, currency text, created_at timestamptz
);

create table tariff_plan (
  id uuid primary key, site_id uuid references site(id),
  name text, type text, vat_rate numeric(5,2),
  fix_per_month numeric(10,2), grid_fee_per_kwh numeric(10,5),
  energy_tax_per_kwh numeric(10,5), feed_in_price_per_kwh numeric(10,5),
  duo_rate_enabled boolean, low_rate_hours text, dynamic_source text,
  supplier_name text, valid_from date, valid_to date
);

create table asset (
  id uuid primary key, site_id uuid references site(id),
  type text, brand text, meta jsonb
);

create table price_point (
  site_id uuid, ts timestamptz, price_ex_vat numeric(10,5),
  primary key (site_id, ts)
);

create table reading (
  site_id uuid, ts timestamptz, kind text, value_kwh numeric(12,5),
  meta jsonb, primary key (site_id, ts, kind)
);

create table monthly_summary (
  site_id uuid, year int, month int,
  data jsonb, primary key (site_id, year, month)
);

create table investment_proposal (
  id uuid primary key, site_id uuid references site(id),
  supplier text, panel_count int, panel_type text, total_wp int,
  annual_kwh numeric(12,2), inverter text, total_cost_eur numeric(12,2),
  price_per_panel_eur numeric(12,2), savings_first_year_eur numeric(12,2),
  payback_years numeric(6,2), metrics jsonb
);
```

---

## 19) Acceptatie-checklist (samengevoegd)

* [ ] 🔷 Alle “blauwe” formuliersecties aanwezig met client- & servervalidatie.
* [ ] ⚙️ Maandtotalen incl./excl. BTW sluiten aan op berekening (§5).
* [ ] Excel-import van de drie tabbladen werkt met duidelijke fout-rapportage.
* [ ] Budget-widget waarschuwt bij overschrijding.
* [ ] Dynamische tarieven ondersteunen DST; som per dag/maand klopt.
* [ ] Export PDF/XLSX levert dezelfde cijfers als het dashboard.
* [ ] Auditlog bevat elke wijziging aan tariefplan en maanddata.
* [ ] **Docker**: alle services `healthy`, volumes persistent, `.env` niet in git.
* [ ] **Backup**: `pg_dump`/restore getest; exports zichtbaar in storage map.
* [ ] **Security**: JWT secret sterk; HTTPS via reverse proxy; geen root-containers.

---

## 20) Self-Hosted Docker/Portainer

### 20.1 Overzicht

* **Services**: `frontend` (PWA), `api` (REST/GraphQL+WS), `worker` (jobs), `db` (PostgreSQL 16), `redis` (cache/queue).
* **Poorten**: Frontend `8080`, API `8081` (intern DB/Redis).
* **Persistente data**: `postgres_data`, `ems_storage` (exports/uploads).
* **Healthchecks** en **logging** geconfigureerd.
* **Arm64/x86_64** ondersteund bij multi-arch images.

### 20.2 Directory-structuur

```
ems/
├─ docker-compose.yml
├─ .env
├─ frontend/      # optioneel: eigen build
│  └─ Dockerfile
├─ api/           # optioneel: eigen build
│  └─ Dockerfile
└─ backup/
```

### 20.3 `.env` (voorbeeld)

```env
TZ=Europe/Amsterdam
EMS_ENV=production

API_PORT=8081
API_BASE_URL=http://api:8081
PUBLIC_API_URL=http://localhost:8081
JWT_SECRET=vervang_dit_door_een_lang_random_secret

FRONTEND_PORT=8080
VITE_API_BASE_URL=http://localhost:${API_PORT}

POSTGRES_DB=ems
POSTGRES_USER=ems
POSTGRES_PASSWORD=super_veilig_wachtwoord
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_URL=redis://redis:6379/0

SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=no-reply@example.com
SMTP_PASS=********
SMTP_FROM="EMS <no-reply@example.com>"
```

### 20.4 `docker-compose.yml` (Portainer-klaar)

```yaml
version: "3.9"

x-common-env: &common_env
  TZ: ${TZ}
  EMS_ENV: ${EMS_ENV}

x-logging: &default_logging
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"

networks:
  ems_net:

volumes:
  postgres_data:
  ems_storage:

services:
  db:
    image: postgres:16-alpine
    container_name: ems_db
    restart: unless-stopped
    environment:
      <<: *common_env
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    command: >
      postgres -c shared_buffers=256MB
               -c max_connections=200
               -c log_min_duration_statement=1000
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 10
    logging: *default_logging
    networks:
      - ems_net

  redis:
    image: redis:7-alpine
    container_name: ems_redis
    restart: unless-stopped
    command: ["redis-server", "--appendonly", "no"]
    healthcheck:
      test: ["CMD", "redis-cli", "PING"]
      interval: 10s
      timeout: 5s
      retries: 10
    logging: *default_logging
    networks:
      - ems_net

  api:
    image: ghcr.io/your-org/ems-api:latest
    container_name: ems_api
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      <<: *common_env
      PORT: ${API_PORT}
      DATABASE_URL: postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
      REDIS_URL: ${REDIS_URL}
      JWT_SECRET: ${JWT_SECRET}
      SMTP_HOST: ${SMTP_HOST}
      SMTP_PORT: ${SMTP_PORT}
      SMTP_USER: ${SMTP_USER}
      SMTP_PASS: ${SMTP_PASS}
      SMTP_FROM: ${SMTP_FROM}
      PUBLIC_API_URL: ${PUBLIC_API_URL}
    volumes:
      - ems_storage:/app/storage
    ports:
      - "${API_PORT}:8081"
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://localhost:8081/healthz"]
      interval: 10s
      timeout: 5s
      retries: 10
    logging: *default_logging
    networks:
      - ems_net

  worker:
    image: ghcr.io/your-org/ems-api:latest
    container_name: ems_worker
    restart: unless-stopped
    depends_on:
      api:
        condition: service_started
    environment:
      <<: *common_env
      WORKER: "true"
      DATABASE_URL: postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
      REDIS_URL: ${REDIS_URL}
    command: ["node", "dist/worker.js"]
    volumes:
      - ems_storage:/app/storage
    healthcheck:
      test: ["CMD", "bash", "-c", "test -f /app/.booted || exit 1; exit 0"]
      interval: 30s
      timeout: 5s
      retries: 5
    logging: *default_logging
    networks:
      - ems_net

  frontend:
    image: ghcr.io/your-org/ems-frontend:latest
    container_name: ems_frontend
    restart: unless-stopped
    environment:
      <<: *common_env
      VITE_API_BASE_URL: ${VITE_API_BASE_URL}
    depends_on:
      api:
        condition: service_started
    ports:
      - "${FRONTEND_PORT}:80"
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://localhost/"]
      interval: 10s
      timeout: 5s
      retries: 10
    logging: *default_logging
    networks:
      - ems_net
```

**Opstarten (CLI):**

```bash
docker compose --env-file .env up -d
```

**Portainer Stack**: *Stacks → Add stack* → plak `docker-compose.yml` → voeg `.env` variabelen toe of upload → *Deploy the stack*.

### 20.5 Backup & restore (PostgreSQL)

**Backup:**

```bash
docker exec -t ems_db pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc > backup/ems_$(date +%F).dump
```

**Restore (stop API/worker tijdelijk):**

```bash
docker stop ems_api ems_worker
docker exec -i ems_db pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists < backup/ems_YYYY-MM-DD.dump
docker start ems_api ems_worker
```

### 20.6 Dockerfiles (als je zelf wil builden)

**API (Node/TS)**

```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev

FROM node:20-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules node_modules
COPY . .
RUN npm run build && npm prune --omit=dev

FROM node:20-alpine
WORKDIR /app
ENV NODE_ENV=production
USER node
COPY --from=build /app/dist dist
COPY --from=build /app/node_modules node_modules
EXPOSE 8081
HEALTHCHECK --interval=10s --timeout=5s --retries=10 CMD wget -qO- http://localhost:8081/healthz || exit 1
CMD ["node", "dist/server.js"]
```

**Frontend (Vite → Nginx)**

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK --interval=10s --timeout=5s --retries=10 CMD wget -qO- http://localhost/ || exit 1
```

**Runtime env voor SPA**: injecteer `/env.js` met `window.__EMS__ = { API_BASE_URL: "…" }` zodat de API-URL niet hard-coded is.

### 20.7 Reverse proxy (HTTPS/hostnames, optioneel Traefik)

Traefik-labels (indicatief):

```yaml
  frontend:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.ems-frontend.rule=Host(`energy.example.com`)"
      - "traefik.http.routers.ems-frontend.entrypoints=websecure"
      - "traefik.http.routers.ems-frontend.tls.certresolver=letsencrypt"
      - "traefik.http.services.ems-frontend.loadbalancer.server.port=80"

  api:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.ems-api.rule=Host(`api.energy.example.com`)"
      - "traefik.http.routers.ems-api.entrypoints=websecure"
      - "traefik.http.routers.ems-api.tls.certresolver=letsencrypt"
      - "traefik.http.services.ems-api.loadbalancer.server.port=8081"
```

Met Nginx/Apache maak je 2 vhosts die naar `frontend:80` en `api:8081` op `ems_net` proxy’en.

### 20.8 Migraties & eerste gebruiker

* API start voert DB-migraties uit (Prisma/Knex/TypeORM: `migrate:deploy`).
* Eerste admin via CLI/seed:

```bash
docker exec -it ems_api node dist/cli.js create-admin --email admin@example.com
```

### 20.9 Health, logging, updates

* Health endpoint: `/healthz` (DB/Redis-check).
* Logs: via Portainer *Container logs*; geroteerd (10MB × 3).
* Updates: versies taggen (`:1.3.0`) of tool als Watchtower; eerst testen in staging.

### 20.10 Beveiliging (self-hosted)

* Containers **zonder root** (API/Frontend voorbeelden doen dat).
* `.env` **niet** in git; Portainer *Environment variables* of **Secrets** gebruiken.
* Sterk `JWT_SECRET`, rotatie via rolling restart.
* Toegang tot 8080/8081 beperken tot LAN of reverse proxy met HTTPS.

### 20.11 Schaalbaarheid

* `worker` replicas opschalen voor snellere aggregaties.
* `api` horizontaal schalen achter reverse proxy (JWT stateless, geen sticky).
* DB: TimescaleDB voor uurlijkse metingen (compressie/chunking).

### 20.12 Portainer stappen (kort)

1. *Stacks → Add stack*
2. Plak `docker-compose.yml`, voeg `.env` variabelen toe/upload.
3. *Deploy the stack*; wacht tot alle containers **healthy** zijn.
4. Open `http://<host>:8080` (frontend) → vul je **🔷** velden in.
5. Richt een backupproces in (cron of handmatig `pg_dump`).

---

## 21) Voorbeeld Codex/LLM-prompts

**Endpoint + validatie maandinvoer**

> “Implementeer in TypeScript/Node een REST-endpoint `POST /sites/:id/monthly-input` dat payload valideert tegen de JSON-schema’s (§6.1). Bereken `cost_ex_vat`, `vat_amount`, `cost_inc_vat` volgens §5 en voer een UPSERT uit naar `monthly_summary`. Schrijf unit-tests voor DST-dagen en negatieve invoer.”

**Excel-import mapping**

> “Maak een parser die het tabblad ‘Awesems 2025’ leest; map kolommen ‘maand’, ‘kwh’, ‘price’, ‘Verbruik - auto’, ‘Verbruik huis’, ‘Opgewekt zelf’, ‘Terugleveren’ naar respectievelijk `month`,`kwh_total`,`price_energy_per_kwh`,`kwh_ev`,`kwh_house`,`kwh_pv_self_used`,`feed_in_kwh`. Onbekende kolommen overslaan; ontbrekende maanden aanvullen met nullen.”

**Docker build & health**

> “Schrijf een GitHub Action die het `ems-api` en `ems-frontend` image bouwt (multi-arch), labels toevoegt, en publiceert naar GHCR met tags `latest` en `vx.y.z`. Valideer `docker-compose.yml` met `compose config`, en ping `/healthz` na deploy.”

---

## Bijlage A — Overzicht blauwe velden (platte lijst)

`site.*`, `account.*`, `tariff.*`, `pv.*`, `battery.*`, `evcharger.*`, `ev.*`, `hp.*`, `m.*` (alleen invoercomponenten), `pv_2025.*`, `inv.*`, `co2.*`, `budget.*`, `goal.*`, `rule.*`.

---

**Klaar.** Deze samengevoegde instructie is direct bruikbaar voor ontwerp, implementatie, self-hosting en als invoer voor een codegenerator. Volgende logische stap is het vastleggen van de JSON-schema’s in je repo en een minimal seed-dataset (2–3 maanden) om de volledige keten — import → berekening → dashboard → export — end-to-end te valideren.
