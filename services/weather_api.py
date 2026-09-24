
# WEATHER API & ON-DEMAND HISTORY MODULE

#
# MAIN PURPOSE:
#
# This module handles weather data retrieval from Open-Meteo
# and prepares the historical weather data required by the
# rainfall prediction model.
#

#
# OVERALL DATA FLOW

#
#                         ┌──────────────────────┐
#                         │   Weather API        │
#                         │    Open-Meteo        │
#                         └──────────┬───────────┘
#                                    │
#                     ┌──────────────┴──────────────┐
#                     │                             │
#                  Archive                       Forecast
#                  API                           API
#                     │                             │
#                     └──────────────┬──────────────┘
#                                    │
#                                    ↓
#                         On-Demand History
#                                    ↑
#                                    │
#                              Local CSV
#                                    │
#                         CSV has priority
#
#
# MAIN FUNCTIONS
#
# [01] Imports
#
# [02] Open-Meteo Forecast URL
#
# [03] Daily Weather Variables
#
# [04] Common Open-Meteo Request
#      → _fetch_open_meteo()
#
# [05] Archive API
#      → fetch_open_meteo_range()
#
# [06] Forecast API
#      → fetch_open_meteo_forecast_range()
#
# [07] Single-Date Weather
#      → fetch_target_weather()
#
# [08] Prepare Local History
#      → prepare_local_history()
#
# [09] Add Station Information
#      → _add_station_info()
#
# [10] Fetch Missing Past History
#      → _fetch_missing_history()
#
# [11] Fetch Missing Recent/Today Data
#      → _fetch_missing_recent_history()
#
# [12] Build On-Demand History
#      → build_on_demand_history()
#

#
# IMPORTANT LOGIC

#
# 1. Local CSV is checked first.
#
# 2. Missing dates before today are requested from the
#    Open-Meteo Archive API.
#
# 3. Missing today/recent dates use the Forecast API as a
#    fallback.
#
# 4. Local CSV data has priority over API data.
#
# 5. Duplicate Station_ID + Date records are removed while
#    keeping the first record.
#
# 6. The model history must be complete.
#
# 7. Missing rainfall values cause prediction preparation
#    to stop with an error.
#
# 8. Future prediction additionally requires previous-day
#    rainfall because it is used as rain_lag_1.
#

#
# QUICK CHANGE GUIDE

#
# Change Forecast API URL
#     → [02]
#
# Change requested weather variables
#     → [03]
#
# Change API timeout
#     → [04]
#
# Change archive cache duration
#     → [05]
#
# Change forecast cache duration
#     → [06]
#
# Change TODAY / FUTURE API behavior
#     → [07]
#
# Change minimum history length
#     → [12]
#
# Change CSV/API priority
#     → [12] LOCAL CSV PRIORITY
#
# Change missing-data behavior
#     → [10], [11], [12]
#




# [01] IMPORTS

#
# streamlit:
#     Used mainly for caching API results.
#
# pandas:
#     Used for date handling and dataframe operations.
#
# requests:
#     Sends HTTP requests to Open-Meteo.
#
# config.settings:
#     Provides the configured Open-Meteo Archive URL and
#     application timezone.
#


import streamlit as st
import pandas as pd
import requests

from config.settings import (
    OPEN_METEO_ARCHIVE_URL,
    TIMEZONE
)


# [02] OPEN-METEO FORECAST URL

#
# This URL is used when forecast/recent weather data is needed.
#
# Archive API URL comes from:
#
#     config.settings.OPEN_METEO_ARCHIVE_URL
#
# Forecast URL is defined locally here.
#


OPEN_METEO_FORECAST_URL = (
    "https://api.open-meteo.com/v1/forecast"
)



# [03] WEATHER VARIABLES

#
# These are the daily weather variables requested from
# Open-Meteo.
#
# They include:
#
#     rainfall
#     temperature
#     apparent temperature
#     sunshine
#     daylight
#     wind
#     solar radiation
#     weather code
#     ET0
#
# IMPORTANT:
#
# If a new API variable is added here, make sure the rest of
# the application can handle the new column.
#


