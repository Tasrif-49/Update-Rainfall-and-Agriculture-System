
# DATA_LOADER.PY — QUICK DEVELOPER INDEX
#
# [01] IMPORTS
#      → Streamlit, Pandas, Pickle এবং project settings
#
# [02] LOAD MODEL
#      → Config অনুযায়ী প্রথম পাওয়া PKL model load
#      → Streamlit resource cache ব্যবহার
#
# [03] LOAD DATASET
#      → Config অনুযায়ী প্রথম পাওয়া CSV load
#      → Streamlit data cache ব্যবহার
#
# [04] VALIDATE DATASET
#      → Required columns আছে কি না check
#
# [05] PREPARE DATASET
#      → Date conversion
#      → Invalid date remove
#      → Date normalize
#      → Station + Date অনুযায়ী sort
#      → Missing Station/District/Division fallback
#
# [06] GET STATION TABLE
#      → প্রতিটি Station_ID-এর metadata তৈরি
#      → Station, District, Division
#      → Latitude, Longitude
#
# [07] GET MODEL HISTORY DAYS
#      → Model feature দেখে কত দিনের historical data দরকার
#        তা automatically detect
#      → Rain lag
#      → Rolling window
#      → Weather lag
#

# QUICK CHANGE GUIDE

#
# Model filename / location     → config.settings
# CSV filename / location       → config.settings
# Required columns              → config.settings
# Date processing               → [05]
# Missing location metadata     → [05]
# Station information           → [06]
# Historical days requirement   → [07]
# Rain lag detection            → [07]
# Rolling feature detection     → [07]
# Weather lag detection         → [07]
#
# IMPORTANT:
# This file mainly handles:
#
#       MODEL + DATASET
#              ↓
#       VALIDATION
#              ↓
#       PREPARATION
#              ↓
#       STATION METADATA
#              ↓
#       MODEL HISTORY REQUIREMENT
#




# [01] IMPORTS


# Streamlit cache এবং application integration-এর জন্য।
import streamlit as st

# CSV dataset processing-এর জন্য।
import pandas as pd

# PKL model/package load করার জন্য।
import pickle

# Project-এর centralized configuration।
from config.settings import (
    MODEL_DIR,
    DATA_DIR,
    MODEL_FILES,
    CSV_FILES,
    REQUIRED_COLUMNS
)



# [02] LOAD MODEL

# Config-এর MODEL_FILES list থেকে প্রথম available PKL model
# খুঁজে load করে।
@st.cache_resource
def load_model():

    # Config-এ থাকা প্রতিটি possible model filename check।
    for filename in MODEL_FILES:

        # Full model file path তৈরি।
        file_path = MODEL_DIR / filename

        # Model file exist করলে।
        if file_path.exists():

            # PKL file binary mode-এ open।
            with open(file_path, "rb") as f:

                # Saved model/package load।
                package = pickle.load(f)

            # Model package এবং actual filename return।
            return package, filename

    # কোনো model পাওয়া না গেলে clear error।
    raise FileNotFoundError(
        f"""
        Model file not found.

        Put your PKL file inside:

        {MODEL_DIR}
        """
    )



# [03] LOAD DATASET

# Config-এর CSV_FILES list থেকে প্রথম available CSV
# খুঁজে dataset load করে।
@st.cache_data
def load_dataset():

    # Config-এ থাকা possible CSV filename check।
    for filename in CSV_FILES:

        # Full CSV path তৈরি।
        file_path = DATA_DIR / filename

        # CSV file exist করলে।
        if file_path.exists():

            # CSV dataset Pandas DataFrame হিসেবে load।
            df = pd.read_csv(file_path)

            # DataFrame এবং actual filename return।
            return df, filename

    # কোনো CSV পাওয়া না গেলে clear error।
    raise FileNotFoundError(
        f"""
        CSV file not found.

        Put your CSV file inside:

        {DATA_DIR}
        """
    )



# [04] VALIDATE DATASET

# Dataset model/application-এর জন্য প্রয়োজনীয় সব column
# ধারণ করে কি না check করে।
def validate_dataset(df):

    # Required columns-এর মধ্যে যেগুলো dataset-এ নেই
    # সেগুলো identify করা।
    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    # কোনো required column missing থাকলে।
    if missing:

        # Missing column list সহ error।
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    # সব required column পাওয়া গেলে True return।
    return True



# [05] PREPARE DATASET

