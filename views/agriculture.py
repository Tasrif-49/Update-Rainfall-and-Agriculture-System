# ============================================================
# ============================================================
#          SMART AGRICULTURE & IRRIGATION PAGE — DEVELOPER GUIDE
# ============================================================
#
# PURPOSE OF THIS FILE
# ------------------------------------------------------------
# This file controls the Streamlit Smart Agriculture & Irrigation
# page, including its voice-assistant (Bangla) behavior.
#
# MAIN RESPONSIBILITIES
# ------------------------------------------------------------
# 1. Play welcome / section / selection / result voice prompts
# 2. Inject page-level CSS styling
# 3. Format numbers and dates into Bangla text
# 4. Provide reusable voice-input helper widgets
# 5. Auto-run rainfall prediction for the selected station/date
# 6. Translate station/district/division names into Bangla
# 7. Collect station + date (Location & Date section)
# 8. Collect weather / rainfall information (Auto or Manual)
# 9. Collect land information (area + unit)
# 10. Collect crop + season information
# 11. Determine planting date and growth stage
# 12. Show crop reference information
# 13. Collect soil information
# 14. Collect existing water in the field
# 15. Determine crop water requirement (Automatic or Manual)
# 16. Collect irrigation system information (method/efficiency)
# 17. Run the smart irrigation calculation
# 18. Display the smart irrigation result (headline, summary,
#     recommendations, full calculation details, chart)
# 19. Drive the overall page controller (show_agriculture())
#
#
# ============================================================
#                    MASTER CODE INDEX
# ============================================================
#
# [01] IMPORTS
#      External libraries and internal project services.
#
# [02] WELCOME VOICE TEXT
#      Constant: AGRICULTURE_WELCOME_TEXT
#      Bangla welcome message spoken when the page opens.
#
# [03] PAGE VOICE STARTUP
#      Function: start_agriculture_welcome()
#      Plays the welcome voice sequence exactly once per session.
#
# [04] VOICE ON/OFF TOGGLE
#      Function: agriculture_voice_toggle()
#      Single page-level toggle that enables/disables all voice.
#
# [05] PAGE STYLING
#      Function: inject_agriculture_styles()
#      Injects all page-level CSS (radio cards, sidebar theme,
#      result cards, info cards, headline cards, etc).
#
#      IF ONLY VISUAL STYLE NEEDS TO CHANGE:
#      Start here.
#
# [06] BANGLA NUMBER FORMATTING
#      Function: bn_num()
#      Converts numbers into Bangla-digit display strings.
#
# [07] IRRIGATION TIME FORMATTING
#      Function: format_irrigation_time_bn()
#      Converts hours into "X ঘণ্টা Y মিনিট" Bangla text.
#
# [08] BANGLA MONTH NAMES
#      Constant: BANGLA_MONTHS
#      Month-number -> Bangla month-name mapping.
#
# [09] DATE DISPLAY TEXT
#      Function: date_text()
#      Formats a date object into Bangla display text.
#
# [10] DATE VOICE TEXT
#      Function: voice_date_text()
#      Formats a date object into Bangla-digit voice text.
#
# [11] VOICE INPUT FIELD HELPER
#      Function: _voice_input_field()
#      Wraps voice_input_widget() and fires the confirmation
#      voice callback whenever a spoken value is applied.
#
# [12] SECTION TITLE RENDERER
#      Function: section_title()
#      Renders the Bangla/English section heading styling.
#
# [13] SECTION-ENTRY VOICE
#      Function: agriculture_section_voice()
#      Speaks a section's intro voice exactly once per session.
#
# [14] SELECTION-CHANGE VOICE
#      Function: selection_voice()
#      Speaks a confirmation only when a tracked value changes.
#
# [15] VOICE CONFIRMATION TEXT BUILDER
#      Function: _voice_value_text()
#      Builds the Bangla confirmation sentence for one widget's
#      current value (numbers, dates, station, dropdowns, etc).
#
#      IF A NEW VOICE-DRIVEN INPUT IS ADDED:
#      Update this function's key checks.
#
# [16] NEXT-INSTRUCTION VOICE MAP
#      Constant: VOICE_NEXT_INSTRUCTION
#      Maps each input's session-state key to the Bangla
#      instruction spoken for the next step.
#
# [17] INPUT VOICE CALLBACK
#      Function: input_voice_callback()
#      on_change callback: speaks "confirmation -> next
#      instruction", including the irrigation-method-specific
#      branching (Drip / Sprinkler / Shallow-Deep).
#
# [18] AUTOMATIC RAINFALL PREDICTION (FOR AGRICULTURE)
#      Function: auto_predict_agriculture_rainfall()
#      Runs the same CatBoost rainfall pipeline used on the
#      Rainfall Prediction page, automatically, for the
#      selected station/date, and stores the result in
#      st.session_state.rain_prediction.
#
#      IF THE RAINFALL PIPELINE ITSELF NEEDS TO CHANGE:
#      That logic lives in views/prediction.py, not here.
#      This function only calls it and prepares the UI values.
#
# [19] BANGLA LOCATION NAME TABLES
#      Constants: BN_DIVISIONS, BN_DISTRICTS, BN_STATIONS
#      English -> Bangla name lookup tables.
#
# [20] BANGLA NAME LOOKUP
#      Function: _bn_lookup()
#      Case-insensitive lookup into a name table with English
#      fallback if no Bangla translation exists.
#
# [21] BANGLA LOCATION LABEL BUILDER
#      Function: build_bn_location_label()
#      Builds "Station, District (Division)" in Bangla.
#
# [22] LOCATION & DATE SECTION
#      Function: agriculture_location_date_section()
#      Station + prediction-date selectors; triggers automatic
#      rainfall prediction once both are chosen.
#
# [23] WEATHER & RAINFALL INFORMATION SECTION
#      Function: weather_information_section()
#      Auto (predicted) vs Manual rainfall/ET0 entry.
#
# [24] LAND INFORMATION SECTION
#      Function: land_information_section()
#      Land area + area unit input.
#
# [25] CROP INFORMATION SECTION
#      Function: crop_information_section()
#      Crop + season selection (season auto-selected for
#      non-rice crops).
#
# [26] PLANTING & GROWTH STAGE SECTION
#      Function: planting_growth_section()
#      Calculation date + planting date; automatic growth-stage
#      determination with manual override / fallback.
#
# [27] CROP REFERENCE INFORMATION CARD
#      Function: crop_reference_section()
#      Displays cultivar / duration / seasonal CWR / IWR
#      reference info for the selected crop+season.
#
# [28] SOIL INFORMATION SECTION
#      Function: soil_information_section()
#      Soil type selector (informational; no irrigation
#      multiplier applied from it).
#
# [29] EXISTING WATER SECTION
#      Function: existing_water_section()
#      Converts a measured field water depth into an estimated
#      water volume (liters / m³).
#
# [30] CROP WATER REQUIREMENT SECTION
#      Function: crop_water_requirement_section()
#      Automatic (ET0 x Kc) vs Manual daily crop water need.
#
# [31] IRRIGATION SYSTEM SECTION
#      Function: irrigation_system_section()
#      Irrigation method selection (Drip / Sprinkler /
#      Fixed-flow), method-specific inputs, and efficiency
#      slider. Reads all method configuration from
#      services/agriculture.py — no method names are
#      hardcoded here.
#
# [32] MAIN INPUT PANEL / CALCULATION TRIGGER
#      Function: _agriculture_input_panel()
#      Orchestrates sections 23–31 in order, validates required
#      inputs, and on "Calculate" runs calculate_irrigation() +
#      calculate_irrigation_time() and stores the full result.
#
#      IF THE IRRIGATION CALCULATION FORMULA NEEDS TO CHANGE:
#      That logic lives in services/agriculture.py
#      (calculate_irrigation / calculate_irrigation_time), not
#      here. This function only calls it and stores the output.
#
# [33] RESULT DISPLAY
#      Function: show_agriculture_result()
#      Renders the headline card, short summary card, smart
#      recommendations, and the full "calculation details"
#      expander (crop water calc, water balance, how much
#      water, irrigation method & time, no-rain scenario,
#      existing water, calculation log, bar chart).
#
# [34] MAIN PAGE CONTROLLER
#      Function: show_agriculture()
#      Top-level Streamlit page controller for the Agriculture
#      page. Calls styling, voice, location/date, input panel,
#      result display, and voice-queue processing in order.
#
#
# ============================================================
#              IMPORTANT CHANGE-LOCATION GUIDE
# ============================================================
#
# Change welcome voice text
# -> [02] WELCOME VOICE TEXT
#
# Change when welcome voice plays
# -> [03] PAGE VOICE STARTUP
#
# Change voice on/off behavior
# -> [04] VOICE TOGGLE
#
# Change page CSS / card styles
# -> [05] PAGE STYLING
#
# Change Bangla number formatting
# -> [06] BANGLA NUMBER
#
# Change irrigation time text format
# -> [07] IRRIGATION TIME FORMAT
#
# Change Bangla month names
# -> [08] BANGLA MONTHS
#
# Change date display / voice text
# -> [09] DATE DISPLAY
# -> [10] DATE VOICE
#
# Change what is spoken when a value is confirmed
# -> [15] VOICE CONFIRMATION TEXT
#
# Change what is spoken next after an input
# -> [16] NEXT-INSTRUCTION MAP
# -> [17] INPUT VOICE CALLBACK
#
# Change automatic rainfall prediction for Agriculture
# -> [18] AUTOMATIC RAINFALL PREDICTION
#
# Change Bangla location name translations
# -> [19] BANGLA LOCATION TABLES
# -> [20] BANGLA LOOKUP
# -> [21] BANGLA LOCATION LABEL
#
# Change Station/Date selection UI
# -> [22] LOCATION & DATE SECTION
#
# Change rainfall/ET0 Auto vs Manual behavior
# -> [23] WEATHER & RAINFALL SECTION
#
# Change land area / unit inputs
# -> [24] LAND INFORMATION SECTION
#
# Change crop / season selection
# -> [25] CROP INFORMATION SECTION
#
# Change growth-stage determination UI
# -> [26] PLANTING & GROWTH STAGE SECTION
#
# Change crop reference info card
# -> [27] CROP REFERENCE CARD
#
# Change soil type selection
# -> [28] SOIL INFORMATION SECTION
#
# Change existing-water estimation
# -> [29] EXISTING WATER SECTION
#
# Change crop water requirement (ET0 x Kc / Manual)
# -> [30] CROP WATER REQUIREMENT SECTION
#
# Change irrigation method inputs / efficiency
# -> [31] IRRIGATION SYSTEM SECTION
#
# Change validation rules / calculation trigger
# -> [32] MAIN INPUT PANEL
#
# Change result cards / recommendations / details expander
# -> [33] RESULT DISPLAY
#
# Change overall page order
# -> [34] MAIN PAGE CONTROLLER
#
#
# ============================================================
#                  IMPORTANT DEPENDENCIES
# ============================================================
#
# This file depends on:
#
# services.data_loader
#     -> get_station_table()
#
# services.weather_api
#     -> build_on_demand_history()
#
# views.prediction
#     -> load_weather_values()
#     -> create_prediction_features()
#     -> condition()
#     -> estimate_rain_probability()
#
# services.voice
#     -> play_welcome()
#     -> selection_voice()   (imported as voice_selection)
#     -> section_voice()
#     -> speak_sequence()
#     -> clean_voice_text()
#     -> agriculture_result_voice()
#     -> agriculture_recommendation_voice()
#     -> growth_stage_auto_voice()
#     -> render_voice_player()
#     -> process_voice_queue()
#     -> reset_voice_hash()
#     -> is_voice_enabled()
#     -> set_voice_enabled()
#
# services.voice_input
#     -> prepare_voice_input()
#     -> voice_input_widget()
#
# services.agriculture
#     -> SOIL_TYPES
#     -> WATER_DEPTH_OPTIONS
#     -> STAGE_LABELS
#     -> STAGE_FROM_LABEL
#     -> get_crop_options()
#     -> get_season_options()
#     -> get_crop_reference()
#     -> determine_growth_stage()
#     -> get_kc()
#     -> convert_area_to_m2()
#     -> convert_water_depth_to_mm()
#     -> calculate_existing_water_volume()
#     -> calculate_irrigation()
#     -> get_irrigation_method_options()
#     -> get_irrigation_method_config()
#     -> calculate_irrigation_time()
#
# External inputs passed into show_agriculture():
#     -> df
#     -> model
#     -> feature_columns
#     -> train_medians
#     -> history_days
#
# IMPORTANT:
# Do not rename these dependencies without checking the files
# where they are created and used.
#
#
# ============================================================
#                  AGRICULTURE PAGE FLOW
# ============================================================
#
# Page opens
#        ↓
# Welcome voice + styles injected
#        ↓
# User selects Station + Date
#        ↓
# Automatic rainfall prediction runs (CatBoost)
#        ↓
# Weather & Rainfall section (Auto prediction / Manual entry)
#        ↓
# Land Information (area + unit)
#        ↓
# Crop + Season selection
#        ↓
# Planting date + automatic Growth Stage
#        ↓
# Crop Reference card
#        ↓
# Soil type
#        ↓
# Existing water in field
#        ↓
# Crop Water Requirement (Automatic ET0×Kc / Manual)
#        ↓
# Irrigation System (method + efficiency)
#        ↓
# User clicks "Calculate Smart Irrigation"
#        ↓
# calculate_irrigation() + calculate_irrigation_time()
#        ↓
# Result stored in session state + result voice spoken
#        ↓
# Result Display:
#   Headline card -> Summary card -> Smart Recommendations
#   -> Full Calculation Details expander (+ bar chart)
#        ↓
# Voice queue processed + voice player rendered
#
#
# ============================================================
# IMPORTANT:
# The comments below document the original code.
# Application logic has intentionally been kept unchanged.
# ============================================================


# ============================================================
# [01] IMPORTS
# ------------------------------------------------------------
# PURPOSE:
# Import all libraries and project services required by this
# Agriculture page (rainfall reuse, voice services, voice
# input, and the core agriculture calculation service).
#
# CHANGE HERE WHEN:
# - adding a new Python library
# - adding a new internal service
#
# IMPORTANT:
# Do not remove an import unless you verify that it is no longer
# used anywhere in this file.
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from datetime import date

from services.data_loader import get_station_table

from services.weather_api import build_on_demand_history

from views.prediction import (
    load_weather_values,
    create_prediction_features,
    condition,
    estimate_rain_probability
)

from services.voice import (
    play_welcome,
    selection_voice as voice_selection,
    section_voice,
    speak_sequence,
    clean_voice_text,
    agriculture_result_voice,
    agriculture_recommendation_voice,
    growth_stage_auto_voice,
    render_voice_player,
    process_voice_queue,
    reset_voice_hash,
    is_voice_enabled,
    set_voice_enabled
)

from services.voice_input import (
    prepare_voice_input,
    voice_input_widget
)

from services.agriculture import (
    SOIL_TYPES,
    WATER_DEPTH_OPTIONS,
    STAGE_LABELS,
    STAGE_FROM_LABEL,
    get_crop_options,
    get_season_options,
    get_crop_reference,
    determine_growth_stage,
    get_kc,
    convert_area_to_m2,
    convert_water_depth_to_mm,
    calculate_existing_water_volume,
    calculate_irrigation,
    get_irrigation_method_options,
    get_irrigation_method_config,
    calculate_irrigation_time
)


# ============================================================
# [02] WELCOME VOICE TEXT
# ------------------------------------------------------------
# CONSTANT:
#     AGRICULTURE_WELCOME_TEXT
#
# PURPOSE:
# Bangla welcome message spoken once when the Agriculture page
# is opened, before asking the user to select station/date.
#
# CHANGE HERE IF:
# - the welcome wording needs to change.
# ============================================================

AGRICULTURE_WELCOME_TEXT = (
    "আসসালামু আলাইকুম। "
    "স্মার্ট কৃষি পরামর্শ সিস্টেমে স্বাগতম। "
    "ফসলের তথ্য দিন। "
    "প্রয়োজনীয় সেচ ও কৃষি পরামর্শ পান।"
)


# ============================================================
# [03] PAGE VOICE STARTUP
# ------------------------------------------------------------
# FUNCTION:
#     start_agriculture_welcome()
#
# PURPOSE:
# Plays the welcome voice sequence exactly once per session:
#   1. Welcome text
#   2. "স্থান ও তারিখ নির্বাচন করুন"
#
# IMPORTANT:
# Other inputs' voice must NOT play automatically on page load;
# only this welcome sequence does.
#
# CHANGE HERE IF:
# - the welcome trigger/guard logic needs to change.
# ============================================================

def start_agriculture_welcome():
    """
    Agriculture page open হলে:
    1. প্রথমে Welcome voice
    2. Welcome শেষ হলে "স্থান ও তারিখ নির্বাচন করুন"

    অন্য কোনো input-এর voice page load-এর সময় বাজবে না।
    """

    if st.session_state.get(
        "agriculture_voice_started",
        False
    ):
        return

    st.session_state[
        "agriculture_voice_started"
    ] = True

    speak_sequence(
        [
            AGRICULTURE_WELCOME_TEXT,
            "স্থান ও তারিখ নির্বাচন করুন"
        ],
        delay=0.10
    )


# ============================================================
# [04] VOICE ON/OFF TOGGLE
# ------------------------------------------------------------
# FUNCTION:
#     agriculture_voice_toggle()
#
# PURPOSE:
# Renders the single page-level ON/OFF toggle that controls
# whether ANY voice on this page is generated or played.
#
# CHANGE HERE IF:
# - toggle placement/label needs to change.
# ============================================================

def agriculture_voice_toggle():
    """
    Page-এর একদম উপরে একটি single ON/OFF বাটন।

    ON: page-এর সব voice স্বাভাবিকভাবে বাজবে।
    OFF: কোনো voice generate বা play হবে না।
    """

    if "agriculture_voice_toggle" not in st.session_state:

        st.session_state[
            "agriculture_voice_toggle"
        ] = is_voice_enabled()

    vcol1, vcol2 = st.columns([5, 2])

    with vcol2:

        voice_on = st.toggle(
            "🔊 ভয়েস (Voice)",
            key="agriculture_voice_toggle"
        )

    set_voice_enabled(voice_on)


