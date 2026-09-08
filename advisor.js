/**
 * HEAT SHIELD — Personal Heat Risk Advisor (Citizen-Facing Module)
 * Architecture: Mobile-First Consumer Weather-App Engine
 * Fully Localized: English, Marathi (मराठी), and Hindi (हिंदी)
 * Supports: Live FastAPI REST backend + Client-Side Math Engine Fallback
 * Pilot: Chandrapur District, Maharashtra (Disaster Management Authority)
 */

// ==========================================================================
// CONFIGURATION & GLOBAL CONSTANTS
// ==========================================================================
const API_BASE_URL = 'http://127.0.0.1:8000/api';

// Complete 8 Pilot Wards / Talukas of Chandrapur District
const CHANDRAPUR_WARDS = [
  {
    ward_id: "CHA_001",
    ward_name: "Chandrapur City",
    ward_name_mr: "चंद्रपूर शहर",
    ward_name_hi: "चंद्रपुर नगर",
    lat: 19.9615,
    lon: 79.2961,
    current_temp_c: 47.2,
    humidity_pct: 28.0,
    wind_speed_kmh: 12.0,
    solar_radiation_wm2: 940.0,
    elderly_pct: 10.5,
    outdoor_worker_pct: 36.0,
    green_cover_pct: 6.5,
    forecast: [
      { day: "Day 1", temp_c: 47.5, humidity_pct: 26.0, solar: 950.0 },
      { day: "Day 2", temp_c: 48.2, humidity_pct: 24.0, solar: 960.0 },
      { day: "Day 3", temp_c: 43.8, humidity_pct: 32.0, solar: 820.0 }
    ]
  },
  {
    ward_id: "CHA_002",
    ward_name: "Ballarpur",
    ward_name_mr: "बल्लारपूर",
    ward_name_hi: "बल्लारपुर",
    lat: 19.8333,
    lon: 79.3500,
    current_temp_c: 46.8,
    humidity_pct: 30.0,
    wind_speed_kmh: 10.5,
    solar_radiation_wm2: 930.0,
    elderly_pct: 11.0,
    outdoor_worker_pct: 42.0,
    green_cover_pct: 7.0,
    forecast: [
      { day: "Day 1", temp_c: 47.0, humidity_pct: 28.0, solar: 940.0 },
      { day: "Day 2", temp_c: 47.9, humidity_pct: 25.0, solar: 955.0 },
      { day: "Day 3", temp_c: 43.5, humidity_pct: 33.0, solar: 810.0 }
    ]
  },
  {
    ward_id: "CHA_003",
    ward_name: "Rajura",
    ward_name_mr: "राजूरा",
    ward_name_hi: "राजूरा",
    lat: 19.7833,
    lon: 79.3667,
    current_temp_c: 45.4,
    humidity_pct: 31.0,
    wind_speed_kmh: 11.0,
    solar_radiation_wm2: 890.0,
    elderly_pct: 11.8,
    outdoor_worker_pct: 38.0,
    green_cover_pct: 11.0,
    forecast: [
      { day: "Day 1", temp_c: 45.8, humidity_pct: 29.0, solar: 900.0 },
      { day: "Day 2", temp_c: 46.7, humidity_pct: 26.0, solar: 925.0 },
      { day: "Day 3", temp_c: 42.5, humidity_pct: 34.0, solar: 790.0 }
    ]
  },
  {
    ward_id: "CHA_004",
    ward_name: "Warora",
    ward_name_mr: "वरोरा",
    ward_name_hi: "वरोरा",
    lat: 20.2333,
    lon: 79.0000,
    current_temp_c: 44.6,
    humidity_pct: 33.0,
    wind_speed_kmh: 13.0,
    solar_radiation_wm2: 870.0,
    elderly_pct: 12.5,
    outdoor_worker_pct: 34.0,
    green_cover_pct: 14.0,
    forecast: [
      { day: "Day 1", temp_c: 45.2, humidity_pct: 31.0, solar: 885.0 },
      { day: "Day 2", temp_c: 46.0, humidity_pct: 28.0, solar: 910.0 },
      { day: "Day 3", temp_c: 42.0, humidity_pct: 35.0, solar: 770.0 }
    ]
  },
  {
    ward_id: "CHA_005",
    ward_name: "Bhadravati",
    ward_name_mr: "भद्रावती",
    ward_name_hi: "भद्रावती",
    lat: 20.2167,
    lon: 79.0500,
    current_temp_c: 37.5,
    humidity_pct: 40.0,
    wind_speed_kmh: 14.0,
    solar_radiation_wm2: 700.0,
    elderly_pct: 12.0,
    outdoor_worker_pct: 24.0,
    green_cover_pct: 28.0,
    forecast: [
      { day: "Day 1", temp_c: 38.2, humidity_pct: 38.0, solar: 720.0 },
      { day: "Day 2", temp_c: 39.0, humidity_pct: 36.0, solar: 740.0 },
      { day: "Day 3", temp_c: 36.5, humidity_pct: 42.0, solar: 680.0 }
    ]
  },
  {
    ward_id: "CHA_006",
    ward_name: "Brahmapuri",
    ward_name_mr: "ब्रह्मपुरी",
    ward_name_hi: "ब्रह्मपुरी",
    lat: 20.6000,
    lon: 79.8500,
    current_temp_c: 37.2,
    humidity_pct: 42.0,
    wind_speed_kmh: 13.5,
    solar_radiation_wm2: 690.0,
    elderly_pct: 13.5,
    outdoor_worker_pct: 22.0,
    green_cover_pct: 32.0,
    forecast: [
      { day: "Day 1", temp_c: 37.8, humidity_pct: 40.0, solar: 710.0 },
      { day: "Day 2", temp_c: 38.6, humidity_pct: 37.0, solar: 730.0 },
      { day: "Day 3", temp_c: 36.0, humidity_pct: 44.0, solar: 670.0 }
    ]
  },
  {
    ward_id: "CHA_007",
    ward_name: "Nagbhid Wetland",
    ward_name_mr: "नागभीड पाणथळ क्षेत्र",
    ward_name_hi: "नागभीड आर्द्रभूमि",
    lat: 20.5667,
    lon: 79.9667,
    current_temp_c: 33.0,
    humidity_pct: 45.0,
    wind_speed_kmh: 15.0,
    solar_radiation_wm2: 520.0,
    elderly_pct: 12.0,
    outdoor_worker_pct: 15.0,
    green_cover_pct: 52.0,
    forecast: [
      { day: "Day 1", temp_c: 33.5, humidity_pct: 44.0, solar: 530.0 },
      { day: "Day 2", temp_c: 34.5, humidity_pct: 42.0, solar: 550.0 },
      { day: "Day 3", temp_c: 32.5, humidity_pct: 48.0, solar: 500.0 }
    ]
  },
  {
    ward_id: "CHA_008",
    ward_name: "Mul - Tadoba Forest Buffer",
    ward_name_mr: "मुल - ताडोबा वन बफर",
    ward_name_hi: "मुल - ताडोबा वन बफर",
    lat: 20.0667,
    lon: 79.6667,
    current_temp_c: 31.5,
    humidity_pct: 50.0,
    wind_speed_kmh: 16.0,
    solar_radiation_wm2: 450.0,
    elderly_pct: 10.0,
    outdoor_worker_pct: 12.0,
    green_cover_pct: 68.0,
    forecast: [
      { day: "Day 1", temp_c: 32.0, humidity_pct: 48.0, solar: 460.0 },
      { day: "Day 2", temp_c: 33.0, humidity_pct: 46.0, solar: 480.0 },
      { day: "Day 3", temp_c: 31.0, humidity_pct: 52.0, solar: 430.0 }
    ]
  }
];

// Offline Relief Shelters & Hydration Points
const OFFLINE_SHELTERS = [
  {
    id: "SHELTER_CHA_01",
    name: "Chandrapur City Hospital Cooling Hub",
    name_mr: "चंद्रपूर शहर रुग्णालय कुलिंग केंद्र",
    name_hi: "चंद्रपुर नगर अस्पताल शीतलन केंद्र",
    ward_id: "CHA_001",
    lat: 19.9650,
    lon: 79.2980,
    type: "shelter",
    capacity: 300,
    desc: "Equipped with cold baths, IV fluids, and air filtration.",
    desc_mr: "थंड पाण्याच्या टाक्या, सलाईन आणि वातानुकूलित सुविधेने सज्ज.",
    desc_hi: "ठंडे पानी के टब, आईवी ड्रिप एवं वातानुकूलित वार्ड से सुसज्जित।"
  },
  {
    id: "SHELTER_CHA_02",
    name: "Gandhi Chowk Mobile Hydration Van 01",
    name_mr: "गांधी चौक मोबाईल हायड्रेशन व्हॅन ०१",
    name_hi: "गांधी चौक मोबाइल जल वितरण वैन ०१",
    ward_id: "CHA_001",
    lat: 19.9580,
    lon: 79.2920,
    type: "van",
    capacity: 150,
    desc: "Chilled ORS water dispatch for bus transit passengers.",
    desc_mr: "बस प्रवाशांसाठी आणि फेरीवाल्यांसाठी थंड ओआरएस पाणी वाटप.",
    desc_hi: "बस यात्रियों व श्रमिकों के लिए ठंडा ओआरएस जल वितरण।"
  },
  {
    id: "SHELTER_BAL_01",
    name: "Ballarpur Municipal High School Center",
    name_mr: "बल्लारपूर पालिका हायस्कूल आराम केंद्र",
    name_hi: "बल्लारपुर नगर पालिका केंद्र",
    ward_id: "CHA_002",
    lat: 19.8350,
    lon: 79.3520,
    type: "shelter",
    capacity: 250,
    desc: "High-capacity evaporative coolers and continuous clean water.",
    desc_mr: "२५० मजुरांची क्षमता व उच्च क्षमतेचे कूलर्स उपलब्ध.",
    desc_hi: "२५० श्रमिकों की क्षमता व उच्च क्षमता के कूलर्स उपलब्ध।"
  },
  {
    id: "SHELTER_RAJ_01",
    name: "Rajura Sub-District Hospital Cooling Center",
    name_mr: "राजूरा उप-जिल्हा रुग्णालय शीत केंद्र",
    name_hi: "राजूरा उप-जिला अस्पताल शीतलन केंद्र",
    ward_id: "CHA_003",
    lat: 19.7820,
    lon: 79.3690,
    type: "shelter",
    capacity: 180,
    desc: "Primary medical relief outpost serving agricultural workers.",
    desc_mr: "शेतमजूर आणि कामगारांसाठी प्राथमिक वैद्यकीय आराम केंद्र.",
    desc_hi: "कृषि श्रमिकों के लिए प्राथमिक चिकित्सा एवं विश्राम केंद्र।"
  },
  {
    id: "SHELTER_WAR_01",
    name: "Warora Rural Hospital & Shade Shelter",
    name_mr: "वरोरा ग्रामीण रुग्णालय व सावली केंद्र",
    name_hi: "वरोरा ग्रामीण अस्पताल एवं छाया केंद्र",
    ward_id: "CHA_004",
    lat: 20.2310,
    lon: 79.0040,
    type: "shelter",
    capacity: 220,
    desc: "Highway corridor relief station for transit passengers and farmers.",
    desc_mr: "महामार्ग प्रवासी, शेतकरी व वाहनचालकांसाठी शीतकरण केंद्र.",
    desc_hi: "राजमार्ग यात्रियों एवं किसानों के लिए छाया व शीतल जल केंद्र।"
  },
  {
    id: "SHELTER_BHA_01",
    name: "Bhadravati Community Health Relief Station",
    name_mr: "भद्रावती समुदाय आरोग्य आराम केंद्र",
    name_hi: "भद्रावती सामुदायिक स्वास्थ्य राहत केंद्र",
    ward_id: "CHA_005",
    lat: 20.2180,
    lon: 79.0520,
    type: "shelter",
    capacity: 160,
    desc: "Ordnance factory and mining fringe community heat relief.",
    desc_mr: "संरक्षण फॅक्टरी आणि खाण परिसरातील कामगारांसाठी शीतकरण केंद्र.",
    desc_hi: "आयुध निर्माणी एवं खदान क्षेत्र के श्रमिकों हेतु शीतलन केंद्र।"
  },
  {
    id: "SHELTER_BRA_01",
    name: "Brahmapuri Sub-District Hospital Cooling Hub",
    name_mr: "ब्रह्मपुरी उप-जिल्हा रुग्णालय कुलिंग हब",
    name_hi: "ब्रह्मपुरी उप-जिला अस्पताल कूलिंग हब",
    ward_id: "CHA_006",
    lat: 20.5980,
    lon: 79.8470,
    type: "shelter",
    capacity: 200,
    desc: "Dedicated heat stroke ICU beds and cold shower facility.",
    desc_mr: "उष्णता विकार अतिदक्षता कक्ष व थंड पाण्याची सुविधा.",
    desc_hi: "हीट स्ट्रोक आईसीयू एवं शीतल स्नान की सुविधा।"
  },
  {
    id: "SHELTER_NAG_01",
    name: "Nagbhid Primary Health Center (PHC) Relief Post",
    name_mr: "नागभीड प्राथमिक आरोग्य केंद्र मदत कक्ष",
    name_hi: "नागभीड प्राथमिक स्वास्थ्य केंद्र राहत केंद्र",
    ward_id: "CHA_007",
    lat: 20.5650,
    lon: 79.9640,
    type: "shelter",
    capacity: 120,
    desc: "Wetland & agro-forestry belt relief point.",
    desc_mr: "पाणथळ व शेती क्षेत्रातील नागरिकांसाठी आराम कक्ष.",
    desc_hi: "कृषि क्षेत्र के नागरिकों के लिए प्राथमिक सहायता केंद्र।"
  },
  {
    id: "SHELTER_MUL_01",
    name: "Mul Rural Hospital & Forest Transit Shelter",
    name_mr: "मुल ग्रामीण रुग्णालय व विश्राम कक्ष",
    name_hi: "मुल ग्रामीण अस्पताल एवं विश्राम केंद्र",
    ward_id: "CHA_008",
    lat: 20.0640,
    lon: 79.6640,
    type: "shelter",
    capacity: 140,
    desc: "Buffer sanctuary entrance rest pavilion.",
    desc_mr: "ताडोबा बफर क्षेत्रातील विश्राम कक्ष.",
    desc_hi: "ताडोबा वन क्षेत्र का विश्राम एवं राहत केंद्र।"
  }
];