# Raw dataset-কে application ব্যবহারের উপযোগী format-এ
# prepare করে।
def prepare_dataset(df):

    # Original DataFrame modify না করে copy।
    df = df.copy()


    # [05-A] DATE CONVERSION
  
    # Date column-কে Pandas datetime format-এ convert।
    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )


    
    # [05-B] REMOVE INVALID DATES
   
    # যেসব row-এর Date valid হয়নি সেগুলো remove।
    df = df.dropna(
        subset=["Date"]
    ).copy()


  
    # [05-C] REMOVE TIME COMPONENT
    
    # Date-এর সাথে থাকা time অংশ বাদ দিয়ে শুধু date রাখা।
    df["Date"] = (
        df["Date"]
        .dt.normalize()
    )


    
    # [05-D] SORT DATASET
   
    # Station এবং Date অনুযায়ী chronological ordering।
    df = (
        df
        .sort_values(
            [
                "Station_ID",
                "Date"
            ]
        )
        .reset_index(
            drop=True
        )
    )


    
    # [05-E] OPTIONAL COLUMNS
    
    # Station/District/Division না থাকলে Station_ID-কে
    # fallback value হিসেবে ব্যবহার করা।
    for column in [
        "Station",
        "District",
        "Division"
    ]:

        # Column missing হলে fallback তৈরি।
        if column not in df.columns:

            # Station_ID string হিসেবে ব্যবহার।
            df[column] = (
                df["Station_ID"]
                .astype(str)
            )

    # Prepared dataset return।
    return df



# [06] GET STATION TABLE

# Main weather dataset থেকে প্রতিটি station-এর একক metadata
# table তৈরি করে।
def get_station_table(df):

    # Station_ID অনুযায়ী group করে station metadata তৈরি।
    meta = (
        df
        .groupby(
            "Station_ID",
            as_index=False
        )
        .agg(

            # Station name-এর প্রথম পাওয়া value।
            Station=(
                "Station",
                "first"
            ),

            # District-এর প্রথম পাওয়া value।
            District=(
                "District",
                "first"
            ),

            # Division-এর প্রথম পাওয়া value।
            Division=(
                "Division",
                "first"
            ),

            # Latitude-এর median value।
            Latitude=(
                "Latitude",
                "median"
            ),

            # Longitude-এর median value।
            Longitude=(
                "Longitude",
                "median"
            )
        )
    )

    # Station metadata table return।
    return meta



# [07] GET MODEL HISTORY DAYS

# Model-এর feature_columns দেখে automatically determine করে
# prediction-এর আগে কত দিনের historical data প্রয়োজন।
def get_model_history_days(
    feature_columns
):

    # Regular expression module locally import।
    import re


 
    # [07-A] FEATURE CATEGORY STORAGE

    # Rainfall lag values এখানে রাখা হবে।
    rain_lags = []

    # Rolling window values এখানে রাখা হবে।
    roll_windows = []

    # Weather lag values এখানে রাখা হবে।
    weather_lags = []


  
    # [07-B] CHECK ALL MODEL FEATURES

    # Model-এর প্রতিটি feature inspect করা।
    for col in feature_columns:


        
        # [07-B1] RAIN LAG
 
        # Expected pattern:
        # rain_lag_1
        # rain_lag_7
        # rain_lag_30
        m = re.fullmatch(
            r"rain_lag_(\d+)",
            col
        )

        # Rain lag match হলে।
        if m:

            # Lag number integer হিসেবে save।
            rain_lags.append(
                int(m.group(1))
            )

            # এই feature-এর জন্য পরের checks দরকার নেই।
            continue


     
        # [07-B2] ROLLING WINDOW
    
        # Expected pattern:
        # rain_roll_mean_7
        # rain_roll_sum_14
        # rain_roll_std_30
        m = re.fullmatch(
            r"rain_roll_(?:mean|sum|std)_(\d+)",
            col
        )

        # Rolling feature match হলে।
        if m:

            # Window size integer হিসেবে save।
            roll_windows.append(
                int(m.group(1))
            )

            # পরের feature-এ যাওয়া।
            continue


        
        # [07-B3] WEATHER LAG
   
        # General pattern:
        # temperature_2m_mean_lag_1
        # wind_speed_lag_7
        # ইত্যাদি।
        m = re.fullmatch(
            r"(.+)_lag_(\d+)",
            col
        )

        # Weather lag match হলে এবং rain feature না হলে।
        if (
            m
            and not col.startswith("rain_")
        ):

            # Weather lag number save।
            weather_lags.append(
                int(m.group(2))
            )


  
    # [07-C] FINAL HISTORY DAYS
   
    # Model-এর সবচেয়ে বড় lag/window বের করা।
    #
    # [1] Rain lag
    # [2] Rolling window
    # [3] Weather lag
    # [4] Minimum fallback = 1 day
    #
    # সবচেয়ে বড় value-টাই required history length।
    return max(
        rain_lags
        +
        roll_windows
        +
        weather_lags
        +
        [1]
    )