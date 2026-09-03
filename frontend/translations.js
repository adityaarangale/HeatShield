// Heat Shield Complete Municipal Control Room Translations (English & Marathi)
const translations = {
  en: {
    // Brand & Navigation
    brand_title: "HEAT SHIELD",
    brand_tagline: "Extreme Heat Early Warning & Action System",
    pilot_location: "Chandrapur District, MH",
    status_operational: "System Operational",
    status_demo: "Demo / Simulation Mode",
    btn_emergency_alert: "TRIGGER EMERGENCY ALERT",

    nav_overview: "Control Center",
    nav_map: "Risk Map",
    nav_wards: "Priority Wards",
    nav_forecast: "5-Day Forecast",
    nav_simulator: "What-If Simulator",
    nav_alerts: "Alert Center",
    nav_actions: "Action Center",
    nav_settings: "Settings",

    // Command Center / Home
    cmd_header: "DISTRICT HEAT RISK STATUS",
    cmd_extreme: "EXTREME HEAT EMERGENCY",
    cmd_sub: "6 of 8 municipal wards require immediate intervention",
    lbl_last_updated: "Last updated",

    kpi_monitored: "Monitored Wards",
    kpi_high_risk: "High-Risk Wards",
    kpi_peak_score: "Peak Risk Score",
    kpi_pop_risk: "Population at Risk",

    sec_priority_actions: "PRIORITY MUNICIPAL ACTIONS",
    act_1: "Activate emergency cooling centers across central Chandrapur",
    act_2: "Enforce outdoor work suspension (11:00 AM – 4:00 PM)",
    act_3: "Alert district emergency health facilities for heat stroke admissions",
    btn_view_actions: "View All Response Actions →",

    sec_ranked_wards: "RANKED PRIORITY WARDS",
    btn_view_map: "Open Interactive GIS Map →",
    col_rank: "#",
    col_ward: "Ward / Taluka",
    col_risk: "Risk Tier",
    col_score: "Score",
    col_temp: "Temp",
    col_wbgt: "WBGT",
    col_driver: "Primary Risk Driver",
    col_action: "Action",
    btn_inspect: "Inspect",

    sec_district_preview: "GIS SPATIAL RISK PREVIEW",

    // Risk Map
    map_title: "GIS SPATIAL RISK MAP",
    map_sub: "Identify high-risk spatial clusters and vulnerability zones",
    map_filter_hdr: "Risk Tier Filter",
    filter_all: "All Wards (8)",
    filter_extreme: "Extreme Risk",
    filter_danger: "Danger Risk",
    filter_caution: "Caution Risk",
    filter_safe: "Safe Level",
    map_side_hdr: "SELECTED WARD SUMMARY",
    map_why_hdr: "WHY IS THIS WARD AT RISK?",
    btn_inspect_ward: "Open Ward Analysis →",

    // Ward Details / Wards Page
    wards_title: "WARD RISK ANALYSIS",
    wards_sub: "In-depth thermal stress, demographic vulnerability, and response status",
    sec_current: "CURRENT WEATHER",
    sec_heat_stress: "THERMAL STRESS",
    sec_vulnerability: "DEMOGRAPHICS",
    sec_why_risk: "RISK DRIVER BREAKDOWN",
    sec_prep: "RESPONSE PREPAREDNESS STATUS",

    lbl_temp: "Temperature",
    lbl_rh: "Relative Humidity",
    lbl_wind: "Wind Speed",
    lbl_solar: "Solar Load",
    lbl_wbgt: "WBGT Index",
    lbl_hi: "Heat Index",
    lbl_app_temp: "Apparent Temp",
    lbl_htsi: "Blended HTSI",
    lbl_elderly: "Elderly Population",
    lbl_workers: "Outdoor Workers",
    lbl_green: "Green Cover",

    driver_temp: "Very high ambient temperature",
    driver_temp_desc: "Major thermal load contributor",
    driver_solar: "High solar radiation exposure",
    driver_solar_desc: "Increases direct solar heat stress",
    driver_workers: "High outdoor worker density",
    driver_workers_desc: "Elevated demographic vulnerability",
    driver_green: "Low green canopy cover",
    driver_green_desc: "Lack of urban shade protection",

    prep_cooling: "Cooling Centers",
    prep_water: "Hydration Stations",
    prep_work: "Work Hours Advisory",
    prep_hospitals: "Hospital Alert",
    prep_elderly: "Elderly Welfare Checks",

    st_active: "ACTIVE",
    st_issued: "ISSUED",
    st_pending: "PENDING",
    st_not_started: "NOT STARTED",

    btn_tech_details: "Show Technical Metrics & Formulas",
    btn_hide_tech_details: "Hide Technical Metrics",

    // Forecast Page
    forecast_title: "5-DAY HEAT RISK OUTLOOK",
    forecast_sub: "Predictive multi-day trend modeling to enable early response planning",
    forecast_summary: "Extreme heat risk is projected to persist for the next 72 hours across central Chandrapur.",
    lbl_today: "Today",
    lbl_tomorrow: "Tomorrow",
    lbl_day3: "Day 3",
    lbl_day4: "Day 4",
    lbl_day5: "Day 5",

    // What-If Simulator Page
    sim_title: "WHAT-IF SCENARIO SIMULATOR",
    sim_sub: "Simulate meteorological & infrastructure changes to assess projected risk impacts.",
    sim_badge: "SIMULATION MODE",
    sim_weather_hdr: "Meteorological Inputs",
    sim_infra_hdr: "Vulnerability & Infrastructure",
    sim_curr_risk: "CURRENT RISK",
    sim_proj_risk: "SIMULATED RISK",
    sim_why_hdr: "WHY DID RISK CHANGE?",
    sim_why_desc: "Increased solar load combined with ambient temperature rise pushed WBGT into extreme threshold.",
    sim_rec_hdr: "PREPAREDNESS RECOMMENDATION",
    sim_rec_desc: "Under this simulated scenario, cooling centers must open 2 hours earlier and hydration distribution expanded.",

    // Alert Center
    alerts_title: "ALERT CENTER",
    alerts_sub: "Operational warning management, emergency broadcasts, and audit log",
    kpi_active_alerts: "Active Warnings",
    kpi_awaiting_act: "Awaiting Response",
    kpi_dispatched_today: "Dispatched Today",
    alerts_active_hdr: "ACTIVE EMERGENCY WARNINGS",
    alerts_log_hdr: "DISPATCH AUDIT LOG",
    col_severity: "Severity",
    col_target: "Target Ward",
    col_time: "Time",
    col_trigger: "Trigger Condition",
    col_status: "Status",
    col_mgmt: "Management",
    btn_ack: "Acknowledge",
    btn_resolve: "Resolve",

    // Action Center
    actions_title: "ACTION CENTER",
    actions_sub: "Standard Operating Procedures (SOP) organized by timeline urgency",
    act_imm_hdr: "IMMEDIATE (0 – 2 HOURS)",
    act_6h_hdr: "NEXT 6 HOURS",
    act_24h_hdr: "NEXT 24 HOURS",
    act_pub_hdr: "PUBLIC ADVISORIES",
    btn_copy: "Copy Advisory Text",
    btn_send: "Broadcast Alert SMS",

    // Settings
    settings_title: "SYSTEM SETTINGS",
    settings_lang: "Default Control Room Language",
    settings_api: "Backend FastAPI Endpoint",
    settings_freshness: "Data Sync Status",

    // Modal Confirmation
    modal_title: "🚨 CONFIRM EMERGENCY ALERT BROADCAST",
    modal_sub: "Review parameter details before dispatching official emergency SMS warnings.",
    modal_target: "Target Ward / Taluka",
    modal_msg: "Proposed SMS Content",
    modal_phone: "Recipient Phone Number (Twilio)",
    btn_cancel: "Cancel",
    btn_broadcast: "Confirm & Broadcast SMS",

    // Risk Bands
    risk_extreme: "Extreme",
    risk_danger: "Danger",
    risk_caution: "Caution",
    risk_safe: "Safe"
  },

  mr: {
    // Brand & Navigation
    brand_title: "हीट शील्ड",
    brand_tagline: "उष्णतेचा धोका पूर्वसूचना व कृती प्रणाली",
    pilot_location: "चंद्रपूर जिल्हा, महाराष्ट्र",
    status_operational: "प्रणाली कार्यरत आहे",
    status_demo: "डेमो / सिम्युलेशन मोड",
    btn_emergency_alert: "आपत्कालीन इशारा पाठवा",

    nav_overview: "नियंत्रण केंद्र",
    nav_map: "जोखीम नकाशा",
    nav_wards: "प्रभाग प्राधान्य",
    nav_forecast: "५-दिवसीय अंदाज",
    nav_simulator: "परिस्थिती सिम्युलेटर",
    nav_alerts: "अ‍ॅलर्ट सेंटर",
    nav_actions: "अ‍ॅक्शन सेंटर",
    nav_settings: "सेटिंग्ज",

    // Command Center / Home
    cmd_header: "जिल्हा उष्णता जोखीम स्थिती",
    cmd_extreme: "अत्यंत उष्णतेची आणीबाणी",
    cmd_sub: "८ पैकी ६ प्रभागांमध्ये तात्काळ पालिका हस्तक्षेपाची गरज आहे",
    lbl_last_updated: "शेवटचे अद्यतन",

    kpi_monitored: "निरीक्षण केलेले प्रभाग",
    kpi_high_risk: "धोकादायक प्रभाग",
    kpi_peak_score: "उच्चतम जोखीम गुण",
    kpi_pop_risk: "धोक्यात असलेली लोकसंख्या",

    sec_priority_actions: "प्राधान्य पालिका कृती",
    act_1: "मध्य चंद्रपूर भागात आपत्कालीन शीतकरण केंद्रे त्वरित सुरू करा",
    act_2: "सकाळी ११:०० ते दुपारी ४:०० दरम्यान कामाची स्थगिती लागू करा",
    act_3: "उष्माघाताच्या रुग्णांसाठी जिल्हा रुग्णालयांना सतर्क करा",
    btn_view_actions: "सर्व पालिका कृती पहा →",

    sec_ranked_wards: "प्रभाग प्राधान्य क्रमवारी",
    btn_view_map: "नकाशा उघडा →",
    col_rank: "#",
    col_ward: "प्रभाग / तालुका",
    col_risk: "जोखीम पातळी",
    col_score: "गुण",
    col_temp: "तापमान",
    col_wbgt: "WBGT",
    col_driver: "मुख्य जोखीम कारण",
    col_action: "कृती",
    btn_inspect: "तपासा",

    sec_district_preview: "जिल्हा जोखीम नकाशा पूर्वदृश्य",

    // Risk Map
    map_title: "GIS प्रभाग जोखीम नकाशा",
    map_sub: "जिल्ह्यातील उष्णतेचे सर्वाधिक धोकादायक क्षेत्र ओळखा",
    map_filter_hdr: "जोखीम पातळीनुसार शोधा",
    filter_all: "सर्व प्रभाग (८)",
    filter_extreme: "अत्यंत धोका",
    filter_danger: "धोकादायक",
    filter_caution: "सावधान",
    filter_safe: "सुरक्षित",
    map_side_hdr: "निवडलेल्या प्रभागाचा सारांश",
    map_why_hdr: "हा प्रभाग धोक्यात का आहे?",
    btn_inspect_ward: "सविस्तर विश्लेषण पहा →",

    // Ward Details / Wards Page
    wards_title: "प्रभाग जोखीम विश्लेषण",
    wards_sub: "सविस्तर उष्णता ताण, लोकसंख्या जोखीम आणि पालिका तयारी स्थिती",
    sec_current: "सध्याची हवामान स्थिती",
    sec_heat_stress: "उष्णता ताण निर्देशांक",
    sec_vulnerability: "लोकसंख्या जोखीम",
    sec_why_risk: "जोखीम निर्माण होण्याची मुख्य कारणे",
    sec_prep: "पालिका तयारी स्थिती",

    lbl_temp: "तापमान",
    lbl_rh: "सापेक्ष आर्द्रता",
    lbl_wind: "वाऱ्याचा वेग",
    lbl_solar: "सौर किरणोत्सर्ग",
    lbl_wbgt: "WBGT निर्देशांक",
    lbl_hi: "हिट इंडेक्स",
    lbl_app_temp: "जाणवणारे तापमान",
    lbl_htsi: "एकत्रित उष्णता ताण",
    lbl_elderly: "ज्येष्ठ नागरिक लोकसंख्या",
    lbl_workers: "बाहेरील कामगार",
    lbl_green: "हरित आच्छादन",

    driver_temp: "हवेचे अत्यंत जास्त तापमान",
    driver_temp_desc: "उष्णतेच्या ताणाचा मुख्य घटक",
    driver_solar: "तीव्र सौर किरणोत्सर्ग",
    driver_solar_desc: "थेट सौर उष्णता वाढवतो",
    driver_workers: "बाहेरील कामगारांचे जास्त प्रमाण",
    driver_workers_desc: "सामाजिक जोखीम वाढवते",
    driver_green: "हरित आच्छादनाची कमतरता",
    driver_green_desc: "शहरी सावलीचा अभाव",

    prep_cooling: "शीतकरण केंद्रे (Cooling Centers)",
    prep_water: "पिण्याच्या पाण्याची केंद्रे",
    prep_work: "कामाच्या तासांचा सल्ला",
    prep_hospitals: "रुग्णालय सूचना",
    prep_elderly: "ज्येष्ठ नागरिकांची तपासणी",

    st_active: "सक्रिय (ACTIVE)",
    st_issued: "जारी (ISSUED)",
    st_pending: "प्रलंबित (PENDING)",
    st_not_started: "शुरू नाही (NOT STARTED)",

    btn_tech_details: "तांत्रिक सूत्रे व गणिते पहा",
    btn_hide_tech_details: "तांत्रिक माहिती लपवा",

    // Forecast Page
    forecast_title: "५-दिवसीय उष्णता जोखीम अंदाज",
    forecast_sub: "आपत्कालीन नियोजनासाठी बहु-दिवसीय अंदाज विश्लेषण",
    forecast_interpretation: "पुढील ७२ तास मध्य चंद्रपूर भागात तीव्र उष्णतेचा ताण राहण्याची शक्यता आहे.",
    lbl_today: "आज",
    lbl_tomorrow: "उद्या",
    lbl_day3: "दिवस ३",
    lbl_day4: "दिवस ४",
    lbl_day5: "दिवस ५",

    // What-If Simulator Page
    sim_title: "परिस्थिती सिम्युलेटर (What-If Heat Scenario)",
    sim_sub: "हवामान आणि पायाभूत सुविधांमधील बदलांचे जोखीम परिणाम पहा.",
    sim_badge: "सिम्युलेशन मोड",
    sim_weather_hdr: "हवामान घटक",
    sim_infra_hdr: "लोकसंख्या व पायाभूत सुविधा",
    sim_curr_risk: "सध्याची जोखीम",
    sim_proj_risk: "सिम्युलेट केलेली जोखीम",
    sim_why_hdr: "जोखीम का बदलली?",
    sim_why_desc: "सौर किरणोत्सर्ग आणि तापमानातील वाढीमुळे WBGT निर्देशांक अत्यंत धोकादायक पातळीवर गेला.",
    sim_rec_hdr: "तयारीची शिफारस",
    sim_rec_desc: "या सिम्युलेट केलेल्या परिस्थितीत, कूलिंग केंद्रे २ तास आधी सुरू करणे आवश्यक आहे.",

    // Alert Center
    alerts_title: "अ‍ॅलर्ट सेंटर",
    alerts_sub: "आपत्कालीन इशारे, संदेश प्रसारण आणि इतिहास नोंद",
    kpi_active_alerts: "सक्रिय इशारे",
    kpi_awaiting_act: "कृती प्रलंबित",
    kpi_dispatched_today: "आज पाठवलेले",
    alerts_active_hdr: "समीक्षेची गरज असलेले सक्रिय इशारे",
    alerts_log_hdr: "पाठवलेल्या संदेशांचा इतिहास",
    col_severity: "तीव्रता",
    col_target: "लक्ष्य प्रभाग",
    col_time: "वेळ",
    col_trigger: "कारण",
    col_status: "स्थिती",
    col_mgmt: "व्यवस्थापन",
    btn_ack: "स्वीकारा (Acknowledge)",
    btn_resolve: "निराकरण करा (Resolve)",

    // Action Center
    actions_title: "अ‍ॅक्शन सेंटर",
    actions_sub: "वेळेच्या तीव्रतेनुसार आयोजित पालिका कार्यपद्धती (SOP)",
    act_imm_hdr: "तात्काळ (० – २ तास)",
    act_6h_hdr: "पुढील ६ तास",
    act_24h_hdr: "पुढील २४ तास",
    act_pub_hdr: "सार्वजनिक सल्ला व सूचना",
    btn_copy: "सल्ला मजकूर कॉपी करा",
    btn_send: "SMS आपत्कालीन इशारा पाठवा",

    // Settings
    settings_title: "सिस्टम सेटिंग्ज",
    settings_lang: "मुख्य नियंत्रण भाषा",
    settings_api: "बॅकएंड एपीआय यूआरएल",
    settings_freshness: "डेटा सिंक स्थिती",

    // Modal Confirmation
    modal_title: "🚨 आपत्कालीन इशारा संदेशाची पुष्टी करा",
    modal_sub: "आपत्कालीन SMS पाठवण्यापूर्वी सर्व तपशील तपासा.",
    modal_target: "लक्ष्य प्रभाग",
    modal_msg: "प्रस्तावित SMS संदेश",
    modal_phone: "फोन नंबर (Twilio SMS)",
    btn_cancel: "रद्द करा",
    btn_broadcast: "पुष्टी करा आणि SMS पाठवा",

    // Risk Bands
    risk_extreme: "अत्यंत धोका",
    risk_danger: "धोकादायक",
    risk_caution: "सावधान",
    risk_safe: "सुरक्षित"
  }
};