# ============================================================
# [05] PAGE STYLING
# ------------------------------------------------------------
# FUNCTION:
#     inject_agriculture_styles()
#
# PURPOSE:
# Injects all page-level CSS: radio-option cards, sidebar
# theme, section titles, result/agri/headline/summary/info
# cards.
#
# CHANGE HERE IF:
# - colors, spacing, card shapes, or any visual style needs to
#   change.
#
# IMPORTANT:
# Purely visual. Does not affect calculation logic.
# ============================================================

def inject_agriculture_styles():

    st.markdown(
        """
        <style>

        section[data-testid="stMain"]
        div[data-testid="stRadio"] div[role="radiogroup"] {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-top: 6px;
        }

        section[data-testid="stMain"]
        div[data-testid="stRadio"] div[role="radiogroup"] > label {
            border: 2px solid #d5dee7;
            border-radius: 12px;
            padding: 14px 16px;
            background: #ffffff;
            width: 100%;
            cursor: pointer;
            transition: border-color .15s ease,
                        background-color .15s ease;
        }

        section[data-testid="stMain"]
        div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
            border-color: #0e9f6e;
            background: #f4fbf8;
        }

        section[data-testid="stMain"]
        div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
            border-color: #0e9f6e;
            background: #e8f9f1;
        }

        section[data-testid="stMain"]
        div[data-testid="stRadio"] div[role="radiogroup"] > label:focus-within {
            outline: 2px solid #0e9f6e;
            outline-offset: 2px;
        }

        section[data-testid="stMain"]
        div[data-testid="stRadio"] div[role="radiogroup"] label p {
            font-size: 16px !important;
            font-weight: 600 !important;
            color: #102a43 !important;
            margin: 0 !important;
        }

        section[data-testid="stMain"]
        div[data-testid="stRadio"] > label p {
            font-size: 17px !important;
            font-weight: 700 !important;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0d1b2a 0%, #102a43 100%);
            border-right: 1px solid rgba(255,255,255,.06);
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] span {
            color: #e6edf3 !important;
        }

        section[data-testid="stSidebar"] h1 {
            font-size: 20px !important;
            font-weight: 700 !important;
            letter-spacing: .2px;
            padding-bottom: 6px;
            border-bottom: 1px solid rgba(255,255,255,.08);
        }

        section[data-testid="stSidebar"]
        div[data-testid="stRadio"] div[role="radiogroup"] {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        section[data-testid="stSidebar"]
        div[data-testid="stRadio"] div[role="radiogroup"] > label {
            background: transparent;
            border: 1px solid transparent;
            border-left: 3px solid transparent;
            border-radius: 8px;
            padding: 10px 12px;
            width: 100%;
            cursor: pointer;
            transition: background-color .15s ease,
                        border-color .15s ease;
        }

        section[data-testid="stSidebar"]
        div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
            background: rgba(255,255,255,.06);
        }

        section[data-testid="stSidebar"]
        div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
            background: rgba(14,159,110,.16);
            border-left-color: #0e9f6e;
        }

        section[data-testid="stSidebar"]
        div[data-testid="stRadio"] div[role="radiogroup"] label p {
            color: #cdd9e5 !important;
            font-size: 15px !important;
            font-weight: 500 !important;
            margin: 0 !important;
        }

        section[data-testid="stSidebar"]
        div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) p {
            color: #ffffff !important;
            font-weight: 600 !important;
        }

        section[data-testid="stSidebar"]
        div[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {
            display: none !important;
        }

        section[data-testid="stSidebar"] hr {
            border-color: rgba(255,255,255,.08);
        }

        section[data-testid="stMain"] div[data-testid="stNumberInput"] label p,
        section[data-testid="stMain"] div[data-testid="stSelectbox"] label p,
        section[data-testid="stMain"] div[data-testid="stDateInput"] label p,
        section[data-testid="stMain"] div[data-testid="stTextInput"] label p,
        section[data-testid="stMain"] div[data-testid="stSlider"] label p {
            font-size: 15px !important;
            font-weight: 600 !important;
        }

        section[data-testid="stMain"] input::placeholder {
            color: #8a9aa8 !important;
            opacity: 1 !important;
        }

        section[data-testid="stMain"]
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 14px !important;
            background: #ffffff;
        }

        .section-title {
            font-size: 20px;
            font-weight: 700;
            border-left: 5px solid #0e9f6e;
            padding-left: 12px;
            margin: 22px 0 12px 0;
        }

        .result-card {
            border-radius: 16px;
            padding: 20px 22px;
            background: linear-gradient(135deg, #0e9f6e 0%, #0b7f59 100%);
            color: #ffffff;
            margin: 6px 0 14px 0;
        }

        .result-card h2 {
            color: #ffffff;
            margin: 0 0 4px 0;
            font-size: 26px;
        }

        .result-card h3 {
            color: rgba(255,255,255,.85);
            margin: 0;
            font-size: 16px;
            font-weight: 500;
        }

        .agri-card {
            border-radius: 14px;
            padding: 16px 18px;
            background: #eef6f2;
            border: 1px solid #cfe6db;
            margin-bottom: 8px;
        }

        .agri-card h3 {
            margin: 0 0 6px 0;
            font-size: 18px;
        }

        .agri-card p {
            margin: 0;
            font-size: 15px;
            line-height: 1.7;
        }

        .headline-card {
            border-radius: 20px;
            padding: 28px 26px;
            background: linear-gradient(135deg, #0e9f6e 0%, #0b7f59 100%);
            color: #ffffff;
            margin: 10px 0 16px 0;
            box-shadow: 0 8px 24px rgba(14,159,110,.25);
        }

        .headline-card .tag {
            display: inline-block;
            font-size: 13px;
            font-weight: 600;
            letter-spacing: .3px;
            background: rgba(255,255,255,.18);
            padding: 4px 12px;
            border-radius: 999px;
            margin-bottom: 12px;
        }

        .headline-card .status {
            font-size: 24px;
            font-weight: 700;
            margin: 0 0 18px 0;
        }

        .headline-card .metrics {
            display: flex;
            flex-wrap: wrap;
            gap: 24px;
        }

        .headline-card .metric-block {
            min-width: 140px;
        }

        .headline-card .metric-label {
            font-size: 13px;
            font-weight: 500;
            color: rgba(255,255,255,.8);
            margin-bottom: 4px;
        }

        .headline-card .metric-value {
            font-size: 30px;
            font-weight: 700;
            line-height: 1.15;
        }

        .headline-card .metric-unit {
            font-size: 15px;
            font-weight: 500;
            color: rgba(255,255,255,.85);
            margin-left: 4px;
        }

        .summary-card {
            border-radius: 16px;
            padding: 18px 20px;
            background: #ffffff;
            border: 1px solid #dfe8e4;
            margin: 4px 0 14px 0;
        }

        .summary-card .summary-title {
            font-size: 15px;
            font-weight: 700;
            color: #0b7f59;
            margin-bottom: 10px;
        }

        .summary-card ul {
            margin: 0;
            padding-left: 18px;
        }

        .summary-card li {
            font-size: 15px;
            line-height: 1.9;
            color: #1f2d3d;
        }

        .info-card {
            border-radius: 16px;
            padding: 18px 20px;
            background: #f4fbf8;
            border: 1px solid #cfe6db;
            margin: 4px 0 14px 0;
        }

        .info-card .info-title {
            font-size: 15px;
            font-weight: 700;
            color: #0b7f59;
            margin: 0 0 12px 0;
        }

        .info-card .info-row {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            padding: 8px 0;
            border-bottom: 1px dashed #cfe6db;
            font-size: 15px;
        }

        .info-card .info-row:last-child {
            border-bottom: none;
        }

        .info-card .info-row .label {
            color: #45566b;
        }

        .info-card .info-row .value {
            font-weight: 700;
            color: #102a43;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# [06] BANGLA NUMBER FORMATTING
# ------------------------------------------------------------
# FUNCTION:
#     bn_num()
#
# PURPOSE:
# Converts a numeric value into a Bangla-digit display string,
# with safe fallback to "N/A" on invalid input.
#
# CHANGE HERE IF:
# - number formatting (decimals, comma grouping) needs to
#   change.
# ============================================================

def bn_num(
    value,
    decimals=2,
    comma=False
):

    if value is None:

        return "N/A"

    try:

        if comma:

            text = f"{float(value):,.{decimals}f}"

        else:

            text = f"{float(value):.{decimals}f}"

        return text.translate(
            str.maketrans(
                "0123456789",
                "০১২৩৪৫৬৭৮৯"
            )
        )

    except Exception:

        return "N/A"


# ============================================================
# [07] IRRIGATION TIME FORMATTING
# ------------------------------------------------------------
# FUNCTION:
#     format_irrigation_time_bn()
#
# PURPOSE:
# Converts decimal hours into "X ঘণ্টা Y মিনিট" Bangla text.
#
# CHANGE HERE IF:
# - irrigation-time wording/rounding needs to change.
# ============================================================

def format_irrigation_time_bn(hours):
    """
    ঘণ্টাকে বাংলায় "X ঘণ্টা Y মিনিট" আকারে দেখায়।

    - ১ ঘণ্টার কম হলে শুধু মিনিট দেখাবে (যেমন: ৪৫ মিনিট)
    - ১ ঘণ্টা বা তার বেশি হলে ঘণ্টা ও মিনিট দুটোই দেখাবে
      (যেমন: ২ ঘণ্টা ৩০ মিনিট)
    - পুরো ঘণ্টা হলে শুধু ঘণ্টা দেখাবে (যেমন: ৩ ঘণ্টা)
    """

    try:

        total_minutes = int(
            round(
                float(hours) * 60
            )
        )

    except Exception:

        return "N/A"

    if total_minutes <= 0:

        return "১ মিনিটের কম"

    h = total_minutes // 60
    m = total_minutes % 60

    parts = []

    if h > 0:

        parts.append(
            f"{bn_num(h, 0)} ঘণ্টা"
        )

    if m > 0:

        parts.append(
            f"{bn_num(m, 0)} মিনিট"
        )

    return " ".join(parts)


# ============================================================
# [08] BANGLA MONTH NAMES
# ------------------------------------------------------------
# CONSTANT:
#     BANGLA_MONTHS
#
# PURPOSE:
# Maps a calendar month number (1–12) to its Bangla name, used
# by date_text() and voice_date_text().
#
# CHANGE HERE IF:
# - month-name spelling needs to change.
# ============================================================

BANGLA_MONTHS = {
    1: "জানুয়ারি",
    2: "ফেব্রুয়ারি",
    3: "মার্চ",
    4: "এপ্রিল",
    5: "মে",
    6: "জুন",
    7: "জুলাই",
    8: "আগস্ট",
    9: "সেপ্টেম্বর",
    10: "অক্টোবর",
    11: "নভেম্বর",
    12: "ডিসেম্বর",
}


# ============================================================
# [09] DATE DISPLAY TEXT
# ------------------------------------------------------------
# FUNCTION:
#     date_text()
#
# PURPOSE:
# Formats a date object into "D Month YYYY" Bangla-labeled
# display text (digits remain ASCII here; see voice_date_text()
# for the Bangla-digit voice version).
#
# CHANGE HERE IF:
# - the display date format needs to change.
# ============================================================

def date_text(value):

    if value is None:

        return "N/A"

    try:
        return f"{value.day} {BANGLA_MONTHS[value.month]} {value.year}"

    except Exception:

        return str(value)


# ============================================================
# [10] DATE VOICE TEXT
# ------------------------------------------------------------
# FUNCTION:
#     voice_date_text()
#
# PURPOSE:
# Formats a date object into fully Bangla-digit voice text
# ("১৫ সেপ্টেম্বর ২০২৬") for use in spoken confirmations.
#
# CHANGE HERE IF:
# - the spoken date format needs to change.
# ============================================================

def voice_date_text(value):

    if value is None:
        return ""

    try:

        day = bn_num(value.day, 0)
        year = bn_num(value.year, 0)
        month = BANGLA_MONTHS.get(value.month, "")

        return f"{day} {month} {year}"

    except Exception:

        return str(value)


# ============================================================
# [11] VOICE INPUT FIELD HELPER
# ------------------------------------------------------------
# FUNCTION:
#     _voice_input_field()
#
# PURPOSE:
# Thin wrapper around voice_input_widget(): renders the mic
# widget for a given key/prompt/type, and — if a spoken value
# was applied to that key — fires input_voice_callback() so the
# usual "confirmation -> next instruction" voice sequence plays
# exactly as it would for a manual change.
#
# CHANGE HERE IF:
# - the voice-applied-value callback wiring needs to change.
# ============================================================

def _voice_input_field(
    key,
    prompt,
    value_type="text",
    options=None,
    minimum=None,
    maximum=None
):

    applied = voice_input_widget(
        key=key,
        prompt=prompt,
        value_type=value_type,
        options=options,
        minimum=minimum,
        maximum=maximum
    )

    if applied:

        input_voice_callback(
            key,
            prompt,
            None
        )

    return applied


# ============================================================
# [12] SECTION TITLE RENDERER
# ------------------------------------------------------------
# FUNCTION:
#     section_title()
#
# PURPOSE:
# Renders the standard "Bangla (English)" section heading used
# at the top of every page section.
#
# CHANGE HERE IF:
# - the heading markup/style needs to change.
# ============================================================

def section_title(
    bangla,
    english
):

    st.markdown(
        f"""
        <div class='section-title'>
            {bangla}
            ({english})
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# [13] SECTION-ENTRY VOICE
# ------------------------------------------------------------
# FUNCTION:
#     agriculture_section_voice()
#
# PURPOSE:
# Speaks a given section's intro text exactly once per session,
# guarded by a per-key session-state flag.
#
# CHANGE HERE IF:
# - the "speak once" guard behavior needs to change.
# ============================================================

def agriculture_section_voice(
    key,
    text
):

    state_key = (
        f"agriculture_section_voice_{key}"
    )

    if st.session_state.get(
        state_key,
        False
    ):

        return

    st.session_state[
        state_key
    ] = True

    section_voice(
        text,
        key=key,
        delay=0.10
    )


# ============================================================
# [14] SELECTION-CHANGE VOICE
# ------------------------------------------------------------
# FUNCTION:
#     selection_voice()
#
# PURPOSE:
# Speaks a confirmation only when a tracked value actually
# changes from its previously stored value (first-time set is
# silent).
#
# CHANGE HERE IF:
# - the change-detection / first-set behavior needs to change.
# ============================================================

def selection_voice(
    key,
    value,
    text
):

    state_key = (
        f"agriculture_voice_{key}"
    )

    old_value = st.session_state.get(
        state_key
    )

    if old_value is None:

        st.session_state[
            state_key
        ] = value

        return

    if old_value == value:

        return

    st.session_state[
        state_key
    ] = value

    voice_selection(
        text,
        key=key,
        delay=0.12
    )


# ============================================================
# [15] VOICE CONFIRMATION TEXT BUILDER
# ------------------------------------------------------------
# FUNCTION:
#     _voice_value_text()
#
# PURPOSE:
# Builds the Bangla confirmation sentence spoken after a given
# widget's value changes (numbers, dates, station, and all
# dropdown/radio selections).
#
# IF A NEW VOICE-DRIVEN INPUT IS ADDED:
# Add its key and wording here so it gets a spoken confirmation.
#
# CHANGE HERE IF:
# - confirmation wording for any specific input needs to change.
# ============================================================

def _voice_value_text(key, value):
    """Return a short Bangla confirmation for one widget value."""

    if value is None:
        return ""

    if key in {
        "agriculture_land_area",
        "agriculture_prediction_fallback_rain",
        "agriculture_prediction_fallback_et0",
        "agriculture_manual_rain",
        "agriculture_manual_et0",
        "agriculture_custom_water_depth",
        "agriculture_manual_crop_water_need",
        "agriculture_irrigation_efficiency",
        "agriculture_dripper_count",
        "agriculture_sprinkler_count",
        "agriculture_sprinkler_flow_lph",
    }:

        try:

            number = float(value)

            if number.is_integer():

                number_text = bn_num(
                    number,
                    0
                )

            else:

                number_text = bn_num(
                    number,
                    2
                )

        except Exception:

            number_text = str(value)

        if key == "agriculture_land_area":

            return (
                f"জমির পরিমাণ "
                f"{number_text} দেওয়া হয়েছে"
            )

        if key in {
            "agriculture_manual_rain",
            "agriculture_prediction_fallback_rain"
        }:

            return (
                f"বৃষ্টির পরিমাণ "
                f"{number_text} দেওয়া হয়েছে"
            )

        if key in {
            "agriculture_manual_et0",
            "agriculture_prediction_fallback_et0"
        }:

            return (
                f"রেফারেন্স বাষ্পীভবনের পরিমাণ "
                f"{number_text} দেওয়া হয়েছে"
            )

        if key == "agriculture_custom_water_depth":

            return (
                f"পানির গভীরতা "
                f"{number_text} সেন্টিমিটার দেওয়া হয়েছে"
            )

        if key == "agriculture_manual_crop_water_need":

            return (
                f"ফসলের পানির চাহিদা "
                f"{number_text} দেওয়া হয়েছে"
            )

        if key == "agriculture_irrigation_efficiency":

            return (
                f"সেচ দক্ষতা "
                f"{number_text} শতাংশ নির্বাচন করা হয়েছে"
            )

        if key == "agriculture_dripper_count":

            return (
                f"ড্রিপারের সংখ্যা "
                f"{number_text} টি দেওয়া হয়েছে"
            )

        if key == "agriculture_sprinkler_count":

            return (
                f"স্প্রিংকলারের সংখ্যা "
                f"{number_text} টি দেওয়া হয়েছে"
            )

        if key == "agriculture_sprinkler_flow_lph":

            return (
                f"প্রতি স্প্রিংকলারের পানির প্রবাহ "
                f"{number_text} লিটার প্রতি ঘণ্টা দেওয়া হয়েছে"
            )

    if key in {
        "agriculture_calculation_date",
        "agriculture_actual_planting_date",
        "agriculture_prediction_date",
    }:

        value_text = voice_date_text(value)

        if key == "agriculture_calculation_date":

            return (
                f"হিসাবের তারিখ "
                f"{value_text} নির্বাচন করা হয়েছে"
            )

        if key == "agriculture_prediction_date":

            return (
                f"পূর্বাভাসের তারিখ "
                f"{value_text} নির্বাচন করা হয়েছে"
            )

        return (
            f"রোপণ বা বপনের তারিখ "
            f"{value_text} নির্বাচন করা হয়েছে"
        )

    if key == "agriculture_station":

        raw_value = str(value)

        bn_part = raw_value

        if "—" in raw_value:

            bn_part = raw_value.split(
                "—"
            )[-1]

        station_bn = bn_part.split(
            ","
        )[0].strip()

        station_text = clean_voice_text(
            station_bn
        )

        if not station_text:

            return ""

        return (
            f"{station_text} নির্বাচন করা হয়েছে"
        )

    text = clean_voice_text(
        str(value)
    )

    if not text:

        return ""

    if key == "agriculture_weather_source":

        return (
            f"{text} নির্বাচন করা হয়েছে"
        )

    if key == "agriculture_area_unit":

        return (
            f"{text} নির্বাচন করা হয়েছে"
        )

    if key == "agriculture_crop_select":

        return (
            f"{text} নির্বাচন করা হয়েছে"
        )

    if key == "agriculture_season_select":

        return (
            f"{text} মৌসুম নির্বাচন করা হয়েছে"
        )

    if key.startswith(
        "agriculture_growth_stage"
    ):

        return (
            f"{text} নির্বাচন করা হয়েছে"
        )

    if key == "agriculture_soil_type":

        return (
            f"{text} নির্বাচন করা হয়েছে"
        )

    if key == "agriculture_water_measurement":

        return (
            f"{text} নির্বাচন করা হয়েছে"
        )

    if key == "agriculture_water_requirement_method":

        return (
            f"{text} নির্বাচন করা হয়েছে"
        )

    if key == "agriculture_irrigation_method":

        return (
            f"{text} নির্বাচন করা হয়েছে"
        )

    if key == "agriculture_reference_period":

        return (
            f"{text} নির্বাচন করা হয়েছে"
        )

    if key == "agriculture_out_of_season_stage":

        return (
            f"{text} নির্বাচন করা হয়েছে"
        )

    return (
        f"{text} নির্বাচন করা হয়েছে"
    )


# ============================================================
# [16] NEXT-INSTRUCTION VOICE MAP
# ------------------------------------------------------------
# CONSTANT:
#     VOICE_NEXT_INSTRUCTION
#
# PURPOSE:
# Maps each input's session-state key to the Bangla instruction
# spoken immediately after that input's confirmation, guiding
# the user to the next step of the form.
#
# IMPORTANT:
# The irrigation-method-specific branching (Drip / Sprinkler /
# Shallow-Deep) is NOT here — it is computed dynamically in
# input_voice_callback() below.
#
# CHANGE HERE IF:
# - the step-by-step voice guidance order/wording changes.
# ============================================================

VOICE_NEXT_INSTRUCTION = {

    "agriculture_weather_source": "",

    "agriculture_manual_rain":
        "রেফারেন্স বাষ্পীভবনের পরিমাণ দিন",

    "agriculture_prediction_fallback_rain":
        "রেফারেন্স বাষ্পীভবনের পরিমাণ দিন",

    "agriculture_manual_et0":
        "জমির পরিমাণ দিন",

    "agriculture_prediction_fallback_et0":
        "জমির পরিমাণ দিন",

    "agriculture_land_area":
        "জমির একক নির্বাচন করুন",

    "agriculture_area_unit":
        "ফসল নির্বাচন করুন",

    "agriculture_crop_select":
        "মৌসুম নির্বাচন করুন",

    "agriculture_season_select":
        "হিসাবের তারিখ নির্বাচন করুন",

    "agriculture_calculation_date":
        "রোপণ বা বপনের তারিখ নির্বাচন করুন",

    "agriculture_actual_planting_date":
        "",

    "agriculture_growth_stage":
        "মাটির ধরন নির্বাচন করুন",

    "agriculture_growth_stage_fallback":
        "মাটির ধরন নির্বাচন করুন",

    "agriculture_out_of_season_stage":
        "",

    "agriculture_reference_period":
        "",

    "agriculture_soil_type":
        "জমিতে থাকা পানির গভীরতা নির্বাচন করুন",

    "agriculture_water_measurement":
        "ফসলের পানির চাহিদা নির্ধারণের পদ্ধতি নির্বাচন করুন",

    "agriculture_custom_water_depth":
        "ফসলের পানির চাহিদা নির্ধারণের পদ্ধতি নির্বাচন করুন",

    "agriculture_water_requirement_method":
        "সেচ পদ্ধতি নির্বাচন করুন",

    "agriculture_manual_crop_water_need":
        "সেচ পদ্ধতি নির্বাচন করুন",

    "agriculture_irrigation_method":
        "স্মার্ট সেচ হিসাব করতে বোতামে চাপ দিন",

    "agriculture_dripper_count":
        "স্মার্ট সেচ হিসাব করতে বোতামে চাপ দিন",

    "agriculture_sprinkler_count":
        "প্রতি স্প্রিংকলারের পানির প্রবাহ দিন",

    "agriculture_sprinkler_flow_lph":
        "স্মার্ট সেচ হিসাব করতে বোতামে চাপ দিন",

    "agriculture_irrigation_efficiency":
        "",
}


# ============================================================
# [17] INPUT VOICE CALLBACK
# ------------------------------------------------------------
# FUNCTION:
#     input_voice_callback()
#
# PURPOSE:
# Streamlit on_change callback used by (almost) every input on
# this page. Speaks:
#     confirmation -> next relevant instruction
#
# Irrigation method has its own special branching:
#     Shallow / Deep -> Calculate
#     Drip           -> Dripper Count -> Calculate
#     Sprinkler      -> Sprinkler Count -> Flow per Sprinkler
#                        -> Calculate
#
# CHANGE HERE IF:
# - the "skip if unchanged" guard needs to change
# - the irrigation-method branching needs to change.
# ============================================================

def input_voice_callback(
    key,
    instruction=None,
    selected_text=None
):
    """
    Streamlit on_change callback.

    Voice flow:
        confirmation -> next relevant instruction

    Irrigation method special flow:
        Shallow / Deep
            -> Calculate

        Drip
            -> Dripper Count
            -> Calculate

        Sprinkler
            -> Sprinkler Count
            -> Flow per Sprinkler
            -> Calculate
    """

    value = st.session_state.get(key)

    if value is None:

        return

    if key == "agriculture_irrigation_efficiency":

        return

    if key == "agriculture_crop_select":

        return

    state_key = (
        f"agriculture_interaction_voice_{key}"
    )

    previous = st.session_state.get(
        state_key
    )

    if previous == value:

        return

    st.session_state[
        state_key
    ] = value

    confirmation = (
        selected_text
        or _voice_value_text(
            key,
            value
        )
    )

    # ------------------------------------------------------------
    # IRRIGATION METHOD → METHOD-SPECIFIC NEXT INPUT
    # ------------------------------------------------------------

    if key == "agriculture_irrigation_method":

        method_text = str(value)

        if method_text.startswith(
            "ড্রিপ"
        ):

            next_instruction = (
                "ড্রিপারের সংখ্যা দিন"
            )

        elif method_text.startswith(
            "স্প্রিংকলার"
        ):

            next_instruction = (
                "স্প্রিংকলারের সংখ্যা দিন"
            )

        else:

            next_instruction = (
                "স্মার্ট সেচ হিসাব করতে বোতামে চাপ দিন"
            )

    else:

        next_instruction = (
            VOICE_NEXT_INSTRUCTION.get(
                key,
                ""
            )
        )

    sequence = []

    if confirmation:

        sequence.append(
            confirmation
        )

    if next_instruction:

        sequence.append(
            next_instruction
        )

    if sequence:

        speak_sequence(
            sequence,
            delay=0.05
        )


# ============================================================
# [18] AUTOMATIC RAINFALL PREDICTION (FOR AGRICULTURE)
# ------------------------------------------------------------
# FUNCTION:
#     auto_predict_agriculture_rainfall()
#
# PURPOSE:
# Runs the same CatBoost rainfall pipeline used on the
# standalone Rainfall Prediction page, automatically and
# silently, for the currently selected station/date, and
# stores the result in st.session_state.rain_prediction so the
# Weather & Rainfall section (see [23]) can display it.
#
# RETURN:
#   The resolved station row (or None if station/date/meta is
#   missing).
#
# IMPORTANT:
# This function does NOT change the underlying prediction
# pipeline (load_weather_values / create_prediction_features /
# condition / estimate_rain_probability all come from
# views.prediction). It only calls that pipeline, caches by
# station+date key, and adapts weather-value fallbacks for the
# Agriculture flow (base = station CSV median per field).
#
# CHANGE HERE IF:
# - the Agriculture-side caching key changes
# - the Agriculture-side weather-fallback/note text changes.
# ============================================================

def auto_predict_agriculture_rainfall(
    df,
    model,
    feature_columns,
    train_medians,
    history_days,
    selected_label,
    target_date
):

    meta = get_station_table(df).copy()

    if meta.empty:

        st.error(
            "❌ কোনো station পাওয়া যায়নি।"
        )

        return None

    if selected_label is None or target_date is None:

        return None

    station = meta.loc[
        meta.apply(
            lambda x: (
                f"{x['Station']}, "
                f"{x['District']} "
                f"({x['Division']})"
            ),
            axis=1
        ) == selected_label
    ]

    if station.empty:

        st.error(
            "❌ নির্বাচিত station পাওয়া যায়নি।"
        )

        return None

    station = station.iloc[0]

    target = pd.Timestamp(
        target_date
    ).normalize()

    weather_key = (
        f"{station['Station_ID']}_"
        f"{target.strftime('%Y%m%d')}"
    )

    if (
        st.session_state.get(
            "agriculture_prediction_key"
        ) == weather_key
        and
        "rain_prediction" in st.session_state
    ):

        return station

    st.session_state.pop(
        "rain_prediction",
        None
    )

    try:

        with st.spinner(
            "🌦️ Station weather data load হচ্ছে..."
        ):

            weather_values, weather_error = (
                load_weather_values(
                    station=station,
                    target=target
                )
            )

        station_df = df[
            df["Station_ID"] == station["Station_ID"]
        ].copy()

        base = station_df.median(
            numeric_only=True
        ).to_dict()

        if weather_values is None:

            values = base

            values["Latitude"] = float(
                station["Latitude"]
            )

            values["Longitude"] = float(
                station["Longitude"]
            )

            weather_note = (
                "Weather API পাওয়া যায়নি; "
                "station-এর CSV median values ব্যবহার করা হয়েছে।"
            )

        else:

            values = dict(
                weather_values
            )

            weather_note = (
                "নির্বাচিত তারিখের station weather data "
                "ব্যবহার করে automatic prediction করা হয়েছে।"
            )

        numeric_weather_fields = [

            "temperature_2m_mean",

            "temperature_2m_max",

            "temperature_2m_min",

            "apparent_temperature_mean",

            "sunshine_duration",

            "daylight_duration",

            "wind_speed_10m_max",

            "wind_gusts_10m_max",

            "wind_direction_10m_dominant",

            "shortwave_radiation_sum",

            "weather_code",

            "et0_fao_evapotranspiration"
        ]

        for col in numeric_weather_fields:

            value = values.get(
                col
            )

            try:

                value = float(value)

            except Exception:

                value = np.nan

            if pd.isna(value):

                value = base.get(
                    col,
                    np.nan
                )

            try:

                value = float(value)

            except Exception:

                value = 0.0

            values[col] = value

        values["Latitude"] = float(
            values.get(
                "Latitude",
                station["Latitude"]
            )
        )

        values["Longitude"] = float(
            values.get(
                "Longitude",
                station["Longitude"]
            )
        )

        with st.spinner(
            "📚 Historical rainfall features তৈরি হচ্ছে..."
        ):

            pred_hist, bridge_note = (
                build_on_demand_history(
                    df=df,
                    station=station,
                    target_date=target,
                    history_days=history_days
                )
            )

        with st.spinner(
            "🤖 Rainfall prediction চলছে..."
        ):

            X = create_prediction_features(
                historical_df=pred_hist,
                station_id=station["Station_ID"],
                target_date=target,
                weather_values=values,
                feature_columns=feature_columns,
                train_medians=train_medians
            )

            if X.empty:

                raise ValueError(
                    "Prediction features are empty."
                )

            if len(X.columns) != len(
                feature_columns
            ):

                raise ValueError(
                    "Feature column count does not match model."
                )

            X = X.replace(
                [np.inf, -np.inf],
                np.nan
            )

            nan_count = int(
                X.isna().sum().sum()
            )

            if nan_count > 0:

                raise ValueError(
                    f"Prediction features contain "
                    f"{nan_count} NaN values."
                )

            prediction_array = np.asarray(
                model.predict(X)
            ).reshape(-1)

            if len(
                prediction_array
            ) == 0:

                raise ValueError(
                    "Model returned no prediction."
                )

            pred = max(
                float(
                    prediction_array[0]
                ),
                0.0
            )

        weather_code = int(
            round(
                float(
                    values.get(
                        "weather_code",
                        0
                    )
                )
            )
        )

        weather_name, message = condition(
            code=weather_code,
            pred=pred
        )

        rain_probability = (
            estimate_rain_probability(
                pred
            )
        )

        try:

            et0 = float(
                values.get(
                    "et0_fao_evapotranspiration",
                    4.0
                )
            )

        except Exception:

            et0 = 4.0

        if not np.isfinite(et0):

            et0 = 4.0

        st.session_state.rain_prediction = {

            "prediction":
                pred,

            "rain_probability":
                rain_probability,

            "station":
                station,

            "date":
                target,

            "weather_values":
                values,

            "condition":
                weather_name,

            "message":
                message,

            "et0":
                et0,

            "history_note":
                bridge_note,

            "is_future":
                target.date() > date.today(),

            "agriculture_auto":
                True,

            "weather_note":
                weather_note,

            "weather_error":
                weather_error
        }

        st.session_state[
            "agriculture_prediction_key"
        ] = weather_key

        return station

    except Exception as exc:

        st.session_state.pop(
            "rain_prediction",
            None
        )

        st.session_state.pop(
            "agriculture_prediction_key",
            None
        )

        st.error(
            "❌ Agriculture-এর জন্য automatic "
            "rainfall prediction করা যায়নি।"
        )

        st.exception(exc)

        return station


# ============================================================
# [19] BANGLA LOCATION NAME TABLES
# ------------------------------------------------------------
# CONSTANTS:
#     BN_DIVISIONS, BN_DISTRICTS, BN_STATIONS
#
# PURPOSE:
# English -> Bangla lookup tables for division, district, and
# station names, used to build Bangla location labels/voice.
#
# CHANGE HERE IF:
# - a station/district/division name or its Bangla spelling
#   needs to be added or corrected.
# ============================================================

BN_DIVISIONS = {
    "Dhaka": "ঢাকা",
    "Chattogram": "চট্টগ্রাম",
    "Chittagong": "চট্টগ্রাম",
    "Rajshahi": "রাজশাহী",
    "Khulna": "খুলনা",
    "Barisal": "বরিশাল",
    "Barishal": "বরিশাল",
    "Sylhet": "সিলেট",
    "Rangpur": "রংপুর",
    "Mymensingh": "ময়মনসিংহ",
}


BN_DISTRICTS = {
    "Dhaka": "ঢাকা",
    "Faridpur": "ফরিদপুর",
    "Gazipur": "গাজীপুর",
    "Gopalganj": "গোপালগঞ্জ",
    "Kishoreganj": "কিশোরগঞ্জ",
    "Madaripur": "মাদারীপুর",
    "Manikganj": "মানিকগঞ্জ",
    "Munshiganj": "মুন্সিগঞ্জ",
    "Narayanganj": "নারায়ণগঞ্জ",
    "Narsingdi": "নরসিংদী",
    "Rajbari": "রাজবাড়ী",
    "Shariatpur": "শরীয়তপুর",
    "Tangail": "টাঙ্গাইল",
    "Bogra": "বগুড়া",
    "Bogura": "বগুড়া",
    "Joypurhat": "জয়পুরহাট",
    "Naogaon": "নওগাঁ",
    "Natore": "নাটোর",
    "Chapainawabganj": "চাঁপাইনবাবগঞ্জ",
    "Nawabganj": "চাঁপাইনবাবগঞ্জ",
    "Pabna": "পাবনা",
    "Rajshahi": "রাজশাহী",
    "Sirajganj": "সিরাজগঞ্জ",
    "Dinajpur": "দিনাজপুর",
    "Gaibandha": "গাইবান্ধা",
    "Kurigram": "কুড়িগ্রাম",
    "Lalmonirhat": "লালমনিরহাট",
    "Nilphamari": "নীলফামারী",
    "Panchagarh": "পঞ্চগড়",
    "Rangpur": "রংপুর",
    "Thakurgaon": "ঠাকুরগাঁও",
    "Bagerhat": "বাগেরহাট",
    "Chuadanga": "চুয়াডাঙ্গা",
    "Jashore": "যশোর",
    "Jessore": "যশোর",
    "Jhenaidah": "ঝিনাইদহ",
    "Khulna": "খুলনা",
    "Kushtia": "কুষ্টিয়া",
    "Magura": "মাগুরা",
    "Meherpur": "মেহেরপুর",
    "Narail": "নড়াইল",
    "Satkhira": "সাতক্ষীরা",
    "Barguna": "বরগুনা",
    "Barisal": "বরিশাল",
    "Barishal": "বরিশাল",
    "Bhola": "ভোলা",
    "Jhalokati": "ঝালকাঠি",
    "Patuakhali": "পটুয়াখালী",
    "Pirojpur": "পিরোজপুর",
    "Habiganj": "হবিগঞ্জ",
    "Moulvibazar": "মৌলভীবাজার",
    "Sunamganj": "সুনামগঞ্জ",
    "Sylhet": "সিলেট",
    "Bandarban": "বান্দরবান",
    "Brahmanbaria": "ব্রাহ্মণবাড়িয়া",
    "Chandpur": "চাঁদপুর",
    "Chattogram": "চট্টগ্রাম",
    "Chittagong": "চট্টগ্রাম",
    "Cumilla": "কুমিল্লা",
    "Comilla": "কুমিল্লা",
    "Cox's Bazar": "কক্সবাজার",
    "Coxs Bazar": "কক্সবাজার",
    "Coxsbazar": "কক্সবাজার",
    "Feni": "ফেনী",
    "Khagrachhari": "খাগড়াছড়ি",
    "Lakshmipur": "লক্ষ্মীপুর",
    "Noakhali": "নোয়াখালী",
    "Rangamati": "রাঙ্গামাটি",
    "Jamalpur": "জামালপুর",
    "Mymensingh": "ময়মনসিংহ",
    "Netrokona": "নেত্রকোণা",
    "Sherpur": "শেরপুর",
}


BN_STATIONS = {
    "Dhaka": "ঢাকা",
    "Faridpur": "ফরিদপুর",
    "Tangail": "টাঙ্গাইল",
    "Mymensingh": "ময়মনসিংহ",
    "Bogra": "বগুড়া",
    "Rangpur": "রংপুর",
    "Dinajpur": "দিনাজপুর",
    "Sylhet": "সিলেট",
    "Srimangal": "শ্রীমঙ্গল",
    "Rajshahi": "রাজশাহী",
    "Ishurdi": "ঈশ্বরদী",
    "Bagerhat": "বাগেরহাট",
    "Chuadanga": "চুয়াডাঙ্গা",
    "Jessore": "যশোর",
    "Jashore": "যশোর",
    "Khulna": "খুলনা",
    "Mongla": "মোংলা",
    "Satkhira": "সাতক্ষীরা",
    "Barisal": "বরিশাল",
    "Barishal": "বরিশাল",
    "Bhola": "ভোলা",
    "Patuakhali": "পটুয়াখালী",
    "Khepupara": "খেপুপাড়া",
    "Chittagong": "চট্টগ্রাম",
    "Chattogram": "চট্টগ্রাম",
    "Comilla": "কুমিল্লা",
    "Cumilla": "কুমিল্লা",
    "Cox's Bazar": "কক্সবাজার",
    "Coxsbazar": "কক্সবাজার",
    "Feni": "ফেনী",
    "Hatiya": "হাতিয়া",
    "Kutubdia": "কুতুবদিয়া",
    "Maijdee Court": "মাইজদী কোর্ট",
    "Rangamati": "রাঙ্গামাটি",
    "Sandwip": "সন্দ্বীপ",
    "Sitakunda": "সীতাকুণ্ড",
    "Teknaf": "টেকনাফ",
    "Chandpur": "চাঁদপুর",
    "Jamalpur": "জামালপুর",
    "Madaripur": "মাদারীপুর",
    "Narail": "নড়াইল",
    "Netrokona": "নেত্রকোণা",
    "Sirajganj": "সিরাজগঞ্জ",
    "Tetulia": "তেঁতুলিয়া",
    "Panchagarh": "পঞ্চগড়",
    "Gopalganj": "গোপালগঞ্জ",
}


# ============================================================
# [20] BANGLA NAME LOOKUP
# ------------------------------------------------------------
# FUNCTION:
#     _bn_lookup()
#
# PURPOSE:
# Case-insensitive lookup of an English name inside one of the
# BN_* tables above; returns the original (English) name if no
# Bangla translation is found.
#
# CHANGE HERE IF:
# - the lookup/fallback strategy needs to change.
# ============================================================

def _bn_lookup(name, table):

    if name is None:

        return ""

    key = str(name).strip()

    if key in table:

        return table[key]

    lowered = key.lower()

    for eng, bn in table.items():

        if eng.lower() == lowered:

            return bn

    return key


# ============================================================
# [21] BANGLA LOCATION LABEL BUILDER
# ------------------------------------------------------------
# FUNCTION:
#     build_bn_location_label()
#
# PURPOSE:
# Builds the Bangla "Station, District (Division)" label used
# alongside the English label in the station dropdown.
#
# CHANGE HERE IF:
# - the label format/order needs to change.
# ============================================================

def build_bn_location_label(
    station,
    district,
    division
):

    station_bn = _bn_lookup(
        station,
        BN_STATIONS
    )

    district_bn = _bn_lookup(
        district,
        BN_DISTRICTS
    )

    division_bn = _bn_lookup(
        division,
        BN_DIVISIONS
    )

    return (
        f"{station_bn}, "
        f"{district_bn} "
        f"({division_bn})"
    )


# ============================================================
# [22] LOCATION & DATE SECTION
# ------------------------------------------------------------
# FUNCTION:
#     agriculture_location_date_section()
#
# PURPOSE:
# Renders the Station + Prediction Date selectors (with voice
# input support) and, once both are chosen, triggers the
# automatic rainfall prediction (see [18]).
#
# RETURN:
#   (selected_label, target_date)
#
# CHANGE HERE IF:
# - station/date selection UI needs to change
# - what happens once both are selected needs to change.
# ============================================================

def agriculture_location_date_section(
    df,
    model,
    feature_columns,
    train_medians,
    history_days
):

    section_title(
        "স্থান ও তারিখ",
        "Location & Date"
    )

    meta = get_station_table(
        df
    ).copy()

    if meta.empty:

        st.error(
            "❌ কোনো station পাওয়া যায়নি।"
        )

        return None, None

    meta["label"] = meta.apply(
        lambda x: (
            f"{x['Station']}, "
            f"{x['District']} "
            f"({x['Division']})"
        ),
        axis=1
    )

    meta["label_bn"] = meta.apply(
        lambda x: build_bn_location_label(
            x["Station"],
            x["District"],
            x["Division"]
        ),
        axis=1
    )

    meta["display_label"] = (
        meta["label"]
        + "  —  "
        + meta["label_bn"]
    )

    display_to_label = dict(
        zip(
            meta["display_label"],
            meta["label"]
        )
    )

    display_labels = sorted(
        meta["display_label"].tolist()
    )

    with st.container(border=True):

        c1, c2 = st.columns(2)

        with c1:

            prepare_voice_input(
                "agriculture_station"
            )

            selected_display_label = (
                st.selectbox(
                    "📍 Location / Station নির্বাচন করুন",
                    display_labels,
                    index=None,
                    key="agriculture_station",
                    on_change=input_voice_callback,
                    args=(
                        "agriculture_station",
                        "Location / Station নির্বাচন করুন",
                        None
                    )
                )
            )

            _voice_input_field(
                "agriculture_station",
                "স্টেশন বা এলাকার নাম বলুন",
                "option",
                display_labels
            )

        with c2:

            prepare_voice_input(
                "agriculture_prediction_date"
            )

            target_date = st.date_input(
                "তারিখ নির্বাচন করুন (Prediction Date)",
                value=None,
                format="YYYY/MM/DD",
                key="agriculture_prediction_date",
                on_change=input_voice_callback,
                args=(
                    "agriculture_prediction_date",
                    "পূর্বাভাসের তারিখ নির্বাচন করুন",
                    None
                )
            )

            _voice_input_field(
                "agriculture_prediction_date",
                "তারিখ বলুন, যেমন ১৫ সেপ্টেম্বর ২০২৬",
                "date"
            )

    selected_label = (
        display_to_label.get(
            selected_display_label
        )
        if selected_display_label is not None
        else None
    )

    if (
        selected_label is None
        or target_date is None
    ):

        st.info(
            "Rainfall prediction-এর জন্য আগে "
            "Location এবং Date নির্বাচন করুন।"
        )

        st.session_state.pop(
            "rain_prediction",
            None
        )

        st.session_state.pop(
            "agriculture_prediction_key",
            None
        )

        return (
            selected_label,
            target_date
        )

    selected_station = (
        auto_predict_agriculture_rainfall(
            df=df,
            model=model,
            feature_columns=feature_columns,
            train_medians=train_medians,
            history_days=history_days,
            selected_label=selected_label,
            target_date=target_date
        )
    )

    # NOTE:
    # The extra "Location / Date / ET0" summary card that used to be
    # shown here (right after the rain prediction success message)
    # has been intentionally removed to reduce clutter. The rain
    # prediction result is still shown to the user in the
    # "আবহাওয়া ও বৃষ্টির তথ্য (Weather & Rainfall Information)"
    # section below.

    return (
        selected_label,
        target_date
    )


# ============================================================
# [23] WEATHER & RAINFALL INFORMATION SECTION
# ------------------------------------------------------------
# FUNCTION:
#     weather_information_section()
#
# PURPOSE:
# Lets the user either use the AUTO (predicted) rainfall/ET0
# from [18], or switch to MANUAL entry. Also speaks the
# predicted-rainfall voice summary once per distinct
# (rain, et0) result.
#
# RETURN:
#   (weather_source, predicted_rain, et0_value)
#
# CHANGE HERE IF:
# - Auto/Manual UI or fallback behavior needs to change
# - the predicted-rainfall voice summary needs to change.
# ============================================================

def weather_information_section():

    section_title(
        "আবহাওয়া ও বৃষ্টির তথ্য",
        "Weather & Rainfall Information"
    )

    st.session_state.pop(
        "agriculture_weather_source",
        None
    )

    with st.container(border=True):

        manual_selected = st.checkbox(
            "☐ নিজে বৃষ্টির পরিমাণ দিতে চাই",
            key="agriculture_manual_rain_choice"
        )

    if manual_selected:

        weather_source = "MANUAL"

    else:

        weather_source = "AUTO"

    predicted_rain = 0.0
    et0_value = 0.0

    if weather_source == "AUTO":

        if "rain_prediction" in st.session_state:

            rain_data = (
                st.session_state.rain_prediction
            )

            try:

                predicted_rain = float(
                    rain_data.get(
                        "prediction",
                        0.0
                    )
                )

            except Exception:

                predicted_rain = 0.0

            try:

                et0_value = float(
                    rain_data.get(
                        "et0",
                        4.0
                    )
                )

            except Exception:

                et0_value = 4.0

            with st.container(border=True):

                st.success(
                    f"""
                    বৃষ্টির পূর্বাভাস:
                    {bn_num(predicted_rain, 2)} mm

                    ET0:
                    {bn_num(et0_value, 2)} mm/day
                    """
                )

            prediction_voice_signature = (

                round(
                    float(predicted_rain),
                    2
                ),

                round(
                    float(et0_value),
                    2
                )
            )

            if (
                st.session_state.get(
                    "agriculture_prediction_weather_voice_signature"
                )
                != prediction_voice_signature
            ):

                st.session_state[
                    "agriculture_prediction_weather_voice_signature"
                ] = prediction_voice_signature

                PAUSE_TOKEN = "।"

                speak_sequence(
                    [

                        (
                            f"আজকে আনুমানিক "
                            f"{bn_num(predicted_rain, 2)} "
                            f"মিলিমিটার বৃষ্টি হতে পারে।"
                        ),

                        (
                            f"রেফারেন্স বাষ্পীভবনের পরিমাণ "
                            f"আনুমানিক "
                            f"{bn_num(et0_value, 2)} "
                            f"মিলিমিটার হতে পারে।"
                        ),

                        "আপনি চাইলে নিজে পরিমাপ দিতে পারেন অথবা পরবর্তী তথ্য",

                        PAUSE_TOKEN,
                        PAUSE_TOKEN,
                        PAUSE_TOKEN,

                        "জমির পরিমাণ দিন"
                    ],
                    delay=0.05
                )

        else:

            with st.container(border=True):

                st.warning(
                    "আগে Rain Prediction করুন অথবা "
                    "নিজে বৃষ্টির পরিমাণ দিন নির্বাচন করুন।"
                )

                c1, c2 = st.columns(2)

                with c1:

                    prepare_voice_input(
                        "agriculture_prediction_fallback_rain"
                    )

                    predicted_rain = st.number_input(
                        "আজকের বৃষ্টির পরিমাণ "
                        "(Today's Rainfall) mm",
                        min_value=0.0,
                        value=0.0,
                        step=0.5,
                        key="agriculture_prediction_fallback_rain",
                        on_change=input_voice_callback,
                        args=(
                            "agriculture_prediction_fallback_rain",
                            "আজকের বৃষ্টির পরিমাণ দিন",
                            None
                        )
                    )

                    _voice_input_field(
                        "agriculture_prediction_fallback_rain",
                        "আজকের বৃষ্টির পরিমাণ বলুন",
                        "number",
                        minimum=0.0
                    )

                with c2:

                    prepare_voice_input(
                        "agriculture_prediction_fallback_et0"
                    )

                    et0_value = st.number_input(
                        "রেফারেন্স বাষ্পীভবন "
                        "(ET0 / Reference Evapotranspiration) mm/day",
                        min_value=0.0,
                        value=4.0,
                        step=0.1,
                        key="agriculture_prediction_fallback_et0",
                        on_change=input_voice_callback,
                        args=(
                            "agriculture_prediction_fallback_et0",
                            "রেফারেন্স বাষ্পীভবনের পরিমাণ দিন",
                            None
                        )
                    )

                    _voice_input_field(
                        "agriculture_prediction_fallback_et0",
                        "রেফারেন্স বাষ্পীভবনের পরিমাণ বলুন",
                        "number",
                        minimum=0.0
                    )

    else:

        with st.container(border=True):

            c1, c2 = st.columns(2)

            with c1:

                prepare_voice_input(
                    "agriculture_manual_rain"
                )

                predicted_rain = st.number_input(
                    "আজকের বৃষ্টির পরিমাণ "
                    "(Today's Rainfall) mm",
                    min_value=0.0,
                    value=0.0,
                    step=0.5,
                    key="agriculture_manual_rain",
                    on_change=input_voice_callback,
                    args=(
                        "agriculture_manual_rain",
                        "আজকের বৃষ্টির পরিমাণ দিন",
                        None
                    )
                )

                _voice_input_field(
                    "agriculture_manual_rain",
                    "আজকের বৃষ্টির পরিমাণ বলুন",
                    "number",
                    minimum=0.0
                )

            with c2:

                prepare_voice_input(
                    "agriculture_manual_et0"
                )

                et0_value = st.number_input(
                    "রেফারেন্স বাষ্পীভবন "
                    "(ET0 / Reference Evapotranspiration) mm/day",
                    min_value=0.0,
                    value=4.0,
                    step=0.1,
                    key="agriculture_manual_et0",
                    on_change=input_voice_callback,
                    args=(
                        "agriculture_manual_et0",
                        "রেফারেন্স বাষ্পীভবনের পরিমাণ দিন",
                        None
                    )
                )

                _voice_input_field(
                    "agriculture_manual_et0",
                    "রেফারেন্স বাষ্পীভবনের পরিমাণ বলুন",
                    "number",
                    minimum=0.0
                )

    return (
        weather_source,
        predicted_rain,
        et0_value
    )


# ============================================================
# [24] LAND INFORMATION SECTION
# ------------------------------------------------------------
# FUNCTION:
#     land_information_section()
#
# PURPOSE:
# Collects land area and its unit (Decimal / Acre / Hectare /
# Square Meter).
#
# RETURN:
#   (land_area, area_unit)
#
# CHANGE HERE IF:
# - available area units need to change.
# ============================================================

def land_information_section():

    section_title(
        "জমির তথ্য",
        "Land Information"
    )

    with st.container(border=True):

        c1, c2 = st.columns(2)

        with c1:

            prepare_voice_input(
                "agriculture_land_area"
            )

            land_area = st.number_input(
                "জমির পরিমাণ (Land Area)",
                min_value=0.01,
                value=None,
                step=0.01,
                placeholder="জমির পরিমাণ লিখুন",
                key="agriculture_land_area",
                on_change=input_voice_callback,
                args=(
                    "agriculture_land_area",
                    "জমির পরিমাণ দিন",
                    None
                )
            )

            _voice_input_field(
                "agriculture_land_area",
                "জমির পরিমাণ বলুন",
                "number",
                minimum=0.01
            )

        with c2:

            prepare_voice_input(
                "agriculture_area_unit"
            )

            area_unit = st.selectbox(
                "জমির একক (Area Unit)",
                [
                    "শতক (Decimal)",
                    "একর (Acre)",
                    "হেক্টর (Hectare)",
                    "বর্গমিটার (Square Meter)"
                ],
                index=None,
                placeholder="জমির একক নির্বাচন করুন",
                key="agriculture_area_unit",
                on_change=input_voice_callback,
                args=(
                    "agriculture_area_unit",
                    "জমির একক নির্বাচন করুন",
                    None
                )
            )

            _voice_input_field(
                "agriculture_area_unit",
                "জমির একক বলুন",
                "option",
                [
                    "শতক (Decimal)",
                    "একর (Acre)",
                    "হেক্টর (Hectare)",
                    "বর্গমিটার (Square Meter)"
                ]
            )

        if (
            land_area is None
            or area_unit is None
        ):

            st.info(
                "জমির পরিমাণ লিখুন এবং একক নির্বাচন করুন।"
            )

    return (
        land_area,
        area_unit
    )


# ============================================================
# [25] CROP INFORMATION SECTION
# ------------------------------------------------------------
# FUNCTION:
#     crop_information_section()
#
# PURPOSE:
# Collects Crop selection, and Season selection — season is a
# manual selectbox for rice crops (ধান) and is auto-selected
# (single option) for all other crops.
#
# RETURN:
#   (crop_label, crop_name, season_label, season_name,
#    crop_error)
#
# CHANGE HERE IF:
# - crop/season selection UI or the rice-vs-other-crop branching
#   needs to change.
# ============================================================

def crop_information_section():

    section_title(
        "ফসলের তথ্য",
        "Crop Information"
    )

    crop_options = get_crop_options()

    if not crop_options:

        st.error(
            "Crop reference dataset পাওয়া যায়নি।"
        )

        return (
            None,
            None,
            None,
            None,
            True
        )

    with st.container(border=True):

        c1, c2 = st.columns(2)

        with c1:

            prepare_voice_input(
                "agriculture_crop_select"
            )

            crop_label = st.selectbox(
                "ফসল নির্বাচন করুন (Select Crop)",
                list(crop_options.keys()),
                index=None,
                placeholder="ফসল নির্বাচন করুন",
                key="agriculture_crop_select",
                on_change=input_voice_callback,
                args=(
                    "agriculture_crop_select",
                    "ফসল নির্বাচন করুন",
                    None
                )
            )

            _voice_input_field(
                "agriculture_crop_select",
                "ফসলের নাম বলুন",
                "option",
                list(crop_options.keys())
            )

        if crop_label is None:

            st.info(
                "উপরের বক্সে একটি ফসল নির্বাচন করুন।"
            )

            return (
                None,
                None,
                None,
                None,
                True
            )

        previous_crop = st.session_state.get(
            "agriculture_previous_crop"
        )

        crop_changed = (
            previous_crop is not None
            and previous_crop != crop_label
        )

        if crop_changed:

            st.session_state.pop(
                "agriculture_season_select",
                None
            )

            st.session_state.pop(
                "agriculture_interaction_voice_agriculture_season_select",
                None
            )

            st.session_state.pop(
                "agriculture_crop_voice_signature",
                None
            )

        st.session_state[
            "agriculture_previous_crop"
        ] = crop_label

        crop_name = crop_options[
            crop_label
        ]

        season_options = get_season_options(
            crop_name
        )

        if not season_options:

            st.error(
                "এই ফসলের Season data পাওয়া যায়নি।"
            )

            return (
                crop_label,
                crop_name,
                None,
                None,
                True
            )

        is_rice = crop_label.startswith(
            "ধান"
        )

        crop_voice_signature = crop_label

        crop_voice_already_spoken = (
            st.session_state.get(
                "agriculture_crop_voice_signature"
            )
            == crop_voice_signature
        )

        if is_rice:

            if not crop_voice_already_spoken:

                st.session_state[
                    "agriculture_crop_voice_signature"
                ] = crop_voice_signature

                speak_sequence(
                    [
                        (
                            f"{clean_voice_text(crop_label)} "
                            f"নির্বাচন করা হয়েছে"
                        ),
                        "মৌসুম নির্বাচন করুন"
                    ],
                    delay=0.10
                )

            with c2:

                prepare_voice_input(
                    "agriculture_season_select"
                )

                season_label = st.selectbox(
                    "মৌসুম নির্বাচন করুন (Select Season)",
                    list(season_options.keys()),
                    index=None,
                    placeholder="মৌসুম নির্বাচন করুন",
                    key="agriculture_season_select",
                    on_change=input_voice_callback,
                    args=(
                        "agriculture_season_select",
                        "মৌসুম নির্বাচন করুন",
                        None
                    )
                )

                _voice_input_field(
                    "agriculture_season_select",
                    "মৌসুমের নাম বলুন",
                    "option",
                    list(season_options.keys())
                )

            if season_label is None:

                st.info(
                    "মৌসুম নির্বাচন করুন।"
                )

                return (
                    crop_label,
                    crop_name,
                    None,
                    None,
                    True
                )

            season_name = season_options[
                season_label
            ]

        else:

            season_label = list(
                season_options.keys()
            )[0]

            season_name = season_options[
                season_label
            ]

            if not crop_voice_already_spoken:

                st.session_state[
                    "agriculture_crop_voice_signature"
                ] = crop_voice_signature

                speak_sequence(
                    [
                        (
                            f"{clean_voice_text(crop_label)} "
                            f"নির্বাচন করা হয়েছে"
                        ),
                        (
                            f"{clean_voice_text(season_label)} "
                            f"মৌসুম স্বয়ংক্রিয়ভাবে নির্বাচন করা হয়েছে।"
                        ),
                        "হিসাবের তারিখ নির্বাচন করুন"
                    ],
                    delay=0.10
                )

            with c2:

                st.info(
                    f"মৌসুম (Season): "
                    f"{season_label}"
                )

    return (
        crop_label,
        crop_name,
        season_label,
        season_name,
        False
    )


# ============================================================
# [26] PLANTING & GROWTH STAGE SECTION
# ------------------------------------------------------------
# FUNCTION:
#     planting_growth_section()
#
# PURPOSE:
# Collects Calculation Date + Planting/Sowing Date, then calls
# determine_growth_stage() to automatically compute the crop's
# current growth stage, with:
#   - a manual override selectbox when a stage is available
#   - a specific "Out of Season" error/reference-period view
#   - a manual fallback selectbox when calendar data is missing
#
# RETURN:
#   (calculation_date, actual_planting_date,
#    use_actual_planting, stage_info, crop_stage,
#    calculation_allowed)
#
# CHANGE HERE IF:
# - date inputs, automatic-stage display, or the
#   override/fallback/out-of-season branching needs to change.
#
# IMPORTANT:
# The growth-stage CALCULATION itself lives in
# services.agriculture.determine_growth_stage(); this function
# only renders the UI around it.
# ============================================================

def planting_growth_section(
    crop_name,
    season_name
):

    section_title(
        "রোপণ/বপন ও বৃদ্ধির পর্যায়",
        "Planting & Growth Stage"
    )

    with st.container(border=True):

        d1, d2 = st.columns(2)

        with d1:

            prepare_voice_input(
                "agriculture_calculation_date"
            )

            calculation_date = st.date_input(
                "হিসাবের তারিখ (Calculation Date)",
                value=None,
                format="YYYY/MM/DD",
                key="agriculture_calculation_date",
                on_change=input_voice_callback,
                args=(
                    "agriculture_calculation_date",
                    "হিসাবের তারিখ নির্বাচন করুন",
                    None
                )
            )

            _voice_input_field(
                "agriculture_calculation_date",
                "হিসাবের তারিখ বলুন, যেমন ১৫ সেপ্টেম্বর ২০২৬",
                "date"
            )

        with d2:

            prepare_voice_input(
                "agriculture_actual_planting_date"
            )

            actual_planting_date = st.date_input(
                "রোপণ/বপনের তারিখ "
                "(Planting / Sowing Date)",
                value=None,
                format="YYYY/MM/DD",
                key="agriculture_actual_planting_date",
                on_change=input_voice_callback,
                args=(
                    "agriculture_actual_planting_date",
                    "রোপণ বা বপনের তারিখ নির্বাচন করুন",
                    None
                )
            )

            _voice_input_field(
                "agriculture_actual_planting_date",
                "রোপণ বা বপনের তারিখ বলুন, যেমন ১০ জুলাই ২০২৬",
                "date"
            )

        if (
            calculation_date is None
            or actual_planting_date is None
        ):

            st.info(
                "হিসাবের তারিখ এবং রোপণ/বপনের তারিখ নির্বাচন করুন। "
                "ক্যালেন্ডার থেকে নির্বাচন করতে পারেন অথবা তারিখ লিখতে পারেন।"
            )

    use_actual_planting = True

    if (
        calculation_date is None
        or actual_planting_date is None
    ):

        return (
            calculation_date,
            actual_planting_date,
            use_actual_planting,
            {
                "available": False,
                "status": "INCOMPLETE"
            },
            None,
            False
        )

    st.caption(
        "ফসলের বয়স ও বৃদ্ধি পর্যায় "
        "রোপণ/বপনের তারিখ থেকে স্বয়ংক্রিয়ভাবে হিসাব করা হবে।"
    )

    stage_info = determine_growth_stage(
        crop_name,
        season_name,
        calculation_date,
        planting_date=actual_planting_date,
        use_actual_planting_date=use_actual_planting
    )

    calculation_allowed = True
    crop_stage = None

    if stage_info.get("available"):

        automatic_stage = (
            stage_info["stage"]
        )

        stage_voice_state_key = (
            "agriculture_auto_stage_voice_signature"
        )

        stage_voice_signature = (
            crop_name,
            season_name,
            str(calculation_date),
            str(actual_planting_date),
            automatic_stage
        )

        if (
            st.session_state.get(
                stage_voice_state_key
            )
            != stage_voice_signature
        ):

            st.session_state[
                stage_voice_state_key
            ] = stage_voice_signature

            growth_stage_auto_voice(
                stage_info.get(
                    "stage_label",
                    automatic_stage
                )
            )

        with st.container(border=True):

            st.markdown(
                f"""
                <div style="font-size:16px; font-weight:600; margin:0 0 10px 0;">
                    স্বয়ংক্রিয়ভাবে নির্ধারিত পর্যায়:
                    {stage_info.get('stage_label', automatic_stage)}
                </div>
                """,
                unsafe_allow_html=True
            )

            c1, c2 = st.columns(2)

            with c1:

                prepare_voice_input(
                    "agriculture_growth_stage"
                )

                manual_stage_label = st.selectbox(
                    "বর্তমান বৃদ্ধি পর্যায় "
                    "(Growth Stage)",
                    [
                        "স্বয়ংক্রিয় (Automatic)",
                        "চারা/প্রাথমিক পর্যায় (Initial Stage)",
                        "বৃদ্ধি পর্যায় (Development Stage)",
                        "মধ্য পর্যায় (Mid Stage)",
                        "পরিপক্বতা পর্যায় (Late Stage)"
                    ],
                    key="agriculture_growth_stage",
                    on_change=input_voice_callback,
                    args=(
                        "agriculture_growth_stage",
                        "বর্তমান বৃদ্ধি পর্যায় নির্বাচন করুন",
                        None
                    )
                )

                _voice_input_field(
                    "agriculture_growth_stage",
                    "বৃদ্ধি পর্যায় বলুন",
                    "option",
                    [
                        "স্বয়ংক্রিয় (Automatic)",
                        "চারা/প্রাথমিক পর্যায় (Initial Stage)",
                        "বৃদ্ধি পর্যায় (Development Stage)",
                        "মধ্য পর্যায় (Mid Stage)",
                        "পরিপক্বতা পর্যায় (Late Stage)"
                    ]
                )

            stage_map = {

                "স্বয়ংক্রিয় (Automatic)":
                    automatic_stage,

                "চারা/প্রাথমিক পর্যায় (Initial Stage)":
                    "Initial",

                "বৃদ্ধি পর্যায় (Development Stage)":
                    "Development",

                "মধ্য পর্যায় (Mid Stage)":
                    "Mid",

                "পরিপক্বতা পর্যায় (Late Stage)":
                    "Late"
            }

            crop_stage = stage_map[
                manual_stage_label
            ]

            c2.info(
                f"""
                ফসলের বয়স

                {bn_num(
                    stage_info.get(
                        'day_of_crop'
                    ),
                    0
                )}
                দিন /

                {bn_num(
                    stage_info.get(
                        'duration_days'
                    ),
                    0
                )}
                দিন
                """
            )

            st.caption(
                "আপনি চাইলে উপরের বৃদ্ধি পর্যায় থেকে "
                "অন্য পর্যায় নির্বাচন করতে পারেন।"
            )

            if stage_info.get(
                "message"
            ):

                st.success(
                    stage_info["message"]
                )

            if stage_info.get(
                "warning"
            ):

                st.warning(
                    stage_info["warning"]
                )

    elif stage_info.get(
        "status"
    ) == "OUT_OF_SEASON":

        calculation_allowed = False

        with st.container(border=True):

            c1, c2 = st.columns(2)

            c1.text_input(
                "ফসলের বৃদ্ধি পর্যায় "
                "(Crop Growth Stage)",
                value="মৌসুমের বাইরে (Out of Season)",
                disabled=True,
                key="agriculture_out_of_season_stage"
            )

            reference_period = (
                f"{date_text(stage_info.get('reference_start_date'))}"
                f" → "
                f"{date_text(stage_info.get('reference_end_date'))}"
            )

            c2.text_input(
                "রেফারেন্স ফসলের সময়কাল "
                "(Reference Crop Period)",
                value=reference_period,
                disabled=True,
                key="agriculture_reference_period"
            )

            st.error(
                "নির্বাচিত হিসাবের তারিখটি এই ফসলের "
                "reference growing season-এর বাইরে। "
                "মৌসুমের মধ্যে একটি তারিখ নির্বাচন করুন "
                "অথবা কৃষকের প্রকৃত রোপণ/বপনের তারিখ ব্যবহার করুন।"
            )

    elif stage_info.get(
        "status"
    ) in [
        "FUTURE_PLANTING_DATE",
        "CROP_CYCLE_COMPLETE",
        "INVALID_PLANTING_DATE"
    ]:

        calculation_allowed = False

        st.error(
            stage_info.get(
                "message",
                "রোপণ/বপনের তারিখ সঠিক নয়। আবার নির্বাচন করুন।"
            )
        )

    else:

        with st.container(border=True):

            st.warning(
                stage_info.get(
                    "message",
                    "Calendar data অসম্পূর্ণ।"
                )
            )

            prepare_voice_input(
                "agriculture_growth_stage_fallback"
            )

            manual_stage_label = st.selectbox(
                "বর্তমান বৃদ্ধি পর্যায় "
                "(Growth Stage)",
                [
                    "চারা/প্রাথমিক পর্যায় (Initial Stage)",
                    "বৃদ্ধি পর্যায় (Development Stage)",
                    "মধ্য পর্যায় (Mid Stage)",
                    "পরিপক্বতা পর্যায় (Late Stage)"
                ],
                index=None,
                placeholder="বৃদ্ধি পর্যায় নির্বাচন করুন",
                key="agriculture_growth_stage_fallback",
                on_change=input_voice_callback,
                args=(
                    "agriculture_growth_stage_fallback",
                    "বর্তমান বৃদ্ধি পর্যায় নির্বাচন করুন",
                    None
                )
            )

            _voice_input_field(
                "agriculture_growth_stage_fallback",
                "বৃদ্ধি পর্যায় বলুন",
                "option",
                [
                    "চারা/প্রাথমিক পর্যায় (Initial Stage)",
                    "বৃদ্ধি পর্যায় (Development Stage)",
                    "মধ্য পর্যায় (Mid Stage)",
                    "পরিপক্বতা পর্যায় (Late Stage)"
                ]
            )

            stage_map = {

                "চারা/প্রাথমিক পর্যায় (Initial Stage)":
                    "Initial",

                "বৃদ্ধি পর্যায় (Development Stage)":
                    "Development",

                "মধ্য পর্যায় (Mid Stage)":
                    "Mid",

                "পরিপক্বতা পর্যায় (Late Stage)":
                    "Late"
            }

            crop_stage = stage_map.get(
                manual_stage_label
            )

            if crop_stage is None:

                calculation_allowed = False

                st.info(
                    "Calendar data অসম্পূর্ণ। "
                    "হিসাব করার আগে বৃদ্ধি পর্যায় নির্বাচন করুন।"
                )

            st.caption(
                "Calendar data অসম্পূর্ণ হওয়ায় "
                "Growth Stage manualভাবে নির্বাচন করা হচ্ছে।"
            )

    return (
        calculation_date,
        actual_planting_date,
        use_actual_planting,
        stage_info,
        crop_stage,
        calculation_allowed
    )


# ============================================================
# [27] CROP REFERENCE INFORMATION CARD
# ------------------------------------------------------------
# FUNCTION:
#     crop_reference_section()
#
# PURPOSE:
# Displays cultivar / reference duration / seasonal CWR / IWR
# reference figures for the selected crop + season.
#
# IMPORTANT:
# These figures are seasonal reference values only — NOT the
# daily irrigation requirement used in the calculation.
#
# CHANGE HERE IF:
# - the reference-card fields/wording need to change.
# ============================================================

def crop_reference_section(
    crop_label,
    season_label,
    crop_reference
):

    if not crop_reference:

        return

    cultivar = (
        crop_reference.get(
            "cultivar"
        )
        or
        "N/A"
    )

    duration_row = ""

    if (
        crop_reference.get(
            "duration_days"
        )
        is not None
    ):

        duration_row = (
            f"<p>রেফারেন্স সময়কাল "
            f"(Reference Duration): "
            f"{bn_num(crop_reference['duration_days'], 0)} দিন</p>"
        )

    cwr_row = ""

    if (
        crop_reference.get(
            "cwr_mm"
        )
        is not None
    ):

        cwr_row = (
            f"<p>মৌসুমি ফসলের পানির চাহিদা "
            f"(Seasonal CWR Reference): "
            f"{bn_num(crop_reference['cwr_mm'], 0)} mm/season</p>"
        )

    iwr_row = ""

    if (
        crop_reference.get(
            "iwr_mm"
        )
        is not None
    ):

        iwr_row = (
            f"<p>মৌসুমি সেচের রেফারেন্স "
            f"(Seasonal IWR Reference): "
            f"{bn_num(crop_reference['iwr_mm'], 0)} mm/season</p>"
        )

    st.markdown(
        f"""
        <div class='agri-card'>
            <h3>ফসলের রেফারেন্স তথ্য (Crop Reference Information)</h3>
            <p>ফসল (Crop): {crop_label}</p>
            <p>মৌসুম (Season): {season_label}</p>
            <p>জাত (Cultivar): {cultivar}</p>
            {duration_row}
            {cwr_row}
            {iwr_row}
            <p style="font-size:13px; opacity:.75; margin-top:8px;">
                নোট: CWR/IWR এখানে seasonal reference। এগুলো আজকের
                daily irrigation requirement নয়।
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# [28] SOIL INFORMATION SECTION
# ------------------------------------------------------------
# FUNCTION:
#     soil_information_section()
#
# PURPOSE:
# Soil type selector. Informational + used for recommendation
# text (see [33]) — NOT used as a multiplier in the irrigation
# calculation itself.
#
# RETURN:
#   soil_type
#
# CHANGE HERE IF:
# - available soil types need to change (see SOIL_TYPES in
#   services.agriculture).
# ============================================================

def soil_information_section():

    section_title(
        "মাটির তথ্য",
        "Soil Information"
    )

    with st.container(border=True):

        prepare_voice_input(
            "agriculture_soil_type"
        )

        soil_type = st.selectbox(
            "মাটির ধরন (Soil Type)",
            list(SOIL_TYPES.keys()),
            key="agriculture_soil_type",
            on_change=input_voice_callback,
            args=(
                "agriculture_soil_type",
                "মাটির ধরন নির্বাচন করুন",
                None
            )
        )

        _voice_input_field(
            "agriculture_soil_type",
            "মাটির ধরন বলুন",
            "option",
            list(SOIL_TYPES.keys())
        )

        st.caption(
            SOIL_TYPES[
                soil_type
            ]["description"]
        )

        st.caption(
            "নোট: মাটির ধরন তথ্য ও পরামর্শের জন্য ব্যবহার করা হচ্ছে। "
            "সেচের পরিমাণে কোনো arbitrary soil multiplier প্রয়োগ করা হচ্ছে না।"
        )

    return soil_type


# ============================================================
# [29] EXISTING WATER SECTION
# ------------------------------------------------------------
# FUNCTION:
#     existing_water_section()
#
# PURPOSE:
# Lets the user pick a preset finger-depth water measurement
# (or a custom depth in cm), converts it to mm, and shows the
# estimated total water already present in the field
# (liters / m³) using the previewed land area.
#
# RETURN:
#   (water_measurement, existing_water_mm,
#    existing_water_volume)
#
# CHANGE HERE IF:
# - preset depth options or the estimation display need to
#   change.
#
# IMPORTANT:
# The mm -> volume conversion itself lives in
# convert_water_depth_to_mm() / calculate_existing_water_volume()
# in services.agriculture; this function only renders the UI.
# ============================================================

def existing_water_section(
    land_area,
    area_unit
):

    section_title(
        "জমিতে আগে থেকে থাকা পানি",
        "Existing Water"
    )

    st.info(
        """
        জমিতে কত মিলিমিটার পানি আছে তা সরাসরি জানা কঠিন।
        তাই আপনি আঙুল দিয়ে পানির গভীরতা মাপতে পারেন।
        সিস্টেম সেই পরিমাপকে আনুমানিক মিলিমিটারে পরিবর্তন করবে।
        এটি একটি আনুমানিক হিসাব।
        """
    )

    with st.container(border=True):

        prepare_voice_input(
            "agriculture_water_measurement"
        )

        water_measurement = st.selectbox(
            "পানির গভীরতা নির্বাচন করুন "
            "(Select Water Depth)",
            list(WATER_DEPTH_OPTIONS.keys())
            +
            [
                "নিজে পরিমাপ দিন "
                "(Custom Measurement)"
            ],
            key="agriculture_water_measurement",
            on_change=input_voice_callback,
            args=(
                "agriculture_water_measurement",
                "পানির গভীরতা নির্বাচন করুন",
                None
            )
        )

        _voice_input_field(
            "agriculture_water_measurement",
            "পানির গভীরতার ধরন বলুন",
            "option",
            list(WATER_DEPTH_OPTIONS.keys())
            +
            [
                "নিজে পরিমাপ দিন (Custom Measurement)"
            ]
        )

        custom_depth_cm = 0.0

        if water_measurement == (
            "নিজে পরিমাপ দিন "
            "(Custom Measurement)"
        ):

            prepare_voice_input(
                "agriculture_custom_water_depth"
            )

            custom_depth_cm = st.number_input(
                "পানির গভীরতা সেন্টিমিটারে দিন "
                "(Water Depth in cm)",
                min_value=0.0,
                value=0.0,
                step=0.5,
                key="agriculture_custom_water_depth",
                on_change=input_voice_callback,
                args=(
                    "agriculture_custom_water_depth",
                    "পানির গভীরতা সেন্টিমিটারে দিন",
                    None
                )
            )

            _voice_input_field(
                "agriculture_custom_water_depth",
                "পানির গভীরতা সেন্টিমিটারে বলুন",
                "number",
                minimum=0.0
            )

    existing_water_mm = (
        convert_water_depth_to_mm(
            water_measurement,
            custom_depth_cm
        )
    )

    area_m2_preview = convert_area_to_m2(
        land_area,
        area_unit
    )

    existing_water_volume = (
        calculate_existing_water_volume(
            area_m2_preview,
            existing_water_mm
        )
    )

    st.markdown(
        f"""
        <div class='info-card'>
            <div class='info-title'>
                আনুমানিক পানির হিসাব (Estimated Water Calculation)
            </div>
            <div class='info-row'>
                <span class='label'>পানির গভীরতা (Water Depth)</span>
                <span class='value'>{bn_num(existing_water_mm, 1)} mm</span>
            </div>
            <div class='info-row'>
                <span class='label'>মোট পানি (Total Water)</span>
                <span class='value'>{bn_num(existing_water_volume['water_liters'], 0, True)} L</span>
            </div>
            <div class='info-row'>
                <span class='label'>পানির পরিমাণ (Water Volume)</span>
                <span class='value'>{bn_num(existing_water_volume['water_m3'], 2)} m³</span>
            </div>
        </div>
        <p style="font-size:13px; color:#5b6b7c; margin-top:-6px;">
            নোট: আঙুল দিয়ে মাপার কারণে এটি আনুমানিক হিসাব।
        </p>
        """,
        unsafe_allow_html=True
    )

    return (
        water_measurement,
        existing_water_mm,
        existing_water_volume
    )


# ============================================================
# [30] CROP WATER REQUIREMENT SECTION
# ------------------------------------------------------------
# FUNCTION:
#     crop_water_requirement_section()
#
# PURPOSE:
# Shows the Automatic daily crop water requirement
# (ET0 x Kc, using get_kc() for the current growth stage) and
# lets the user choose between Automatic and Manual Override
# for the value actually used in the calculation.
#
# RETURN:
#   (kc_preview, automatic_etc_preview,
#    water_requirement_method, manual_crop_water_need_mm)
#
# CHANGE HERE IF:
# - the Automatic vs Manual Override UI/wording needs to change.
#
# IMPORTANT:
# get_kc() (Kc lookup) lives in services.agriculture; this
# function only previews ET0 x Kc for display.
# ============================================================

def crop_water_requirement_section(
    crop_name,
    crop_stage,
    et0_value,
    predicted_rain
):

    section_title(
        "ফসলের পানির চাহিদা",
        "Crop Water Requirement"
    )

    kc_preview = None
    automatic_etc_preview = None

    if crop_stage is not None:

        try:

            kc_preview = get_kc(
                crop_name,
                crop_stage
            )

        except Exception:

            kc_preview = None

        if kc_preview is not None:

            automatic_etc_preview = (
                float(et0_value)
                *
                float(kc_preview["kc"])
            )

    if automatic_etc_preview is not None:

        st.markdown(
            f"""
            <div class='info-card'>
                <div class='info-title'>
                    দৈনিক ফসলের পানির চাহিদা (Daily Crop Water Requirement)
                </div>
                <div class='info-row'>
                    <span class='label'>ET0 (Reference Evapotranspiration)</span>
                    <span class='value'>{bn_num(et0_value, 2)} mm/day</span>
                </div>
                <div class='info-row'>
                    <span class='label'>ফসল সহগ (Crop Coefficient / Kc)</span>
                    <span class='value'>{bn_num(kc_preview['kc'], 2)}</span>
                </div>
                <div class='info-row'>
                    <span class='label'>দৈনিক পানির চাহিদা (ETc)</span>
                    <span class='value'>{bn_num(automatic_etc_preview, 2)} mm/day</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if predicted_rain <= 0:

            st.warning(
                f"""
                আজ বৃষ্টি না হলেও এই ফসলের বর্তমান stage অনুযায়ী
                আনুমানিক {bn_num(automatic_etc_preview, 2)} mm/day
                পানি প্রয়োজন। জমিতে পর্যাপ্ত পানি না থাকলে
                সেচ প্রয়োজন হতে পারে।
                """
            )

    with st.container(border=True):

        prepare_voice_input(
            "agriculture_water_requirement_method"
        )

        water_requirement_method = st.radio(
            "পানির চাহিদা নির্ধারণের পদ্ধতি "
            "(Water Requirement Method)",
            [
                "স্বয়ংক্রিয়ভাবে পানির চাহিদা নির্ধারণ করুন "
                "(Automatic — Recommended)",

                "নিজে দৈনিক পানির চাহিদা দিন "
                "(Manual Override)"
            ],
            index=None,
            key="agriculture_water_requirement_method",
            on_change=input_voice_callback,
            args=(
                "agriculture_water_requirement_method",
                "পানির চাহিদা নির্ধারণের পদ্ধতি নির্বাচন করুন",
                None
            )
        )

        _voice_input_field(
            "agriculture_water_requirement_method",
            "পানির চাহিদা নির্ধারণের পদ্ধতি বলুন",
            "option",
            [
                "স্বয়ংক্রিয়ভাবে পানির চাহিদা নির্ধারণ করুন (Automatic — Recommended)",
                "নিজে দৈনিক পানির চাহিদা দিন (Manual Override)"
            ]
        )

        if water_requirement_method is None:

            st.info(
                "উপরের যেকোনো একটি বক্স নির্বাচন করুন।"
            )

    if water_requirement_method is None:

        return (
            kc_preview,
            automatic_etc_preview,
            None,
            None
        )

    manual_crop_water_need_mm = None

    if water_requirement_method.startswith(
        "নিজে"
    ):

        default_manual_need = (
            float(automatic_etc_preview)
            if automatic_etc_preview is not None
            else 0.0
        )

        with st.container(border=True):

            if (
                "agriculture_manual_crop_water_need"
                not in st.session_state
            ):

                st.session_state[
                    "agriculture_manual_crop_water_need"
                ] = default_manual_need

            prepare_voice_input(
                "agriculture_manual_crop_water_need"
            )

            manual_crop_water_need_mm = st.number_input(
                "দৈনিক ফসলের পানির চাহিদা "
                "(Daily Crop Water Requirement) mm/day",
                min_value=0.0,
                step=0.1,
                key="agriculture_manual_crop_water_need",
                on_change=input_voice_callback,
                args=(
                    "agriculture_manual_crop_water_need",
                    "দৈনিক ফসলের পানির চাহিদা দিন",
                    None
                )
            )

            _voice_input_field(
                "agriculture_manual_crop_water_need",
                "দৈনিক ফসলের পানির চাহিদা বলুন",
                "number",
                minimum=0.0
            )

            st.warning(
                "Manual Override ব্যবহার করলে irrigation calculation "
                "আপনার দেওয়া daily crop water requirement অনুযায়ী হবে। "
                "Automatic ET0 × Kc value reference হিসেবে উপরে দেখানো থাকবে।"
            )

    return (
        kc_preview,
        automatic_etc_preview,
        water_requirement_method,
        manual_crop_water_need_mm
    )


# ======================================================================
# [31] IRRIGATION SYSTEM SECTION
# ----------------------------------------------------------------------
# FUNCTION:
#     irrigation_system_section()
#
# PURPOSE:
# Irrigation method selector (Drip / Sprinkler / Fixed-flow —
# names/config read entirely from services.agriculture, none
# hardcoded here), plus method-specific inputs:
#   PER_DRIPPER    -> dripper count
#   PER_SPRINKLER  -> sprinkler count + flow per sprinkler
#   FIXED_FLOW     -> no extra input (representative flow from
#                      config)
# and the Irrigation Efficiency % slider (default seeded from
# the method's own configured default_efficiency, and reset
# whenever the method changes).
#
# RETURN:
#   (irrigation_method, irrigation_efficiency, dripper_count,
#    sprinkler_count, sprinkler_flow_lph)
#
# CHANGE HERE IF:
# - method-specific input fields/labels need to change.
#
# IMPORTANT:
# Irrigation method NAMES and CONFIGURATION are the single
# source of truth in services.agriculture
# (get_irrigation_method_options / get_irrigation_method_config).
# Do not hardcode method names in this section.
# ======================================================================

def irrigation_system_section():

    section_title(
        "সেচ ব্যবস্থা",
        "Irrigation System"
    )

    # ------------------------------------------------------------
    # Use services/agriculture.py as the single source of truth.
    # No irrigation method names are hardcoded here.
    # ------------------------------------------------------------

    irrigation_options = (
        get_irrigation_method_options()
    )

    if not irrigation_options:

        st.error(
            "কোনো সেচ পদ্ধতি পাওয়া যায়নি। "
            "services/agriculture.py-এর irrigation configuration পরীক্ষা করুন।"
        )

        return (
            None,
            None,
            None,
            None,
            None
        )

    with st.container(border=True):

        prepare_voice_input(
            "agriculture_irrigation_method"
        )

        irrigation_method = st.selectbox(
            "সেচ পদ্ধতি নির্বাচন করুন "
            "(Select Irrigation Method)",
            irrigation_options,
            key="agriculture_irrigation_method",
            on_change=input_voice_callback,
            args=(
                "agriculture_irrigation_method",
                "সেচ পদ্ধতি নির্বাচন করুন",
                None
            )
        )

        _voice_input_field(
            "agriculture_irrigation_method",
            "সেচ পদ্ধতির নাম বলুন",
            "option",
            irrigation_options
        )

        # --------------------------------------------------------
        # Get selected method configuration from service.
        # --------------------------------------------------------

        method_config = (
            get_irrigation_method_config(
                irrigation_method
            )
        )

        if method_config is None:

            st.error(
                "নির্বাচিত সেচ পদ্ধতির configuration পাওয়া যায়নি।"
            )

            return (
                irrigation_method,
                None,
                None,
                None,
                None
            )

        method_type = (
            method_config.get(
                "type"
            )
        )

        default_efficiency = int(
            method_config.get(
                "default_efficiency",
                60
            )
        )

        # --------------------------------------------------------
        # Detect method change.
        # This also prevents stale method-specific inputs.
        # --------------------------------------------------------

        method_signature_key = (
            "agriculture_efficiency_method_signature"
        )

        previous_method = (
            st.session_state.get(
                method_signature_key
            )
        )

        method_changed = (
            previous_method != irrigation_method
        )

        if method_changed:

            st.session_state[
                method_signature_key
            ] = irrigation_method

            # Method-specific inputs are cleared whenever the
            # selected irrigation method changes.
            st.session_state[
                "agriculture_dripper_count"
            ] = None

            st.session_state[
                "agriculture_sprinkler_count"
            ] = None

            st.session_state[
                "agriculture_sprinkler_flow_lph"
            ] = None

            # Reset efficiency according to service configuration.
            st.session_state[
                "agriculture_irrigation_efficiency"
            ] = default_efficiency

            # Clear old method-specific voice interaction states.
            st.session_state.pop(
                "agriculture_interaction_voice_agriculture_dripper_count",
                None
            )

            st.session_state.pop(
                "agriculture_interaction_voice_agriculture_sprinkler_count",
                None
            )

            st.session_state.pop(
                "agriculture_interaction_voice_agriculture_sprinkler_flow_lph",
                None
            )

        # --------------------------------------------------------
        # Method-specific inputs
        # --------------------------------------------------------

        dripper_count = None
        sprinkler_count = None
        sprinkler_flow_lph = None

        # --------------------------------------------------------
        # DRIP
        # --------------------------------------------------------

        if method_type == "PER_DRIPPER":

            prepare_voice_input(
                "agriculture_dripper_count"
            )

            dripper_count = st.number_input(
                "ড্রিপারের সংখ্যা "
                "(Number of Drippers)",
                min_value=1.0,
                value=None,
                step=1.0,
                placeholder="ড্রিপারের সংখ্যা লিখুন",
                key="agriculture_dripper_count",
                on_change=input_voice_callback,
                args=(
                    "agriculture_dripper_count",
                    "ড্রিপারের সংখ্যা দিন",
                    None
                )
            )

            _voice_input_field(
                "agriculture_dripper_count",
                "ড্রিপারের সংখ্যা বলুন",
                "number",
                minimum=1.0
            )

            st.caption(
                "প্রতি ড্রিপারের flow service configuration অনুযায়ী "
                "স্বয়ংক্রিয়ভাবে ব্যবহার করা হবে।"
            )

        # --------------------------------------------------------
        # SPRINKLER
        # --------------------------------------------------------

        elif method_type == "PER_SPRINKLER":

            prepare_voice_input(
                "agriculture_sprinkler_count"
            )

            sprinkler_count = st.number_input(
                "স্প্রিংকলারের সংখ্যা "
                "(Number of Sprinklers)",
                min_value=1.0,
                value=None,
                step=1.0,
                placeholder="স্প্রিংকলারের সংখ্যা লিখুন",
                key="agriculture_sprinkler_count",
                on_change=input_voice_callback,
                args=(
                    "agriculture_sprinkler_count",
                    "স্প্রিংকলারের সংখ্যা দিন",
                    None
                )
            )

            _voice_input_field(
                "agriculture_sprinkler_count",
                "স্প্রিংকলারের সংখ্যা বলুন",
                "number",
                minimum=1.0
            )

            prepare_voice_input(
                "agriculture_sprinkler_flow_lph"
            )

            sprinkler_flow_lph = st.number_input(
                "প্রতি স্প্রিংকলারের পানির প্রবাহ "
                "(Flow per Sprinkler) L/hour",
                min_value=0.1,
                value=None,
                step=0.1,
                placeholder="প্রতি ঘণ্টায় লিটার লিখুন",
                key="agriculture_sprinkler_flow_lph",
                on_change=input_voice_callback,
                args=(
                    "agriculture_sprinkler_flow_lph",
                    "প্রতি স্প্রিংকলারের পানির প্রবাহ দিন",
                    None
                )
            )

            _voice_input_field(
                "agriculture_sprinkler_flow_lph",
                "প্রতি স্প্রিংকলারের পানির প্রবাহ বলুন",
                "number",
                minimum=0.1
            )

        # --------------------------------------------------------
        # FIXED FLOW METHODS
        # Shallow Pump / Deep Tubewell
        # --------------------------------------------------------

        elif method_type == "FIXED_FLOW":

            st.caption(
                "এই সেচ পদ্ধতির representative flow "
                "services/agriculture.py-এর configuration থেকে "
                "স্বয়ংক্রিয়ভাবে ব্যবহার করা হবে।"
            )

        # --------------------------------------------------------
        # Efficiency
        # --------------------------------------------------------

        if (
            "agriculture_irrigation_efficiency"
            not in st.session_state
        ):

            st.session_state[
                "agriculture_irrigation_efficiency"
            ] = default_efficiency

        irrigation_efficiency = st.slider(
            "সেচ দক্ষতা (Irrigation Efficiency %)",
            min_value=30,
            max_value=100,
            key="agriculture_irrigation_efficiency",
            on_change=input_voice_callback,
            args=(
                "agriculture_irrigation_efficiency",
                "সেচ দক্ষতা নির্বাচন করুন",
                None
            )
        )

        st.caption(
            "নোট: Default efficiency values planning assumption হিসেবে "
            "ব্যবহৃত হচ্ছে। প্রয়োজন হলে field condition অনুযায়ী "
            "slider পরিবর্তন করুন।"
        )

    return (
        irrigation_method,
        irrigation_efficiency,
        dripper_count,
        sprinkler_count,
        sprinkler_flow_lph
    )


# ============================================================
# [32] MAIN INPUT PANEL / CALCULATION TRIGGER
# ------------------------------------------------------------
# FUNCTION:
#     _agriculture_input_panel()
#
# PURPOSE:
# Orchestrates sections [23]–[31] in order, validates all
# required inputs (including method-specific dripper/sprinkler
# requirements), enables/disables the "Calculate" button
# accordingly, and — on click — runs calculate_irrigation() +
# calculate_irrigation_time(), computes the "no rain today"
# scenario, and stores everything in
# st.session_state.agri_result. Also speaks the simplified
# result voice.
#
# CHANGE HERE IF:
# - required-input validation rules need to change
# - what gets stored in agri_result needs to change
# - the no-rain-scenario math needs to change.
#
# IMPORTANT:
# calculate_irrigation() and calculate_irrigation_time() are
# NOT modified here — this function only calls them and stores
# their output. They remain the single source of truth for the
# actual irrigation formulas.
# ============================================================

def _agriculture_input_panel():

    (
        weather_source,
        predicted_rain,
        et0_value
    ) = weather_information_section()

    if weather_source is None:

        return

    (
        land_area,
        area_unit
    ) = land_information_section()

    if (
        land_area is None
        or area_unit is None
    ):

        return

    (
        crop_label,
        crop_name,
        season_label,
        season_name,
        crop_error
    ) = crop_information_section()

    if crop_error:

        return

    crop_reference = get_crop_reference(
        crop_name,
        season_name
    )

    (
        calculation_date,
        actual_planting_date,
        use_actual_planting,
        stage_info,
        crop_stage,
        calculation_allowed
    ) = planting_growth_section(
        crop_name,
        season_name
    )

    crop_reference_section(
        crop_label,
        season_label,
        crop_reference
    )

    soil_type = (
        soil_information_section()
    )

    (
        water_measurement,
        existing_water_mm,
        existing_water_volume
    ) = existing_water_section(
        land_area,
        area_unit
    )

    (
        kc_preview,
        automatic_etc_preview,
        water_requirement_method,
        manual_crop_water_need_mm
    ) = crop_water_requirement_section(
        crop_name,
        crop_stage,
        et0_value,
        predicted_rain
    )

    (
        irrigation_method,
        irrigation_efficiency,
        dripper_count,
        sprinkler_count,
        sprinkler_flow_lph
    ) = irrigation_system_section()

    missing_inputs = []

    if water_requirement_method is None:

        missing_inputs.append(
            "পানির চাহিদা নির্ধারণের পদ্ধতি"
        )

        calculation_allowed = False

    if crop_stage is None:

        missing_inputs.append(
            "ফসলের বৃদ্ধি পর্যায়"
        )

        calculation_allowed = False

    if irrigation_method is None:

        missing_inputs.append(
            "সেচ পদ্ধতি"
        )

        calculation_allowed = False

    # ------------------------------------------------------------
    # Method-specific required input validation
    # ------------------------------------------------------------

    irrigation_method_config = (
        get_irrigation_method_config(
            irrigation_method
        )
        if irrigation_method is not None
        else None
    )

    method_type = (
        irrigation_method_config.get(
            "type"
        )
        if irrigation_method_config
        else None
    )

    if method_type == "PER_DRIPPER":

        if (
            dripper_count is None
            or float(dripper_count) <= 0
        ):

            missing_inputs.append(
                "ড্রিপারের সংখ্যা"
            )

            calculation_allowed = False

    elif method_type == "PER_SPRINKLER":

        if (
            sprinkler_count is None
            or float(sprinkler_count) <= 0
        ):

            missing_inputs.append(
                "স্প্রিংকলারের সংখ্যা"
            )

            calculation_allowed = False

        if (
            sprinkler_flow_lph is None
            or float(sprinkler_flow_lph) <= 0
        ):

            missing_inputs.append(
                "প্রতি স্প্রিংকলারের পানির প্রবাহ"
            )

            calculation_allowed = False

    current_signature = (

        crop_name,

        season_name,

        str(calculation_date),

        str(actual_planting_date),

        use_actual_planting,

        crop_stage,

        float(predicted_rain),

        float(et0_value),

        float(existing_water_mm),

        float(land_area),

        area_unit,

        soil_type,

        irrigation_method,

        int(irrigation_efficiency),

        water_requirement_method,

        (
            None
            if manual_crop_water_need_mm is None
            else float(
                manual_crop_water_need_mm
            )
        ),

        (
            None
            if dripper_count is None
            else float(
                dripper_count
            )
        ),

        (
            None
            if sprinkler_count is None
            else float(
                sprinkler_count
            )
        ),

        (
            None
            if sprinkler_flow_lph is None
            else float(
                sprinkler_flow_lph
            )
        )
    )

    calculate_clicked = st.button(
        "স্মার্ট সেচ হিসাব করুন "
        "(Calculate Smart Irrigation)",
        type="primary",
        use_container_width=True,
        disabled=not calculation_allowed,
        key="agriculture_calculate_button"
    )

    if not calculation_allowed:

        if missing_inputs:

            st.caption(
                "হিসাব করার আগে নির্বাচন/তথ্য দিন: "
                + ", ".join(
                    missing_inputs
                )
                + "।"
            )

        else:

            st.caption(
                "সঠিক Season / Planting Date নির্বাচন না করা পর্যন্ত "
                "calculation চালানো যাবে না।"
            )

    if calculate_clicked:

        try:

            # ====================================================
            # IMPORTANT:
            # calculate_irrigation() is NOT changed.
            # Existing irrigation calculation remains the source
            # of truth for required water.
            # ====================================================

            result = calculate_irrigation(

                land_area=land_area,

                area_unit=area_unit,

                crop_name=crop_name,

                crop_stage=crop_stage,

                soil_type=soil_type,

                existing_water_mm=existing_water_mm,

                predicted_rain_mm=predicted_rain,

                et0_value=et0_value,

                irrigation_efficiency=irrigation_efficiency,

                manual_crop_water_need_mm=(
                    manual_crop_water_need_mm
                )
            )

            # ====================================================
            # NO-RAIN SCENARIO
            # Existing logic preserved.
            # ====================================================

            no_rain_net_mm = max(

                float(
                    result["crop_water_need"]
                )
                -
                float(
                    result["available_water"]
                ),

                0.0
            )

            efficiency_ratio = (
                float(
                    irrigation_efficiency
                )
                /
                100.0
            )

            no_rain_gross_mm = (

                no_rain_net_mm
                /
                efficiency_ratio

                if efficiency_ratio > 0

                else 0.0
            )

            no_rain_water_liters = (

                no_rain_gross_mm
                *
                float(
                    result["area_m2"]
                )
            )

            if no_rain_net_mm > 0:

                no_rain_message = (

                    f"যদি আজ কোনো বৃষ্টি না হয়, "
                    f"তাহলে জমিতে থাকা পানি বাদ দেওয়ার পর "
                    f"প্রায় {no_rain_gross_mm:.1f} মিলিমিটার অথবা "
                    f"{no_rain_water_liters:.0f} লিটার পানি "
                    f"সেচ দিতে হবে।"
                )

            else:

                no_rain_message = (

                    "যদি আজ কোনো বৃষ্টি না হয়, "
                    "তবুও জমিতে থাকা পানি ফসলের বর্তমান "
                    "দৈনিক পানির চাহিদা পূরণ করতে যথেষ্ট। "
                    "অতিরিক্ত সেচের প্রয়োজন হবে না।"
                )

            # ====================================================
            # IRRIGATION TIME
            #
            # IMPORTANT:
            # Only calculate time when irrigation is actually
            # needed.
            #
            # calculate_irrigation_time() is the source of truth.
            # No local flow/time formula is duplicated here.
            # ====================================================

            irrigation_needed = (
                result.get(
                    "status"
                )
                !=
                "NO_IRRIGATION"
            )

            irrigation_time_result = None
            irrigation_time_hours = None

            if irrigation_needed:

                irrigation_time_result = (
                    calculate_irrigation_time(

                        result.get(
                            "water_liters",
                            0.0
                        ),

                        irrigation_needed,

                        irrigation_method,

                        num_drippers=(
                            dripper_count
                        ),

                        num_sprinklers=(
                            sprinkler_count
                        ),

                        flow_per_sprinkler_lph=(
                            sprinkler_flow_lph
                        )
                    )
                )

                if (
                    irrigation_time_result
                    and
                    irrigation_time_result.get(
                        "available"
                    )
                ):

                    raw_hours = (
                        irrigation_time_result.get(
                            "hours"
                        )
                    )

                    try:

                        if raw_hours is not None:

                            irrigation_time_hours = float(
                                raw_hours
                            )

                    except Exception:

                        irrigation_time_hours = None

            # ====================================================
            # NO-RAIN SCENARIO — IRRIGATION TIME
            #
            # Same calculate_irrigation_time() service, just fed
            # with the "if there is no rain today" water amount
            # instead of the main result's water_liters. Only
            # computed when the no-rain scenario actually needs
            # extra irrigation.
            # ====================================================

            no_rain_time_result = None
            no_rain_time_hours = None

            if no_rain_net_mm > 0:

                no_rain_time_result = (
                    calculate_irrigation_time(

                        no_rain_water_liters,

                        True,

                        irrigation_method,

                        num_drippers=(
                            dripper_count
                        ),

                        num_sprinklers=(
                            sprinkler_count
                        ),

                        flow_per_sprinkler_lph=(
                            sprinkler_flow_lph
                        )
                    )
                )

                if (
                    no_rain_time_result
                    and
                    no_rain_time_result.get(
                        "available"
                    )
                ):

                    raw_no_rain_hours = (
                        no_rain_time_result.get(
                            "hours"
                        )
                    )

                    try:

                        if raw_no_rain_hours is not None:

                            no_rain_time_hours = float(
                                raw_no_rain_hours
                            )

                    except Exception:

                        no_rain_time_hours = None

            # ====================================================
            # STORE RESULT
            # ====================================================

            st.session_state.agri_result = {

                "input_signature":
                    current_signature,

                "result":
                    result,

                "crop_label":
                    crop_label,

                "crop_name":
                    crop_name,

                "season_label":
                    season_label,

                "season_name":
                    season_name,

                "crop_stage":
                    crop_stage,

                "crop_stage_label":
                    STAGE_LABELS.get(
                        crop_stage,
                        crop_stage
                    ),

                "stage_info":
                    stage_info,

                "actual_planting_date":
                    actual_planting_date,

                "calculation_date":
                    calculation_date,

                "soil_type":
                    soil_type,

                "predicted_rain":
                    predicted_rain,

                "existing_water":
                    existing_water_mm,

                "existing_water_liters":
                    existing_water_volume[
                        "water_liters"
                    ],

                "existing_water_m3":
                    existing_water_volume[
                        "water_m3"
                    ],

                "water_measurement":
                    water_measurement,

                "et0":
                    et0_value,

                "land_area":
                    land_area,

                "area_unit":
                    area_unit,

                # ------------------------------------------------
                # Irrigation method data
                # ------------------------------------------------

                "irrigation_method":
                    irrigation_method,

                "efficiency":
                    irrigation_efficiency,

                "dripper_count":
                    dripper_count,

                "sprinkler_count":
                    sprinkler_count,

                "sprinkler_flow_lph":
                    sprinkler_flow_lph,

                "irrigation_time_result":
                    irrigation_time_result,

                "irrigation_time_hours":
                    irrigation_time_hours,

                "water_requirement_method":
                    water_requirement_method,

                "manual_crop_water_need_mm":
                    manual_crop_water_need_mm,

                "crop_reference":
                    crop_reference,

                "no_rain_net_mm":
                    no_rain_net_mm,

                "no_rain_gross_mm":
                    no_rain_gross_mm,

                "no_rain_water_liters":
                    no_rain_water_liters,

                "no_rain_message":
                    no_rain_message,

                "no_rain_time_result":
                    no_rain_time_result,

                "no_rain_time_hours":
                    no_rain_time_hours,
            }

            # ====================================================
            # RESULT VOICE
            #
            # Simplified, farmer-friendly voice — only says:
            #   1) সেচ লাগবে কিনা + কত পানি
            #   2) কত ঘণ্টা সেচ দিতে হবে
            #   3) বৃষ্টি না হলে কত পানি + কত ঘণ্টা
            #
            # No ET0 / Kc / effective rain / available water /
            # net-vs-gross breakdown is spoken anymore — that
            # detail stays as text only in the "বিস্তারিত" expander.
            # ====================================================

            try:

                reset_voice_hash()

                agriculture_result_voice(

                    irrigation_needed=(
                        irrigation_needed
                    ),

                    water_liters=float(
                        result.get(
                            "water_liters",
                            0.0
                        )
                    ),

                    irrigation_time_hours=(
                        irrigation_time_hours
                        if irrigation_needed
                        else None
                    ),

                    no_rain_water_liters=
                        no_rain_water_liters,

                    no_rain_time_hours=
                        no_rain_time_hours
                )

            except Exception as exc:

                st.warning(
                    f"ফলাফল ভয়েস তৈরি করা যায়নি "
                    f"(Result voice failed): {exc}"
                )

            st.session_state[
                "agriculture_show_recommendations"
            ] = False

            st.rerun()

        except Exception as exc:

            st.error(
                f"সেচ হিসাব করা যায়নি "
                f"(Irrigation calculation failed): {exc}"
            )


# ============================================================
# [33] RESULT DISPLAY
# ------------------------------------------------------------
# FUNCTION:
#     show_agriculture_result()
#
# PURPOSE:
# Renders the full smart-irrigation result, laid out as:
#
#   1. Headline card
#        - Irrigation needed: water needed + gross mm +
#          irrigation time
#        - No irrigation needed: available water vs crop need
#
#   2. Short summary card (2–3 lines: water balance, net/gross
#      irrigation or "not needed", no-rain scenario)
#
#   3. Smart Recommendation section (button-triggered voice +
#      bullet list, built from status / no-rain / rain-forecast
#      / soil-type / irrigation-method rules)
#
#   4. "Show Full Calculation Details" expander:
#        - Crop water calculation (ET0, Kc, ETc)
#        - Water balance (effective rain, available water, net,
#          gross)
#        - How much water (liters, m³, area)
#        - Irrigation method & time
#        - If-no-rain-today scenario
#        - Existing water information
#        - Calculation log (crop/season/dates/stage/etc)
#        - Bar chart (Plotly) of the water-balance categories
#
# CHANGE HERE IF:
# - result cards, metric labels, recommendation rules, or the
#   details expander/chart need to change.
#
# IMPORTANT:
# This function only DISPLAYS st.session_state.agri_result; it
# does not recompute the irrigation numbers (aside from
# recomputing the no-rain figures as a display-time fallback
# when they were not already stored).
# ============================================================

def show_agriculture_result():

    if "agri_result" not in st.session_state:

        return

    data = st.session_state.agri_result

    result = data["result"]

    stage_info = data.get(
        "stage_info"
    ) or {}

    st.divider()

    st.subheader(
        "স্মার্ট সেচের ফলাফল "
        "(Smart Irrigation Result)"
    )

    # ================================================================
    # Recompute the "no rain today" numbers (used both in the headline
    # and in the details section below).
    # ================================================================

    no_rain_net_mm = data.get(
        "no_rain_net_mm"
    )

    if no_rain_net_mm is None:

        no_rain_net_mm = max(
            float(
                result["crop_water_need"]
            )
            -
            float(
                result["available_water"]
            ),
            0.0
        )

        efficiency_ratio = (
            float(
                data.get(
                    "efficiency",
                    100
                )
            )
            /
            100.0
        )

        no_rain_gross_mm = (
            no_rain_net_mm
            /
            efficiency_ratio
            if efficiency_ratio > 0
            else 0.0
        )

        no_rain_water_liters = (
            no_rain_gross_mm
            *
            float(
                result["area_m2"]
            )
        )

    else:

        no_rain_gross_mm = float(
            data.get(
                "no_rain_gross_mm",
                0.0
            )
        )

        no_rain_water_liters = float(
            data.get(
                "no_rain_water_liters",
                0.0
            )
        )

    irrigation_needed = (
        result.get("status") != "NO_IRRIGATION"
    )

    irrigation_time_hours = data.get(
        "irrigation_time_hours"
    )

    # ================================================================
    # 1) HEADLINE CARD
    #    Only the two numbers a farmer actually needs right now:
    #    কতটুকু পানি + কতক্ষণ সেচ
    # ================================================================

    if irrigation_needed:

        tag_text = "সেচের পরামর্শ (Irrigation Needed)"

        time_html = ""

        if (
            irrigation_time_hours is not None
            and float(irrigation_time_hours) > 0
        ):

            # NOTE:
            # Built as a single line (no leading/trailing newline or
            # indentation inside the f-string) and .strip()-ed, so
            # this never leaves a blank/whitespace-only line inside
            # the outer HTML block below. A blank line there makes
            # Streamlit's markdown parser end the HTML block early,
            # which used to leak a literal "</div>" onto the page.
            time_html = (
                f'<div class="metric-block">'
                f'<div class="metric-label">আনুমানিক সেচের সময় (Irrigation Time)</div>'
                f'<div class="metric-value">{format_irrigation_time_bn(irrigation_time_hours)}</div>'
                f'</div>'
            ).strip()

        st.markdown(
            f"""
            <div class='headline-card'>
                <div class="tag">{tag_text}</div>
                <div class="status">{result['status_bn']}</div>
                <div class="metrics">
                    <div class="metric-block">
                        <div class="metric-label">মোট পানি প্রয়োজন (Water Needed)</div>
                        <div class="metric-value">{bn_num(result['water_liters'], 0, True)}<span class="metric-unit">লিটার</span></div>
                    </div>
                    <div class="metric-block">
                        <div class="metric-label">সেচের পরিমাণ (Gross Irrigation)</div>
                        <div class="metric-value">{bn_num(result['gross_water_mm'], 1)}<span class="metric-unit">mm</span></div>
                    </div>
                    {time_html}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"""
            <div class='headline-card'>
                <div class="tag">আজ সেচের প্রয়োজন নেই (No Irrigation Needed)</div>
                <div class="status">{result['status_bn']}</div>
                <div class="metrics">
                    <div class="metric-block">
                        <div class="metric-label">জমিতে থাকা + বৃষ্টির পানি</div>
                        <div class="metric-value">{bn_num(result['available_water'] + result['effective_rain'], 1)}<span class="metric-unit">mm</span></div>
                    </div>
                    <div class="metric-block">
                        <div class="metric-label">ফসলের চাহিদা</div>
                        <div class="metric-value">{bn_num(result['crop_water_need'], 1)}<span class="metric-unit">mm/day</span></div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ================================================================
    # 2) SHORT SUMMARY CARD (2-3 lines)
    #    Covers: water balance, existing water, no-rain scenario.
    # ================================================================

    summary_lines = []

    summary_lines.append(
        f"ফসলের দৈনিক পানির চাহিদা "
        f"<b>{bn_num(result['crop_water_need'], 2)} mm/day</b>, "
        f"যার মধ্যে বৃষ্টি ও জমিতে থাকা পানি থেকে "
        f"<b>{bn_num(result['effective_rain'] + result['available_water'], 2)} mm</b> "
        f"পাওয়া যাচ্ছে।"
    )

    if irrigation_needed:

        summary_lines.append(
            f"তাই নিট সেচের প্রয়োজন "
            f"<b>{bn_num(result['net_water_needed'], 2)} mm</b> "
            f"(মোট <b>{bn_num(result['gross_water_mm'], 2)} mm</b>, "
            f"সেচ দক্ষতা {bn_num(data['efficiency'], 0)}% ধরে)।"
        )

    else:

        summary_lines.append(
            "জমিতে থাকা পানি ও কার্যকর বৃষ্টি ফসলের বর্তমান চাহিদা "
            "পূরণ করতে যথেষ্ট, তাই আজ অতিরিক্ত সেচ লাগবে না।"
        )

    if no_rain_net_mm > 0:

        summary_lines.append(
            f"আজ যদি কোনো বৃষ্টি না হয়, তাহলে প্রায় "
            f"<b>{bn_num(no_rain_gross_mm, 1)} mm</b> "
            f"({bn_num(no_rain_water_liters, 0, True)} লিটার) "
            f"পানি সেচ দিতে হতে পারে।"
        )

    else:

        summary_lines.append(
            "আজ বৃষ্টি না হলেও জমিতে থাকা পানি ফসলের চাহিদা পূরণে যথেষ্ট।"
        )

    summary_items_html = "".join(
        f"<li>{line}</li>" for line in summary_lines
    )

    st.markdown(
        f"""
        <div class='summary-card'>
            <div class="summary-title">সংক্ষিপ্ত বিবরণ (Summary)</div>
            <ul>
                {summary_items_html}
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ================================================================
    # 3) SMART RECOMMENDATION
    # ================================================================

    section_title(
        "স্মার্ট পরামর্শ",
        "Smart Recommendation"
    )

    recommendations = []

    if result["status"] == "NO_IRRIGATION":

        recommendations.append(
            "আজ অতিরিক্ত সেচ দেওয়ার প্রয়োজন নেই।"
        )

        recommendations.append(
            "জমিতে থাকা পানি এবং কার্যকর বৃষ্টির পানি "
            "ফসলের বর্তমান পানির চাহিদা পূরণের জন্য যথেষ্ট।"
        )

    elif result["status"] == "LOW":

        recommendations.append(
            "অল্প পরিমাণ সেচ দিন।"
        )

    elif result["status"] == "MEDIUM":

        recommendations.append(
            "মাঝারি পরিমাণ সেচ দেওয়া ভালো হবে।"
        )

    else:

        recommendations.append(
            "আজ ফসলের পানির চাহিদা বেশি। "
            "পর্যাপ্ত সেচ দিন।"
        )

    if data.get(
        "no_rain_message"
    ):

        recommendations.append(
            data["no_rain_message"]
        )

    if data["predicted_rain"] >= 20:

        recommendations.append(
            "বৃষ্টির পরিমাণ বেশি হতে পারে। "
            "সেচ দেওয়ার আগে বৃষ্টির পরিস্থিতি বিবেচনা করুন।"
        )

    if (
        data["existing_water"]
        >=
        result["crop_water_need"]
    ):

        recommendations.append(
            "জমিতে আগে থেকেই পর্যাপ্ত পানি আছে। "
            "অতিরিক্ত পানি জমে থাকলে ফসলের ক্ষতি হতে পারে।"
        )

    if data["soil_type"].startswith(
        "বেলে"
    ):

        recommendations.append(
            "বেলে মাটিতে পানি দ্রুত নিচে চলে যায়। "
            "প্রয়োজন হলে একবারে বেশি পানি না দিয়ে "
            "ভাগ করে সেচ দিন।"
        )

    if data["soil_type"].startswith(
        "এঁটেল"
    ):

        recommendations.append(
            "এঁটেল মাটি পানি বেশি সময় ধরে রাখে। "
            "সেচ দেওয়ার আগে জমিতে পানি জমে আছে কিনা "
            "পরীক্ষা করুন।"
        )

    if data["irrigation_method"].startswith(
        "ড্রিপ"
    ):

        recommendations.append(
            "ড্রিপ সেচ পানি সাশ্রয়ে কার্যকর এবং "
            "নিয়ন্ত্রিতভাবে পানি সরবরাহ করতে সাহায্য করে।"
        )

    if (
        "agriculture_show_recommendations"
        not in st.session_state
    ):

        st.session_state[
            "agriculture_show_recommendations"
        ] = False

    recommendation_clicked = st.button(
        "স্মার্ট পরামর্শ দেখুন ও শুনুন "
        "(Show & Listen to Smart Recommendations)",
        use_container_width=True,
        key="agriculture_recommendation_button"
    )

    if recommendation_clicked:

        st.session_state[
            "agriculture_show_recommendations"
        ] = True

        reset_voice_hash()

        agriculture_recommendation_voice(
            recommendations
        )

    if st.session_state.get(
        "agriculture_show_recommendations",
        False
    ):

        with st.container(border=True):

            for rec in recommendations:

                st.write(
                    f"• {rec}"
                )

    # ================================================================
    # 4) EVERYTHING ELSE -> collapsed under one details expander
    #    (Crop Water Calculation, Water Balance, How Much Water,
    #     Irrigation Method & Time, No-Rain scenario, Existing Water,
    #     the raw calculation log and the bar chart.)
    # ================================================================

    with st.expander(
        "হিসাবের বিস্তারিত দেখুন (Show Full Calculation Details)"
    ):

        st.markdown(
            "**ফসলের পানির হিসাব (Crop Water Calculation)**"
        )

        a, b, c = st.columns(3)

        a.metric(
            "ET0",
            f"{bn_num(result['et0_mm'], 2)} mm/day"
        )

        b.metric(
            "Kc",
            f"{bn_num(result['kc'], 2)}"
        )

        c.metric(
            "ETc",
            f"{bn_num(result['automatic_etc_mm'], 2)} mm/day"
        )

        st.caption(
            (
                "ব্যবহৃত পদ্ধতি: Manual Override"
                if result.get("water_requirement_method") == "MANUAL"
                else "ব্যবহৃত পদ্ধতি: ET0 × Kc (Automatic)"
            )
            + f" → {bn_num(result['crop_water_need'], 2)} mm/day"
        )

        st.divider()

        st.markdown(
            "**পানির ভারসাম্য (Water Balance)**"
        )

        a, b, c, d = st.columns(4)

        a.metric(
            "কার্যকর বৃষ্টি",
            f"{bn_num(result['effective_rain'], 2)} mm"
        )

        b.metric(
            "জমিতে থাকা পানি",
            f"{bn_num(result['available_water'], 2)} mm"
        )

        c.metric(
            "নিট সেচ",
            f"{bn_num(result['net_water_needed'], 2)} mm"
        )

        d.metric(
            "মোট সেচ",
            f"{bn_num(result['gross_water_mm'], 2)} mm"
        )

        st.divider()

        st.markdown(
            "**কতটুকু পানি (How Much Water)**"
        )

        a, b, c = st.columns(3)

        a.metric(
            "লিটার",
            f"{bn_num(result['water_liters'], 0, True)} L"
        )

        b.metric(
            "ঘনমিটার",
            f"{bn_num(result['water_m3'], 2, True)} m³"
        )

        c.metric(
            "জমির আয়তন",
            f"{bn_num(result['area_m2'], 0, True)} m²"
        )

        if irrigation_needed:

            st.divider()

            st.markdown(
                "**সেচ পদ্ধতি ও সময় (Irrigation Method & Time)**"
            )

            irrigation_method = data.get(
                "irrigation_method"
            )

            if irrigation_method:

                st.write(
                    f"নির্বাচিত সেচ পদ্ধতি: "
                    f"**{irrigation_method}**"
                )

            if (
                irrigation_time_hours is not None
                and
                float(irrigation_time_hours) > 0
            ):

                st.success(
                    f"আনুমানিক সেচের সময়: প্রায় "
                    f"{format_irrigation_time_bn(irrigation_time_hours)}"
                )

            else:

                time_result = data.get(
                    "irrigation_time_result"
                ) or {}

                if time_result.get(
                    "needs_flow_input"
                ):

                    st.warning(
                        "এই সেচ পদ্ধতির জন্য প্রয়োজনীয় "
                        "flow/input সম্পূর্ণ পাওয়া যায়নি।"
                    )

                else:

                    st.info(
                        "সেচের সময় নির্ধারণ করা যায়নি।"
                    )

        st.divider()

        st.markdown(
            "**আজ বৃষ্টি না হলে করণীয় (If There Is No Rain Today)**"
        )

        a, b, c = st.columns(3)

        a.metric(
            "নিট চাহিদা",
            f"{bn_num(no_rain_net_mm, 2)} mm"
        )

        b.metric(
            "মোট সেচ",
            f"{bn_num(no_rain_gross_mm, 2)} mm"
        )

        c.metric(
            "প্রয়োজনীয় পানি",
            f"{bn_num(no_rain_water_liters, 0, True)} L"
        )

        st.divider()

        st.markdown(
            "**জমিতে থাকা পানির তথ্য (Existing Water Information)**"
        )

        a, b, c = st.columns(3)

        a.metric(
            "পানির গভীরতা",
            f"{bn_num(data['existing_water'], 1)} mm"
        )

        b.metric(
            "মোট পানি",
            f"{bn_num(data['existing_water_liters'], 0, True)} L"
        )

        c.metric(
            "পানির পরিমাণ",
            f"{bn_num(data['existing_water_m3'], 2, True)} m³"
        )

        st.caption(
            f"ব্যবহৃত পরিমাপ: {data['water_measurement']}। "
            f"এটি একটি আনুমানিক হিসাব।"
        )

        st.divider()

        st.markdown(
            "**হিসাবের লগ (Calculation Log)**"
        )

        st.write(
            f"ফসল (Crop): {data['crop_label']}"
        )

        st.write(
            f"মৌসুম (Season): {data['season_label']}"
        )

        st.write(
            f"হিসাবের তারিখ: {data['calculation_date']}"
        )

        st.write(
            f"রোপণ/বপনের তারিখ: {data['actual_planting_date']}"
        )

        st.write(
            f"ফসলের বয়স: "
            f"{bn_num(stage_info.get('day_of_crop'), 0)} / "
            f"{bn_num(stage_info.get('duration_days'), 0)} দিন"
        )

        st.write(
            f"স্বয়ংক্রিয়ভাবে নির্ধারিত পর্যায়: "
            f"{stage_info.get('stage_label', 'N/A')}"
        )

        st.write(
            f"ব্যবহৃত বৃদ্ধি পর্যায়: {data['crop_stage_label']}"
        )

        st.write(
            f"বৃষ্টির পূর্বাভাস: {bn_num(data['predicted_rain'], 2)} mm"
        )

        st.write(
            f"সেচ দক্ষতা: {bn_num(data['efficiency'], 0)}%"
        )

        if data.get("dripper_count") is not None:

            st.write(
                f"ড্রিপারের সংখ্যা: "
                f"{bn_num(data['dripper_count'], 0)} টি"
            )

        if data.get("sprinkler_count") is not None:

            st.write(
                f"স্প্রিংকলারের সংখ্যা: "
                f"{bn_num(data['sprinkler_count'], 0)} টি"
            )

        if data.get("sprinkler_flow_lph") is not None:

            st.write(
                f"প্রতি স্প্রিংকলারের flow: "
                f"{bn_num(data['sprinkler_flow_lph'], 2)} L/hour"
            )

        st.caption(
            "Formula: Automatic ETc = ET0 × Kc; "
            "Net Irrigation = max("
            "Applied Crop Water Requirement − "
            "Effective Rainfall − "
            "Available Water, 0); "
            "Gross Irrigation = "
            "Net Irrigation ÷ Efficiency; "
            "No-Rain Net = max("
            "Applied Crop Water Requirement − "
            "Available Water, 0). "
            "Irrigation Time = calculated by the "
            "configured irrigation service."
        )

        st.divider()

        st.markdown(
            "**কৃষি পানির ভারসাম্য গ্রাফ (Agricultural Water Balance Graph)**"
        )

        chart_df = pd.DataFrame({

            "বিভাগ (Category)": [

                "ফসলের পানির চাহিদা",

                "কার্যকর বৃষ্টি",

                "জমিতে থাকা পানি",

                "নিট সেচ",

                "মোট সেচ",

                "বৃষ্টি ছাড়া মোট সেচ"
            ],

            "পানি (Water mm)": [

                result["crop_water_need"],

                result["effective_rain"],

                result["available_water"],

                result["net_water_needed"],

                result["gross_water_mm"],

                no_rain_gross_mm
            ]
        })

        fig = px.bar(
            chart_df,
            x="বিভাগ (Category)",
            y="পানি (Water mm)",
            title=(
                "কৃষি পানির ভারসাম্য "
                "(Agricultural Water Balance)"
            ),
            text_auto=".2f"
        )

        fig.update_layout(
            xaxis_title="",
            yaxis_title="পানির পরিমাণ (Water in mm)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# [34] MAIN PAGE CONTROLLER
# ------------------------------------------------------------
# FUNCTION:
#     show_agriculture()
#
# PURPOSE:
# Top-level Streamlit page controller for the Agriculture page.
#
# ORDER OF OPERATIONS:
#   1. Inject styles
#   2. Voice ON/OFF toggle
#   3. Play welcome voice (once)
#   4. Page title + intro
#   5. Intro "agri-card"
#   6. Location & Date section (triggers rainfall prediction)
#   7. Main input panel (weather -> land -> crop -> growth ->
#      reference -> soil -> existing water -> crop water need ->
#      irrigation system -> Calculate button)
#   8. Result display
#   9. Process queued voice + render voice player
#
# CHANGE HERE IF:
# - the overall page order needs to change.
# ============================================================

def show_agriculture(
    df,
    model,
    feature_columns,
    train_medians,
    history_days
):

    inject_agriculture_styles()

    agriculture_voice_toggle()

    start_agriculture_welcome()

    st.title(
        "Smart Agriculture & Irrigation"
    )

    st.caption(
        "ফসল, মৌসুম, রোপণ/বপনের তারিখ, জমির পরিমাণ, "
        "মাটির ধরন, বৃষ্টির পূর্বাভাস এবং জমিতে থাকা পানি "
        "অনুযায়ী সেচের পানি হিসাব করুন।"
    )

    st.markdown(
        """
        <div class='agri-card'>
            <h3>Smart Irrigation Recommendation</h3>
            <p>
            ফসলের মৌসুম, প্রকৃত রোপণ/বপনের তারিখ,
            বৃদ্ধি পর্যায়, জমির পরিমাণ, বৃষ্টির পূর্বাভাস
            এবং ET0 ব্যবহার করে প্রয়োজনীয় সেচের পরিমাণ
            হিসাব করা হবে।
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    agriculture_location_date_section(
        df=df,
        model=model,
        feature_columns=feature_columns,
        train_medians=train_medians,
        history_days=history_days
    )

    _agriculture_input_panel()

    show_agriculture_result()

    process_voice_queue()

    render_voice_player()


# ============================================================
#                  END OF FILE
# ============================================================
#
# QUICK DEVELOPER REFERENCE
# ------------------------------------------------------------
#
# If you need to change...
#
# Welcome voice text
#       -> [02]
#
# Welcome voice trigger
#       -> [03]
#
# Voice on/off
#       -> [04]
#
# Page CSS
#       -> [05]
#
# Bangla number format
#       -> [06]
#
# Irrigation time text
#       -> [07]
#
# Bangla month names
#       -> [08]
#
# Date display / voice text
#       -> [09] / [10]
#
# Voice input helper
#       -> [11]
#
# Section heading style
#       -> [12]
#
# Section-entry voice
#       -> [13]
#
# Selection-change voice
#       -> [14]
#
# Voice confirmation wording
#       -> [15]
#
# Next-step voice instruction
#       -> [16]
#
# Input voice callback / irrigation-method branching
#       -> [17]
#
# Automatic rainfall prediction for Agriculture
#       -> [18]
#
# Bangla location name tables
#       -> [19]
#
# Bangla name lookup
#       -> [20]
#
# Bangla location label
#       -> [21]
#
# Station/date selection
#       -> [22]
#
# Weather & rainfall Auto/Manual
#       -> [23]
#
# Land information
#       -> [24]
#
# Crop / season selection
#       -> [25]
#
# Growth stage determination UI
#       -> [26]
#
# Crop reference card
#       -> [27]
#
# Soil information
#       -> [28]
#
# Existing water estimation
#       -> [29]
#
# Crop water requirement (ET0 x Kc / Manual)
#       -> [30]
#
# Irrigation method / efficiency inputs
#       -> [31]
#
# Validation + calculation trigger
#       -> [32]
#
# Result cards / recommendations / details expander
#       -> [33]
#
# Overall page order
#       -> [34]
#
# ============================================================