DAILY_VARIABLES = [

    # Daily rainfall in millimeters.
    "rain_sum",

    # Mean daily air temperature.
    "temperature_2m_mean",

    # Maximum daily air temperature.
    "temperature_2m_max",

    # Minimum daily air temperature.
    "temperature_2m_min",

    # Mean apparent/feels-like temperature.
    "apparent_temperature_mean",

    # Total sunshine duration.
    "sunshine_duration",

    # Total daylight duration.
    "daylight_duration",

    # Maximum wind speed at 10 meters.
    "wind_speed_10m_max",

    # Maximum wind gust at 10 meters.
    "wind_gusts_10m_max",

    # Dominant wind direction at 10 meters.
    "wind_direction_10m_dominant",

    # Total shortwave radiation.
    "shortwave_radiation_sum",

    # Open-Meteo weather condition code.
    "weather_code",

    # Reference evapotranspiration.
    "et0_fao_evapotranspiration"
]



# [04] COMMON API REQUEST

#
# FUNCTION:
#     _fetch_open_meteo()
#
# PURPOSE:
#     Common internal function used by both:
#
#         Archive API
#         Forecast API
#
# Instead of duplicating request logic, both public API
# functions call this function with a different URL.
#


def _fetch_open_meteo(
    url,
    lat,
    lon,
    start_date,
    end_date
):


    # [04-A] NORMALIZE START DATE
    #
    # Converts the provided start date into a Python date.
    #

    start_date = pd.Timestamp(
        start_date
    ).date()



    # [04-B] NORMALIZE END DATE

    end_date = pd.Timestamp(
        end_date
    ).date()


   
    # [04-C] INVALID DATE RANGE CHECK

    #
    # If start date is after end date, no API request is made.
    #

    if start_date > end_date:

        return pd.DataFrame()



    # [04-D] API PARAMETERS
    #
    # latitude / longitude:
    #     Station location.
    #
    # daily:
    #     Requested daily weather variables.
    #
    # timezone:
    #     Application timezone.
    #
    # start_date / end_date:
    #     Requested period.

    params = {

        "latitude":
        float(lat),

        "longitude":
        float(lon),

        "daily":
        ",".join(
            DAILY_VARIABLES
        ),

        "timezone":
        TIMEZONE,

        "start_date":
        str(start_date),

        "end_date":
        str(end_date)
    }


  
    # [04-E] SEND API REQUEST
   
    #
    # timeout=30:
    #     The request is allowed to run for up to 30 seconds.
    #
  

    response = requests.get(
        url,
        params=params,
        timeout=30
    )


 
    # [04-F] CHECK HTTP RESPONSE
   
    #
    # If the API returns an HTTP error, raise_for_status()
    # raises an exception.
    #

    response.raise_for_status()


  
    # [04-G] CONVERT RESPONSE TO JSON
 

    data = response.json()


 
    # [04-H] GET DAILY DATA


    daily_data = data.get(
        "daily",
        {}
    )


    # [04-I] CHECK DAILY DATA

    if not daily_data:

        raise ValueError(
            "Weather API returned no daily data."
        )


 
    # [04-J] CHECK TIME COLUMN
  
    #
    # Open-Meteo daily response should contain "time".
    #
    # Without it, the dataframe cannot be constructed with
    # a valid Date column.

    if "time" not in daily_data:

        raise ValueError(
            "Weather API response has no time data."
        )


    # [04-K] CREATE DATAFRAME

    out = pd.DataFrame(
        daily_data
    )


   
    # [04-L] RENAME API TIME COLUMN
  
    #
    # Open-Meteo returns:
    #
    #     time
    #
    # Application uses:
    #
    #     Date

    out = out.rename(
        columns={
            "time":
            "Date"
        }
    )


    
    # [04-M] NORMALIZE DATE
    #
    # Removes the time component and keeps daily date values.

    out["Date"] = pd.to_datetime(
        out["Date"]
    ).dt.normalize()


    # [04-N] RETURN API DATA

    return out

# [05] ARCHIVE API
#
# FUNCTION:
#     fetch_open_meteo_range()
#
# PURPOSE:
#     Retrieves historical weather data from the configured
#     Open-Meteo Archive API.
#
# CACHE:
#     3600 seconds = 1 hour.
#
# This reduces repeated API calls for the same parameters.

