
# ============================================================
# ============================================================
#          RAINFALL PREDICTION PAGE — DEVELOPER GUIDE
# ============================================================
#
# PURPOSE OF THIS FILE
# ------------------------------------------------------------
# This file controls the Streamlit Rainfall Prediction page.
#
# MAIN RESPONSIBILITIES
# ------------------------------------------------------------
# 1. Select weather station
# 2. Select prediction date
# 3. Determine Past / Today / Future mode
# 4. Load weather data from API
# 5. Fall back to station CSV median values if API fails
# 6. Allow user to edit weather values manually
# 7. Prepare historical rainfall data
# 8. Create lag / rolling / calendar / weather features
# 9. Match features with the trained CatBoost model
# 10. Run rainfall prediction
# 11. Estimate rainfall likelihood for UI display
# 12. Show rainfall condition and prediction result
# 13. Display rainfall probability speedometer
#
#
# ============================================================
#                    MASTER CODE INDEX
# ============================================================
#
# [01] IMPORTS
#      External libraries and internal project services.
#
# [02] WEATHER CONDITION
#      Function: condition()
#      Converts weather code / predicted rainfall into a
#      human-readable weather condition and message.
#
# [03] RAIN PROBABILITY
#      Function: estimate_rain_probability()
#      Converts predicted rainfall amount into an estimated
#      UI rainfall likelihood percentage.
#
#      IMPORTANT:
#      This is NOT a statistical/calibrated probability.
#
# [04] SAFE NUMBER CONVERSION
#      Function: safe_float()
#      Prevents invalid / missing numeric values from breaking
#      the prediction pipeline.
#
# [05] PREDICTION FEATURE ENGINEERING
#      Function: create_prediction_features()
#
#      This is the CORE ML preprocessing section.
#
#      It creates:
#        - Target row
#        - Calendar features
#        - Cyclic date features
#        - Rainfall lag features
#        - Rain occurrence lag features
#        - Rolling rainfall features
#        - Weather lag features
#        - Station dummy variables
#        - Model feature matrix
#        - Missing-value filling
#        - Final feature-column ordering
#
#      IF MODEL FEATURES NEED TO BE CHANGED:
#      Start here.
#
# [06] WEATHER DATA LOADING
#      Function: load_weather_values()
#      Gets target-date weather from weather API and attaches
#      station latitude/longitude.
#
# [07] PREDICTION PAGE
#      Function: show_prediction()
#      Main Streamlit page controller.
#
#      This function handles:
#        - Page title
#        - Station selection
#        - Date selection
#        - Past/Today/Future mode
#        - Session-state management
#        - Weather loading
#        - Weather form
#        - User-submitted prediction
#        - Historical data preparation
#        - Feature creation
#        - Model prediction
#        - Result storage
#        - Result display
#
# [08] STATION SELECTION
#      Determines which Bangladesh weather station is used.
#
# [09] DATE SELECTION
#      Determines target prediction date.
#
# [10] PAST / TODAY / FUTURE MODE
#      Controls which weather source and prediction message
#      are used according to selected date.
#
# [11] SESSION KEY / RESULT RESET
#      Prevents old station/date prediction results from being
#      incorrectly displayed after user changes station/date.
#
# [12] WEATHER DATA SOURCE
#      API weather -> if unavailable -> CSV median fallback.
#
# [13] WEATHER INPUT FORM
#      User-visible weather input fields.
#
#      IF YOU WANT TO ADD / REMOVE WEATHER INPUTS:
#      Change this section AND also update the values dictionary
#      used for prediction.
#
# [14] HISTORICAL RAINFALL PREPARATION
#      Calls build_on_demand_history().
#
# [15] PREDICTION FEATURE CREATION
#      Calls create_prediction_features().
#
# [16] MODEL VALIDATION
#      Checks whether the generated feature matrix is valid.
#
# [17] CATBOOST PREDICTION
#      Sends prepared features to the trained model.
#
# [18] RESULT STORAGE
#      Stores prediction information in Streamlit session state.
#
# [19] RESULT DISPLAY
#      Displays:
#        - Rain probability
#        - Speedometer
#        - Predicted rainfall
#        - Weather condition
#        - ET0
#        - Probability message
#        - General weather message
#        - Historical data note
#        - Future prediction message
#
# [20] RAIN PROBABILITY GAUGE
#      Plotly semicircle speedometer.
#
#      IF ONLY THE GAUGE DESIGN NEEDS TO CHANGE:
#      Change this section.
#
#
# ============================================================
#              IMPORTANT CHANGE-LOCATION GUIDE
# ============================================================
#
# Change rainfall condition text
# -> [02] WEATHER CONDITION
#
# Change rainfall probability calculation
# -> [03] RAIN PROBABILITY
#
# Change missing-value handling
# -> [04] SAFE NUMBER
# -> [05] FILL MISSING section
#
# Change rainfall lag days
# -> [05] RAIN LAGS
#
# Change rainfall occurrence lag days
# -> [05] RAIN OCCURRENCE
#
# Change rolling rainfall windows
# -> [05] ROLLING FEATURES
#
# Change weather lag days
# -> [05] WEATHER LAGS
#
# Change model input features
# -> [05] MODEL FEATURES
#
# Change station dummy generation
# -> [05] STATION DUMMIES
#
# Change model missing-value fallback
# -> [05] FILL MISSING
#
# Change weather API behavior
# -> [06] LOAD WEATHER VALUES
#
# Change station dropdown
# -> [08] STATION DATA / STATION SELECT
#
# Change date selection
# -> [09] DATE SELECT
#
# Change Past/Today/Future behavior
# -> [10] STATUS / MODE
#
# Change API -> CSV fallback
# -> [12] WEATHER DATA
#
# Change weather input fields
# -> [13] WEATHER FORM
#
# Change prediction calculation pipeline
# -> [14] HISTORY
# -> [15] FEATURES
# -> [16] VALIDATION
# -> [17] MODEL PREDICTION
#
# Change what is saved after prediction
# -> [18] SAVE RESULT
#
# Change result cards / metrics
# -> [19] MAIN METRICS
#
# Change rainfall probability messages
# -> [19] PROBABILITY MESSAGE
#
# Change speedometer appearance
# -> [20] RAIN PROBABILITY GAUGE
#
# Change future prediction message
# -> [19] FUTURE MESSAGE
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
#     -> fetch_target_weather()
#
# External model object:
#     -> model
#
# Model-related inputs passed into show_prediction():
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
#                  PREDICTION FLOW
# ============================================================
#
# User selects Station
#        ↓
# User selects Date
#        ↓
# Determine Past / Today / Future
#        ↓
# Create station + date session key
#        ↓
# Load weather from API
#        ↓
# API fails?
#    YES ↓        NO ↓
# CSV median       API weather
#        ↓             ↓
#        └──────→ Weather Form
#                       ↓
#               User clicks Predict
#                       ↓
#             Prepare historical data
#                       ↓
#              Create ML features
#                       ↓
#                Validate features
#                       ↓
#                CatBoost model
#                       ↓
#             Predicted rainfall
#                       ↓
#        Condition + estimated probability
#                       ↓
#                 Save result
#                       ↓
#              Display result/gauge
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
# rainfall prediction page.
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
import plotly.graph_objects as go