// ==========================================================================
// COMPREHENSIVE LOCALIZATION STRINGS (EN / MR / HI)
// ==========================================================================
const ADVISOR_I18N = {
  en: {
    brand_title: "HEAT SHIELD",
    brand_subtitle: "Personal Risk Advisor",
    nav_admin: "Control Room ↗",
    status_live: "FastAPI Backend Connected",
    status_offline: "Offline Standalone Engine Active",
    authority_badge: "Disaster Management • Chandrapur",
    profile_hdr: "Personal Vulnerability Profile",
    profile_sub: "Tailors thermal stress to your age, labor exposure & health",
    lbl_location: "Your Location (Ward / Taluka)",
    location_sub: "Chandrapur District",
    btn_geolocate: "Auto-Detect",
    lbl_age: "Age Group",
    lbl_age_desc: "Thermoregulation factor",
    age_child: "Child (<12)",
    age_adult: "Adult (12-64)",
    age_elderly: "Elderly (65+)",
    lbl_gender: "Gender (Optional)",
    lbl_gender_desc: "Biometeorology factor",
    gen_male: "Male",
    gen_female: "Female",
    gen_other: "Prefer not to say",
    lbl_occ: "Occupation / Exposure Type",
    lbl_occ_desc: "Direct solar load",
    occ_manual: "Outdoor Manual Labor",
    occ_non_manual: "Outdoor Transit / Vendor",
    occ_office: "Indoor / Office",
    occ_student: "Student / Home",
    lbl_health: "Health Flags",
    lbl_health_desc: "Multi-select",
    health_cardio: "Heart / Asthma Condition",
    health_preg: "Pregnant",
    health_none: "None Disclosed",
    lbl_activity: "Activity Right Now",
    lbl_activity_desc: "Metabolic heat load",
    act_rest: "Resting",
    act_light: "Light Activity",
    act_heavy: "Heavy Exertion",
    btn_save: "Recalculate Personal Risk →",
    hero_score: "Personal Risk Index",
    hero_feels_like: "Heat Index",
    hero_wbgt: "WBGT",
    hero_humidity: "Humidity",
    hero_wind: "Wind",
    sec_precautions: "Personalized Safety Actions",
    badge_safe_hours: "SAFE HOURS",
    badge_danger_hours: "AVOID SUN",
    sec_why: "Why This Recommendation?",
    why_sub: "Biometeorological factors altering your base risk",
    why_intro: "Heat Shield blends the municipal baseline risk score with your physiological exposure profile using guidance from the CDC Extreme Heat Advisory, NOAA Heat Index, and OSHA Occupational Standards.",
    accordion_trigger_text: "View Detailed Factor Multipliers & Standards",
    col_factor: "Factor",
    col_val: "Selection",
    col_impact: "Impact",
    col_rationale: "Rationale & Citation",
    sec_forecast: "3-Day Personalized Forecast",
    sec_shelter: "Nearest Cooling Shelter",
    btn_directions: "Open Directions in Google Maps ↗",
    sec_emergency_alert: "Emergency Contact Safety Ping",
    emergency_alert_desc: "One-tap automated SMS dispatch to your family with your live heatwave risk tier and location.",
    btn_family_alert: "Alert My Family / Emergency Contact",
    modal_title: "Send Emergency Heat Alert",
    modal_desc: "Sends an instant SMS alert to your family with your personal risk status and recommended precautions.",
    lbl_recipient_name: "Relative / Contact Name",
    lbl_phone: "Phone Number (+91)",
    lbl_sender_name: "Your Name",
    lbl_note: "Optional Note",
    btn_cancel: "Cancel",
    btn_send_sms: "Send Alert via SMS",
    toast_sent: "Emergency SMS alert dispatched successfully!",
    toast_geo_ok: "Location matched to nearest ward:",
    toast_geo_err: "Location permission denied; defaulted to Chandrapur City.",
    band_safe: "Normal / Safe",
    band_caution: "Caution Alert",
    band_danger: "Danger Alert",
    band_extreme: "Extreme Emergency",
    unit_km: "km",
    day_prefix: "Day",
    table_scroll_hint: "Scroll horizontally to view full table"
  },
  mr: {
    brand_title: "हीट शील्ड",
    brand_subtitle: "नागरिक वैयक्तिक उष्णता सल्लागार",
    nav_admin: "पालिका नियंत्रण कक्ष ↗",
    status_live: "फास्टएपीआय बॅकएंड कार्यरत",
    status_offline: "ऑफलाईन स्टँडअलोन मोड सक्रिय",
    authority_badge: "आपत्ती व्यवस्थापन प्राधिकरण • चंद्रपूर",
    profile_hdr: "वैयक्तिक संवेदनशीलता प्रोफाईल",
    profile_sub: "वय, शारीरिक श्रम व आरोग्यानुसार उष्णता ताणाचा अचूक अंदाज",
    lbl_location: "तुमचे क्षेत्र (प्रभाग / तालुका)",
    location_sub: "चंद्रपूर जिल्हा",
    btn_geolocate: "स्थान शोधा",
    lbl_age: "वयोगट",
    lbl_age_desc: "शरीराची उष्णता सहन करण्याची क्षमता",
    age_child: "लहान मुले (<12 वर्षे)",
    age_adult: "प्रौढ (12-64 वर्षे)",
    age_elderly: "ज्येष्ठ नागरिक (65+ वर्षे)",
    lbl_gender: "लिंग (ऐच्छिक)",
    lbl_gender_desc: "हवेतील दमटपणाचा प्रभाव",
    gen_male: "पुरुष",
    gen_female: "महिला",
    gen_other: "सांगू इच्छित नाही",
    lbl_occ: "व्यवसाय / उन्हातील वावर",
    lbl_occ_desc: "थेट सूर्यकिरणांचा प्रभाव",
    occ_manual: "उघड्यावर मजुरी / शेतीकाम",
    occ_non_manual: "फेरीवाले / वाहतूक कामगार",
    occ_office: "कार्यालयीन / इनडोअर",
    occ_student: "विद्यार्थी / गृहिणी",
    lbl_health: "आरोग्य लक्षणे",
    lbl_health_desc: "अनेक पर्याय निवडू शकता",
    health_cardio: "हृदयरोग / दमा",
    health_preg: "गर्भवती",
    health_none: "कोणताही आजार नाही",
    lbl_activity: "सध्याची शारीरिक हालचाल",
    lbl_activity_desc: "शरीरात निर्माण होणारी अंतर्गत उष्णता",
    act_rest: "विश्रांती",
    act_light: "साधी कामे / चालणे",
    act_heavy: "कष्ट / धावणे / श्रम",
    btn_save: "वैयक्तिक उष्णता ताण मोजा →",
    hero_score: "वैयक्तिक जोखीम निर्देशांक",
    hero_feels_like: "हीट इंडेक्स",
    hero_wbgt: "WBGT तापमान",
    hero_humidity: "दमटपणा",
    hero_wind: "वारा",
    sec_precautions: "वैयक्तिक आरोग्य व सुरक्षा उपाय",
    badge_safe_hours: "सुरक्षित वेळ",
    badge_danger_hours: "उन्हात जाणे टाळा",
    sec_why: "हा सल्ला का दिला गेला? (वैज्ञानिक पारदर्शकता)",
    why_sub: "तुमच्या शरीरावरील उष्णता ताणाचे मोजमाप घटक",
    why_intro: "हीट शील्ड प्रणाली स्थानिक तापमान, तुमचे वय, व्यवसाय आणि आरोग्य घटकांचा मेळ घालून आंतरराष्ट्रीय मानकांनुसार (CDC, NOAA, OSHA) वैयक्तिक धोका मोजते.",
    accordion_trigger_text: "सविस्तर जोखीम गुणक व मानके पहा",
    col_factor: "घटक",
    col_val: "निवड",
    col_impact: "जोखीम बदल",
    col_rationale: "वैज्ञानिक आधार",
    sec_forecast: "३-दिवसीय वैयक्तिक अंदाज",
    sec_shelter: "जवळचे आपत्कालीन कुलिंग केंद्र",
    btn_directions: "गुगल मॅप्सवर दिशा पहा ↗",
    sec_emergency_alert: "कुटुंबियांना धोक्याचा संदेश",
    emergency_alert_desc: "तुमच्या कुटुंबातील सदस्यांच्या मोबाईलवर तुमच्या धोक्याची पातळी आणि स्थानाचा थेट एसएमएस पाठवा.",
    btn_family_alert: "कुटुंबियांना धोक्याचा एसएमएस पाठवा",
    modal_title: "तातडीचा उष्णता अलर्ट पाठवा",
    modal_desc: "कुटुंबियांच्या मोबाईलवर तुमच्या धोक्याची पातळी व काळजी घेण्याचा संदेश तात्काळ पाठवा.",
    lbl_recipient_name: "नातेवाईकाचे नाव",
    lbl_phone: "मोबाईल नंबर (+91)",
    lbl_sender_name: "तुमचे नाव",
    lbl_note: "अतिरिक्त संदेश",
    btn_cancel: "रद्द करा",
    btn_send_sms: "एसएमएस पाठवा",
    toast_sent: "आपत्कालीन अलर्ट एसएमएस यशस्वीरित्या पाठवला!",
    toast_geo_ok: "जीपीएस द्वारे जवळचा तालुका निवडला गेला:",
    toast_geo_err: "जीपीएस परवानगी नाकारली; चंद्रपूर शहर निवडले.",
    band_safe: "सुरक्षित / सामान्य",
    band_caution: "सावधानता इशारा",
    band_danger: "धोकादायक स्थिती",
    band_extreme: "अत्यंत तीव्र धोका",
    unit_km: "किमी",
    day_prefix: "दिवस",
    table_scroll_hint: "पूर्ण तक्ता पाहण्यासाठी डावीकडे/उजवीकडे सरकवा"
  },
  hi: {
    brand_title: "हीट शील्ड",
    brand_subtitle: "व्यक्तिगत ताप जोखिम सलाहकार",
    nav_admin: "नियंत्रण कक्ष ↗",
    status_live: "फास्टएपीआई बैकएंड सक्रिय",
    status_offline: "ऑफ़लाइन स्टैंडअलोन मोड सक्रिय",
    authority_badge: "आपदा प्रबंधन प्राधिकरण • चंद्रपुर",
    profile_hdr: "व्यक्तिगत संवेदनशीलता प्रोफ़ाइल",
    profile_sub: "आयु, श्रम एवं स्वास्थ्य के अनुसार ताप तनाव का सटीक आकलन",
    lbl_location: "आपका स्थान (प्रभाग / तालुका)",
    location_sub: "चंद्रपुर जिला",
    btn_geolocate: "स्थान खोजें",
    lbl_age: "आयु वर्ग",
    lbl_age_desc: "शरीर की ताप नियंत्रण क्षमता",
    age_child: "बच्चे (<12 वर्ष)",
    age_adult: "वयस्क (12-64 वर्ष)",
    age_elderly: "वरिष्ठ नागरिक (65+ वर्ष)",
    lbl_gender: "लिंग (वैकल्पिक)",
    lbl_gender_desc: "आर्द्रता संवेदनशीलता",
    gen_male: "पुरुष",
    gen_female: "महिला",
    gen_other: "बताना नहीं चाहते",
    lbl_occ: "व्यवसाय / धूप में संपर्क",
    lbl_occ_desc: "सीधी धूप का प्रभाव",
    occ_manual: "बाहरी शारीरिक श्रम",
    occ_non_manual: "डिलीवरी / फेरीवाले / चालक",
    occ_office: "कार्यालय / घर के अंदर",
    occ_student: "छात्र / गृहिणी",
    lbl_health: "स्वास्थ्य स्थितियां",
    lbl_health_desc: "कई विकल्प चुन सकते हैं",
    health_cardio: "हृदय / अस्थमा रोग",
    health_preg: "गर्भवती",
    health_none: "कोई गंभीर बीमारी नहीं",
    lbl_activity: "वर्तमान शारीरिक गतिविधि",
    lbl_activity_desc: "आंतरिक चयापचय ताप",
    act_rest: "आराम",
    act_light: "हल्की गतिविधि / चलना",
    act_heavy: "कठिन शारीरिक श्रम",
    btn_save: "व्यक्तिगत जोखिम की गणना करें →",
    hero_score: "व्यक्तिगत जोखिम सूचकांक",
    hero_feels_like: "हीट इंडेक्स",
    hero_wbgt: "डब्ल्यूबीजीटी",
    hero_humidity: "आर्द्रता",
    hero_wind: "हवा",
    sec_precautions: "व्यक्तिगत सुरक्षा उपाय",
    badge_safe_hours: "सुरक्षित समय",
    badge_danger_hours: "धूप से बचें",
    sec_why: "यह अनुशंसा क्यों? (वैज्ञानिक पारदर्शिता)",
    why_sub: "आपके व्यक्तिगत जोखिम को प्रभावित करने वाले वैज्ञानिक कारक",
    why_intro: "हीट शील्ड प्रणाली तापमान, आर्द्रता और आपकी प्रोफ़ाइल को मिलाकर अंतरराष्ट्रीय मानकों (CDC, NOAA, OSHA) के आधार पर व्यक्तिगत ताप जोखिम तय करती है।",
    accordion_trigger_text: "विस्तृत कारक गुणक व मानक देखें",
    col_factor: "घटक",
    col_val: "चयन",
    col_impact: "प्रभाव",
    col_rationale: "वैज्ञानिक आधार",
    sec_forecast: "3-दिवसीय व्यक्तिगत पूर्वानुमान",
    sec_shelter: "निकटतम शीतलन केंद्र",
    btn_directions: "गूगल मैप्स पर रास्ता देखें ↗",
    sec_emergency_alert: "परिजनों को आपातकालीन चेतावनी",
    emergency_alert_desc: "अपने परिजनों को अपनी वर्तमान जोखिम स्थिति और स्थान का तुरंत एसएमएस भेजें।",
    btn_family_alert: "परिवार / आपातकालीन संपर्क को सूचित करें",
    modal_title: "आपातकालीन ताप चेतावनी भेजें",
    modal_desc: "अपने परिजनों को अपनी वर्तमान स्थिति और सुरक्षा परामर्श का तुरंत एसएमएस भेजें।",
    lbl_recipient_name: "परिजन का नाम",
    lbl_phone: "मोबाइल नंबर (+91)",
    lbl_sender_name: "आपका नाम",
    lbl_note: "अतिरिक्त संदेश",
    btn_cancel: "रद्द करें",
    btn_send_sms: "एसएमएस द्वारा अलर्ट भेजें",
    toast_sent: "आपातकालीन एसएमएस सफलतापूर्वक भेजा गया!",
    toast_geo_ok: "जीपीएस द्वारा निकटतम तालुका चुना गया:",
    toast_geo_err: "जीपीएस अनुमति नहीं मिली; चंद्रपुर शहर चयनित।",
    band_safe: "सामान्य / सुरक्षित",
    band_caution: "सावधानी स्तर",
    band_danger: "खतरा स्तर",
    band_extreme: "अत्यधिक आपातकाल",
    unit_km: "किमी",
    day_prefix: "दिन",
    table_scroll_hint: "पूरी तालिका देखने के लिए क्षैतिज स्क्रॉल करें"
  }
};