@st.cache_data(
    ttl=3600,
    show_spinner=False
)
def fetch_open_meteo_range(
    lat,
    lon,
    start_date,
    end_date
):

    return _fetch_open_meteo(

        url=OPEN_METEO_ARCHIVE_URL,

        lat=lat,

        lon=lon,

        start_date=start_date,

        end_date=end_date
    )



# [06] FORECAST API
#
# FUNCTION:
#     fetch_open_meteo_forecast_range()
#
# PURPOSE:
#     Retrieves recent/future weather information from the
#     Open-Meteo Forecast API.
#
# CACHE:
#     900 seconds = 15 minutes.
#
# A shorter cache is used because recent/forecast information
# can change more frequently.

@st.cache_data(
    ttl=900,
    show_spinner=False
)
def fetch_open_meteo_forecast_range(
    lat,
    lon,
    start_date,
    end_date
):

    return _fetch_open_meteo(

        url=OPEN_METEO_FORECAST_URL,

        lat=lat,

        lon=lon,

        start_date=start_date,

        end_date=end_date
    )

# [07] SINGLE-DATE WEATHER
#
# FUNCTION:
#     fetch_target_weather()
#
# PURPOSE:
#     Fetch weather information for exactly one station and
#     one target date.
#
# API RULE:
#
#     target_date <= today
#         → Archive API
#
#     target_date > today
#         → Forecast API
#
# IMPORTANT:
#     This preserves the existing TODAY behavior where today
#     is handled by the archive branch.
#

def fetch_target_weather(
    station,
    target_date
):


    
    # [07-A] NORMALIZE TARGET DATE
   

    target_date = pd.Timestamp(
        target_date
    ).normalize()


   
    # [07-B] GET TODAY'S DATE

    today = pd.Timestamp(
        "today"
    ).normalize()


    # [07-C] GET STATION COORDINATES


    lat = float(
        station["Latitude"]
    )

    lon = float(
        station["Longitude"]
    )


    # [07-D] CHOOSE ARCHIVE OR FORECAST API
   
    #
    # TODAY AND PAST:
    #     Archive API
    #
    # FUTURE:
    #     Forecast API

    if target_date <= today:

        weather_df = fetch_open_meteo_range(

            lat=lat,

            lon=lon,

            start_date=target_date,

            end_date=target_date
        )

    else:

        weather_df = fetch_open_meteo_forecast_range(

            lat=lat,

            lon=lon,

            start_date=target_date,

            end_date=target_date
        )


   
    # [07-E] CHECK API RESULT

    if weather_df.empty:

        raise ValueError(
            "Could not fetch weather data "
            "for selected date."
        )


 
    # [07-F] KEEP EXACT TARGET DATE
    #
    # Even though only one date was requested, the API response
    # is filtered again to guarantee that the returned record
    # exactly matches the selected target date.


    weather_df = weather_df[
        weather_df["Date"]
        == target_date
    ].copy()


  
    # [07-G] CHECK EXACT DATE

    if weather_df.empty:

        raise ValueError(
            "Selected date was not returned "
            "by weather API."
        )



    # [07-H] CONVERT FIRST ROW TO DICTIONARY
 

    row = (
        weather_df
        .iloc[0]
        .to_dict()
    )


    return row



# [08] PREPARE LOCAL HISTORY

#
# FUNCTION:
#     prepare_local_history()
#
# PURPOSE:
#     Searches the local dataframe/CSV for records belonging
#     to one station and one requested date range.
#
# IMPORTANT:
#     This function does NOT call the API.
#
#     It only checks the locally available dataset.

def prepare_local_history(
    df,
    station_id,
    start_date,
    end_date
):

  
    # [08-A] COPY LOCAL DATA

    local = df.copy()



    # [08-B] NORMALIZE DATE COLUMN

    local["Date"] = pd.to_datetime(
        local["Date"]
    ).dt.normalize()


    
    # [08-C] NORMALIZE REQUESTED DATE RANGE

    start_date = pd.Timestamp(
        start_date
    ).normalize()

    end_date = pd.Timestamp(
        end_date
    ).normalize()


   
    # [08-D] FILTER STATION AND DATE RANGE

    #
    # Only records satisfying BOTH conditions are retained:
    #
    #     Station_ID == requested station
    #
    #     start_date <= Date <= end_date

    local = local[
        (
            local["Station_ID"]
            == station_id
        )
        &
        (
            local["Date"]
            >= start_date
        )
        &
        (
            local["Date"]
            <= end_date
        )
    ].copy()


    return local



