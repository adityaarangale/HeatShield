import os
import math
import logging
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, status

from models import Ward, WardResponse, ForecastRiskTrendItem
from logic import (
    load_wards_dataset,
    evaluate_ward_detail,
    calculate_risk_score,
    calculate_wbgt,
    calculate_heat_index,
    calculate_apparent_temperature,
    calculate_solar_adjusted_wbgt
)

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/api", tags=["Personal Risk Advisor"])


# =====================================================================
# EMERGENCY COOLING CENTERS & RELIEF DATASET (CHANDRAPUR DISTRICT)
# =====================================================================
COOLING_SHELTERS: List[Dict[str, Any]] = [
    {
        "id": "SHELTER_CHA_01",
        "name": "Chandrapur City Hospital Cooling Hub",
        "name_mr": "चंद्रपूर शहर रुग्णालय कूलिंग हब",
        "name_hi": "चंद्रपुर नगर अस्पताल कूलिंग केंद्र",
        "ward_id": "CHA_001",
        "taluka": "Chandrapur City",
        "lat": 19.9650,
        "lon": 79.2980,
        "type": "shelter",
        "capacity": 300,
        "amenities": ["Air-conditioned recovery ward", "Cold electrolyte immersion", "ORS hydration bar", "24x7 Medical staff"],
        "desc": "Equipped with cold baths, IV fluids, air filtration, and emergency triage for heat exhaustion.",
        "desc_mr": "थंड पाण्याच्या टाक्या, सलाईन आणि वातानुकूलित सुविधेने सज्ज.",
        "phone": "+91-7172-252100"
    },
    {
        "id": "SHELTER_CHA_02",
        "name": "Gandhi Chowk Mobile Hydration Van 01",
        "name_mr": "गांधी चौक मोबाईल हायड्रेशन व्हॅन ०१",
        "name_hi": "गांधी चौक मोबाइल जल वितरण वैन ०१",
        "ward_id": "CHA_001",
        "taluka": "Chandrapur City",
        "lat": 19.9580,
        "lon": 79.2920,
        "type": "van",
        "capacity": 150,
        "amenities": ["Chilled drinking water", "Free ORS sachets", "Misting fans"],
        "desc": "Chilled ORS water dispatch for bus transit passengers and market vendors.",
        "desc_mr": "बस प्रवाशांसाठी आणि फेरीवाल्यांसाठी थंड ओआरएस पाणी वाटप.",
        "phone": "+91-7172-252101"
    },
    {
        "id": "SHELTER_BAL_01",
        "name": "Ballarpur Municipal High School Center",
        "name_mr": "बल्लारपूर पालिका हायस्कूल केंद्र",
        "name_hi": "बल्लारपुर नगर पालिका केंद्र",
        "ward_id": "CHA_002",
        "taluka": "Ballarpur",
        "lat": 19.8350,
        "lon": 79.3520,
        "type": "shelter",
        "capacity": 250,
        "amenities": ["High-capacity evaporative coolers", "Resting cots", "Continuous clean water supply"],
        "desc": "Dedicated rest center for industrial and municipal sanitation workers.",
        "desc_mr": "२५० मजुरांची क्षमता व उच्च क्षमतेचे कूलर्स उपलब्ध.",
        "phone": "+91-7172-240222"
    },
    {
        "id": "SHELTER_BAL_02",
        "name": "WCL Coal Mines Mobile Aid Van 02",
        "name_mr": "WCL खाण मोबाईल मदत व्हॅन ०२",
        "name_hi": "डब्लूसीएल खदान मोबाइल राहत वैन ०२",
        "ward_id": "CHA_002",
        "taluka": "Ballarpur",
        "lat": 19.8300,
        "lon": 79.3450,
        "type": "van",
        "capacity": 200,
        "amenities": ["Continuous cold water refills", "Ice packs", "First aid paramedics"],
        "desc": "Rapid-response hydration replenishment for open-cast pit laborers.",
        "desc_mr": "उघड्यावर काम करणाऱ्या मजुरांसाठी निरंतर पिण्याच्या पाण्याचा पुरवठा.",
        "phone": "+91-7172-240225"
    },
    {
        "id": "SHELTER_RAJ_01",
        "name": "Rajura Sub-District Hospital Cooling Center",
        "name_mr": "राजूरा उप-जिल्हा रुग्णालय शीत केंद्र",
        "name_hi": "राजूरा उप-जिला अस्पताल शीतलन केंद्र",
        "ward_id": "CHA_003",
        "taluka": "Rajura",
        "lat": 19.7820,
        "lon": 79.3690,
        "type": "shelter",
        "capacity": 180,
        "amenities": ["Climate-controlled recovery beds", "ORS dispensing", "Emergency IV access"],
        "desc": "Primary medical relief outpost serving agricultural workers and lime-kiln laborers.",
        "desc_mr": "शेतमजूर आणि वीटभट्टी मजुरांसाठी प्राथमिक वैद्यकीय आराम केंद्र.",
        "phone": "+91-7173-222110"
    },
    {
        "id": "SHELTER_WAR_01",
        "name": "Warora Rural Hospital & Shade Shelter",
        "name_mr": "वरोरा ग्रामीण रुग्णालय व सावली केंद्र",
        "name_hi": "वरोरा ग्रामीण अस्पताल एवं छाया केंद्र",
        "ward_id": "CHA_004",
        "taluka": "Warora",
        "lat": 20.2310,
        "lon": 79.0040,
        "type": "shelter",
        "capacity": 220,
        "amenities": ["Shaded recovery pavilion", "Chilled water coolers", "Doctor on call"],
        "desc": "Highway corridor relief station for transit passengers, cotton farmers, and truck crews.",
        "desc_mr": "महामार्ग प्रवासी, कापूस शेतकरी व वाहनचालकांसाठी शीतकरण केंद्र.",
        "phone": "+91-7176-282050"
    },
    {
        "id": "SHELTER_BHA_01",
        "name": "Bhadravati Community Health Relief Station",
        "name_mr": "भद्रावती समुदाय आरोग्य आराम केंद्र",
        "name_hi": "भद्रावती सामुदायिक स्वास्थ्य राहत केंद्र",
        "ward_id": "CHA_005",
        "taluka": "Bhadravati",
        "lat": 20.2180,
        "lon": 79.0520,
        "type": "shelter",
        "capacity": 160,
        "amenities": ["Air cooling", "Rest areas", "Free rehydration packs"],
        "desc": "Ordnance factory and mining fringe community heat relief facility.",
        "desc_mr": "संरक्षण फॅक्टरी आणि खाण परिसरातील कामगारांसाठी शीतकरण केंद्र.",
        "phone": "+91-7175-266100"
    },
    {
        "id": "SHELTER_BRA_01",
        "name": "Brahmapuri Sub-District Hospital Cooling Hub",
        "name_mr": "ब्रह्मपुरी उप-जिल्हा रुग्णालय कूलिंग हब",
        "name_hi": "ब्रह्मपुरी उप-जिला अस्पताल कूलिंग हब",
        "ward_id": "CHA_006",
        "taluka": "Brahmapuri",
        "lat": 20.5980,
        "lon": 79.8470,
        "type": "shelter",
        "capacity": 200,
        "amenities": ["Dedicated heat stroke ICU beds", "Cold shower facility", "ORS distribution"],
        "desc": "Serves eastern Chandrapur paddy farming communities with emergency thermal care.",
        "desc_mr": "पूर्व चंद्रपुरातील भातशेती मजुरांसाठी समर्पित उष्णता उपचार कक्ष.",
        "phone": "+91-7177-272020"
    },
    {
        "id": "SHELTER_NAG_01",
        "name": "Nagbhid Primary Health Center (PHC) Relief Post",
        "name_mr": "नागभीड प्राथमिक आरोग्य केंद्र मदत कक्ष",
        "name_hi": "नागभीड प्राथमिक स्वास्थ्य केंद्र राहत केंद्र",
        "ward_id": "CHA_007",
        "taluka": "Nagbhid Wetland",
        "lat": 20.5650,
        "lon": 79.9640,
        "type": "shelter",
        "capacity": 120,
        "amenities": ["Drinking water cooler", "ORS packs", "Shaded lawn rest areas"],
        "desc": "Wetland & agro-forestry belt relief point with natural cooling buffer assistance.",
        "desc_mr": "पाणथळ व शेती क्षेत्रातील नागरिकांसाठी आराम कक्ष.",
        "phone": "+91-7179-245010"
    },
    {
        "id": "SHELTER_MUL_01",
        "name": "Mul Rural Hospital & Forest Transit Shelter",
        "name_mr": "मुल ग्रामीण रुग्णालय व वन विश्राम कक्ष",
        "name_hi": "मुल ग्रामीण अस्पताल एवं वन विश्राम केंद्र",
        "ward_id": "CHA_008",
        "taluka": "Mul - Tadoba Forest Buffer",
        "lat": 20.0640,
        "lon": 79.6640,
        "type": "shelter",
        "capacity": 140,
        "amenities": ["Natural shade canopy", "Fresh groundwater taps", "ORS packs", "Emergency triage"],
        "desc": "Buffer sanctuary entrance rest pavilion for forest guards, farmers, and eco-tourists.",
        "desc_mr": "ताडोबा बफर क्षेत्रातील वनरक्षक, शेतकरी व पर्यटकांसाठी विश्राम कक्ष.",
        "phone": "+91-7174-230040"
    }
]