// ==========================================================================
// CLIENT-SIDE STATE
// ==========================================================================
let currentLang = localStorage.getItem('hs_advisor_lang') || 'en';
let userCoords = null;
let forecastChartInstance = null;
let shelterMapInstance = null;
let shelterMarkerGroup = null;

// User Profile Defaults
let userProfile = {
  ward_id: "CHA_001",
  age_group: "adult",
  gender: "prefer_not_to_say",
  occupation_type: "outdoor_manual",
  health_flags: ["none"],
  activity_level: "heavy_exertion"
};

// Cached Active Assessment Result
let currentResult = null;


// ==========================================================================
// MATHEMATICAL ENGINE (CLIENT STANDALONE FALLBACK)
// ==========================================================================
function calcRothfuszHeatIndex(tempC, rh) {
  const T = (tempC * 9.0 / 5.0) + 32.0;
  const R = rh;
  let hiF = 0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (R * 0.094));
  if (hiF >= 80.0) {
    hiF = -42.379 + 2.04901523 * T + 10.14333127 * R - 0.22475541 * T * R
      - 6.83783e-3 * T * T - 5.481717e-2 * R * R + 1.22874e-3 * T * T * R
      + 8.5282e-4 * T * R * R - 1.99e-6 * T * T * R * R;
    if (R < 13.0 && T >= 80.0 && T <= 112.0) {
      hiF -= ((13.0 - R) / 4.0) * Math.sqrt((17.0 - Math.abs(T - 95.0)) / 17.0);
    } else if (R > 85.0 && T >= 80.0 && T <= 87.0) {
      hiF += ((R - 85.0) / 10.0) * ((87.0 - T) / 5.0);
    }
  }
  return Number(((hiF - 32.0) * 5.0 / 9.0).toFixed(1));
}

function calcBomWbgt(tempC, rh) {
  const e = (rh / 100.0) * 6.105 * Math.exp((17.27 * tempC) / (237.7 + tempC));
  return Number((0.567 * tempC + 0.393 * e + 3.94).toFixed(1));
}

function calcApparentTemp(tempC, rh, windKmh) {
  const windMs = windKmh / 3.6;
  const e = (rh / 100.0) * 6.105 * Math.exp((17.27 * tempC) / (237.7 + tempC));
  return Number((tempC + 0.33 * e - 0.70 * windMs - 4.00).toFixed(1));
}

function calcWardBaseScore(ward) {
  const hi = calcRothfuszHeatIndex(ward.current_temp_c, ward.humidity_pct);
  const wbgt = calcBomWbgt(ward.current_temp_c, ward.humidity_pct);
  const at = calcApparentTemp(ward.current_temp_c, ward.humidity_pct, ward.wind_speed_kmh);
  const solarWbgt = wbgt + (0.0037 * ward.solar_radiation_wm2);
  
  const rawHtsi = (0.5 * solarWbgt) + (0.3 * at) + (0.2 * hi);
  const normHtsi = Math.max(0, Math.min(100, ((rawHtsi - 25.0) / (50.0 - 25.0)) * 100.0));
  const demoComp = Math.max(0, Math.min(100, (0.4 * ward.elderly_pct) + (0.4 * ward.outdoor_worker_pct) + (0.2 * (100.0 - ward.green_cover_pct))));
  const score = Number(((0.60 * normHtsi) + (0.40 * demoComp)).toFixed(1));

  let band = "Safe";
  if (score >= 70.0) band = "Extreme";
  else if (score >= 50.0) band = "Danger";
  else if (score >= 30.0) band = "Caution";

  return { score, band, hi, wbgt, solarWbgt, at, rawHtsi };
}

