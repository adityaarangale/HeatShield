# Heat Shield — Personal Heat Risk Advisor (Citizen-Facing Module)

**SIH Problem Code:** SIH26083 | **Ministry:** Ministry of Earth Sciences (MoES)  
**Deployment Pilot:** Chandrapur District, Maharashtra

---

## 1. Executive Summary

While the **Heat Shield Municipal Dashboard** (`index.html`) equips district collectors and disaster management authorities with spatial GIS risk heatmaps, ward-level resource allocation, and mass broadcast alerts, the **Personal Heat Risk Advisor** (`advisor.html`) translates high-level biometeorological intelligence directly to the individual citizen.

Presented with a consumer weather-app interface, a citizen receives an individualized assessment of their thermal stress risk. An elderly citizen, an open-cast mining laborer, a pregnant woman, or an office worker in the same district face vastly divergent health outcomes under identical ambient dry-bulb temperatures. This module personalizes those risks and delivers life-saving, targeted precautions.

---

## 2. System Architecture & Connection to Existing Dashboard

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    HEAT SHIELD FULL SYSTEM TOPOLOGY                     │
├───────────────────────────────────┬─────────────────────────────────────┤
│   MUNICIPAL CONTROL ROOM          │   CITIZEN PERSONAL ADVISOR          │
│   (Administrator Portal)          │   (Consumer Weather App)            │
│   • File: index.html              │   • Files: advisor.html, .css, .js  │
│   • GIS Ward Heatmap (Leaflet)    │   • Geolocation / Taluka Dropdown   │
│   • 8 Talukas Spatial Intelligence│   • Personalized Risk Hero Card     │
│   • Batch Fast2SMS/Twilio Alerts  │   • CDC/OSHA Multipliers Breakdown  │
│   • Heat Action Plan (HAP) KPIs   │   • Nearest Cooling Shelter Locator │
└─────────────────┬─────────────────┴──────────────────┬──────────────────┘
                  │                                    │
                  │   HTTP REST API (Port 8000)        │
                  ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  FASTAPI BACKEND SERVICE (backend/)                     │
├─────────────────────────────────────────────────────────────────────────┤
│ • main.py: ASGI Service Entrypoint & CORS configuration                 │
│ • logic.py: Rothfusz Heat Index, Australian BOM WBGT, HTSI Algorithm   │
│ • personal_risk.py: Citizen Biometeorological Multiplier Engine         │
│ • data/wards.json: 8 Chandrapur Taluka Demographics & 5-Day Forecasts  │
│ • Cooling Relief Infrastructure: 10 Emergency Shelters & Mobile Vans    │
└─────────────────────────────────────────────────────────────────────────┘
```

Both portals share the same FastAPI backend (`http://127.0.0.1:8000`), ensuring a single source of mathematical truth across municipal administration and citizen advisories.

---

## 3. Biometeorological Personal Risk Scoring Methodology

Standard municipal warnings rely on ambient dry-bulb temperature, which fails to account for human thermoregulatory limits under humidity, direct solar radiation, and internal metabolic heat generation.

The Personal Risk Advisor calculates an individualized score:

$$\text{Personal Risk Score} = \min\left(100.0, \max\left(0.0, \text{Base Ward Score} \times M_{\text{composite}}\right)\right)$$

Where $M_{\text{composite}}$ is the product of grounded heuristic multipliers:

$$M_{\text{composite}} = M_{\text{age}} \times M_{\text{gender}} \times M_{\text{occupation}} \times M_{\text{health}} \times M_{\text{activity}}$$

### Multiplier Factors & Scientific Basis