# [09] ADD STATION INFORMATION
#
# FUNCTION:
#     _add_station_info()
#
# PURPOSE:
#     API data does not necessarily contain the application's
#     station metadata.
#
# This function attaches station information to API-generated
# records.
#
# Added information may include:
#
#     Station_ID
#     Latitude
#     Longitude
#     Station
#     District
#     Division

def _add_station_info(
    api_data,
    station
):

    # [09-A] EMPTY DATA CHECK

    if api_data.empty:

        return api_data


   
    # [09-B] ADD STATION ID

    api_data["Station_ID"] = (
        station["Station_ID"]
    )


  
    # [09-C] ADD COORDINATES


    api_data["Latitude"] = float(
        station["Latitude"]
    )

    api_data["Longitude"] = float(
        station["Longitude"]
    )


    
    # [09-D] ADD STATION NAME


    if "Station" in station.index:

        api_data["Station"] = (
            station["Station"]
        )


  
    # [09-E] ADD DISTRICT
   

    if "District" in station.index:

        api_data["District"] = (
            station["District"]
        )


   
    # [09-F] ADD DIVISION
  

    if "Division" in station.index:

        api_data["Division"] = (
            station["Division"]
        )


    return api_data


# [10] FETCH PAST MISSING HISTORY

#
# FUNCTION:
#     _fetch_missing_history()
#
# PURPOSE:
#     Retrieves missing historical dates from the Archive API.
#
# This function is used only for dates identified as:
#
#     date < today

def _fetch_missing_history(
    station,
    missing_dates
):



    # [10-A] NO MISSING DATES

    if not missing_dates:

        return pd.DataFrame()


   
    # [10-B] DETERMINE API REQUEST RANGE

    #
    # Instead of requesting every missing date separately,
    # the function requests one continuous date range from the
    # earliest missing date to the latest missing date.

    start_date = min(
        missing_dates
    )

    end_date = max(
        missing_dates
    )


  
    # [10-C] REQUEST ARCHIVE DATA

    #
    # Any API exception is converted into an empty dataframe.
    # This allows the main history-building process to handle
    # the missing data check later.

    try:

        api_data = fetch_open_meteo_range(

            lat=float(
                station["Latitude"]
            ),

            lon=float(
                station["Longitude"]
            ),

            start_date=start_date,

            end_date=end_date
        )

    except Exception:

        return pd.DataFrame()


    # [10-D] CHECK API DATA

    if api_data.empty:

        return pd.DataFrame()


  
    # [10-E] KEEP ONLY REQUESTED MISSING DATES

    #
    # The API request may return dates that were not actually
    # missing, so only dates in missing_dates are retained.

    api_data = api_data[
        api_data["Date"].isin(
            missing_dates
        )
    ].copy()


    if api_data.empty:

        return pd.DataFrame()


 
    # [10-F] ADD STATION INFORMATION


    return _add_station_info(
        api_data,
        station
    )


# [11] FETCH RECENT / TODAY MISSING DATA
#
# PURPOSE:
#     Provides a fallback for recent/today missing dates.
#
# IMPORTANT:
#
#     This function is ONLY a fallback.
#
#     Local CSV data has priority.
#
# The Forecast API is used here because recent data may not yet
# be available through the historical archive source.

def _fetch_missing_recent_history(
    station,
    missing_dates
):
    # [11-A] NO MISSING DATES

    if not missing_dates:

        return pd.DataFrame()

    # [11-B] DETERMINE REQUEST RANGE

    start_date = min(
        missing_dates
    )

    end_date = max(
        missing_dates
    )



    # [11-C] REQUEST FORECAST API

    try:

        api_data = (
            fetch_open_meteo_forecast_range(

                lat=float(
                    station["Latitude"]
                ),

                lon=float(
                    station["Longitude"]
                ),

                start_date=start_date,

                end_date=end_date
            )
        )

    except Exception:

        return pd.DataFrame()



    # [11-D] CHECK API DATA

    if api_data.empty:

        return pd.DataFrame()


  
    # [11-E] KEEP ONLY REQUESTED DATES


    api_data = api_data[
        api_data["Date"].isin(
            missing_dates
        )
    ].copy()


    if api_data.empty:

        return pd.DataFrame()


   
    # [11-F] ADD STATION INFORMATION

    return _add_station_info(
        api_data,
        station
    )