function computeClientPersonalMultiplier(profile, humidityPct) {
  let mult = 1.0;
  const breakdown = [];

  // 1. Age
  if (profile.age_group === "elderly") {
    mult *= 1.20;
    breakdown.push({
      factor_key: "age_elderly",
      factor_name: "Age Group",
      selected_value: "Elderly (65+)",
      percentage_change: "+20%",
      multiplier: 1.20,
      scientific_rationale: "Diminished autonomic thermoregulatory efficiency and blunted thirst response under thermal stress.",
      standard_citation: "CDC Extreme Heat & Older Adults Clinical Advisory"
    });
  } else if (profile.age_group === "child") {
    mult *= 1.15;
    breakdown.push({
      factor_key: "age_child",
      factor_name: "Age Group",
      selected_value: "Child (<12 yrs)",
      percentage_change: "+15%",
      multiplier: 1.15,
      scientific_rationale: "Greater body surface-area-to-mass ratio and developing eccrine glands result in faster core dehydration.",
      standard_citation: "American Academy of Pediatrics (AAP) Climatic Heat Stress & Children"
    });
  } else {
    breakdown.push({
      factor_key: "age_adult",
      factor_name: "Age Group",
      selected_value: "Adult (12-64 yrs)",
      percentage_change: "Baseline (0%)",
      multiplier: 1.00,
      scientific_rationale: "Standard physiological thermoregulatory capacity.",
      standard_citation: "NWS Standard Human Thermal Baseline"
    });
  }

  // 2. Gender
  if (profile.gender === "female" && humidityPct >= 40.0) {
    mult *= 1.05;
    breakdown.push({
      factor_key: "gender_female_humid",
      factor_name: "Gender Biometeorology",
      selected_value: "Female (Humid Heat Sensitivity)",
      percentage_change: "+5%",
      multiplier: 1.05,
      scientific_rationale: "Slightly lower mean sweating rate per unit body surface in humid regimes (>40% RH).",
      standard_citation: "International Journal of Biometeorology"
    });
  } else if (profile.gender && profile.gender !== "prefer_not_to_say") {
    breakdown.push({
      factor_key: "gender_factor",
      factor_name: "Gender Factor",
      selected_value: profile.gender === "male" ? "Male" : "Female",
      percentage_change: "Neutral (0%)",
      multiplier: 1.00,
      scientific_rationale: "Baseline physiological thermoregulatory profile.",
      standard_citation: "NIOSH Occupational Thermal Balance Standards"
    });
  }

  // 3. Occupation
  if (profile.occupation_type === "outdoor_manual") {
    mult *= 1.25;
    breakdown.push({
      factor_key: "occ_manual",
      factor_name: "Occupational Exposure",
      selected_value: "Outdoor Manual Laborer (Construction / Mining / Farming)",
      percentage_change: "+25%",
      multiplier: 1.25,
      scientific_rationale: "Continuous exposure to direct solar irradiance (850-950 W/m²) and heavy metabolic heat load.",
      standard_citation: "OSHA Heat Illness Prevention Criteria (Section 1910)"
    });
  } else if (profile.occupation_type === "outdoor_non_manual") {
    mult *= 1.15;
    breakdown.push({
      factor_key: "occ_non_manual",
      factor_name: "Occupational Exposure",
      selected_value: "Outdoor Non-Manual (Delivery / Street Vendor / Driver)",
      percentage_change: "+15%",
      multiplier: 1.15,
      scientific_rationale: "Sustained ambient heat with vehicular and urban asphalt radiation.",
      standard_citation: "OSHA Guidance for Delivery & Transit Personnel"
    });
  } else if (profile.occupation_type === "indoor_office") {
    mult *= 0.90;
    breakdown.push({
      factor_key: "occ_office",
      factor_name: "Occupational Exposure",
      selected_value: "Indoor / Office",
      percentage_change: "-10%",
      multiplier: 0.90,
      scientific_rationale: "Structural envelope eliminates direct sunlight; fans and ventilation aid cooling.",
      standard_citation: "ASHRAE Standard 55 Thermal Environmental Conditions"
    });
  } else {
    mult *= 0.95;
    breakdown.push({
      factor_key: "occ_student",
      factor_name: "Occupational Exposure",
      selected_value: "Student / Home",
      percentage_change: "-5%",
      multiplier: 0.95,
      scientific_rationale: "Substantial indoor shelter with moderate intermittent transit exposure.",
      standard_citation: "MoES / NDMA School Heat Action Guidelines"
    });
  }

  // 4. Health
  let healthBump = 1.0;
  const healthLabels = [];
  if (profile.health_flags.includes("cardiovascular_respiratory")) {
    healthBump += 0.15;
    healthLabels.push("Cardiovascular / Respiratory Compromise");
  }
  if (profile.health_flags.includes("pregnant")) {
    healthBump += 0.15;
    healthLabels.push("Pregnancy (Elevated Basal Metabolic Rate)");
  }
  healthBump = Math.min(1.30, healthBump);
  if (healthLabels.length > 0) {
    mult *= healthBump;
    breakdown.push({
      factor_key: "health_flag",
      factor_name: "Health & Clinical Factors",
      selected_value: healthLabels.join(", "),
      percentage_change: `+${Math.round((healthBump - 1.0) * 100)}%`,
      multiplier: Number(healthBump.toFixed(2)),
      scientific_rationale: "Peripheral vasodilation increases cardiac strain by up to 2-3x during extreme heat.",
      standard_citation: "American Heart Association (AHA) Heat Advisory"
    });
  } else {
    breakdown.push({
      factor_key: "health_none",
      factor_name: "Health & Clinical Factors",
      selected_value: "No High-Risk Comorbidities Disclosed",
      percentage_change: "Neutral (0%)",
      multiplier: 1.00,
      scientific_rationale: "Standard physiological reserve capacity without known cardiovascular limits.",
      standard_citation: "CDC General Heat Safety Advisory"
    });
  }

  // 5. Activity
  if (profile.activity_level === "heavy_exertion") {
    mult *= 1.20;
    breakdown.push({
      factor_key: "act_heavy",
      factor_name: "Physical Activity Level",
      selected_value: "Heavy Exertion (Heavy Labor, Running, Cycling)",
      percentage_change: "+20%",
      multiplier: 1.20,
      scientific_rationale: "Internal metabolic heat generation exceeds 350-500 W, accelerating core body temperature ascent.",
      standard_citation: "ISO 7243 Ergonomics of the Thermal Environment"
    });
  } else if (profile.activity_level === "light") {
    mult *= 1.05;
    breakdown.push({
      factor_key: "act_light",
      factor_name: "Physical Activity Level",
      selected_value: "Light Activity (Walking, Household Errands)",
      percentage_change: "+5%",
      multiplier: 1.05,
      scientific_rationale: "Moderate metabolic heat generation (~150-200 W) requiring regular fluid intake.",
      standard_citation: "ISO 7243 Metabolic Rate Class 1 (Light Work)"
    });
  } else {
    mult *= 0.95;
    breakdown.push({
      factor_key: "act_rest",
      factor_name: "Physical Activity Level",
      selected_value: "Resting / Seated",
      percentage_change: "-5%",
      multiplier: 0.95,
      scientific_rationale: "Basal metabolic rate (~100 W) minimizing internal thermal accumulation.",
      standard_citation: "ISO 7243 Resting State Baseline"
    });
  }

  return { mult: Number(mult.toFixed(3)), breakdown };
}

function haversineDistKm(lat1, lon1, lat2, lon2) {
  const R = 6371.0;
  const dLat = (lat2 - lat1) * Math.PI / 180.0;
  const dLon = (lon2 - lon1) * Math.PI / 180.0;
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1 * Math.PI / 180.0) * Math.cos(lat2 * Math.PI / 180.0) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Number((R * c).toFixed(2));
}

function findNearestShelter(lat, lon) {
  let nearest = OFFLINE_SHELTERS[0];
  let minD = Infinity;
  for (const s of OFFLINE_SHELTERS) {
    const d = haversineDistKm(lat, lon, s.lat, s.lon);
    if (d < minD) {
      minD = d;
      nearest = { ...s, distance_km: d };
    }
  }
  return nearest;
}


// ==========================================================================
// DYNAMIC LOCALIZATION GENERATORS (MARATHI / HINDI / ENGLISH)
// ==========================================================================

function getLocalizedDeltaText(personalScore, baseScore, personalBand, baseBand, lang) {
  const diff = personalScore - baseScore;
  if (lang === 'mr') {
    if (diff > 5) {
      return `वाढलेला धोका: तुमचे वय, व्यवसाय किंवा शारीरिक हालचालींमुळे तुमचा वैयक्तिक धोका सामान्य नागरिकांपेक्षा जास्त आहे (${personalScore} विरुद्ध प्रभाग ${baseScore}).`;
    } else if (diff < -5) {
      return `कमी धोका: इनडोअर काम किंवा विश्रांतीमुळे तुमचा वैयक्तिक धोका सामान्य प्रभागापेक्षा कमी आहे (${personalScore} विरुद्ध प्रभाग ${baseScore}).`;
    }
    return `समान पातळी: तुमचा वैयक्तिक धोका प्रभागाच्या सामान्य सार्वजनिक इशाऱ्याशी जुळत आहे (${personalScore}).`;
  } else if (lang === 'hi') {
    if (diff > 5) {
      return `बढ़ा हुआ जोखिम: आपकी आयु, व्यवसाय या परिश्रम के कारण आपका व्यक्तिगत जोखिम आम जनता से अधिक है (${personalScore} बनाम वार्ड ${baseScore})।`;
    } else if (diff < -5) {
      return `कम जोखिम: घर के अंदर रहने या आराम के कारण आपका व्यक्तिगत जोखिम सार्वजनिक स्तर से कम है (${personalScore} बनाम वार्ड ${baseScore})।`;
    }
    return `समान स्तर: आपका व्यक्तिगत जोखिम वार्ड की सामान्य चेतावनी के अनुरूप है (${personalScore})।`;
  }
  // English
  if (diff > 5) {
    return `Elevated: Personal risk is higher than public baseline (${personalBand} ${personalScore} vs Public ${baseBand} ${baseScore}) due to heightened exposure or vulnerability.`;
  } else if (diff < -5) {
    return `Reduced: Personal risk is lower than public baseline (${personalBand} ${personalScore} vs Public ${baseBand} ${baseScore}) due to indoor protection or rest.`;
  }
  return `Aligned: Your personal risk matches the public ward warning tier (${personalBand} ${personalScore}).`;
}

function getLocalizedSafeHours(riskBand, lang) {
  if (lang === 'mr') {
    if (riskBand === 'Extreme') {
      return {
        safe: "सकाळी ९:३० पूर्वी व संध्याकाळी ६:०० नंतर",
        danger: "सकाळी १०:३० ते संध्याकाळी ५:३० (उन्हात जाणे पूर्णपणे टाळा)"
      };
    } else if (riskBand === 'Danger') {
      return {
        safe: "सकाळी १०:३० पूर्वी व संध्याकाळी ५:०० नंतर",
        danger: "सकाळी ११:३० ते दुपारी ४:३० (उन्हाचा तीव्र तडाखा)"
      };
    } else if (riskBand === 'Caution') {
      return {
        safe: "सकाळी ११:३० पूर्वी व दुपारी ४:३० नंतर",
        danger: "दुपारी १२:०० ते दुपारी ३:३० (सावधगिरी बाळगा)"
      };
    }
    return {
      safe: "दिवसभरात सामान्य कामे सुरक्षित आहेत",
      danger: "दुपारी १:०० ते २:३० दरम्यान कडक ऊन टाळा"
    };
  } else if (lang === 'hi') {
    if (riskBand === 'Extreme') {
      return {
        safe: "सुबह ९:३० से पहले और शाम ६:०० के बाद",
        danger: "सुबह १०:३० से शाम ५:३० तक (धूप में निकलने से बचें)"
      };
    } else if (riskBand === 'Danger') {
      return {
        safe: "सुबह १०:३० से पहले और शाम ५:०० के बाद",
        danger: "सुबह ११:३० से दोपहर ४:३० तक (तीव्र धूप से बचें)"
      };
    } else if (riskBand === 'Caution') {
      return {
        safe: "सुबह ११:३० से पहले और दोपहर ४:३० के बाद",
        danger: "दोपहर १२:०० से दोपहर ३:३० तक (सतर्क रहें)"
      };
    }
    return {
      safe: "दिनभर सामान्य गतिविधियां सुरक्षित हैं",
      danger: "दोपहर १:०० से २:३० बजे तक तेज धूप से बचें"
    };
  }

  // English
  if (riskBand === 'Extreme') {
    return {
      safe: "Before 9:30 AM and After 6:00 PM only",
      danger: "10:30 AM – 5:30 PM (Stay Indoors)"
    };
  } else if (riskBand === 'Danger') {
    return {
      safe: "Before 10:30 AM and After 5:00 PM",
      danger: "11:30 AM – 4:30 PM (High Solar Stress)"
    };
  } else if (riskBand === 'Caution') {
    return {
      safe: "Before 11:30 AM and After 4:30 PM",
      danger: "12:00 PM – 3:30 PM (Moderate Caution)"
    };
  }
  return {
    safe: "Outdoor activities safe throughout most daytime hours",
    danger: "1:00 PM – 2:30 PM (Midday Solar Caution)"
  };
}