from datetime import date

from services.data_loader import get_station_table

from services.weather_api import (
    build_on_demand_history,
    fetch_target_weather
)


# ============================================================
# [02] WEATHER CONDITION
# ------------------------------------------------------------
# FUNCTION:
#     condition()
#
# PURPOSE:
# Converts either:
#   1. predicted rainfall amount
# OR
#   2. weather API weather code
#
# into:
#   - weather name
#   - human-readable message
#
# CHANGE HERE IF:
# - rainfall category thresholds need to change
# - weather labels need to change
# - weather messages need to change
#
# IMPORTANT:
# When prediction is available, predicted rainfall takes
# priority over weather code.
# ============================================================

def condition(code, pred=None):

    if pred is not None:

        if pred < 1:
            return (
                "☀️ Sunny",
                "Mostly dry conditions expected."
            )

        elif pred < 10:
            return (
                "🌤️ Light Rain",
                "Light rainfall is possible."
            )

        elif pred < 25:
            return (
                "🌧️ Moderate Rain",
                "Noticeable rainfall is expected."
            )

        elif pred < 50:
            return (
                "⛈️ Heavy Rain",
                "Heavy rainfall expected."
            )

        else:
            return (
                "🚨 Very Heavy Rain",
                "Very heavy rainfall expected."
            )

    if code in [0, 1]:

        return (
            "☀️ Sunny",
            "Clear weather."
        )

    elif code in [2, 3, 45, 48]:

        return (
            "☁️ Cloudy",
            "Cloudy conditions."
        )

    else:

        return (
            "🌧️ Rainy",
            "Rainy conditions."
        )


# ============================================================
# [03] RAIN PROBABILITY
# ------------------------------------------------------------
# FUNCTION:
#     estimate_rain_probability()
#
# PURPOSE:
# Converts predicted rainfall amount into a percentage used
# only for the UI rainfall-likelihood display.
#
# IMPORTANT:
# This is NOT a calibrated probability produced by the
# regression model.
#
# CHANGE HERE IF:
# - probability curve needs adjustment
# - probability thresholds need adjustment
#
# DO NOT describe this as statistical model probability unless
# the underlying methodology is changed and validated.
# ============================================================

def estimate_rain_probability(pred):

    """
    Estimate rainfall likelihood from predicted rainfall amount.

    IMPORTANT:
    This is an estimated UI score based on predicted rainfall.
    It is NOT a calibrated statistical probability from the
    regression model.
    """

    pred = max(float(pred), 0.0)

    if pred <= 0:

        probability = 5.0

    else:

        probability = 100 * (
            1 - np.exp(-pred / 18)
        )

    probability = min(
        max(probability, 0),
        100
    )

    return probability


# ============================================================
# [04] SAFE NUMBER CONVERSION
# ------------------------------------------------------------
# FUNCTION:
#     safe_float()
#
# PURPOSE:
# Safely converts a value to float.
#
# If the value is:
#   - NaN
#   - missing
#   - invalid
#
# a default value is returned instead of allowing the prediction
# pipeline to crash.
#
# CHANGE HERE IF:
# - numeric fallback behavior needs to change.
# ============================================================

def safe_float(value, default=0.0):

    try:

        if pd.isna(value):

            return float(default)

        return float(value)

    except Exception:

        return float(default)


# ============================================================
# [05] CORE ML FEATURE ENGINEERING
# ------------------------------------------------------------
# FUNCTION:
#     create_prediction_features()
#
# PURPOSE:
# Creates the exact type of feature matrix expected by the
# trained rainfall prediction model.
#
# THIS IS ONE OF THE MOST IMPORTANT FUNCTIONS IN THIS FILE.
#
# INPUTS:
#   historical_df
#       Historical station weather/rainfall data.
#
#   station_id
#       Selected weather station.
#
#   target_date
#       Date for which rainfall is being predicted.
#
#   weather_values
#       Weather values for the target date.
#
#   feature_columns
#       Exact feature-column list expected by the model.
#
#   train_medians
#       Training-data median fallback values.
#
# OUTPUT:
#   X_prediction
#       Final model-ready feature matrix.
#
# CHANGE THIS FUNCTION ONLY CAREFULLY.
#
# Any change here can directly affect model predictions.
# ============================================================