| Category | Input Option | Multiplier | Percentage | Standard Citation & Physiological Justification |
| :--- | :--- | :---: | :---: | :--- |
| **Age Group** | **Elderly (65+)** | `1.20x` | $+20\%$ | **CDC Heat & Older Adults / NWS**: Diminished sweat gland output, delayed skin vasodilation, blunted thirst perception, and reduced cardiac reserve. |
| | **Child (<12)** | `1.15x` | $+15\%$ | **American Academy of Pediatrics (AAP)**: Greater surface-area-to-mass ratio accelerates dry-bulb heat absorption; immature thermoregulation leads to faster core hyperthermia. |
| | **Adult (12–64)** | `1.00x` | $0\%$ | Baseline adult human thermoregulatory profile. |
| **Gender** | **Female** | `1.05x` | $+5\%$ | **Int. Journal of Biometeorology**: Applied when relative humidity $\ge 40\%$ due to lower mean sweating rate per unit skin surface in humid conditions. |
| | **Male / Other** | `1.00x` | $0\%$ | Baseline physiological thermoregulatory profile under dry radiant heat. |
| **Occupation / Exposure** | **Outdoor Manual Laborer** | `1.25x` | $+25\%$ | **OSHA Heat Illness Prevention Standard / ACGIH**: Sustained direct solar irradiance (850–950 W/m²), continuous high metabolic rate (300–450 W), reflective surface albedo (coal/concrete), and heat-trapping PPE. |
| | **Outdoor Non-Manual** | `1.15x` | $+15\%$ | **OSHA Transit Guidance**: Sustained ambient exposure (delivery, vendors, auto drivers) with intermittent access to shade. |
| | **Indoor / Office** | `0.90x` | $-10\%$ | **ASHRAE Standard 55**: Shielded from radiant solar flux; structural insulation and fan circulation assist convective cooling. |
| | **Student / Home** | `0.95x` | $-5\%$ | **NDMA School Heat Guidelines**: Substantial indoor shelter with brief commute exposure. |
| **Health Conditions** | **Cardiovascular / Asthma** | `1.15x` | $+15\%$ | **American Heart Association (AHA)**: Peripheral vasodilation triples cardiac output demand, dramatically increasing risk of heat syncope, myocardial ischemia, and respiratory distress. |
| | **Pregnancy** | `1.15x` | $+15\%$ | **ACOG Clinical Guidance**: Elevated basal metabolic rate, increased risk of dehydration-induced contractions, and maternal hyperthermia risks. |
| | **Compound Cap** | $\le 1.30\text{x}$ | Max $+30\%$ | Compound cap prevents unrealistic inflation for co-occurring risk flags. |
| **Activity Level** | **Heavy Exertion** | `1.20x` | $+20\%$ | **ISO 7243 / ACGIH Heat Stress Index**: Internal metabolic heat generation exceeds 350–500 W, accelerating core temperature rise to $>38.5^\circ\text{C}$ in $<45$ min. |
| | **Light Activity** | `1.05x` | $+5\%$ | **ISO 7243 Class 1**: Moderate metabolic heat (~150–200 W) requiring regular fluid intake. |
| | **Resting / Seated** | `0.95x` | $-5\%$ | **ISO 7243 Baseline**: Basal metabolic rate (~100 W) minimizing internal heat buildup. |

### Personal Risk Bands

| Personal Score | Risk Band | Color | Actionable Summary |
| :---: | :---: | :---: | :--- |
| **$\ge 70.0$** | **Extreme** | 🔴 Red | Mandatory cessation of physical labor; seek air-conditioned shelter; hydrate with 750ml–1L/hr ORS. |
| **$50.0 - 69.9$** | **Danger** | 🟠 Orange | High risk of heat exhaustion/cramps; 20m rest per 40m work; avoid midday exposure (11:30 AM–4:30 PM). |
| **$30.0 - 49.9$** | **Caution** | 🟡 Yellow | Moderate solar stress; wear loose cotton; continuous hydration every 30–40 min. |
| **$< 30.0$** | **Safe** | 🟢 Green | Normal weather parameters; maintain standard hydration (2.0–2.5 L/day). |

---

## 4. API Endpoints Reference

All endpoints are hosted by FastAPI and fully documented in Swagger UI at `http://127.0.0.1:8000/docs`:

### `GET /api/ward/{ward_id}/current`
Returns real-time meteorological metrics, WBGT, Heat Index, and baseline risk for a specific ward.

### `GET /api/ward/{ward_id}/forecast`
Returns the 3–5 day predictive meteorological and thermal risk forecast for a ward.

### `GET /api/cooling-shelters`
Returns the list of 10 Chandrapur emergency cooling shelters and mobile hydration relief vans with coordinates, capacity, and amenities.

### `POST /api/personal-risk`
Calculates an individual citizen's personalized thermal risk score, factor breakdown, tailored precautions, and finds the nearest relief shelter.
```json
{
  "ward_id": "CHA_001",
  "age_group": "elderly",
  "gender": "female",
  "occupation_type": "outdoor_manual",
  "health_flags": ["cardiovascular_respiratory"],
  "activity_level": "heavy_exertion",
  "user_lat": 19.9615,
  "user_lon": 79.2961
}
```

### `POST /api/personal-risk/alert`
Citizen-facing one-tap family emergency SMS dispatch via Fast2SMS / Twilio (with automatic simulated fallback if credentials are unset).

---

## 5. How to Run Both Applications Together

### Step 1: Start the FastAPI Backend
In your terminal:
```bash
cd backend
python main.py
```
*Runs on `http://127.0.0.1:8000` (Interactive API docs at `http://127.0.0.1:8000/docs`).*

### Step 2: Serve the Frontend
In another terminal at the project root:
```bash
python -m http.server 3000
```

### Step 3: Access the Applications
- **Citizen Personal Advisor**: Open [`http://localhost:3000/advisor.html`](http://localhost:3000/advisor.html) (or double-click `advisor.html`).
- **Municipal Command Center**: Open [`http://localhost:3000/index.html`](http://localhost:3000/index.html).

Both interfaces contain seamless two-way cross-navigation buttons:
- On `index.html`: Click **"👤 Citizen View ↗"** in the top bar or sidebar.
- On `advisor.html`: Click **"🏛️ Control Room ↗"** in the top bar.

---

## 6. Offline / Standalone Fallback Resilience

During judging or field deployments without active internet or local server execution:
1. `advisor.js` contains a built-in mathematical engine that executes the identical Rothfusz, Australian BOM, and CDC multiplier algorithms in the browser.
2. If the FastAPI backend is offline, the status pill automatically switches to **"Offline Standalone Engine Active"** without throwing blocking exceptions.
3. Citizens can still select their profile, inspect their personalized risk score, view the 3-day forecast, and locate nearest cooling centers completely offline.