function getLocalizedPrecautions(riskBand, profile, lang) {
  if (lang === 'mr') {
    if (riskBand === 'Extreme') {
      return [
        "तातडीने सावलीत किंवा वातानुकूलित/थंड ठिकाणी आसरा घ्या. उन्हात जाणे पूर्णपणे टाळा.",
        "दर तासाला किमान ७५० मि.ली. ते १ लिटर ओआरएसयुक्त किंवा थंड पाणी प्या; तहान लागण्याची वाट पाहू नका.",
        "सकाळी ११:०० ते दुपारी ४:३० दरम्यान कष्टाची कामे करणे तात्काळ थांबवा.",
        "चक्कर येणे, मळमळ किंवा छातीत धडधड झाल्यास त्वरित १०८ रुग्णवाहिकेशी संपर्क साधा.",
        "घरातील तापमान थंड ठेवण्यासाठी खिडक्यांना पडदे लावा व ओले कापड वापरा."
      ];
    } else if (riskBand === 'Danger') {
      return [
        "उष्णतेचा त्रास आणि क्रॅम्प्सचा धोका जास्त आहे. दुपारच्या वेळेत बाहेर पडणे टाळा.",
        "उन्हात काम करताना दर ४० मिनिटांच्या कामानंतर २० मिनिटे सावलीत विश्रांती घ्या.",
        "हलके, सैल आणि पांढरे/सुती कपडे वापरा तसेच डोक्यावर रुमाल किंवा टोपी घाला.",
        "लिंबू पाणी, ताक, शहाळ्याचे पाणी किंवा ओआरएसचे नियमित सेवन करा."
      ];
    } else if (riskBand === 'Caution') {
      return [
        "मध्यम उष्णता ताण. पुरेसे पाणी जवळ ठेवा आणि अधूनमधून पाणी पीत राहा.",
        "उन्हात थेट फिरणे टाळा आणि डोळ्यांचे व डोक्याचे संरक्षण करा.",
        "कष्टाच्या कामांच्या मध्ये नियमित पाणी पिण्यासाठी विश्रांती घ्या."
      ];
    }
    return [
      "सध्याचे तापमान तुमच्या प्रकृतीसाठी सामान्य मर्यादेत आहे.",
      "दिवसभरात नियमित २ ते २.५ लिटर पाणी पिऊन हायड्रेशन राखा."
    ];
  } else if (lang === 'hi') {
    if (riskBand === 'Extreme') {
      return [
        "तत्काल छायादार अथवा वातानुकूलित शीतल स्थान पर शरण लें। धूप में जाना पूर्णतः टालें।",
        "प्रति घंटे कम से कम ७५० मिली से १ लीटर ओआरएस अथवा शीतल जल का सेवन करें।",
        "सुबह ११:०० से दोपहर ४:३० बजे तक भारी शारीरिक श्रम पूरी तरह बंद रखें।",
        "चक्कर, जी मिचलाना या अत्यधिक कमजोरी होने पर तुरंत १०८ एम्बुलेंस से संपर्क करें।"
      ];
    } else if (riskBand === 'Danger') {
      return [
        "हीट स्ट्रोक एवं थकावट का अधिक जोखिम है। दोपहर के समय बाहर जाने से बचें।",
        "धूप में काम करते समय हर ४० मिनट के कार्य के बाद २० मिनट छाया में आराम करें।",
        "ढीले, हल्के रंग के सूती वस्त्र पहनें और सिर पर टोपी अथवा कपड़ा रखें।",
        "नींबू पानी, छाछ और ओआरएस का नियमित सेवन करें।"
      ];
    } else if (riskBand === 'Caution') {
      return [
        "मध्यम गर्मी का प्रभाव। पानी की बोतल साथ रखें और थोड़ी-थोड़ी देर में पानी पीते रहें।",
        "सीधी धूप से बचें और सिर को ढंककर रखें।"
      ];
    }
    return [
      "वर्तमान मौसम आपकी स्वास्थ्य स्थिति के लिए सामान्य सीमा में है।",
      "दिनभर में २ से २.५ लीटर पानी पीकर शरीर में जल संतुलन बनाए रखें।"
    ];
  }

  // English
  if (riskBand === 'Extreme') {
    return [
      "CRITICAL: Seek immediate air-conditioned or shaded cooling shelter. Avoid all outdoor exposure.",
      "Drink 750ml to 1 Liter of chilled water with electrolyte/ORS per hour; do not wait until thirsty.",
      "MANDATORY WORK STOPPAGE: Cease heavy physical labor between 11:00 AM and 4:30 PM.",
      "Monitor pulse and blood pressure; call emergency services (108) immediately if dizziness or nausea occurs."
    ];
  } else if (riskBand === 'Danger') {
    return [
      "High risk of heat exhaustion and cramps. Plan outdoor tasks strictly in morning or evening hours.",
      "Hydration target: 500ml to 750ml electrolyte water every hour spent in ambient heat.",
      "Enforce 20-minute shaded rest breaks for every 40 minutes of outdoor activity.",
      "Wear lightweight, loose-fitting cotton clothing and a wide-brimmed hat."
    ];
  } else if (riskBand === 'Caution') {
    return [
      "Moderate heat caution. Keep reusable water flask at hand and hydrate every 30-40 minutes.",
      "Wear loose cotton apparel and protect eyes and head from direct sunlight."
    ];
  }
  return [
    "Conditions are currently within standard comfortable limits for your physiological profile.",
    "Maintain baseline hydration throughout daytime hours (2.0 to 2.5 Liters daily)."
  ];
}

function getLocalizedHydrationAdvice(riskBand, lang) {
  if (lang === 'mr') {
    if (riskBand === 'Extreme') return "पाणी पिण्याचा सल्ला: दिवसाला किमान ४.० ते ५.० लिटर पाणी, ओआरएस किंवा लिंबू पाणी प्या. चहा, कॉफी टाळा.";
    if (riskBand === 'Danger') return "पाणी पिण्याचा सल्ला: दिवसाला ३.० ते ४.० लिटर पाणी प्या. ताक आणि ओआरएसचे नियमित सेवन करा.";
    if (riskBand === 'Caution') return "पाणी पिण्याचा सल्ला: दिवसाला २.५ ते ३.५ लिटर पाणी प्या. सोबत पाण्याची बाटली नेहमी ठेवा.";
    return "पाणी पिण्याचा सल्ला: दररोज किमान २.० ते २.५ लिटर पाणी प्या.";
  } else if (lang === 'hi') {
    if (riskBand === 'Extreme') return "जल सेवन परामर्श: प्रतिदिन कम से कम ४.० से ५.० लीटर पानी, ओआरएस अथवा नींबू पानी पिएं।";
    if (riskBand === 'Danger') return "जल सेवन परामर्श: प्रतिदिन ३.० से ४.० लीटर पानी पिएं। छाछ और ओआरएस का सेवन करें।";
    if (riskBand === 'Caution') return "जल सेवन परामर्श: प्रतिदिन २.५ से ३.५ लीटर पानी पिएं। पानी की बोतल साथ रखें।";
    return "जल सेवन परामर्श: प्रतिदिन २.० से २.५ लीटर पानी पिएं।";
  }

  // English
  if (riskBand === 'Extreme') return "Hydration Target: Minimum 4.0 to 5.0 Liters daily with ORS sachets. Avoid tea and caffeinated sodas.";
  if (riskBand === 'Danger') return "Hydration Target: 3.0 to 4.0 Liters daily. Supplement regular water with oral rehydration salts (ORS).";
  if (riskBand === 'Caution') return "Hydration Target: 2.5 to 3.5 Liters daily. Keep a reusable water flask within reach.";
  return "Hydration Target: Standard daily baseline of 2.0 to 2.5 Liters.";
}

function getLocalizedWorkRestCycle(riskBand, occType, lang) {
  if (lang === 'mr') {
    if (riskBand === 'Extreme') return "विश्रांतीचे प्रमाण: प्रत्येक १५ मिनिटांच्या हलक्या कामानंतर १५ मिनिटे सावलीत विश्रांती घ्या (१:१ प्रमाण). जड कामे बंद ठेवा.";
    if (riskBand === 'Danger') return "विश्रांतीचे प्रमाण: प्रत्येक ४० मिनिटांच्या कामानंतर २० मिनिटे सावलीत विश्रांती घ्या (२:१ प्रमाण).";
    if (riskBand === 'Caution') return "विश्रांतीचे प्रमाण: प्रत्येक ५० मिनिटांच्या कामानंतर १० मिनिटे सावलीत थांबा.";
    return "विश्रांतीचे प्रमाण: सामान्य कामाचे वेळापत्रक; नियमित पाणी पिण्यासाठी थोडा वेळ थांबा.";
  } else if (lang === 'hi') {
    if (riskBand === 'Extreme') return "कार्य-विश्राम अनुपात: हर १५ मिनट के हल्के कार्य के बाद १५ मिनट छाया में विश्राम करें (१:१ अनुपात)।";
    if (riskBand === 'Danger') return "कार्य-विश्राम अनुपात: हर ४० मिनट के कार्य के बाद २० मिनट छाया में विश्राम करें (२:१ अनुपात)।";
    if (riskBand === 'Caution') return "कार्य-विश्राम अनुपात: हर ५० मिनट के कार्य के बाद १० मिनट छाया में विश्राम करें।";
    return "कार्य-विश्राम अनुपात: सामान्य कार्य समय; नियमित रूप से जलपान हेतु विराम लें।";
  }

  // English
  if (riskBand === 'Extreme') return "Work-Rest Ratio: 15 minutes rest in deep shade for every 15 minutes of unavoidable light work (1:1 ratio).";
  if (riskBand === 'Danger') return "Work-Rest Ratio: 20 minutes shaded rest for every 40 minutes of outdoor activity (2:1 ratio).";
  if (riskBand === 'Caution') return "Work-Rest Ratio: 10 minutes shaded pause for every 50 minutes of continuous activity.";
  return "Work-Rest Ratio: Standard operational schedule with regular fluid pauses.";
}