# [12] BUILD ON-DEMAND HISTORY

#
# FUNCTION:
#     build_on_demand_history()
#
# PURPOSE:
#     Builds the complete historical dataset required for
#     creating rainfall prediction features.
#
# INPUT:
#
#     df
#         Local weather dataset.
#
#     station
#         Selected station information.
#
#     target_date
#         Date for which rainfall prediction is being prepared.
#
#     history_days
#         Number of previous days required by the model.
#
# OUTPUT:
#
#     history
#         Complete historical weather dataframe.
#
#     note
#         Human-readable information about where the data came
#         from and how it was prepared.
#

def build_on_demand_history(
    df,
    station,
    target_date,
    history_days
):


    # [12-A] NORMALIZE TARGET DATE

    target_date = pd.Timestamp(
        target_date
    ).normalize()


   
    # [12-B] CONVERT HISTORY LENGTH TO INTEGER


    history_days = int(
        history_days
    )


    
    # [12-C] MINIMUM HISTORY REQUIREMENT
  
    #
    # The prediction system requires at least 30 previous days.
    #
    # If a smaller value is supplied, it is automatically
    # increased to 30.

    if history_days < 30:

        history_days = 30



    # [12-D] CALCULATE HISTORY RANGE
    #
    # Example:
    #
    # Target date = 2025-12-31
    # History days = 30
    #
    # The history ends on:
    #
    #     2025-12-30
    #
    # The target date itself is NOT included in history.

    start_date = (
        target_date
        - pd.Timedelta(
            days=history_days
        )
    )

    end_date = (
        target_date
        - pd.Timedelta(
            days=1
        )
    )



    # [12-E] GET STATION ID


    station_id = (
        station["Station_ID"]
    )


    # [12-F] GET TODAY


    today = pd.Timestamp(
        "today"
    ).normalize()


  
    # [12-G] READ LOCAL CSV HISTORY
    
    #
    # Local dataset is checked first.
    #
    # This is important because local historical data has
    # priority over API fallback data.
    #
    

    local = prepare_local_history(

        df=df,

        station_id=station_id,

        start_date=start_date,

        end_date=end_date
    )


    
    # [12-H] CREATE EXPECTED DATE LIST
   
    #
    # Generates every date that should exist in the history.
    #
    # This list is later compared against the actual local/API
    # records to identify missing dates.
   

    expected_dates = pd.date_range(

        start=start_date,

        end=end_date,

        freq="D"
    )


  
    # [12-I] FIND LOCAL DATES
   

    if not local.empty:

        local_dates = set(
            pd.to_datetime(
                local["Date"]
            ).dt.normalize()
        )

    else:

        local_dates = set()


    # [12-J] FIND MISSING DATES
  
    #
    # Any expected date that does not exist in the local CSV
    # becomes a missing date.

    missing_dates = [

        day

        for day in expected_dates

        if day not in local_dates
    ]


  
    # [12-K] SPLIT MISSING DATES
    #
    # Missing dates are separated into:
    #
    #     past_missing
    #         → dates before today
    #
    #     recent_missing
    #         → today or later
    #
    # Different API sources are used for these two groups.


    past_missing = [

        day

        for day in missing_dates

        if day < today
    ]


    recent_missing = [

        day

        for day in missing_dates

        if day >= today
    ]


  
    # [12-L] INITIALIZE API DATAFRAMES
 

    fetched_archive = pd.DataFrame()

    fetched_recent = pd.DataFrame()



    # [12-M] PAST MISSING DATES → ARCHIVE API
  
    #
    # Only missing historical dates are requested.
    #
    # Existing CSV records are NOT replaced.

    if past_missing:

        fetched_archive = (
            _fetch_missing_history(

                station=station,

                missing_dates=past_missing
            )
        )


    
    # [12-N] TODAY/RECENT MISSING → FORECAST FALLBACK

    # Again, only missing dates are requested.
    #
    # CSV data remains the priority.

    if recent_missing:

        fetched_recent = (
            _fetch_missing_recent_history(

                station=station,

                missing_dates=recent_missing
            )
        )


   
    # [12-O] MERGE LOCAL + API DATA
    #
    # Order is important:
    #
    #     1. local
    #     2. archive API
    #     3. recent fallback API
    #
    # Because duplicate records later keep the FIRST record,
    # local CSV data gets priority.

    history = pd.concat(

        [

            local,

            fetched_archive,

            fetched_recent

        ],

        ignore_index=True,

        sort=False
    )


    
    # [12-P] CHECK COMPLETELY EMPTY HISTORY


    if history.empty:

        raise ValueError(
            "No historical weather data available."
        )


    # [12-Q] NORMALIZE FINAL HISTORY DATES


    history["Date"] = pd.to_datetime(
        history["Date"]
    ).dt.normalize()


  
    # [12-R] LOCAL CSV PRIORITY
    #
    # Duplicate key:
    #
    #     Station_ID + Date
    #
    # keep="first" means:
    #
    #     local CSV record
    #         gets priority
    #
    # over:
    #
    #     archive API record
    #         or recent fallback API record
    #
    # because local records were concatenated first.
    #


    history = history.drop_duplicates(

        subset=[
            "Station_ID",
            "Date"
        ],

        keep="first"
    )


 
    # [12-S] SORT HISTORY
   
    #
    # Sorted by:
    #
    #     Station_ID
    #     Date
    #
    # This gives the prediction feature-building stage a
    # consistent chronological order.


    history = history.sort_values(

        [
            "Station_ID",
            "Date"
        ]

    ).reset_index(
        drop=True
    )



    # [12-T] CHECK FOR STILL-MISSING DATES
    #
    # After combining CSV and API data, the system checks again
    # whether every expected history date is present.
    #
    # If even one required date is missing, prediction history
    # is considered incomplete.


    actual_dates = set(
        history["Date"]
    )


    still_missing = [

        day.strftime(
            "%Y-%m-%d"
        )

        for day in expected_dates

        if day not in actual_dates
    ]


    if still_missing:

        raise ValueError(

            "Historical data incomplete: "
            +
            ", ".join(
                still_missing[:10]
            )
        )


  
    # [12-U] VALIDATE RAINFALL COLUMN
   
    #
    # Rainfall is essential because the prediction feature
    # pipeline uses:
    #
    #     rain_lag_1
    #     rain_lag_2
    #     ...
    #     rolling rainfall features
 

    if "rain_sum" not in history.columns:

        raise ValueError(
            "rain_sum column not found in history."
        )


  
    # [12-V] CONVERT RAINFALL TO NUMERIC

    history["rain_sum"] = pd.to_numeric(

        history["rain_sum"],

        errors="coerce"
    )



    # [12-W] CHECK MISSING RAINFALL VALUES
 
    #
    # If any rainfall value is missing, the history cannot be
    # safely used for lag and rolling rainfall features.

    if history["rain_sum"].isna().any():

        missing_rain_dates = (

            history.loc[
                history["rain_sum"].isna(),
                "Date"
            ]

            .dt.strftime(
                "%Y-%m-%d"
            )

            .tolist()
        )


        raise ValueError(

            "Historical rainfall contains "
            "missing values: "
            +
            ", ".join(
                missing_rain_dates[:10]
            )
        )



    # [12-X] DATA SOURCE COUNTS
    #
    # These values are used only to create the explanatory
    # note returned by this function.
    #
    # They show how many rows came from:
    #
    #     Local CSV
    #     Archive API
    #     Recent fallback API

    local_count = len(local)

    archive_count = len(
        fetched_archive
    )

    recent_count = len(
        fetched_recent
    )


 
    # [12-Y] CREATE HISTORY NOTE
    # This note can be displayed by the prediction page to
    # explain how the required history was collected.
    #
    # Example meaning:
    #
    #     Model needs 30 previous days.
    #     Used local CSV days,
    #     archive API days,
    #     and recent fallback API days.

    note = (

        f"Model needs {history_days} previous days. "

        f"Used {local_count} local CSV days, "

        f"{archive_count} archive API days "

        f"and {recent_count} recent fallback API days."
    )


   
    # [12-Z] FUTURE TARGET VALIDATION

    #
    # Future prediction requires an additional check.
    #
    # Why?
    #
    # For a future target date, the model needs:
    #
    #     previous day's rainfall
    #
    # because it becomes:
    #
    #     rain_lag_1
    #
    # This value must therefore exist before future prediction
    # can be created.

    if target_date > today:



        # [12-Z1] FIND PREVIOUS DAY

        previous_day = (
            target_date
            - pd.Timedelta(
                days=1
            )
        )


       
        # [12-Z2] FIND PREVIOUS DAY RECORD

        previous_row = history[

            (
                history["Date"]
                == previous_day
            )

            &

            (
                history["Station_ID"]
                == station_id
            )
        ]


     
        # [12-Z3] CHECK PREVIOUS DAY DATA
    

        if previous_row.empty:

            raise ValueError(

                "Previous day data is missing. "
                "Future prediction cannot be created."
            )


       
        # [12-Z4] READ PREVIOUS DAY RAINFALL
      

        previous_rain = pd.to_numeric(

            previous_row.iloc[0]["rain_sum"],

            errors="coerce"
        )


      
        # [12-Z5] CHECK PREVIOUS RAINFALL
      

        if pd.isna(previous_rain):

            raise ValueError(

                "Previous day rainfall is missing. "
                "Future prediction cannot use rain_lag_1."
            )


      
        # [12-Z6] IDENTIFY PREVIOUS-DAY DATA SOURCE

        # Default assumption:
        #
        #     API
        #
        # If the previous day existed in the original local
        # CSV, source is changed to:
        #
        #     CSV


        previous_source = "API"

        if previous_day in local_dates:

            previous_source = "CSV"


       
        # [12-Z7] ADD PREVIOUS-DAY INFORMATION TO NOTE
      
        #
        # This explains:
        #
        #     Previous date
        #     Rainfall amount
        #     Data source
        #     Usage as rain_lag_1


        note += (

            f" Previous day rainfall "

            f"({previous_day.strftime('%Y-%m-%d')}) "

            f"= {float(previous_rain):.2f} mm "

            f"from {previous_source}; "

            f"this value is used for rain_lag_1 "
            f"and rolling rainfall features."
        )


       
        # [12-Z8] SPECIAL TODAY WARNING
      
        #
        # If the target date is tomorrow, then previous_day is
        # today.
        #
        # If today's data was not present in the CSV, the
        # fallback API value is being used.
        #
        # A warning is therefore added to the note.
    

        if previous_day == today:

            if previous_day not in local_dates:

                note += (

                    " WARNING: Today's rainfall was not "
                    "available in the CSV, so the fallback "
                    "API value was used."
                )


    # [12-Z9] RETURN FINAL RESULT
    # Returns:
    #
    #     history
    #         Complete validated historical dataset.
    #
    #     note
    #         Explanation of history source and preparation.
    #

    return history, note