def create_prediction_features(
    historical_df,
    station_id,
    target_date,
    weather_values,
    feature_columns,
    train_medians
):

    # ========================================================
    # [05-A] COPY AND NORMALIZE DATA
    # --------------------------------------------------------
    # Makes a working copy and normalizes dates so that
    # comparisons are consistent.
    # ========================================================

    data = historical_df.copy()

    data["Date"] = pd.to_datetime(
        data["Date"],
        errors="coerce"
    ).dt.normalize()

    target_date = pd.Timestamp(
        target_date
    ).normalize()

    data = data.sort_values(
        ["Station_ID", "Date"]
    ).reset_index(drop=True)

    # Remove an existing target-date row for the same station.
    # A new target row will be created using current weather
    # values below.
    data = data[
        ~(
            (data["Station_ID"] == station_id)
            &
            (data["Date"] == target_date)
        )
    ].copy()

    # ========================================================
    # [05-B] TARGET ROW
    # --------------------------------------------------------
    # Creates the row representing the date we want to predict.
    #
    # Target rainfall is intentionally set to NaN because that
    # is the value the model is trying to predict.
    #
    # CHANGE HERE IF:
    # - new target-date weather fields are introduced
    # - existing weather fields are renamed
    #
    # IMPORTANT:
    # The feature names should remain compatible with the
    # training pipeline.
    # ========================================================

    target_row = {

        "Date": target_date,

        "Station_ID": station_id,

        "Latitude": safe_float(
            weather_values.get("Latitude")
        ),

        "Longitude": safe_float(
            weather_values.get("Longitude")
        ),

        "temperature_2m_mean": safe_float(
            weather_values.get(
                "temperature_2m_mean"
            )
        ),

        "temperature_2m_max": safe_float(
            weather_values.get(
                "temperature_2m_max"
            )
        ),

        "temperature_2m_min": safe_float(
            weather_values.get(
                "temperature_2m_min"
            )
        ),

        "apparent_temperature_mean": safe_float(
            weather_values.get(
                "apparent_temperature_mean"
            )
        ),

        "sunshine_duration": safe_float(
            weather_values.get(
                "sunshine_duration"
            )
        ),

        "daylight_duration": safe_float(
            weather_values.get(
                "daylight_duration"
            )
        ),

        "wind_speed_10m_max": safe_float(
            weather_values.get(
                "wind_speed_10m_max"
            )
        ),

        "wind_gusts_10m_max": safe_float(
            weather_values.get(
                "wind_gusts_10m_max"
            )
        ),

        "wind_direction_10m_dominant": safe_float(
            weather_values.get(
                "wind_direction_10m_dominant"
            )
        ),

        "shortwave_radiation_sum": safe_float(
            weather_values.get(
                "shortwave_radiation_sum"
            )
        ),

        "weather_code": safe_float(
            weather_values.get(
                "weather_code"
            )
        ),

        "et0_fao_evapotranspiration": safe_float(
            weather_values.get(
                "et0_fao_evapotranspiration"
            )
        ),

        "rain_sum": np.nan
    }

    target_df = pd.DataFrame(
        [target_row]
    )

    data = pd.concat(
        [
            data,
            target_df
        ],
        ignore_index=True,
        sort=False
    )

    data = data.sort_values(
        ["Station_ID", "Date"]
    ).reset_index(drop=True)

    # ========================================================
    # [05-C] CALENDAR FEATURES
    # --------------------------------------------------------
    # Creates date-based features used by the ML model.
    #
    # Includes:
    #   year
    #   month
    #   day
    #   dayofyear
    #   dayofweek
    #   weekofyear
    #
    # CHANGE HERE IF:
    # - calendar features need to be added/removed.
    #
    # IMPORTANT:
    # The training pipeline must use the same feature logic.
    # ========================================================

    data["year"] = data["Date"].dt.year

    data["month"] = data["Date"].dt.month

    data["day"] = data["Date"].dt.day

    data["dayofyear"] = (
        data["Date"].dt.dayofyear
    )

    data["dayofweek"] = (
        data["Date"].dt.dayofweek
    )

    data["weekofyear"] = (
        data["Date"]
        .dt.isocalendar()
        .week
        .astype(int)
    )

    # ========================================================
    # [05-D] CYCLIC FEATURES
    # --------------------------------------------------------
    # Converts periodic calendar values into sine/cosine
    # representations.
    #
    # This helps the model understand that:
    #   December -> January
    # is a continuous seasonal cycle.
    #
    # CHANGE HERE IF:
    # - seasonal encoding needs modification.
    # ========================================================

    data["month_sin"] = (
        np.sin(
            2 * np.pi * data["month"] / 12
        )
    )

    data["month_cos"] = (
        np.cos(
            2 * np.pi * data["month"] / 12
        )
    )

    data["dayofyear_sin"] = (
        np.sin(
            2 * np.pi
            * data["dayofyear"]
            / 365.25
        )
    )

    data["dayofyear_cos"] = (
        np.cos(
            2 * np.pi
            * data["dayofyear"]
            / 365.25
        )
    )

    data["dayofweek_sin"] = (
        np.sin(
            2 * np.pi
            * data["dayofweek"]
            / 7
        )
    )

    data["dayofweek_cos"] = (
        np.cos(
            2 * np.pi
            * data["dayofweek"]
            / 7
        )
    )

    # ========================================================
    # [05-E] RAINFALL LAG FEATURES
    # --------------------------------------------------------
    # Uses previous rainfall observations from the same station.
    #
    # Example:
    # rain_lag_1  -> previous day's rainfall
    # rain_lag_7  -> rainfall 7 days earlier
    #
    # CURRENT LAG WINDOWS:
    # 1, 2, 3, 5, 7, 14, 21, 30 days
    #
    # CHANGE HERE IF:
    # - different lag periods are required.
    #
    # IMPORTANT:
    # Training and prediction feature definitions must match.
    # ========================================================

    RAIN_LAGS = [
        1,
        2,
        3,
        5,
        7,
        14,
        21,
        30
    ]

    for lag in RAIN_LAGS:

        data[
            f"rain_lag_{lag}"
        ] = (
            data
            .groupby("Station_ID")["rain_sum"]
            .shift(lag)
        )

    # ========================================================
    # [05-F] RAIN OCCURRENCE FEATURES
    # --------------------------------------------------------
    # Converts rainfall into a binary indicator:
    #
    #   rainfall > 0 -> 1
    #   rainfall <= 0 -> 0
    #
    # Then creates lagged occurrence features.
    #
    # CURRENT LAGS:
    # 1, 2, 3, 7 days
    #
    # CHANGE HERE IF:
    # rainfall occurrence definition needs to change.
    # ========================================================

    rain_occurrence = (
        data["rain_sum"] > 0
    ).astype(int)

    for lag in [1, 2, 3, 7]:

        data[
            f"rain_occurrence_lag_{lag}"
        ] = (
            rain_occurrence
            .groupby(data["Station_ID"])
            .shift(lag)
        )

    # ========================================================
    # [05-G] ROLLING RAINFALL FEATURES
    # --------------------------------------------------------
    # Creates historical rainfall summaries.
    #
    # CURRENT WINDOWS:
    #   3 days
    #   7 days
    #   14 days
    #   30 days
    #
    # FEATURES CREATED FOR EACH WINDOW:
    #   rain_roll_mean
    #   rain_roll_sum
    #   rain_roll_std
    #
    # IMPORTANT:
    # shifted_rain uses shift(1), meaning the target day's
    # rainfall is not included in its own rolling history.
    #
    # This is important for avoiding direct target leakage.
    #
    # CHANGE HERE IF:
    # - rolling windows need to change
    # - additional rolling statistics are needed.
    # ========================================================

    shifted_rain = (
        data
        .groupby("Station_ID")["rain_sum"]
        .shift(1)
    )

    for window in [3, 7, 14, 30]:

        data[
            f"rain_roll_mean_{window}"
        ] = (
            shifted_rain
            .groupby(data["Station_ID"])
            .transform(
                lambda x:
                x.rolling(
                    window=window,
                    min_periods=1
                ).mean()
            )
        )

        data[
            f"rain_roll_sum_{window}"
        ] = (
            shifted_rain
            .groupby(data["Station_ID"])
            .transform(
                lambda x:
                x.rolling(
                    window=window,
                    min_periods=1
                ).sum()
            )
        )

        data[
            f"rain_roll_std_{window}"
        ] = (
            shifted_rain
            .groupby(data["Station_ID"])
            .transform(
                lambda x:
                x.rolling(
                    window=window,
                    min_periods=2
                ).std()
            )
        )

    # ========================================================
    # [05-H] WEATHER LAG FEATURES
    # --------------------------------------------------------
    # Creates lagged versions of historical weather variables.
    #
    # CURRENT WEATHER VARIABLES:
    #   temperature
    #   apparent temperature
    #   sunshine
    #   daylight
    #   wind speed
    #   wind gusts
    #   wind direction
    #   radiation
    #   weather code
    #   ET0
    #
    # CURRENT LAGS:
    #   1, 2, 3, 7 days
    #
    # CHANGE HERE IF:
    # - weather variables change
    # - lag periods change.
    #
    # IMPORTANT:
    # Keep this synchronized with model training features.
    # ========================================================

    same_day_weather = [

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

    for feature in same_day_weather:

        for lag in [1, 2, 3, 7]:

            data[
                f"{feature}_lag_{lag}"
            ] = (
                data
                .groupby("Station_ID")[feature]
                .shift(lag)
            )

    # ========================================================
    # [05-I] STATION DUMMY VARIABLES
    # --------------------------------------------------------
    # Converts Station_ID into one-hot encoded station columns.
    #
    # Example:
    #   station_1
    #   station_2
    #   station_3
    #
    # CHANGE HERE IF:
    # - station encoding strategy changes.
    #
    # IMPORTANT:
    # Model training must use compatible station encoding.
    # ========================================================

    station_dummies = pd.get_dummies(
        data["Station_ID"],
        prefix="station",
        dtype=int
    )

    data = pd.concat(
        [
            data,
            station_dummies
        ],
        axis=1
    )

    # ========================================================
    # [05-J] GET TARGET ROW
    # --------------------------------------------------------
    # Extracts the exact station/date row that needs prediction.
    #
    # There must be exactly ONE matching row.
    # ========================================================

    prediction_row = data[
        (data["Station_ID"] == station_id)
        &
        (data["Date"] == target_date)
    ].copy()

    if len(prediction_row) != 1:

        raise ValueError(
            "Could not create prediction row."
        )

    # ========================================================
    # [05-K] SELECT MODEL FEATURES
    # --------------------------------------------------------
    # Selects ONLY the columns expected by the trained model.
    #
    # feature_columns comes from the trained model/package.
    #
    # IMPORTANT:
    # This is where the large generated dataframe becomes the
    # actual model input.
    #
    # CHANGE CAREFULLY.
    # ========================================================

    X_prediction = (
        prediction_row
        .reindex(columns=feature_columns)
    )

    # ========================================================
    # [05-L] NUMERIC CONVERSION
    # --------------------------------------------------------
    # Ensures all model input values are numeric.
    #
    # Invalid values become NaN and are handled later.
    # ========================================================

    for col in X_prediction.columns:

        X_prediction[col] = pd.to_numeric(
            X_prediction[col],
            errors="coerce"
        )

    X_prediction = X_prediction.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # ========================================================
    # [05-M] STATION HISTORY
    # --------------------------------------------------------
    # Gets only historical rows from the selected station and
    # only dates before the prediction date.
    #
    # Used to calculate station-specific median fallback values.
    #
    # This gives the prediction pipeline a station-specific
    # missing-value fallback before using training medians.
    # ========================================================

    station_history = data[
        (data["Station_ID"] == station_id)
        &
        (data["Date"] < target_date)
    ].copy()

    station_history = (
        station_history
        .reindex(columns=feature_columns)
    )

    for col in station_history.columns:

        station_history[col] = pd.to_numeric(
            station_history[col],
            errors="coerce"
        )

    station_medians = (
        station_history
        .median(numeric_only=True)
    )

    # ========================================================
    # [05-N] FILL MISSING VALUES
    # --------------------------------------------------------
    # Missing values are filled in THREE stages:
    #
    # 1. Selected station's historical median
    # 2. Training-data median
    # 3. Zero as final fallback
    #
    # CHANGE HERE IF:
    # missing-value strategy needs to change.
    #
    # IMPORTANT:
    # Changing preprocessing can affect prediction behavior.
    # ========================================================

    X_prediction = (
        X_prediction
        .fillna(station_medians)
    )

    X_prediction = (
        X_prediction
        .fillna(train_medians)
    )

    X_prediction = (
        X_prediction
        .fillna(0)
    )

    # ========================================================
    # [05-O] FINAL FEATURE COLUMN ORDER
    # --------------------------------------------------------
    # Reorders the final dataframe to exactly match the model's
    # expected feature order.
    #
    # This is important because ML models expect the same
    # feature arrangement used during training.
    # ========================================================

    X_prediction = (
        X_prediction
        .reindex(
            columns=feature_columns,
            fill_value=0
        )
    )

    return X_prediction


# ============================================================
# [06] WEATHER DATA LOADING
# ------------------------------------------------------------
# FUNCTION:
#     load_weather_values()
#
# PURPOSE:
# Requests target-date weather from the weather API.
#
# It also attaches station latitude and longitude.
#
# RETURN:
#   Success -> (weather_data, None)
#   Failure -> (None, error_message)
#
# IMPORTANT:
# This function does NOT directly perform the prediction.
# It only prepares weather values.
#
# CHANGE HERE IF:
# - weather API source changes
# - API response processing changes
# ============================================================

def load_weather_values(
    station,
    target
):

    try:

        weather = fetch_target_weather(
            station=station,
            target_date=target
        )

        weather["Latitude"] = float(
            station["Latitude"]
        )

        weather["Longitude"] = float(
            station["Longitude"]
        )

        return weather, None

    except Exception as e:

        return None, str(e)


# ============================================================
# [07] MAIN PREDICTION PAGE
# ------------------------------------------------------------
# FUNCTION:
#     show_prediction()
#
# PURPOSE:
# This is the main controller of the Streamlit prediction page.
#
# PARAMETERS:
#
# df
#   Historical weather/rainfall dataframe.
#
# model
#   Trained rainfall prediction model.
#
# feature_columns
#   Exact model feature list.
#
# train_medians
#   Training median fallback values.
#
# history_days
#   Number of historical days used for feature preparation.
#
# IMPORTANT:
# Most user interaction and prediction flow happens here.
# ============================================================

def show_prediction(
    df,
    model,
    feature_columns,
    train_medians,
    history_days
):

    # ========================================================
    # [07-A] PAGE TITLE
    # --------------------------------------------------------
    # User-visible title and explanation.
    #
    # CHANGE HERE IF:
    # - page title
    # - introductory description
    # needs to change.
    # ========================================================

    st.title(
        "🔮 Rainfall Prediction"
    )

    st.caption(
        "Use weather data according to station and date "
        "to predict rainfall using the CatBoost model. "
        "For future prediction, previous rainfall data "
        "is used for lag and rolling features."
    )

    # ========================================================
    # [07-B] STATION DATA PREPARATION
    # --------------------------------------------------------
    # Gets station metadata and creates a human-readable label.
    #
    # The station dropdown later uses these labels.
    #
    # CHANGE HERE IF:
    # - station label format needs to change.
    # ========================================================

    meta = get_station_table(df).copy()

    meta["label"] = meta.apply(
        lambda x:
        f"{x['Station']}, "
        f"{x['District']} "
        f"({x['Division']})",
        axis=1
    )

    labels = sorted(
        meta["label"].tolist()
    )

    # ========================================================
    # [08] STATION SELECTION
    # --------------------------------------------------------
    # User selects the weather station.
    #
    # The selected label is mapped back to the full station row.
    #
    # CHANGE HERE IF:
    # - station selection UI changes
    # - station display format changes.
    # ========================================================

    selected_label = st.selectbox(
        "📍 Select Station",
        labels,
        key="prediction_station"
    )

    station = meta.loc[
        meta["label"] == selected_label
    ].iloc[0]

    # ========================================================
    # [09] DATE SELECTION
    # --------------------------------------------------------
    # Controls the target prediction date.
    #
    # The selected date determines whether the application
    # operates in:
    #   - Future mode
    #   - Today mode
    #   - Historical mode
    #
    # CHANGE HERE IF:
    # - calendar behavior changes
    # - date restrictions are needed.
    # ========================================================

    today = date.today()

    # ========================================================
    # [09-A] STREAMLIT CALENDAR STATE
    # --------------------------------------------------------
    # Keeps the selected calendar date synchronized with
    # session state.
    #
    # This prevents date-change issues during Streamlit
    # reruns.
    # ========================================================

    if "prediction_date" not in st.session_state:
        st.session_state.prediction_date = today

    selected_date = st.date_input(
        "📅 Prediction Date",
        value=st.session_state.prediction_date,
        key="calendar_date",
        format="YYYY/MM/DD",
        on_change=lambda: st.session_state.update(
            prediction_date=st.session_state.calendar_date
        )
    )

    # Always update target after calendar change
    st.session_state.prediction_date = selected_date

    target = pd.Timestamp(
        selected_date
    ).normalize()

    # ========================================================
    # [10] PAST / TODAY / FUTURE MODE
    # --------------------------------------------------------
    # Determines how the selected date should be treated.
    #
    # Future:
    #   Forecast weather source.
    #
    # Today:
    #   Today's/archive weather source.
    #
    # Past:
    #   Historical/archive weather source.
    #
    # CHANGE HERE IF:
    # - mode behavior changes
    # - user-facing mode messages change.
    # ========================================================

    is_future = selected_date > today

    is_today = selected_date == today

    is_past = selected_date < today

    if is_future:

        st.info(
            "🔮 Future Forecast Mode: "
            "Forecast weather data will be used "
            "for rainfall prediction. Previous rainfall "
            "data will be used for lag and rolling features."
        )

    elif is_today:

        st.info(
            "📅 Today Mode: "
            "Today's weather data will use the "
            "historical/archive weather source."
        )

    elif is_past:

        st.info(
            "📚 Historical Mode: "
            "Historical/archive weather data will be used "
            "for the selected date."
        )

    # ========================================================
    # [11] SESSION KEY
    # --------------------------------------------------------
    # Creates a unique identifier using:
    #
    #   Station_ID + target date
    #
    # Used to detect when the user changes station/date.
    #
    # When station/date changes, old weather/prediction state
    # is cleared.
    #
    # IMPORTANT:
    # This prevents displaying an old prediction for a new
    # station or date.
    # ========================================================

    weather_key = (
        f"{station['Station_ID']}_"
        f"{target.strftime('%Y%m%d')}"
    )

    # Clear cached weather/result whenever station or date changes
    if (
        st.session_state.get("last_calendar_key")
        != weather_key
    ):
        st.session_state.last_calendar_key = weather_key

        if "weather_data_key" in st.session_state:
            del st.session_state.weather_data_key

        if "weather_values" in st.session_state:
            del st.session_state.weather_values

        if "rain_prediction" in st.session_state:
            del st.session_state.rain_prediction

    # ========================================================
    # [11-A] CLEAR OLD PREDICTION RESULT
    # --------------------------------------------------------
    # Additional protection against showing an old prediction
    # after station/date changes.
    # ========================================================

    if "last_prediction_key" in st.session_state:

        if (
            st.session_state.last_prediction_key
            != weather_key
        ):

            if "rain_prediction" in st.session_state:

                del st.session_state[
                    "rain_prediction"
                ]

    # ========================================================
    # [12] WEATHER LOAD BUTTON
    # --------------------------------------------------------
    # Provides a manual button for reloading target weather.
    #
    # The actual loading logic is below in AUTO FETCH.
    # ========================================================

    col1, col2 = st.columns([1, 3])

    with col1:

        refresh_weather = st.button(
            "🔄 Load Weather Data",
            width="stretch",
            key="refresh_prediction_weather"
        )

    # ========================================================
    # [12-A] AUTO WEATHER FETCH
    # --------------------------------------------------------
    # Weather is loaded automatically when:
    #
    #   - user clicks Load Weather Data
    # OR
    #   - weather has not been loaded yet
    # OR
    #   - station/date has changed
    #
    # If API loading fails:
    #   weather_values = None
    #
    # Later the code falls back to station CSV median values.
    #
    # CHANGE HERE IF:
    # - API loading behavior changes
    # - automatic refresh behavior changes.
    # ========================================================

    if (
        refresh_weather
        or
        "weather_data_key" not in st.session_state
        or
        st.session_state.weather_data_key
        != weather_key
    ):

        with st.spinner(
            "Loading station weather data..."
        ):

            weather_data, error = (
                load_weather_values(
                    station=station,
                    target=target
                )
            )

            if error:

                st.warning(
                    "⚠️ Real weather data could not be loaded. "
                    "CSV median values are being used."
                )

                st.session_state.weather_values = None

                st.session_state.weather_error = error

            else:

                st.session_state.weather_values = (
                    weather_data
                )

                st.session_state.weather_error = None

            st.session_state.weather_data_key = (
                weather_key
            )

    # ========================================================
    # [12-B] BASE CSV MEDIAN
    # --------------------------------------------------------
    # Calculates median numeric values for the selected station
    # from the loaded dataframe.
    #
    # This is the fallback weather source when API data is
    # unavailable.
    #
    # CHANGE HERE IF:
    # - fallback strategy changes.
    # ========================================================

    station_df = df[
        df["Station_ID"] == station["Station_ID"]
    ].copy()

    base = (
        station_df
        .median(numeric_only=True)
        .to_dict()
    )

    # ========================================================
    # [12-C] SELECT WEATHER SOURCE
    # --------------------------------------------------------
    # Priority:
    #
    # 1. API / forecast weather values
    # 2. CSV station median values
    #
    # This section decides which source is sent to the
    # weather input form.
    # ========================================================

    api_values = st.session_state.get(
        "weather_values",
        None
    )

    if api_values is None:

        values_source = base

        st.info(
            "ℹ️ Default CSV values are being displayed. "
            "You can edit them if needed."
        )

    else:

        values_source = api_values

        if is_future:

            st.success(
                f"🔮 Forecast Weather Loaded: "
                f"{target.strftime('%Y-%m-%d')}"
            )

        elif is_today:

            st.success(
                f"✅ Today's Weather Data Loaded: "
                f"{target.strftime('%Y-%m-%d')}"
            )

        else:

            st.success(
                f"📚 Historical Weather Data Loaded: "
                f"{target.strftime('%Y-%m-%d')}"
            )

    # ========================================================
    # [13] WEATHER INPUT FORM
    # --------------------------------------------------------
    # User-visible weather input section.
    #
    # Values are initially populated from:
    #   API data OR CSV median fallback.
    #
    # User can manually edit the values before prediction.
    #
    # IF ADDING A NEW WEATHER INPUT:
    #
    # 1. Add the input here.
    # 2. Add it to the 'values' dictionary below.
    # 3. Make sure create_prediction_features() supports it.
    # 4. Make sure the model was trained with the corresponding
    #    feature if it is intended to be a model feature.
    #
    # IMPORTANT:
    # Simply adding a UI field does NOT automatically make the
    # ML model use that field.
    # ========================================================

    with st.form(
        "prediction_weather_form"
    ):

        st.subheader(
            "🌦️ Weather Information"
        )

        st.caption(
            "Weather values have been loaded automatically. "
            "You can edit any value if needed."
        )

        # ====================================================
        # [13-A] WEATHER INPUT ROW 1
        # ====================================================

        c1, c2, c3, c4 = st.columns(4)

        mean_temp = c1.number_input(
            "Mean Temperature °C",
            value=safe_float(
                values_source.get(
                    "temperature_2m_mean"
                ),
                25
            )
        )

        max_temp = c2.number_input(
            "Max Temperature °C",
            value=safe_float(
                values_source.get(
                    "temperature_2m_max"
                ),
                30
            )
        )

        min_temp = c3.number_input(
            "Min Temperature °C",
            value=safe_float(
                values_source.get(
                    "temperature_2m_min"
                ),
                20
            )
        )

        apparent_temp = c4.number_input(
            "Apparent Temperature °C",
            value=safe_float(
                values_source.get(
                    "apparent_temperature_mean"
                ),
                25
            )
        )

        # ====================================================
        # [13-B] WEATHER INPUT ROW 2
        # ====================================================

        c1, c2, c3, c4 = st.columns(4)

        sunshine = c1.number_input(
            "Sunshine Duration",
            value=safe_float(
                values_source.get(
                    "sunshine_duration"
                )
            )
        )

        daylight = c2.number_input(
            "Daylight Duration",
            value=safe_float(
                values_source.get(
                    "daylight_duration"
                )
            )
        )

        wind_speed = c3.number_input(
            "Wind Speed",
            value=safe_float(
                values_source.get(
                    "wind_speed_10m_max"
                )
            )
        )

        wind_gusts = c4.number_input(
            "Wind Gusts",
            value=safe_float(
                values_source.get(
                    "wind_gusts_10m_max"
                )
            )
        )

        # ====================================================
        # [13-C] WEATHER INPUT ROW 3
        # ====================================================

        c1, c2, c3, c4 = st.columns(4)

        wind_direction = c1.number_input(
            "Wind Direction",
            value=safe_float(
                values_source.get(
                    "wind_direction_10m_dominant"
                )
            )
        )

        radiation = c2.number_input(
            "Shortwave Radiation",
            value=safe_float(
                values_source.get(
                    "shortwave_radiation_sum"
                )
            )
        )

        weather_code = c3.number_input(
            "Weather Code",
            value=int(
                safe_float(
                    values_source.get(
                        "weather_code"
                    )
                )
            ),
            step=1
        )

        et0 = c4.number_input(
            "ET0",
            value=safe_float(
                values_source.get(
                    "et0_fao_evapotranspiration"
                )
            )
        )

        # ====================================================
        # [13-D] PREDICTION SUBMIT BUTTON
        # ----------------------------------------------------
        # The form only sends the user's values into the
        # prediction pipeline when this button is clicked.
        # ====================================================

        submitted = st.form_submit_button(
            "🌧️ Predict Rainfall",
            type="primary",
            width="stretch"
        )

    # ========================================================
    # [14] PREDICTION EXECUTION
    # --------------------------------------------------------
    # Everything inside this block runs after the user clicks
    # "Predict Rainfall".
    #
    # Main flow:
    #
    # Weather values
    #      ↓
    # Historical data
    #      ↓
    # Future validation
    #      ↓
    # Feature engineering
    #      ↓
    # Validation
    #      ↓
    # CatBoost prediction
    #      ↓
    # Condition
    #      ↓
    # Probability
    #      ↓
    # Session state
    # ========================================================

    if submitted:

        try:

            # =================================================
            # [14-A] COLLECT FINAL WEATHER VALUES
            # -------------------------------------------------
            # Converts the form values into the dictionary
            # used by create_prediction_features().
            #
            # CHANGE HERE IF:
            # - weather input names change
            # - a new model input is added.
            # =================================================

            values = {

                "Latitude":
                float(
                    station["Latitude"]
                ),

                "Longitude":
                float(
                    station["Longitude"]
                ),

                "temperature_2m_mean":
                mean_temp,

                "temperature_2m_max":
                max_temp,

                "temperature_2m_min":
                min_temp,

                "apparent_temperature_mean":
                apparent_temp,

                "sunshine_duration":
                sunshine,

                "daylight_duration":
                daylight,

                "wind_speed_10m_max":
                wind_speed,

                "wind_gusts_10m_max":
                wind_gusts,

                "wind_direction_10m_dominant":
                wind_direction,

                "shortwave_radiation_sum":
                radiation,

                "weather_code":
                int(weather_code),

                "et0_fao_evapotranspiration":
                et0
            }

            # =================================================
            # [14-B] HISTORICAL RAINFALL PREPARATION
            # -------------------------------------------------
            # Builds the historical rainfall dataset required
            # for lag and rolling feature generation.
            #
            # Function:
            #     build_on_demand_history()
            #
            # CHANGE HERE IF:
            # - history length
            # - historical data preparation
            # needs to change.
            # =================================================

            with st.spinner(
                "Preparing historical rainfall data..."
            ):

                pred_hist, bridge_note = (
                    build_on_demand_history(
                        df=df,
                        station=station,
                        target_date=target,
                        history_days=history_days
                    )
                )

            # =================================================
            # [14-C] FUTURE-DATE VALIDATION
            # -------------------------------------------------
            # For future prediction, verifies that previous
            # day's rainfall is available.
            #
            # This matters because future prediction depends on
            # historical lag/rolling rainfall information.
            #
            # CHANGE HERE IF:
            # - future-date validation rules change.
            # =================================================

            if is_future:

                target_previous_day = (
                    target - pd.Timedelta(days=1)
                )

                previous_day = pred_hist[
                    (
                        pd.to_datetime(
                            pred_hist["Date"]
                        ).dt.normalize()
                        == target_previous_day
                    )
                    &
                    (
                        pred_hist["Station_ID"]
                        == station["Station_ID"]
                    )
                ]

                if previous_day.empty:

                    raise ValueError(
                        "Previous day's rainfall data "
                        "could not be prepared for "
                        "future prediction."
                    )

                previous_rain = pd.to_numeric(
                    previous_day.iloc[0][
                        "rain_sum"
                    ],
                    errors="coerce"
                )

                if pd.isna(previous_rain):

                    raise ValueError(
                        "Previous day's rainfall value "
                        "is missing."
                    )

            # =================================================
            # [15] FEATURE CREATION
            # -------------------------------------------------
            # Converts historical data + target weather into
            # the final model-ready feature matrix.
            #
            # MAIN FUNCTION:
            #     create_prediction_features()
            #
            # This is the main bridge between raw weather/history
            # and the CatBoost model.
            # =================================================

            with st.spinner(
                "Creating rolling and lag features..."
            ):

                X = create_prediction_features(
                    historical_df=pred_hist,
                    station_id=station["Station_ID"],
                    target_date=target,
                    weather_values=values,
                    feature_columns=feature_columns,
                    train_medians=train_medians
                )

            # =================================================
            # [16] MODEL INPUT VALIDATION
            # -------------------------------------------------
            # Performs safety checks before sending X to model.
            #
            # Checks:
            #   1. X is not empty
            #   2. Feature count matches model
            #   3. No NaN values remain
            #
            # CHANGE HERE IF:
            # - additional model-input validation is needed.
            # =================================================

            if X.empty:

                raise ValueError(
                    "Prediction features are empty."
                )

            if len(X.columns) != len(feature_columns):

                raise ValueError(
                    "Feature column count does not "
                    "match model."
                )

            nan_count = int(
                X.isna().sum().sum()
            )

            if nan_count > 0:

                raise ValueError(
                    f"Prediction features contain "
                    f"{nan_count} NaN values."
                )

            # =================================================
            # [17] CATBOOST MODEL PREDICTION
            # -------------------------------------------------
            # Sends the final feature matrix to the trained model.
            #
            # model.predict(X)
            #
            # IMPORTANT:
            # The model object is passed into show_prediction().
            # This file does not train the model.
            #
            # CHANGE MODEL:
            # The model loading/injection code is outside this
            # function. This section only performs prediction.
            # =================================================

            with st.spinner(
                "CatBoost model is predicting..."
            ):

                prediction_array = np.asarray(
                    model.predict(X)
                ).reshape(-1)

            if len(prediction_array) == 0:

                raise ValueError(
                    "Model returned no prediction."
                )

            # Prevent negative rainfall prediction.
            pred = max(
                float(prediction_array[0]),
                0.0
            )

            # =================================================
            # [17-A] WEATHER CONDITION
            # -------------------------------------------------
            # Converts prediction into a readable weather
            # condition/message.
            # =================================================

            weather_name, message = condition(
                code=int(weather_code),
                pred=pred
            )

            # =================================================
            # [17-B] ESTIMATED RAINFALL PROBABILITY
            # -------------------------------------------------
            # Converts predicted rainfall amount into the UI
            # rainfall-likelihood percentage.
            #
            # IMPORTANT:
            # This is an estimated UI score, not a calibrated
            # regression probability.
            # =================================================

            rain_probability = (
                estimate_rain_probability(pred)
            )

            # =================================================
            # [18] SAVE PREDICTION RESULT
            # -------------------------------------------------
            # Stores all prediction-related information in
            # Streamlit session_state.
            #
            # Why?
            # Streamlit reruns the script frequently. Session
            # state allows the result to remain available after
            # the prediction button interaction.
            #
            # CHANGE HERE IF:
            # - additional result information needs to be stored.
            # =================================================

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
                float(et0),

                "history_note":
                bridge_note,

                "is_future":
                is_future
            }

            # Stores the station/date combination associated
            # with the current prediction.
            st.session_state.last_prediction_key = (
                weather_key
            )

        except Exception as e:

            # =================================================
            # [18-A] PREDICTION ERROR HANDLING
            # -------------------------------------------------
            # Any unexpected error during prediction is shown
            # to the developer/user instead of silently failing.
            #
            # CHANGE HERE IF:
            # - production error display needs to be customized.
            # =================================================

            st.error(
                "❌ Prediction Failed"
            )

            st.exception(e)

    # ========================================================
    # [19] RESULT DISPLAY
    # --------------------------------------------------------
    # This section displays the previously stored prediction.
    #
    # It only displays the result if:
    #
    #   - a prediction exists
    #   - prediction station == current station
    #   - prediction date == current date
    #
    # This prevents stale results from appearing for a different
    # station/date.
    # ========================================================

    if "rain_prediction" in st.session_state:

        result = (
            st.session_state.rain_prediction
        )

        same_station = (
            result["station"]["Station_ID"]
            == station["Station_ID"]
        )

        same_date = (
            pd.Timestamp(
                result["date"]
            ).normalize()
            == target
        )

        if same_station and same_date:

            pred = result["prediction"]

            st.divider()

            # =================================================
            # [19-A] RAIN PROBABILITY SECTION
            # -------------------------------------------------
            # Displays rainfall probability before the main
            # prediction metrics.
            #
            # CHANGE HERE IF:
            # - probability section placement changes.
            # =================================================

            probability = float(
                result.get(
                    "rain_probability",
                    estimate_rain_probability(
                        pred
                    )
                )
            )

            st.markdown(
                "### 🌧️ Rainfall Probability"
            )

            # =================================================
            # [20] RAIN PROBABILITY SPEEDOMETER
            # -------------------------------------------------
            # Creates the Plotly semicircular rainfall
            # probability gauge.
            #
            # COMPONENTS:
            #   1. Colored probability segments
            #   2. White inner face
            #   3. Needle
            #   4. Center knob
            #   5. Percentage text
            #   6. RAIN PROBABILITY label
            #
            # CHANGE ONLY THE GAUGE DESIGN HERE IF:
            # - colors change
            # - size changes
            # - needle design changes
            # - labels change
            #
            # This section does NOT calculate the model prediction.
            # It only visualizes the already-calculated probability.
            # =================================================

            theta = np.linspace(0, 180, 120)

            # =================================================
            # [20-A] GAUGE MATHEMATICS / FIGURE
            # =================================================

            import math

            fig = go.Figure()

            # Donut style semicircle using scatter filled shapes
            center_x = 0
            center_y = 0

            outer_r = 1.0
            inner_r = 0.78

            # =================================================
            # [20-B] GAUGE COLOR SEGMENTS
            # -------------------------------------------------
            # Current ranges:
            #
            # 0–25
            # 25–50
            # 50–75
            # 75–100
            #
            # CHANGE HERE IF:
            # - gauge color ranges need to change.
            # =================================================

            segments = [
                (0, 25, "#22C55E"),
                (25, 50, "#FACC15"),
                (50, 75, "#FB923C"),
                (75, 100, "#EF4444")
            ]

            for low, high, color in segments:

                a1 = math.pi - math.pi * high / 100
                a2 = math.pi - math.pi * low / 100

                angles = np.linspace(a1, a2, 120)

                x_outer = outer_r * np.cos(angles)
                y_outer = outer_r * np.sin(angles)

                x_inner = inner_r * np.cos(angles[::-1])
                y_inner = inner_r * np.sin(angles[::-1])

                x = np.concatenate([x_outer, x_inner])
                y = np.concatenate([y_outer, y_inner])

                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=y,
                        fill="toself",
                        mode="lines",
                        line=dict(
                            width=0
                        ),
                        fillcolor=color,
                        hoverinfo="skip",
                        showlegend=False
                    )
                )

            # =================================================
            # [20-C] GAUGE INNER FACE
            # =================================================

            face_angles = np.linspace(math.pi, 0, 200)

            fig.add_trace(
                go.Scatter(
                    x=inner_r*np.cos(face_angles),
                    y=inner_r*np.sin(face_angles),
                    fill="toself",
                    mode="lines",
                    line=dict(width=0),
                    fillcolor="#FFFFFF",
                    hoverinfo="skip",
                    showlegend=False
                )
            )

            # =================================================
            # [20-D] GAUGE NEEDLE
            # -------------------------------------------------
            # Needle position is calculated from the already
            # calculated probability value.
            #
            # IMPORTANT:
            # Changing this does NOT change probability itself.
            # It only changes how the probability is displayed.
            # =================================================

            needle_angle = math.pi - math.pi * probability / 100

            fig.add_trace(
                go.Scatter(
                    x=[
                        0,
                        0.68*math.cos(needle_angle)
                    ],
                    y=[
                        0,
                        0.68*math.sin(needle_angle)
                    ],
                    mode="lines",
                    line=dict(
                        color="#F97316",
                        width=6
                    ),
                    hoverinfo="skip",
                    showlegend=False
                )
            )

            # =================================================
            # [20-E] GAUGE CENTER KNOB
            # =================================================

            fig.add_trace(
                go.Scatter(
                    x=[0],
                    y=[0],
                    mode="markers",
                    marker=dict(
                        size=18,
                        color="#F97316",
                        line=dict(
                            color="white",
                            width=3
                        )
                    ),
                    hoverinfo="skip",
                    showlegend=False
                )
            )

            # =================================================
            # [20-F] GAUGE TEXT
            # =================================================

            fig.add_annotation(
                x=0,
                y=0.25,
                text=f"<b>{probability:.1f}%</b>",
                showarrow=False,
                font=dict(
                    size=38,
                    color="#0F172A"
                )
            )

            fig.add_annotation(
                x=0,
                y=-0.05,
                text="RAIN PROBABILITY",
                showarrow=False,
                font=dict(
                    size=12,
                    color="#64748B"
                )
            )

            # =================================================
            # [20-G] GAUGE LAYOUT
            # -------------------------------------------------
            # Controls size, margins, axes and interaction.
            #
            # CHANGE HERE IF:
            # - gauge size
            # - spacing
            # - responsiveness
            # - interaction settings
            # need to change.
            # =================================================

            fig.update_layout(
                height=330,
                autosize=True,
                margin=dict(
                    l=20,
                    r=20,
                    t=10,
                    b=10
                ),
                dragmode=False,
                hovermode=False,
                xaxis=dict(
                    visible=False,
                    fixedrange=True,
                    range=[-1.15,1.15],
                    scaleanchor="y",
                    scaleratio=1
                ),
                yaxis=dict(
                    visible=False,
                    fixedrange=True,
                    range=[-0.2,1.1]
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "scrollZoom": False,
                    "doubleClick": False,
                    "staticPlot": True,
                    "responsive": True
                }
            )

            # =================================================
            # [20-H] PROBABILITY DISCLAIMER
            # -------------------------------------------------
            # Explains what the displayed probability represents.
            # =================================================

            st.caption(
                "Probability is estimated from the predicted rainfall amount."
            )

            # =================================================
            # [19-B] PREDICTION RESULT TITLE
            # -------------------------------------------------
            # Future predictions receive a different heading.
            # Historical/today predictions use the normal heading.
            #
            # CHANGE HERE IF:
            # - result title text changes.
            # =================================================

            if result.get(
                "is_future",
                False
            ):

                st.subheader(
                    "🔮 Future Prediction Result"
                )

            else:

                st.subheader(
                    "🌧️ Prediction Result"
                )

            # =================================================
            # [19-C] MAIN RESULT METRICS
            # -------------------------------------------------
            # Displays the three main prediction outputs:
            #
            #   Predicted Rainfall
            #   Weather
            #   ET0
            #
            # CHANGE HERE IF:
            # - result cards
            # - metric labels
            # - displayed values
            # need to change.
            # =================================================

            a, b, c = st.columns(3)

            a.metric(
                "Predicted Rainfall",
                f"{pred:.2f} mm"
            )

            b.metric(
                "Weather",
                result["condition"]
            )

            c.metric(
                "ET0",
                f"{result['et0']:.2f}"
            )

            # =================================================
            # [19-D] PROBABILITY MESSAGE
            # -------------------------------------------------
            # Converts the estimated probability into a
            # user-friendly message.
            #
            # CURRENT LEVELS:
            #
            # <20    -> Low
            # <50    -> Moderate
            # <75    -> High
            # >=75   -> Very High
            #
            # CHANGE HERE IF:
            # - probability message thresholds change
            # - wording changes.
            # =================================================

            if probability < 20:

                st.info(
                    "☀️ Low rainfall likelihood."
                )

            elif probability < 50:

                st.info(
                    "🌤️ Moderate rainfall likelihood."
                )

            elif probability < 75:

                st.warning(
                    "🌧️ High rainfall likelihood."
                )

            else:

                st.success(
                    "⛈️ Very high rainfall likelihood."
                )

            # =================================================
            # [19-E] GENERAL WEATHER MESSAGE
            # -------------------------------------------------
            # Displays the message generated by condition().
            #
            # If rainfall amount was used for condition(),
            # this message corresponds to the prediction category.
            # =================================================

            st.info(
                result["message"]
            )

            # =================================================
            # [19-F] HISTORY NOTE
            # -------------------------------------------------
            # Shows information returned from
            # build_on_demand_history().
            # =================================================

            st.caption(
                result["history_note"]
            )

            # =================================================
            # [19-G] FUTURE PREDICTION MESSAGE
            # -------------------------------------------------
            # Shows an additional explanation for future
            # predictions.
            #
            # CHANGE HERE IF:
            # - future prediction explanation changes.
            # =================================================

            if result.get(
                "is_future",
                False
            ):

                st.success(
                    "🔮 Future prediction completed. "
                    "Previous rainfall data was used "
                    "for rain lag and rolling rainfall "
                    "features when available."
                )

            else:

                st.success(
                    "🌱 This prediction can be used "
                    "on the Agriculture page."
                )