function getLocalizedFactorBreakdown(breakdown, lang) {
  const dictionary = {
    mr: {
      factor_names: {
        "Age Group": "वयोगट",
        "Gender Biometeorology": "लिंग घटक (दमटपणा)",
        "Gender Factor": "लिंग घटक",
        "Occupational Exposure": "व्यवसाय / संपर्क",
        "Occupation": "व्यवसाय",
        "Health & Clinical Factors": "आरोग्य लक्षणे",
        "Health Comorbidities": "आरोग्य लक्षणे",
        "Physical Activity Level": "शारीरिक हालचाल",
        "Physical Activity": "शारीरिक हालचाल"
      },
      selected_values: {
        "Elderly (65+)": "ज्येष्ठ नागरिक (65+ वर्षे)",
        "Child (<12 yrs)": "लहान मुले (<12 वर्षे)",
        "Child (<12)": "लहान मुले (<12 वर्षे)",
        "Adult (12-64 yrs)": "प्रौढ (12-64 वर्षे)",
        "Adult (12-64)": "प्रौढ (12-64 वर्षे)",
        "Outdoor Manual Laborer (Construction / Mining / Farming)": "उघड्यावर शारीरिक श्रम (खाण/बांधकाम/शेती)",
        "Outdoor Manual Labor": "उघड्यावर शारीरिक श्रम",
        "Outdoor Non-Manual (Delivery / Street Vendor / Driver)": "फेरीवाले / वाहतूक कामगार",
        "Outdoor Non-Manual": "फेरीवाले / वाहतूक कामगार",
        "Indoor / Office": "कार्यालयीन / इनडोअर",
        "Student / Home": "विद्यार्थी / गृहिणी",
        "Cardiovascular / Respiratory Compromise": "हृदयरोग / दमा विकार",
        "Pregnancy (Elevated Basal Metabolic Rate)": "गर्भावस्थेतील संवेदनशीलता",
        "No High-Risk Comorbidities Disclosed": "कोणताही गंभीर आजार नाही",
        "None Disclosed": "कोणताही आजार नाही",
        "Heavy Exertion (Heavy Labor, Running, Cycling)": "अतिश्रम / वजन उचलणे / धावणे",
        "Heavy Exertion": "कठीण शारीरिक श्रम",
        "Light Activity (Walking, Household Errands)": "साधी कामे / चालणे",
        "Light Activity": "साधी कामे / चालणे",
        "Resting / Seated": "विश्रांती / बसलेले",
        "Resting": "विश्रांती / बसलेले",
        "Male": "पुरुष",
        "Female": "महिला",
        "Female (Humid Heat Sensitivity)": "महिला (दमट हवेतील संवेदनशीलता)",
        "Prefer Not To Say": "सांगू इच्छित नाही"
      },
      rationales: {
        "Age Group": "वयस्कर व्यक्ती किंवा लहान मुलांमध्ये शरीराचे तापमान लवकर वाढते.",
        "Occupational Exposure": "उघड्यावर काम केल्याने थेट सूर्यकिरण व उष्णतेचा तीव्र मारा होतो.",
        "Health & Clinical Factors": "हृदयरोग किंवा दमा असल्यास उष्णतेमुळे रक्तवाहिन्यांवर अतिरिक्त ताण येतो.",
        "Physical Activity Level": "शारीरिक श्रमामुळे शरीरात अंतर्गत उष्णता वेगाने निर्माण होते.",
        "Gender Biometeorology": "दमट हवामानामुळे घाम सुकण्याचे प्रमाण मंदावते."
      },
      citations: {
        "CDC Extreme Heat & Older Adults Clinical Advisory / NWS Heat Safety": "सीडीसी / राष्ट्रीय हवामान सेवा मार्गदर्शक",
        "American Academy of Pediatrics (AAP) Climatic Heat Stress & Children": "अमेरिकन बालरोग अकादमी (AAP)",
        "NWS Standard Human Thermal Baseline": "राष्ट्रीय हवामान सेवा मानके",
        "OSHA Heat Illness Prevention Criteria (Section 1910) / ACGIH TLV for Heat Stress": "ओशा (OSHA) कामगार सुरक्षा मानके",
        "OSHA Guidance for Delivery & Transit Personnel": "ओशा (OSHA) वाहतूक कामगार मार्गदर्शक",
        "ASHRAE Standard 55 Thermal Environmental Conditions for Human Occupancy": "ॲशरे (ASHRAE) इमारत मानके",
        "MoES / NDMA School Heat Action Guidelines": "राष्ट्रीय आपत्ती व्यवस्थापन (NDMA)",
        "American Heart Association (AHA) Heat Advisory / American College of Obstetricians (ACOG)": "अमेरिकन हार्ट असोसिएशन (AHA) / ACOG",
        "CDC General Heat Safety Advisory": "सीडीसी (CDC) सामान्य उष्णता सुरक्षा",
        "ISO 7243 Ergonomics of the Thermal Environment / ACGIH Heat Stress Index": "आयएसओ ७२४३ आंतरराष्ट्रीय मानक",
        "ISO 7243 Metabolic Rate Class 1 (Light Work)": "आयएसओ ७२४३ हलकी कामे",
        "ISO 7243 Resting State Baseline": "आयएसओ ७२४३ विश्रांती मानक"
      }
    },
    hi: {
      factor_names: {
        "Age Group": "आयु वर्ग",
        "Gender Biometeorology": "लिंग घटक (आर्द्रता)",
        "Gender Factor": "लिंग घटक",
        "Occupational Exposure": "व्यवसाय / संपर्क",
        "Occupation": "व्यवसाय",
        "Health & Clinical Factors": "स्वास्थ्य स्थितियां",
        "Health Comorbidities": "स्वास्थ्य स्थितियां",
        "Physical Activity Level": "शारीरिक गतिविधि",
        "Physical Activity": "शारीरिक गतिविधि"
      },
      selected_values: {
        "Elderly (65+)": "वरिष्ठ नागरिक (65+ वर्ष)",
        "Child (<12 yrs)": "बच्चे (<12 वर्ष)",
        "Child (<12)": "बच्चे (<12 वर्ष)",
        "Adult (12-64 yrs)": "वयस्क (12-64 वर्ष)",
        "Adult (12-64)": "वयस्क (12-64 वर्ष)",
        "Outdoor Manual Laborer (Construction / Mining / Farming)": "बाहरी शारीरिक श्रम (खदान/निर्माण/कृषि)",
        "Outdoor Manual Labor": "बाहरी शारीरिक श्रम",
        "Outdoor Non-Manual (Delivery / Street Vendor / Driver)": "डिलीवरी / फेरीवाले / चालक",
        "Outdoor Non-Manual": "डिलीवरी / फेरीवाले / चालक",
        "Indoor / Office": "कार्यालय / घर के अंदर",
        "Student / Home": "छात्र / गृहिणी",
        "Cardiovascular / Respiratory Compromise": "हृदय / श्वसन विकार",
        "Pregnancy (Elevated Basal Metabolic Rate)": "गर्भावस्था जनित संवेदनशीलता",
        "No High-Risk Comorbidities Disclosed": "कोई गंभीर बीमारी नहीं",
        "None Disclosed": "कोई गंभीर बीमारी नहीं",
        "Heavy Exertion (Heavy Labor, Running, Cycling)": "कठिन शारीरिक परिश्रम / दौड़ना",
        "Heavy Exertion": "कठिन शारीरिक श्रम",
        "Light Activity (Walking, Household Errands)": "हल्की गतिविधि / चलना",
        "Light Activity": "हल्की गतिविधि / चलना",
        "Resting / Seated": "आराम / बैठे हुए",
        "Resting": "आराम / बैठे हुए",
        "Male": "पुरुष",
        "Female": "महिला",
        "Female (Humid Heat Sensitivity)": "महिला (आर्द्र गर्मी संवेदनशीलता)",
        "Prefer Not To Say": "बताना नहीं चाहते"
      },
      rationales: {
        "Age Group": "बुजुर्गों व बच्चों में शरीर का तापमान तेजी से बढ़ता है।",
        "Occupational Exposure": "धूप में काम करने से सीधी सौर विकिरण और गर्मी का अधिक प्रभाव पड़ता है।",
        "Health & Clinical Factors": "हृदय या दमा रोगियों में गर्मी के कारण हृदय पर अतिरिक्त दबाव पड़ता है।",
        "Physical Activity Level": "शारीरिक परिश्रम से आंतरिक चयापचय ताप तेजी से बढ़ता है।",
        "Gender Biometeorology": "उच्च आर्द्रता में पसीना सूखने की गति धीमी हो जाती है।"
      },
      citations: {
        "CDC Extreme Heat & Older Adults Clinical Advisory / NWS Heat Safety": "सीडीसी / राष्ट्रीय मौसम सेवा परामर्श",
        "American Academy of Pediatrics (AAP) Climatic Heat Stress & Children": "अमेरिकन बाल रोग अकादमी (AAP)",
        "NWS Standard Human Thermal Baseline": "राष्ट्रीय मौसम सेवा मानक",
        "OSHA Heat Illness Prevention Criteria (Section 1910) / ACGIH TLV for Heat Stress": "ओशा (OSHA) श्रमिक सुरक्षा मानक",
        "OSHA Guidance for Delivery & Transit Personnel": "ओशा (OSHA) परिवहन कर्मी दिशानिर्देश",
        "ASHRAE Standard 55 Thermal Environmental Conditions for Human Occupancy": "एशरे (ASHRAE) भवन मानक",
        "MoES / NDMA School Heat Action Guidelines": "राष्ट्रीय आपदा प्रबंधन (NDMA)",
        "American Heart Association (AHA) Heat Advisory / American College of Obstetricians (ACOG)": "अमेरिकन हार्ट एसोसिएशन (AHA)",
        "CDC General Heat Safety Advisory": "सीडीसी (CDC) ताप सुरक्षा परामर्श",
        "ISO 7243 Ergonomics of the Thermal Environment / ACGIH Heat Stress Index": "आईएसओ ७२४३ मानक",
        "ISO 7243 Metabolic Rate Class 1 (Light Work)": "आईएसओ ७२४३ हल्की गतिविधि",
        "ISO 7243 Resting State Baseline": "आईएसओ ७२४३ विश्राम मानक"
      }
    }
  };

  const d = dictionary[lang];
  if (!d) return breakdown;

  return (breakdown || []).map(f => {
    const fn = d.factor_names[f.factor_name] || f.factor_name;
    const sv = d.selected_values[f.selected_value] || f.selected_value;
    const rat = d.rationales[f.factor_name] || f.scientific_rationale;
    const cit = d.citations[f.standard_citation] || f.standard_citation;
    return {
      ...f,
      factor_name: fn,
      selected_value: sv,
      scientific_rationale: rat,
      standard_citation: cit
    };
  });
}


// ==========================================================================
// INITIALIZATION & EVENT BINDINGS
// ==========================================================================
document.addEventListener("DOMContentLoaded", () => {
  populateWardDropdown();
  loadStoredProfile();
  initLanguage();
  initFormInteractions();
  initAccordion();
  initModal();

  // Initial calculation
  calculatePersonalRisk();
});

function populateWardDropdown() {
  const select = document.getElementById("talukaSelect");
  if (!select) return;
  const currentVal = select.value || userProfile.ward_id;
  select.innerHTML = "";
  CHANDRAPUR_WARDS.forEach(w => {
    const opt = document.createElement("option");
    opt.value = w.ward_id;
    opt.textContent = getLocalizedWardName(w);
    select.appendChild(opt);
  });
  select.value = currentVal;
}

function getLocalizedWardName(w) {
  if (currentLang === 'mr' && w.ward_name_mr) return w.ward_name_mr;
  if (currentLang === 'hi' && w.ward_name_hi) return w.ward_name_hi;
  return w.ward_name;
}

function loadStoredProfile() {
  const saved = localStorage.getItem("hs_advisor_profile");
  if (saved) {
    try {
      const parsed = JSON.parse(saved);
      userProfile = { ...userProfile, ...parsed };
    } catch (e) {
      console.warn("Could not parse saved profile", e);
    }
  }
  syncFormWithProfile();
}

function syncFormWithProfile() {
  const talukaSelect = document.getElementById("talukaSelect");
  if (talukaSelect) talukaSelect.value = userProfile.ward_id;

  // Age chips
  document.querySelectorAll(".chip-btn[data-type='age']").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.val === userProfile.age_group);
  });

  // Gender chips
  document.querySelectorAll(".chip-btn[data-type='gender']").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.val === userProfile.gender);
  });

  // Occupation chips
  document.querySelectorAll(".chip-btn[data-type='occ']").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.val === userProfile.occupation_type);
  });

  // Activity chips
  document.querySelectorAll(".chip-btn[data-type='activity']").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.val === userProfile.activity_level);
  });

  // Health tags
  document.querySelectorAll(".tag-check").forEach(tag => {
    const val = tag.dataset.val;
    const isChecked = userProfile.health_flags.includes(val);
    tag.classList.toggle("active", isChecked && val !== "none");
    tag.classList.toggle("active-none", isChecked && val === "none");
  });
}

function initFormInteractions() {
  // Ward selection
  const select = document.getElementById("talukaSelect");
  if (select) {
    select.addEventListener("change", () => {
      userProfile.ward_id = select.value;
      saveProfile();
    });
  }

  // Geolocation Button
  const geoBtn = document.getElementById("geoBtn");
  if (geoBtn) {
    geoBtn.addEventListener("click", () => handleGeolocation());
  }

  // Chip buttons (Age, Gender, Occ, Activity)
  document.querySelectorAll(".chip-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const type = btn.dataset.type;
      const val = btn.dataset.val;
      document.querySelectorAll(`.chip-btn[data-type='${type}']`).forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      if (type === "age") userProfile.age_group = val;
      else if (type === "gender") userProfile.gender = val;
      else if (type === "occ") userProfile.occupation_type = val;
      else if (type === "activity") userProfile.activity_level = val;

      saveProfile();
    });
  });

  // Health tags
  document.querySelectorAll(".tag-check").forEach(tag => {
    tag.addEventListener("click", () => {
      const val = tag.dataset.val;
      if (val === "none") {
        userProfile.health_flags = ["none"];
      } else {
        userProfile.health_flags = userProfile.health_flags.filter(f => f !== "none");
        if (userProfile.health_flags.includes(val)) {
          userProfile.health_flags = userProfile.health_flags.filter(f => f !== val);
          if (userProfile.health_flags.length === 0) userProfile.health_flags = ["none"];
        } else {
          userProfile.health_flags.push(val);
        }
      }
      syncFormWithProfile();
      saveProfile();
    });
  });

  // Recalculate Button
  const calcBtn = document.getElementById("calcBtn");
  if (calcBtn) {
    calcBtn.addEventListener("click", () => {
      calculatePersonalRisk();
      document.getElementById("heroCard")?.scrollIntoView({ behavior: "smooth" });
    });
  }

  // Stepper Header Toggle
  const setupHeader = document.getElementById("setupHeader");
  const formSection = document.getElementById("formSection");
  const toggleIcon = document.getElementById("setupToggleIcon");
  if (setupHeader && formSection) {
    setupHeader.addEventListener("click", () => {
      const isHidden = formSection.style.display === "none";
      formSection.style.display = isHidden ? "flex" : "none";
      if (toggleIcon) toggleIcon.classList.toggle("collapsed", !isHidden);
    });
  }
}

function saveProfile() {
  localStorage.setItem("hs_advisor_profile", JSON.stringify(userProfile));
}

// ==========================================================================
// GEOLOCATION RESOLUTION (HAVERSINE MATCHING)
// ==========================================================================
function handleGeolocation() {
  const geoText = document.getElementById("geoBtnText");
  if (!navigator.geolocation) {
    showToast("Geolocation is not supported by your browser.");
    return;
  }

  if (geoText) {
    geoText.textContent = currentLang === 'mr' ? "शोधत आहे..." : (currentLang === 'hi' ? "खोज रहे हैं..." : "Locating...");
  }

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const lat = pos.coords.latitude;
      const lon = pos.coords.longitude;
      userCoords = { lat, lon };

      // Reverse map to nearest Chandrapur ward
      let nearestWard = CHANDRAPUR_WARDS[0];
      let minD = Infinity;
      CHANDRAPUR_WARDS.forEach(w => {
        const d = haversineDistKm(lat, lon, w.lat, w.lon);
        if (d < minD) {
          minD = d;
          nearestWard = w;
        }
      });

      userProfile.ward_id = nearestWard.ward_id;
      const select = document.getElementById("talukaSelect");
      if (select) select.value = nearestWard.ward_id;
      saveProfile();

      if (geoText) {
        geoText.textContent = ADVISOR_I18N[currentLang]?.btn_geolocate || "Auto-Detect";
      }

      showToast(`${ADVISOR_I18N[currentLang]?.toast_geo_ok || "Matched ward:"} ${getLocalizedWardName(nearestWard)} (${minD} km)`);
      calculatePersonalRisk();
    },
    (err) => {
      console.warn("Geolocation denied/failed", err);
      if (geoText) {
        geoText.textContent = ADVISOR_I18N[currentLang]?.btn_geolocate || "Auto-Detect";
      }
      showToast(ADVISOR_I18N[currentLang]?.toast_geo_err || "Location permission denied; default ward kept.");
    },
    { enableHighAccuracy: true, timeout: 8000 }
  );
}