### খুব গুরুত্বপূর্ণ developer logic

## এই module-টার মূল architecture হলো:

##**Local CSV → Missing date detection → Archive/Forecast API fallback → Merge → CSV priority → Completeness check → Rainfall validation → Future previous-day validation → Prediction feature generation-এর জন্য history return**

##বিশেষ করে এই অংশটা মনে রাখতে হবে:

##* **Past missing date** → Archive API
##* **Today/recent missing date** → Forecast API fallback
##* **Local CSV থাকলে সেটাই priority**
##* একই `Station_ID + Date` থাকলে প্রথম record রাখা হয়, তাই local record আগে থাকায় API record-এর ওপর CSV priority পায়।
##* Future prediction-এর ক্ষেত্রে **previous day's `rain_sum` অবশ্যই থাকতে হবে**, কারণ সেটা `rain_lag_1` এবং rolling rainfall features-এর জন্য ব্যবহৃত হয়।
##* `history_days < 30` দিলে code নিজেই **30 দিন minimum** করে নেয়।

##আর একটা বিষয়: আমি ইচ্ছা করেই Bangla explanation-গুলো code-এর logic-এর সঙ্গে `#` comment হিসেবে দিয়েছি, আর যেসব text `st.markdown()`-এর ভিতরে থাকে সেগুলোর ক্ষেত্রে আলাদা করে HTML comment ব্যবহার করার নিয়মটা আগের `About` page-এর মতো প্রযোজ্য হবে।   