# ============================================================
#                  END OF FILE
# ============================================================
#
# QUICK DEVELOPER REFERENCE
# ------------------------------------------------------------
#
# If you need to change...
#
# Weather category
#       -> [02]
#
# Probability formula
#       -> [03]
#
# Number safety/fallback
#       -> [04]
#
# ML feature engineering
#       -> [05]
#
# Rain lags
#       -> [05-E]
#
# Rain occurrence
#       -> [05-F]
#
# Rolling rainfall
#       -> [05-G]
#
# Weather lags
#       -> [05-H]
#
# Station encoding
#       -> [05-I]
#
# Missing-value strategy
#       -> [05-N]
#
# Weather API
#       -> [06]
#
# Station dropdown
#       -> [08]
#
# Date picker
#       -> [09]
#
# Future/Past/Today logic
#       -> [10]
#
# Session/reset behavior
#       -> [11]
#
# API/CSV fallback
#       -> [12]
#
# Weather form
#       -> [13]
#
# Historical rainfall preparation
#       -> [14-B]
#
# Future data validation
#       -> [14-C]
#
# Model feature preparation
#       -> [15]
#
# Feature validation
#       -> [16]
#
# CatBoost prediction
#       -> [17]
#
# Prediction result storage
#       -> [18]
#
# Result UI
#       -> [19]
#
# Probability gauge
#       -> [20]
#
# Gauge colors
#       -> [20-B]
#
# Gauge needle
#       -> [20-D]
#
# Gauge size/layout
#       -> [20-G]
#
# ============================================================