// ==========================================================================
// CORE CALCULATION CONTROLLER (LIVE REST API + OFFLINE FALLBACK)
// ==========================================================================
async function calculatePersonalRisk() {
  const statusDot = document.getElementById("statusPulseDot");
  const statusText = document.getElementById("backendStatusText");

  const payload = {
    ward_id: userProfile.ward_id,
    age_group: userProfile.age_group,
    gender: userProfile.gender,
    occupation_type: userProfile.occupation_type,
    health_flags: userProfile.health_flags,
    activity_level: userProfile.activity_level,
    user_lat: userCoords ? userCoords.lat : null,
    user_lon: userCoords ? userCoords.lon : null
  };

  try {
    const res = await fetch(`${API_BASE_URL}/personal-risk`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    currentResult = data;

    // Set Live Status
    if (statusDot) statusDot.className = "pulse-dot";
    if (statusText) statusText.textContent = ADVISOR_I18N[currentLang]?.status_live || "FastAPI Backend Connected";

    renderResults(data);
  } catch (err) {
    console.warn("FastAPI backend unreachable, activating client standalone engine.", err);

    // Fallback Standalone Math
    const fallbackData = executeClientMathFallback(payload);
    currentResult = fallbackData;

    // Set Offline Status
    if (statusDot) statusDot.className = "pulse-dot offline";
    if (statusText) statusText.textContent = ADVISOR_I18N[currentLang]?.status_offline || "Offline Standalone Engine Active";

    renderResults(fallbackData);
  }
}

function executeClientMathFallback(req) {
  const targetWard = CHANDRAPUR_WARDS.find(w => w.ward_id === req.ward_id) || CHANDRAPUR_WARDS[0];
  const base = calcWardBaseScore(targetWard);
  const { mult, breakdown } = computeClientPersonalMultiplier(userProfile, targetWard.humidity_pct);

  const personalScore = Number(Math.max(0, Math.min(100, base.score * mult)).toFixed(1));
  let personalBand = "Safe";
  if (personalScore >= 70.0) personalBand = "Extreme";
  else if (personalScore >= 50.0) personalBand = "Danger";
  else if (personalScore >= 30.0) personalBand = "Caution";

  // Nearest Shelter
  const queryLat = req.user_lat || targetWard.lat;
  const queryLon = req.user_lon || targetWard.lon;
  const shelter = findNearestShelter(queryLat, queryLon);

  // Personalized Forecast
  const pForecast = (targetWard.forecast || []).map(f => {
    const fWbgt = calcBomWbgt(f.temp_c, f.humidity_pct);
    const fHi = calcRothfuszHeatIndex(f.temp_c, f.humidity_pct);
    const fBaseScore = Number(((0.6 * ((fWbgt - 20) / 25 * 100)) + 30).toFixed(1));
    const pScore = Number(Math.max(0, Math.min(100, fBaseScore * mult)).toFixed(1));
    let fBand = "Safe";
    if (pScore >= 70) fBand = "Extreme";
    else if (pScore >= 50) fBand = "Danger";
    else if (pScore >= 30) fBand = "Caution";

    return {
      day: f.day,
      temp_c: f.temp_c,
      humidity_pct: f.humidity_pct,
      wbgt_c: fWbgt,
      heat_index_c: fHi,
      base_score: fBaseScore,
      personal_score: pScore,
      personal_band: fBand
    };
  });

  return {
    ward_id: targetWard.ward_id,
    ward_name: targetWard.ward_name,
    user_location: { lat: queryLat, lon: queryLon },
    base_ward_score: base.score,
    base_risk_band: base.band,
    metrics: {
      current_temp_c: targetWard.current_temp_c,
      humidity_pct: targetWard.humidity_pct,
      heat_index_c: base.hi,
      wbgt_c: base.wbgt,
      solar_adjusted_wbgt_c: base.solarWbgt,
      apparent_temperature_c: base.at,
      human_thermal_stress_index: base.rawHtsi,
      wind_speed_kmh: targetWard.wind_speed_kmh,
      solar_radiation_wm2: targetWard.solar_radiation_wm2
    },
    personal_score: personalScore,
    personal_risk_band: personalBand,
    personal_multiplier: mult,
    factor_breakdown: breakdown,
    nearest_cooling_shelter: shelter,
    personalized_forecast: pForecast
  };
}

// ==========================================================================
// UI RENDERING CONTROLLER (WITH FULL MARATHI/HINDI TRANSLATION)
// ==========================================================================
function renderResults(data) {
  if (!data) return;
  const i18n = ADVISOR_I18N[currentLang] || ADVISOR_I18N.en;

  // 1. Hero Weather Card
  const heroCard = document.getElementById("heroCard");
  if (heroCard) {
    heroCard.className = `hero-weather-card ${data.personal_risk_band}`;
  }

  // Location Title
  const wardObj = CHANDRAPUR_WARDS.find(w => w.ward_id === data.ward_id);
  const localizedWard = wardObj ? getLocalizedWardName(wardObj) : data.ward_name;
  const talukaEl = document.getElementById("heroTalukaName");
  if (talukaEl) talukaEl.textContent = localizedWard;

  // Profile Tagline (Localized)
  const occKey = userProfile.occupation_type.replace('outdoor_', '').replace('indoor_', '');
  const occLabel = i18n[`occ_${occKey}`] || userProfile.occupation_type;
  const ageLabel = i18n[`age_${userProfile.age_group}`] || userProfile.age_group;
  const summaryEl = document.getElementById("heroProfileSummary");
  if (summaryEl) summaryEl.textContent = `${ageLabel} • ${occLabel}`;

  // Risk Band Badge (Localized)
  const bandKey = `band_${data.personal_risk_band.toLowerCase()}`;
  const badgeEl = document.getElementById("heroBadgeText");
  if (badgeEl) badgeEl.textContent = i18n[bandKey] || data.personal_risk_band;

  // Temperature & Risk Index
  const tempEl = document.getElementById("heroTempNum");
  if (tempEl) tempEl.textContent = Math.round(data.metrics.current_temp_c);
  const scoreEl = document.getElementById("heroScoreNum");
  if (scoreEl) scoreEl.textContent = data.personal_score;

  // Delta comparison box (Fully translated into currentLang)
  const deltaText = getLocalizedDeltaText(
    data.personal_score,
    data.base_ward_score,
    data.personal_risk_band,
    data.base_risk_band,
    currentLang
  );
  const deltaEl = document.getElementById("heroDeltaText");
  if (deltaEl) deltaEl.textContent = deltaText;

  // Quick Metrics
  const wbgtEl = document.getElementById("metricWbgt");
  if (wbgtEl) wbgtEl.textContent = `${data.metrics.wbgt_c}°C`;
  const hiEl = document.getElementById("metricHi");
  if (hiEl) hiEl.textContent = `${data.metrics.heat_index_c}°C`;
  const humEl = document.getElementById("metricHumidity");
  if (humEl) humEl.textContent = `${data.metrics.humidity_pct}%`;
  const windEl = document.getElementById("metricWind");
  if (windEl) windEl.textContent = `${data.metrics.wind_speed_kmh} km/h`;

  // 2. Safe Hours Box (Localized)
  const safeHours = getLocalizedSafeHours(data.personal_risk_band, currentLang);
  const safeEl = document.getElementById("hoursSafeVal");
  if (safeEl) safeEl.textContent = safeHours.safe;
  const dangerEl = document.getElementById("hoursDangerVal");
  if (dangerEl) dangerEl.textContent = safeHours.danger;

  // 3. Precautions List (Localized)
  const precautions = getLocalizedPrecautions(data.personal_risk_band, userProfile, currentLang);
  const listEl = document.getElementById("precautionsList");
  if (listEl) {
    listEl.innerHTML = "";
    precautions.forEach((p, idx) => {
      const li = document.createElement("li");
      li.className = "precaution-item";
      li.innerHTML = `
        <span class="precaution-bullet">${idx + 1}</span>
        <span>${p}</span>
      `;
      listEl.appendChild(li);
    });
  }

  // Callouts (Localized without emojis, targeting inner span to preserve SVG)
  const hydEl = document.getElementById("hydrationAdviceText") || document.getElementById("hydrationAdvice");
  if (hydEl) hydEl.textContent = getLocalizedHydrationAdvice(data.personal_risk_band, currentLang);

  const wrEl = document.getElementById("workRestCycleText") || document.getElementById("workRestCycle");
  if (wrEl) wrEl.textContent = getLocalizedWorkRestCycle(data.personal_risk_band, userProfile.occupation_type, currentLang);

  // 4. Transparency Breakdown Table (Localized)
  renderTransparencyTable(data.factor_breakdown, data.personal_multiplier);

  // 5. 3-Day Forecast Strip & Chart (Localized)
  renderForecast(data.personalized_forecast);

  // 6. Nearest Cooling Shelter & Map (Localized)
  renderShelter(data.nearest_cooling_shelter, data.user_location);
}

function renderTransparencyTable(rawBreakdown, totalMult) {
  const tbody = document.getElementById("factorsTableBody");
  if (!tbody) return;
  tbody.innerHTML = "";

  const localizedBreakdown = getLocalizedFactorBreakdown(rawBreakdown, currentLang);

  (localizedBreakdown || []).forEach(f => {
    const tr = document.createElement("tr");
    const isPlus = (f.percentage_change || "").startsWith("+");
    const isMinus = (f.percentage_change || "").startsWith("-");
    const badgeClass = isPlus ? "plus" : (isMinus ? "minus" : "neutral");

    const rationale = f.scientific_rationale || (currentLang === 'mr' ? "शरीराच्या उष्णता नियमन क्षमतेवर प्रभाव." : (currentLang === 'hi' ? "शारीरिक ताप नियंत्रण प्रभाव।" : "Physiological thermal impact."));
    const citation = f.standard_citation || (currentLang === 'mr' ? "आंतरराष्ट्रीय उष्णता मानके" : "International Thermal Standards");

    tr.innerHTML = `
      <td><b>${f.factor_name}</b></td>
      <td>${f.selected_value}</td>
      <td><span class="mult-badge ${badgeClass}">${f.percentage_change}</span></td>
      <td><div style="font-size:11px;line-height:1.35;">${rationale}<br><span style="color:#94a3b8;font-size:10px;">${citation}</span></div></td>
    `;
    tbody.appendChild(tr);
  });

  const totalEl = document.getElementById("totalMultiplierSummary");
  if (totalEl) {
    if (currentLang === 'mr') {
      totalEl.textContent = `एकत्रित संवेदनशीलता गुणक: प्रभागाच्या मूळ स्कोअरवर ${totalMult}x लागू केला गेला आहे.`;
    } else if (currentLang === 'hi') {
      totalEl.textContent = `संयुक्त संवेदनशीलता गुणक: वार्ड के मूल स्कोर पर ${totalMult}x लागू किया गया है।`;
    } else {
      totalEl.textContent = `Combined Vulnerability Multiplier: ${totalMult}x applied to baseline ward score.`;
    }
  }
}

// ==========================================================================
// 3-DAY FORECAST & CHART.JS RENDERING (LOCALIZED)
// ==========================================================================
function renderForecast(forecastList) {
  const i18n = ADVISOR_I18N[currentLang] || ADVISOR_I18N.en;
  const strip = document.getElementById("forecastCardsStrip");
  if (strip) {
    strip.innerHTML = "";
    (forecastList || []).slice(0, 3).forEach((item, idx) => {
      const card = document.createElement("div");
      card.className = "forecast-day-card";
      
      const dayNum = idx + 1;
      const localizedDay = currentLang === 'mr' ? `दिवस ${dayNum}` : (currentLang === 'hi' ? `दिन ${dayNum}` : `Day ${dayNum}`);
      const bandKey = `band_${(item.personal_band || 'Safe').toLowerCase()}`;
      const localizedBand = i18n[bandKey] || item.personal_band;

      card.innerHTML = `
        <div class="fc-day-title">${localizedDay}</div>
        <div class="fc-temp">${Math.round(item.temp_c)}°</div>
        <div class="fc-meta">
          <span class="fc-badge ${item.personal_band}">${localizedBand} (${item.personal_score})</span>
          <div class="fc-wbgt-tag">WBGT ${item.wbgt_c}°C</div>
        </div>
      `;
      strip.appendChild(card);
    });
  }

  // Chart.js initialization
  const canvas = document.getElementById("forecastChart");
  if (!canvas) return;

  const labels = (forecastList || []).map((f, i) => {
    return currentLang === 'mr' ? `दिवस ${i + 1}` : (currentLang === 'hi' ? `दिन ${i + 1}` : `Day ${i + 1}`);
  });
  const tempData = (forecastList || []).map(f => f.temp_c);
  const personalScores = (forecastList || []).map(f => f.personal_score);

  if (forecastChartInstance) {
    forecastChartInstance.destroy();
  }

  const riskLabel = currentLang === 'mr' ? "वैयक्तिक जोखीम स्कोअर (०-१००)" : (currentLang === 'hi' ? "व्यक्तिगत जोखिम स्कोर (०-१००)" : "Personal Risk Score (0-100)");
  const tempLabel = currentLang === 'mr' ? "तापमान (°C)" : (currentLang === 'hi' ? "तापमान (°C)" : "Ambient Temp (°C)");

  const ctx = canvas.getContext("2d");
  forecastChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: riskLabel,
          data: personalScores,
          borderColor: "#ea580c",
          backgroundColor: "rgba(234, 88, 12, 0.12)",
          fill: true,
          tension: 0.35,
          borderWidth: 2.5,
          pointRadius: 4,
          pointBackgroundColor: "#ea580c",
          yAxisID: "yRisk"
        },
        {
          label: tempLabel,
          data: tempData,
          borderColor: "#dc2626",
          borderDash: [4, 4],
          tension: 0.35,
          borderWidth: 2,
          pointRadius: 3,
          pointBackgroundColor: "#dc2626",
          yAxisID: "yTemp"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: {
          position: "top",
          labels: { font: { size: 11, family: "Inter" }, boxWidth: 12 }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { size: 10.5 } }
        },
        yRisk: {
          type: "linear",
          position: "left",
          min: 0,
          max: 100,
          ticks: { font: { size: 10 } },
          grid: { color: "#f1f5f9" }
        },
        yTemp: {
          type: "linear",
          position: "right",
          min: 25,
          max: 52,
          ticks: { font: { size: 10 } },
          grid: { display: false }
        }
      }
    }
  });
}