# =====================================================================
# HAVERSINE DISTANCE HELPER
# =====================================================================
def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance in kilometers between two points on the earth.
    """
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)


def find_nearest_cooling_shelter(lat: float, lon: float) -> Dict[str, Any]:
    """
    Find the closest cooling shelter or relief station to a given coordinate pair.
    """
    nearest = None
    min_dist = float("inf")
    for s in COOLING_SHELTERS:
        dist = haversine_distance(lat, lon, s["lat"], s["lon"])
        if dist < min_dist:
            min_dist = dist
            nearest = dict(s)
            nearest["distance_km"] = dist
    return nearest or dict(COOLING_SHELTERS[0], distance_km=0.0)


# =====================================================================
# REQUEST & RESPONSE PYDANTIC SCHEMAS
# =====================================================================
class PersonalRiskRequest(BaseModel):
    ward_id: str = Field(..., description="Selected or detected Ward ID (e.g., CHA_001)", examples=["CHA_001"])
    age_group: str = Field("adult", description="Age category: child (<12), adult (12-64), elderly (65+)", examples=["elderly"])
    gender: Optional[str] = Field("prefer_not_to_say", description="Gender: male, female, or prefer_not_to_say", examples=["female"])
    occupation_type: str = Field("outdoor_manual", description="Occupation: outdoor_manual, outdoor_non_manual, indoor_office, student", examples=["outdoor_manual"])
    health_flags: List[str] = Field(default_factory=list, description="Health flags: pregnant, cardiovascular_respiratory, none", examples=[["cardiovascular_respiratory"]])
    activity_level: str = Field("heavy_exertion", description="Current activity: resting, light, heavy_exertion", examples=["heavy_exertion"])
    user_lat: Optional[float] = Field(None, description="Optional current user latitude for pinpoint shelter distance", examples=[19.9615])
    user_lon: Optional[float] = Field(None, description="Optional current user longitude for pinpoint shelter distance", examples=[79.2961])


class FactorExplanation(BaseModel):
    factor_name: str
    selected_value: str
    multiplier: float
    percentage_change: str
    scientific_rationale: str
    standard_citation: str


class PersonalRiskResponse(BaseModel):
    ward_id: str
    ward_name: str
    user_location: Dict[str, Any]

    # Baseline Ward Context
    base_ward_score: float
    base_risk_band: str
    metrics: Dict[str, float]

    # Personalized Assessment
    personal_score: float
    personal_risk_band: str
    risk_level_delta: str
    personal_multiplier: float
    factor_breakdown: List[FactorExplanation]

    # Actionable Citizen Output
    precautions: List[str]
    safe_outdoor_hours: Dict[str, str]
    hydration_advice: str
    work_rest_cycle: str

    # Cooling Infrastructure
    nearest_cooling_shelter: Dict[str, Any]

    # 3-Day Personalized Trend
    personalized_forecast: List[Dict[str, Any]]


class PersonalAlertRequest(BaseModel):
    ward_id: str = Field(..., examples=["CHA_001"])
    recipient_name: Optional[str] = Field("Family Member", examples=["Father"])
    recipient_phone: str = Field(..., examples=["+919876543210"])
    sender_name: Optional[str] = Field("Your Family Member", examples=["Aditya"])
    personal_score: float = Field(..., examples=[76.5])
    personal_risk_band: str = Field(..., examples=["Extreme"])
    custom_note: Optional[str] = Field(None, examples=["I am resting at the shelter right now."])
    api_key: Optional[str] = Field(None)


class PersonalAlertResponse(BaseModel):
    status: str
    recipient_phone: str
    message: str
    provider: str


# =====================================================================
# BIOMETEOROLOGICAL PERSONAL SCORING METHODOLOGY
# =====================================================================
def compute_personal_risk_multipliers(
    age_group: str,
    gender: Optional[str],
    occupation_type: str,
    health_flags: List[str],
    activity_level: str,
    humidity_pct: float
) -> tuple[float, List[FactorExplanation]]:
    """
    Computes transparent, documented personal vulnerability multipliers
    grounded in CDC, NOAA/NWS, OSHA, and Australian BOM biometeorological standards.
    """
    factors: List[FactorExplanation] = []
    total_mult = 1.0

    # 1. Age Group Multiplier (CDC / AAP Heat Vulnerability Guidance)
    age_clean = (age_group or "adult").lower()
    if age_clean == "elderly":
        mult = 1.20
        factors.append(FactorExplanation(
            factor_name="Age Group",
            selected_value="Elderly (65+)",
            multiplier=mult,
            percentage_change="+20%",
            scientific_rationale="Diminished autonomic thermoregulatory efficiency, delayed sweating threshold, blunted thirst response, and heightened cardiovascular load under thermal stress.",
            standard_citation="CDC Extreme Heat & Older Adults Clinical Advisory / NWS Heat Safety"
        ))
    elif age_clean == "child":
        mult = 1.15
        factors.append(FactorExplanation(
            factor_name="Age Group",
            selected_value="Child (<12 yrs)",
            multiplier=mult,
            percentage_change="+15%",
            scientific_rationale="Greater body surface-area-to-mass ratio accelerates dry-bulb heat absorption; developing eccrine glands result in lower sweat rates and faster core dehydration.",
            standard_citation="American Academy of Pediatrics (AAP) Climatic Heat Stress & Children"
        ))
    else:
        mult = 1.00
        factors.append(FactorExplanation(
            factor_name="Age Group",
            selected_value="Adult (12-64 yrs)",
            multiplier=mult,
            percentage_change="Baseline (0%)",
            scientific_rationale="Standard physiological thermoregulatory capacity and baseline evaporative cooling rate.",
            standard_citation="NWS Standard Human Thermal Baseline"
        ))
    total_mult *= mult

    # 2. Gender Physiological Factor (Biometeorology Humidity Variance)
    gender_clean = (gender or "prefer_not_to_say").lower()
    if gender_clean == "female" and humidity_pct >= 40.0:
        mult = 1.05
        factors.append(FactorExplanation(
            factor_name="Gender Biometeorology",
            selected_value="Female (Humid Heat Sensitivity)",
            multiplier=mult,
            percentage_change="+5%",
            scientific_rationale="Slightly lower mean sweating rate per unit body surface in humid regimes (>40% RH) requires added vigilance for core temperature accumulation.",
            standard_citation="International Journal of Biometeorology / NIOSH Gender Heat Stress Reviews"
        ))
    else:
        mult = 1.00
        factors.append(FactorExplanation(
            factor_name="Gender Factor",
            selected_value=gender_clean.replace("_", " ").title(),
            multiplier=mult,
            percentage_change="Neutral (0%)",
            scientific_rationale="Baseline physiological thermoregulatory profile under dry radiant heat.",
            standard_citation="NIOSH Occupational Thermal Balance Standards"
        ))
    total_mult *= mult

    # 3. Occupation / Exposure Profile (OSHA Heat Illness Prevention Standard)
    occ_clean = (occupation_type or "outdoor_manual").lower()
    if occ_clean == "outdoor_manual":
        mult = 1.25
        factors.append(FactorExplanation(
            factor_name="Occupational Exposure",
            selected_value="Outdoor Manual Laborer (Construction / Mining / Farming)",
            multiplier=mult,
            percentage_change="+25%",
            scientific_rationale="Continuous exposure to direct solar irradiance (850-950 W/m²), heavy metabolic heat production (300-450 W), reflective surface albedo, and personal protective clothing heat retention.",
            standard_citation="OSHA Heat Illness Prevention Criteria (Section 1910) / ACGIH TLV for Heat Stress"
        ))
    elif occ_clean == "outdoor_non_manual":
        mult = 1.15
        factors.append(FactorExplanation(
            factor_name="Occupational Exposure",
            selected_value="Outdoor Non-Manual (Delivery / Street Vendor / Driver)",
            multiplier=mult,
            percentage_change="+15%",
            scientific_rationale="Sustained ambient radiant exposure with intermittent access to shade; vehicular and urban asphalt radiant heat magnification.",
            standard_citation="OSHA Guidance for Delivery & Transit Personnel"
        ))
    elif occ_clean == "indoor_office":
        mult = 0.90
        factors.append(FactorExplanation(
            factor_name="Occupational Exposure",
            selected_value="Indoor / Office",
            multiplier=mult,
            percentage_change="-10%",
            scientific_rationale="Structural building envelope eliminates direct solar radiant flux; mechanical ventilation and fans aid convective heat dissipation.",
            standard_citation="ASHRAE Standard 55 Thermal Environmental Conditions for Human Occupancy"
        ))
    else:  # student or home
        mult = 0.95
        factors.append(FactorExplanation(
            factor_name="Occupational Exposure",
            selected_value="Student / Home",
            multiplier=mult,
            percentage_change="-5%",
            scientific_rationale="Substantial indoor protection with moderate intermittent transit exposure.",
            standard_citation="MoES / NDMA School Heat Action Guidelines"
        ))
    total_mult *= mult

    # 4. Health Flags & Comorbidities (CDC / AHA / ACOG Clinical Guidelines)
    health_mult = 1.0
    flags_applied = []
    clean_flags = [f.lower().strip() for f in health_flags if f.strip().lower() not in ["none", ""]]

    if "cardiovascular_respiratory" in clean_flags or "heart_asthma" in clean_flags:
        health_mult += 0.15
        flags_applied.append("Cardiovascular / Respiratory Compromise")
    if "pregnant" in clean_flags:
        health_mult += 0.15
        flags_applied.append("Pregnancy (Elevated Basal Metabolic Rate)")

    # Compound cap for health multiplier
    health_mult = min(1.30, health_mult)
    if flags_applied:
        factors.append(FactorExplanation(
            factor_name="Health & Clinical Factors",
            selected_value=", ".join(flags_applied),
            multiplier=round(health_mult, 2),
            percentage_change=f"+{round((health_mult - 1.0) * 100)}%",
            scientific_rationale="Severe thermoregulation strain: peripheral vasodilation diverts cardiac output by up to 2-3x, increasing risks of heat syncope, cardiac ischemia, and acute respiratory distress.",
            standard_citation="American Heart Association (AHA) Heat Advisory / American College of Obstetricians (ACOG)"
        ))
    else:
        factors.append(FactorExplanation(
            factor_name="Health & Clinical Factors",
            selected_value="No High-Risk Comorbidities Disclosed",
            multiplier=1.00,
            percentage_change="Neutral (0%)",
            scientific_rationale="Standard physiological reserve capacity without known cardiovascular or pulmonary limitations.",
            standard_citation="CDC General Heat Safety Advisory"
        ))
    total_mult *= health_mult

    # 5. Activity Level Right Now (ISO 7243 / ACGIH Metabolic Heat Load)
    act_clean = (activity_level or "resting").lower()
    if act_clean == "heavy_exertion":
        mult = 1.20
        factors.append(FactorExplanation(
            factor_name="Physical Activity Level",
            selected_value="Heavy Exertion (Heavy Labor, Running, Cycling)",
            multiplier=mult,
            percentage_change="+20%",
            scientific_rationale="Internal metabolic heat generation exceeds 350-500 W, accelerating core body temperature ascent to >38.5°C within 30-45 minutes without aggressive cooling breaks.",
            standard_citation="ISO 7243 Ergonomics of the Thermal Environment / ACGIH Heat Stress Index"
        ))
    elif act_clean == "light":
        mult = 1.05
        factors.append(FactorExplanation(
            factor_name="Physical Activity Level",
            selected_value="Light Activity (Walking, Household Errands)",
            multiplier=mult,
            percentage_change="+5%",
            scientific_rationale="Moderate metabolic heat generation (~150-200 W) requiring regular fluid intake and intermittent shade pauses.",
            standard_citation="ISO 7243 Metabolic Rate Class 1 (Light Work)"
        ))
    else:
        mult = 0.95
        factors.append(FactorExplanation(
            factor_name="Physical Activity Level",
            selected_value="Resting / Seated",
            multiplier=mult,
            percentage_change="-5%",
            scientific_rationale="Basal metabolic rate (~100 W) minimizing internal thermal accumulation.",
            standard_citation="ISO 7243 Resting State Baseline"
        ))
    total_mult *= mult

    return round(total_mult, 3), factors


# =====================================================================
# TAILORED CITIZEN PRECAUTIONS & SCHEDULES
# =====================================================================
def generate_personalized_precautions(
    personal_score: float,
    risk_band: str,
    age_group: str,
    occupation_type: str,
    health_flags: List[str],
    activity_level: str,
    temp_c: float,
    wbgt_c: float
) -> Dict[str, Any]:
    precautions: List[str] = []
    age_clean = (age_group or "adult").lower()
    occ_clean = (occupation_type or "outdoor_manual").lower()
    clean_flags = [f.lower().strip() for f in health_flags if f.strip().lower() not in ["none", ""]]

    # Primary Risk Tier Rules
    if personal_score >= 70.0:
        precautions.append("CRITICAL: Seek immediate air-conditioned or shaded cooling shelter. Avoid all outdoor exposure.")
        precautions.append("Drink 750ml to 1 Liter of chilled water with electrolyte/ORS per hour; do not wait until thirsty.")
        if occ_clean == "outdoor_manual" or activity_level == "heavy_exertion":
            precautions.append("MANDATORY OSHA WORK STOPPAGE: Cease heavy physical exertion between 11:00 AM and 4:30 PM.")
        if "cardiovascular_respiratory" in clean_flags:
            precautions.append("Monitor blood pressure and pulse rate; contact emergency services (108) immediately if experiencing dizziness, rapid heartbeat, or confusion.")
        if age_clean == "elderly":
            precautions.append("Ensure indoor room temperature is below 32°C using fans, wet curtains, or evaporative coolers; stay in frequent contact with relatives.")
        if age_clean == "child":
            precautions.append("Keep children strictly indoors in ventilated areas; never leave children inside unattended vehicles or unshaded rooms.")
        if "pregnant" in clean_flags:
            precautions.append("Elevate feet while resting in cool shade; drink coconut water or lemon ORS to maintain amniotic hydration balance.")

        safe_hours = {
            "safe_window": "Before 9:30 AM and After 6:00 PM only",
            "danger_window": "10:30 AM – 5:30 PM (EXTREME DANGER: Stay Indoors)",
            "peak_risk_hours": "12:30 PM – 4:00 PM (Maximum solar irradiance >900 W/m²)"
        }
        hydration = "Minimum 4.0 to 5.0 Liters daily with ORS sachets / electro-beverages. Avoid tea, coffee, and sugary sodas."
        work_rest = "15 minutes rest in deep shade for every 15 minutes of unavoidable light work (1:1 work-rest ratio). Heavy labor must be halted."

    elif personal_score >= 50.0:
        precautions.append("High risk of heat exhaustion and cramps. Plan outdoor activities strictly in morning or evening.")
        precautions.append("Hydration target: 500ml to 750ml electrolyte water every hour spent in ambient heat.")
        if occ_clean in ["outdoor_manual", "outdoor_non_manual"]:
            precautions.append("Enforce 20-minute shaded rest breaks every 40 minutes of work. Wear wide-brimmed cloth hats and loose light-colored cotton.")
        if "cardiovascular_respiratory" in clean_flags:
            precautions.append("Keep emergency inhaler/medication on hand. Avoid high-humidity zones that impede evaporative sweating.")
        if age_clean == "elderly":
            precautions.append("Sponge skin with cool water if sweating diminishes; limit household cooking during peak noon heat.")
        if "pregnant" in clean_flags:
            precautions.append("Stay off feet during noon hours; consume cooling fluids (chaas, buttermilk, tender coconut water).")

        safe_hours = {
            "safe_window": "Before 10:30 AM and After 5:00 PM",
            "danger_window": "11:30 AM – 4:30 PM (High Heat Stress: Seek Shade)",
            "peak_risk_hours": "1:00 PM – 3:30 PM"
        }
        hydration = "3.0 to 4.0 Liters daily. Supplement regular water with oral rehydration salts (ORS) or lime salt water."
        work_rest = "20 minutes shaded rest for every 40 minutes of outdoor activity (2:1 work-rest ratio)."

    elif personal_score >= 30.0:
        precautions.append("Moderate heat caution. Wear lightweight, loose cotton clothing and protect eyes/head from direct sunlight.")
        precautions.append("Maintain continuous hydration; drink water at least every 30-40 minutes.")
        if occ_clean in ["outdoor_manual", "outdoor_non_manual"]:
            precautions.append("Take regular hydration pauses under trees or covered awnings.")

        safe_hours = {
            "safe_window": "Before 11:30 AM and After 4:30 PM",
            "danger_window": "12:00 PM – 3:30 PM (Moderate Solar Stress)",
            "peak_risk_hours": "1:30 PM – 3:00 PM"
        }
        hydration = "2.5 to 3.5 Liters daily. Keep a reusable water flask at hand."
        work_rest = "10 minutes shaded pause for every 50 minutes of continuous activity."

    else:
        precautions.append("Conditions are currently within standard comfortable limits for your physiological profile.")
        precautions.append("Maintain baseline hydration throughout daytime hours (2.0 to 2.5 Liters).")
        safe_hours = {
            "safe_window": "Outdoor activities safe throughout most daytime hours",
            "danger_window": "Observe routine caution during direct noon sun (1:00 PM – 2:30 PM)",
            "peak_risk_hours": "None (Safe Band)"
        }
        hydration = "Standard daily baseline: 2.0 to 2.5 Liters."
        work_rest = "Standard operational schedule; regular fluid breaks recommended."

    return {
        "precautions": precautions,
        "safe_outdoor_hours": safe_hours,
        "hydration_advice": hydration,
        "work_rest_cycle": work_rest
    }


# =====================================================================
# REST ENDPOINTS
# =====================================================================

@router.get("/ward/{ward_id}/current", tags=["Ward Intelligence"])
def get_ward_current_metrics(ward_id: str):
    """
    GET /api/ward/{ward_id}/current
    Returns real-time thermal metrics, weather conditions, and demographic score for a specific ward/taluka.
    """
    wards = load_wards_dataset()
    for w in wards:
        if w.ward_id.upper() == ward_id.upper() or w.ward_name.lower() == ward_id.lower():
            evaluated = evaluate_ward_detail(w, include_trend=False)
            return {
                "ward_id": evaluated.ward_id,
                "ward_name": evaluated.ward_name,
                "lat": evaluated.lat,
                "lon": evaluated.lon,
                "population": evaluated.population,
                "current_temp_c": evaluated.current_temp_c,
                "humidity_pct": evaluated.humidity_pct,
                "wind_speed_kmh": evaluated.wind_speed_kmh,
                "solar_radiation_wm2": evaluated.solar_radiation_wm2,
                "heat_index_c": evaluated.heat_index,
                "wbgt_c": evaluated.wbgt,
                "solar_adjusted_wbgt_c": evaluated.solar_adjusted_wbgt,
                "apparent_temperature_c": evaluated.apparent_temperature_c,
                "human_thermal_stress_index": evaluated.human_thermal_stress_index,
                "base_risk_score": evaluated.risk_score,
                "base_risk_band": evaluated.risk_band,
                "elderly_pct": evaluated.elderly_pct,
                "outdoor_worker_pct": evaluated.outdoor_worker_pct,
                "green_cover_pct": evaluated.green_cover_pct,
                "advisories": evaluated.advisories
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Ward with identifier '{ward_id}' not found in Chandrapur pilot registry."
    )


@router.get("/ward/{ward_id}/forecast", tags=["Ward Intelligence"])
def get_ward_forecast_metrics(ward_id: str):
    """
    GET /api/ward/{ward_id}/forecast
    Returns the multi-day thermal and meteorological forecast for a specific ward.
    """
    wards = load_wards_dataset()
    for w in wards:
        if w.ward_id.upper() == ward_id.upper() or w.ward_name.lower() == ward_id.lower():
            evaluated = evaluate_ward_detail(w, include_trend=True)
            return {
                "ward_id": evaluated.ward_id,
                "ward_name": evaluated.ward_name,
                "forecast_days": evaluated.forecast_3day,
                "forecast_risk_trend": evaluated.forecast_risk_trend
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Ward with identifier '{ward_id}' not found in Chandrapur pilot registry."
    )


@router.get("/cooling-shelters", tags=["Cooling Relief Infrastructure"])
def list_all_cooling_shelters(ward_id: Optional[str] = None):
    """
    GET /api/cooling-shelters
    List all cooling hubs and mobile hydration relief vans, optionally filtered by ward_id.
    """
    if ward_id:
        filtered = [s for s in COOLING_SHELTERS if s["ward_id"].upper() == ward_id.upper()]
        return {"total": len(filtered), "shelters": filtered}
    return {"total": len(COOLING_SHELTERS), "shelters": COOLING_SHELTERS}


@router.post("/personal-risk", response_model=PersonalRiskResponse, tags=["Personal Risk Advisor"])
def calculate_personal_risk(req: PersonalRiskRequest):
    """
    POST /api/personal-risk
    Accepts citizen profile (age, gender, occupation, health flags, activity level) and maps
    to the target ward to calculate an individual's personal thermal risk score, risk band,
    breakdown multipliers, tailored precautions, and closest cooling relief center.
    """
    wards = load_wards_dataset()
    target_ward: Optional[Ward] = None
    for w in wards:
        if w.ward_id.upper() == req.ward_id.upper() or w.ward_name.lower() == req.ward_id.lower():
            target_ward = w
            break

    if not target_ward:
        # Fallback to Chandrapur City if invalid
        target_ward = wards[0]

    evaluated_ward = evaluate_ward_detail(target_ward, include_trend=True)
    base_score = evaluated_ward.risk_score

    # Compute personal biometeorological multiplier
    personal_multiplier, factor_breakdown = compute_personal_risk_multipliers(
        age_group=req.age_group,
        gender=req.gender,
        occupation_type=req.occupation_type,
        health_flags=req.health_flags,
        activity_level=req.activity_level,
        humidity_pct=target_ward.humidity_pct
    )

    # Calculate personalized score
    personal_score = round(max(0.0, min(100.0, base_score * personal_multiplier)), 1)

    # Classify personal risk band
    if personal_score >= 70.0:
        personal_band = "Extreme"
    elif personal_score >= 50.0:
        personal_band = "Danger"
    elif personal_score >= 30.0:
        personal_band = "Caution"
    else:
        personal_band = "Safe"

    # Compare against ward baseline band
    if personal_score > base_score + 5.0:
        delta_msg = f"Elevated: Your personal risk is higher than the general public ({personal_band} vs Public {evaluated_ward.risk_band}) due to heightened exposure or vulnerability."
    elif personal_score < base_score - 5.0:
        delta_msg = f"Reduced: Your personal risk is lower than the general public ({personal_band} vs Public {evaluated_ward.risk_band}) due to indoor protection or rest state."
    else:
        delta_msg = f"Aligned: Your personal risk matches the public ward warning tier ({personal_band})."

    # Generate tailored precautions
    advice_package = generate_personalized_precautions(
        personal_score=personal_score,
        risk_band=personal_band,
        age_group=req.age_group,
        occupation_type=req.occupation_type,
        health_flags=req.health_flags,
        activity_level=req.activity_level,
        temp_c=target_ward.current_temp_c,
        wbgt_c=evaluated_ward.wbgt
    )

    # Nearest cooling shelter calculation (use user coordinates if supplied, else ward center)
    query_lat = req.user_lat if req.user_lat is not None else target_ward.lat
    query_lon = req.user_lon if req.user_lon is not None else target_ward.lon
    nearest_shelter = find_nearest_cooling_shelter(query_lat, query_lon)

    # Personalized Forecast (re-scored with personal multiplier)
    personalized_forecast = []
    if evaluated_ward.forecast_risk_trend:
        for f_item in evaluated_ward.forecast_risk_trend:
            p_forecast_score = round(max(0.0, min(100.0, f_item.risk_score * personal_multiplier)), 1)
            if p_forecast_score >= 70.0:
                p_band = "Extreme"
            elif p_forecast_score >= 50.0:
                p_band = "Danger"
            elif p_forecast_score >= 30.0:
                p_band = "Caution"
            else:
                p_band = "Safe"

            personalized_forecast.append({
                "day": f_item.day,
                "temp_c": f_item.temp_c,
                "humidity_pct": f_item.humidity_pct,
                "wbgt_c": f_item.wbgt,
                "heat_index_c": f_item.heat_index,
                "base_score": f_item.risk_score,
                "personal_score": p_forecast_score,
                "personal_band": p_band
            })

    return PersonalRiskResponse(
        ward_id=target_ward.ward_id,
        ward_name=target_ward.ward_name,
        user_location={
            "lat": query_lat,
            "lon": query_lon,
            "ward_center_lat": target_ward.lat,
            "ward_center_lon": target_ward.lon
        },
        base_ward_score=base_score,
        base_risk_band=evaluated_ward.risk_band,
        metrics={
            "current_temp_c": target_ward.current_temp_c,
            "humidity_pct": target_ward.humidity_pct,
            "heat_index_c": evaluated_ward.heat_index,
            "wbgt_c": evaluated_ward.wbgt,
            "solar_adjusted_wbgt_c": evaluated_ward.solar_adjusted_wbgt,
            "apparent_temperature_c": evaluated_ward.apparent_temperature_c,
            "human_thermal_stress_index": evaluated_ward.human_thermal_stress_index,
            "wind_speed_kmh": target_ward.wind_speed_kmh,
            "solar_radiation_wm2": target_ward.solar_radiation_wm2
        },
        personal_score=personal_score,
        personal_risk_band=personal_band,
        risk_level_delta=delta_msg,
        personal_multiplier=personal_multiplier,
        factor_breakdown=factor_breakdown,
        precautions=advice_package["precautions"],
        safe_outdoor_hours=advice_package["safe_outdoor_hours"],
        hydration_advice=advice_package["hydration_advice"],
        work_rest_cycle=advice_package["work_rest_cycle"],
        nearest_cooling_shelter=nearest_shelter,
        personalized_forecast=personalized_forecast
    )


@router.post("/personal-risk/alert", response_model=PersonalAlertResponse, tags=["Personal Risk Advisor"])
def send_personal_family_alert(req: PersonalAlertRequest):
    """
    POST /api/personal-risk/alert
    Citizen-facing one-tap family alert SMS dispatch.
    Sends a concise, localized heat safety alert to a relative or emergency contact.
    """
    wards = load_wards_dataset()
    ward_name = req.ward_id
    for w in wards:
        if w.ward_id.upper() == req.ward_id.upper() or w.ward_name.lower() == req.ward_id.lower():
            ward_name = w.ward_name
            break

    sender = req.sender_name or "Your Family Member"
    sms_text = (
        f"HEAT SHIELD CITIZEN ALERT: {sender} in {ward_name} is under {req.personal_risk_band.upper()} "
        f"Heat Stress (Personal Score: {req.personal_score}/100). "
        f"Recommended Action: Ensure adequate hydration and move to a cool shaded shelter."
    )
    if req.custom_note and req.custom_note.strip():
        sms_text += f" Note: \"{req.custom_note.strip()}\""

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_phone = os.getenv("TWILIO_PHONE_NUMBER")
    recipient_phone = req.recipient_phone.strip()
    fast2sms_key = req.api_key or os.getenv("FAST2SMS_API_KEY")

    provider = "Console Audit Log (Simulated)"

    if account_sid and auth_token and from_phone:
        try:
            from twilio.rest import Client
            client = Client(account_sid, auth_token)
            client.messages.create(
                body=sms_text,
                from_=from_phone,
                to=recipient_phone
            )
            provider = "Twilio SMS Gateway"
            logger.info(f"[Personal Alert Twilio SMS Sent] to {recipient_phone}")
            return PersonalAlertResponse(
                status="sent",
                recipient_phone=recipient_phone,
                message=sms_text,
                provider=provider
            )
        except Exception as e:
            logger.warning(f"[Twilio Personal Alert Error]: {str(e)}. Falling back to mock log.")

    if fast2sms_key:
        try:
            import urllib.request
            import json
            clean_num = recipient_phone.replace("+91", "").replace("+", "").strip()
            if len(clean_num) == 10 and clean_num.isdigit():
                req_payload = json.dumps({
                    "route": "q",
                    "message": sms_text,
                    "language": "english",
                    "flash": 0,
                    "numbers": clean_num
                }).encode("utf-8")
                req_obj = urllib.request.Request(
                    "https://www.fast2sms.com/dev/bulkV2",
                    data=req_payload,
                    headers={
                        "authorization": fast2sms_key,
                        "Content-Type": "application/json"
                    }
                )
                with urllib.request.urlopen(req_obj, timeout=8) as resp:
                    resp_body = resp.read().decode()
                    logger.info(f"[Fast2SMS Personal Alert Response]: {resp_body}")
                provider = "Fast2SMS India Cellular Gateway"
                return PersonalAlertResponse(
                    status="sent",
                    recipient_phone=recipient_phone,
                    message=sms_text,
                    provider=provider
                )
        except Exception as e:
            logger.warning(f"[Fast2SMS Personal Alert Error]: {str(e)}")

    # Fallback simulated console log for hackathon demo
    print(f"\n=======================================================")
    print(f"[PERSONAL CITIZEN FAMILY ALERT LOG]")
    print(f"Recipient: {req.recipient_name} ({recipient_phone})")
    print(f"Message: {sms_text}")
    print(f"=======================================================\n")

    return PersonalAlertResponse(
        status="simulated",
        recipient_phone=recipient_phone,
        message=sms_text,
        provider=provider
    )