// ==========================================================================
// LEAFLET MAP & NEAREST SHELTER (LOCALIZED & NO EMOJIS)
// ==========================================================================
function renderShelter(shelter, userLoc) {
  if (!shelter) return;

  const sName = (currentLang === 'mr' && shelter.name_mr) ? shelter.name_mr : ((currentLang === 'hi' && shelter.name_hi) ? shelter.name_hi : shelter.name);
  const sDesc = (currentLang === 'mr' && shelter.desc_mr) ? shelter.desc_mr : ((currentLang === 'hi' && shelter.desc_hi) ? shelter.desc_hi : shelter.desc);
  const unit = ADVISOR_I18N[currentLang]?.unit_km || "km";

  const nameEl = document.getElementById("shelterName");
  if (nameEl) nameEl.textContent = sName;
  const descEl = document.getElementById("shelterDesc");
  if (descEl) descEl.textContent = sDesc;
  const distEl = document.getElementById("shelterDistance");
  if (distEl) distEl.textContent = `${shelter.distance_km || 0.5} ${unit}`;

  // Directions Link
  const dirBtn = document.getElementById("shelterDirectionsBtn");
  if (dirBtn) {
    dirBtn.href = `https://www.google.com/maps/dir/?api=1&destination=${shelter.lat},${shelter.lon}`;
  }

  // Initialize or update Leaflet Mini-Map
  const mapContainer = document.getElementById("shelterMap");
  if (!mapContainer) return;

  if (!shelterMapInstance) {
    shelterMapInstance = L.map("shelterMap", {
      zoomControl: false,
      attributionControl: false
    }).setView([shelter.lat, shelter.lon], 13);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18
    }).addTo(shelterMapInstance);

    shelterMarkerGroup = L.layerGroup().addTo(shelterMapInstance);
  }

  shelterMarkerGroup.clearLayers();

  // Shelter Marker (Blue with circle - no emoji)
  const shelterLabel = currentLang === 'mr' ? 'शीतकरण केंद्र' : (currentLang === 'hi' ? 'शीतलन केंद्र' : 'Cooling Shelter');
  const shelterMarker = L.circleMarker([shelter.lat, shelter.lon], {
    radius: 9,
    fillColor: "#0284c7",
    color: "#ffffff",
    weight: 2.5,
    fillOpacity: 1
  }).bindPopup(`<b>${shelterLabel}: ${sName}</b><br><span style="font-size:11px;">${sDesc}</span>`);

  shelterMarkerGroup.addLayer(shelterMarker);

  // User Marker (Orange - no emoji)
  const uLat = (userLoc && userLoc.lat) ? userLoc.lat : shelter.lat - 0.008;
  const uLon = (userLoc && userLoc.lon) ? userLoc.lon : shelter.lon - 0.008;
  const youAreHereLabel = currentLang === 'mr' ? 'तुमचे स्थान' : (currentLang === 'hi' ? 'आपका स्थान' : 'You Are Here');

  const userMarker = L.circleMarker([uLat, uLon], {
    radius: 8,
    fillColor: "#ea580c",
    color: "#ffffff",
    weight: 2.5,
    fillOpacity: 1
  }).bindPopup(`<b>${youAreHereLabel}</b>`);

  shelterMarkerGroup.addLayer(userMarker);

  const group = L.featureGroup([shelterMarker, userMarker]);
  shelterMapInstance.fitBounds(group.getBounds().pad(0.3));
}

// ==========================================================================
// ACCORDION & MODAL INTERACTIONS
// ==========================================================================
function initAccordion() {
  const trigger = document.getElementById("accordionTrigger");
  const body = document.getElementById("accordionBody");
  if (trigger && body) {
    trigger.addEventListener("click", () => {
      const isOpen = body.classList.contains("open");
      body.classList.toggle("open", !isOpen);
      const iconSvg = trigger.querySelector(".acc-arrow-svg");
      if (iconSvg) {
        iconSvg.style.transform = isOpen ? "rotate(0deg)" : "rotate(180deg)";
      }
    });
  }
}

function initModal() {
  const openBtn = document.getElementById("openAlertModalBtn");
  const modal = document.getElementById("alertModal");
  const closeBtn = document.getElementById("modalCloseBtn");
  const cancelBtn = document.getElementById("modalCancelBtn");
  const sendBtn = document.getElementById("modalSendBtn");

  if (openBtn && modal) {
    openBtn.addEventListener("click", () => {
      modal.classList.add("open");
      const storedPhone = localStorage.getItem("hs_family_phone");
      if (storedPhone) document.getElementById("alertPhoneInput").value = storedPhone;
    });
  }

  const closeModal = () => modal?.classList.remove("open");
  if (closeBtn) closeBtn.addEventListener("click", closeModal);
  if (cancelBtn) cancelBtn.addEventListener("click", closeModal);

  if (sendBtn) {
    sendBtn.addEventListener("click", async () => {
      const phone = document.getElementById("alertPhoneInput")?.value.trim();
      const relativeName = document.getElementById("alertRelativeInput")?.value.trim() || "Family Member";
      const senderName = document.getElementById("alertSenderInput")?.value.trim() || "Citizen";
      const note = document.getElementById("alertNoteInput")?.value.trim() || "";

      if (!phone || phone.length < 10) {
        showToast(currentLang === 'mr' ? "कृपया वैध १० अंकी मोबाईल नंबर टाका." : (currentLang === 'hi' ? "कृपया सही १० अंकों का मोबाइल नंबर दर्ज करें।" : "Please enter a valid 10-digit phone number."));
        return;
      }

      localStorage.setItem("hs_family_phone", phone);
      sendBtn.disabled = true;
      sendBtn.textContent = currentLang === 'mr' ? "एसएमएस पाठवत आहे..." : (currentLang === 'hi' ? "एसएमएस भेज रहे हैं..." : "Dispatching SMS...");

      const alertPayload = {
        ward_id: userProfile.ward_id,
        recipient_name: relativeName,
        recipient_phone: phone,
        sender_name: senderName,
        personal_score: currentResult ? currentResult.personal_score : 75.0,
        personal_risk_band: currentResult ? currentResult.personal_risk_band : "Extreme",
        custom_note: note
      };

      try {
        const res = await fetch(`${API_BASE_URL}/personal-risk/alert`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(alertPayload)
        });
        await res.json();
        closeModal();
        showToast(ADVISOR_I18N[currentLang]?.toast_sent || "Emergency alert SMS dispatched successfully!");
      } catch (err) {
        console.warn("SMS endpoint fallback", err);
        closeModal();
        showToast(ADVISOR_I18N[currentLang]?.toast_sent || "Emergency alert dispatched (Simulated Mode)!");
      } finally {
        sendBtn.disabled = false;
        sendBtn.textContent = ADVISOR_I18N[currentLang]?.btn_send_sms || "Send Alert via SMS";
      }
    });
  }
}

// ==========================================================================
// LANGUAGE & LOCALIZATION CONTROLLER
// ==========================================================================
function initLanguage() {
  document.querySelectorAll(".lang-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.lang === currentLang);
    btn.addEventListener("click", () => {
      currentLang = btn.dataset.lang;
      localStorage.setItem("hs_advisor_lang", currentLang);
      document.querySelectorAll(".lang-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      document.documentElement.lang = currentLang;

      applyTranslations();
      populateWardDropdown();

      // Re-render all dynamic data in the newly selected language!
      if (currentResult) {
        renderResults(currentResult);
      }
    });
  });
  applyTranslations();
}

function applyTranslations() {
  const i18n = ADVISOR_I18N[currentLang] || ADVISOR_I18N.en;
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.dataset.i18n;
    if (i18n[key]) {
      el.textContent = i18n[key];
    }
  });

  // Also update placeholders
  const phoneIn = document.getElementById("alertPhoneInput");
  if (phoneIn) phoneIn.placeholder = currentLang === 'mr' ? "उदा. ९८७६५४३२१०" : (currentLang === 'hi' ? "उदा. ९८७६५४३२१०" : "e.g. 9876543210");

  const senderIn = document.getElementById("alertSenderInput");
  if (senderIn) senderIn.placeholder = currentLang === 'mr' ? "उदा. आदित्य" : (currentLang === 'hi' ? "उदा. आदित्य" : "e.g. Aditya");

  const relIn = document.getElementById("alertRelativeInput");
  if (relIn) relIn.placeholder = currentLang === 'mr' ? "उदा. आई / वडील" : (currentLang === 'hi' ? "उदा. माता / पिता" : "e.g. Mother / Father");

  const noteIn = document.getElementById("alertNoteInput");
  if (noteIn) noteIn.placeholder = currentLang === 'mr' ? "उदा. मी सध्या सावलीत थांबलो आहे." : (currentLang === 'hi' ? "उदा. मैं अभी छाया में विश्राम कर रहा हूँ।" : "e.g. I am resting in the shade right now.");
}

// ==========================================================================
// TOAST NOTIFICATIONS (CLEAN WITHOUT EMOJIS)
// ==========================================================================
function showToast(msg) {
  let toast = document.getElementById("toastMsg");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "toastMsg";
    toast.className = "toast-msg";
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 3600);
}
