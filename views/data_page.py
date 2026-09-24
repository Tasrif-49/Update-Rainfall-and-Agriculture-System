
# ============================================================
# HISTORICAL WEATHER DATA PAGE — DEVELOPER GUIDE
# ============================================================
#
# MAIN FUNCTION:
#     show_data_page(df)
#
# PURPOSE:
#     This page displays the historical weather dataset and
#     allows users to filter records by:
#         1. Station
#         2. Division
#         3. Date range
#
# MAIN FLOW:
#
#     Raw Dataset
#          ↓
#     Ensure Date Format
#          ↓
#     Dataset Summary
#          ↓
#     Station / Division / Date Filters
#          ↓
#     Apply Filters
#          ↓
#     Display Filtered Dataset
#
# ============================================================
#
# CODE INDEX
# ============================================================
#
# [01] Imports
#
# [02] Main Function
#
# [03] Ensure Date Format
#      [03-A] Copy dataframe
#      [03-B] Convert Date column
#      [03-C] Remove invalid dates
#
# [04] Dataset Summary
#      [04-A] Minimum date
#      [04-B] Maximum date
#      [04-C] Records metric
#      [04-D] Stations metric
#      [04-E] Period metric
#
# [05] Filter Controls
#      [05-A] Station filter
#      [05-B] Division filter
#
# [06] Date Range Filter
#      [06-A] Date range selector
#
# [07] Apply Station Filter
#
# [08] Apply Division Filter
#
# [09] Apply Date Filter
#      [09-A] Two-date range
#      [09-B] Single selected date
#
# [10] Display Filtered Data
#      [10-A] Record count
#      [10-B] Data table
#
# ============================================================
#
# QUICK CHANGE GUIDE
# ============================================================
#
# Change page title
#     → Section [02]
#
# Change summary metrics
#     → Section [04]
#
# Add/remove station filter
#     → Section [05-A]
#
# Add/remove division filter
#     → Section [05-B]
#
# Change date selection behavior
#     → Section [06] and [09]
#
# Change table height
#     → Section [10-B]
#
# Change table columns
#     → Section [10-B]
#
# Change "Showing X records"
#     → Section [10-A]
#
# ============================================================


# ============================================================
# [01] IMPORTS
# ============================================================
#
# streamlit:
#     Used for the complete Streamlit user interface.
#
# pandas:
#     Used for date conversion, filtering and dataframe
#     manipulation.
#
# ============================================================

import streamlit as st
import pandas as pd


# ============================================================
# [02] MAIN FUNCTION
# ============================================================
#
# show_data_page(df)
#
# INPUT:
#     df = Main weather dataset loaded by the application.
#
# IMPORTANT DATASET COLUMNS USED BY THIS PAGE:
#
#     Date
#     Station_ID
#     Station
#     Division
#
# The function does not permanently modify the original
# dataframe because a copy is created in Section [03].
#
# ============================================================

def show_data_page(df):

    # --------------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------------
    #
    # To change the page heading, edit the text below.
    #
    # --------------------------------------------------------

    st.title(
        "📂 Historical Weather Dataset"
    )


    # ========================================================
    # [03] ENSURE DATE FORMAT
    # ========================================================
    #
    # PURPOSE:
    #     Make sure the Date column is consistently stored as
    #     pandas datetime values before performing date
    #     filtering.
    #
    # WHY THIS IS IMPORTANT:
    #     Date filtering can produce incorrect results if some
    #     values are strings while others are datetime objects.
    #
    # ========================================================


    # --------------------------------------------------------
    # [03-A] COPY DATAFRAME
    # --------------------------------------------------------
    #
    # Creates a separate copy so that date conversion and
    # filtering do not directly modify the original dataframe.
    #
    # --------------------------------------------------------

    df = df.copy()


    # --------------------------------------------------------
    # [03-B] CONVERT DATE COLUMN
    # --------------------------------------------------------
    #
    # pd.to_datetime():
    #     Converts the Date column into datetime format.
    #
    # errors="coerce":
    #     Invalid date values become NaT instead of causing
    #     the application to crash.
    #
    # .dt.normalize():
    #     Removes the time portion and keeps only the date.
    #
    # Example:
    #
    #     2025-01-15 14:30:00
    #
    # becomes:
    #
    #     2025-01-15 00:00:00
    #
    # --------------------------------------------------------

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    ).dt.normalize()


    # --------------------------------------------------------
    # [03-C] REMOVE INVALID DATES
    # --------------------------------------------------------
    #
    # Any row where Date could not be converted becomes NaT.
    #
    # Those rows are removed because the page depends on
    # valid dates for summary and filtering.
    #
    # --------------------------------------------------------

    df = df.dropna(
        subset=["Date"]
    ).copy()


    # ========================================================
    # [04] DATASET SUMMARY
    # ========================================================
    #
    # Displays three summary metrics:
    #
    #     1. Total records
    #     2. Total stations
    #     3. Dataset date period
    #
    # These values are calculated from the cleaned dataframe.
    #
    # ========================================================


    # --------------------------------------------------------
    # [04-A] FIND MINIMUM DATE
    # --------------------------------------------------------

    min_date = df["Date"].min().date()


    # --------------------------------------------------------
    # [04-B] FIND MAXIMUM DATE
    # --------------------------------------------------------

    max_date = df["Date"].max().date()


    # --------------------------------------------------------
    # [04-C] CREATE THREE SUMMARY COLUMNS
    # --------------------------------------------------------

    c1, c2, c3 = st.columns(3)


    # --------------------------------------------------------
    # [04-D] RECORD COUNT
    # --------------------------------------------------------
    #
    # Shows the total number of valid weather records currently
    # available in the dataset before filters are applied.
    #
    # --------------------------------------------------------

    c1.metric(
        "Records",
        f"{len(df):,}"
    )


    # --------------------------------------------------------
    # [04-E] STATION COUNT
    # --------------------------------------------------------
    #
    # Counts the number of unique Station_ID values.
    #
    # IMPORTANT:
    #     This is based on Station_ID, not Station name.
    #
    # --------------------------------------------------------

    c2.metric(
        "Stations",
        df["Station_ID"].nunique()
    )


    # --------------------------------------------------------
    # [04-F] DATASET PERIOD
    # --------------------------------------------------------
    #
    # Displays the earliest and latest available dates.
    #
    # Date format:
    #
    #     DD/MM/YYYY
    #
    # Example:
    #
    #     01/01/2016 → 31/12/2025
    #
    # --------------------------------------------------------

    c3.metric(
        "Period",
        f"{min_date.strftime('%d/%m/%Y')} → "
        f"{max_date.strftime('%d/%m/%Y')}"
    )


    # ========================================================
    # [05] FILTER CONTROLS
    # ========================================================
    #
    # Users can filter the historical dataset using:
    #
    #     Station
    #     Division
    #
    # Date filtering is handled separately in Section [06].
    #
    # ========================================================

    s1, s2, s3 = st.columns(3)


    # --------------------------------------------------------
    # [05-A] STATION FILTER
    # --------------------------------------------------------
    #
    # "All" means no station filtering.
    #
    # Otherwise, only records belonging to the selected
    # station are displayed.
    #
    # astype(str):
    #     Converts station values to string so that the
    #     selectbox values remain consistent.
    #
    # key:
    #     Used by Streamlit to maintain this widget's state.
    #
    # --------------------------------------------------------

    station = s1.selectbox(
        "Station",
        ["All"] + sorted(
            df["Station"]
            .astype(str)
            .unique()
            .tolist()
        ),
        key="historical_station"
    )


    # --------------------------------------------------------
    # [05-B] DIVISION FILTER
    # --------------------------------------------------------
    #
    # "All" means no division filtering.
    #
    # Otherwise, only records belonging to the selected
    # division are displayed.
    #
    # --------------------------------------------------------

    division = s2.selectbox(
        "Division",
        ["All"] + sorted(
            df["Division"]
            .astype(str)
            .unique()
            .tolist()
        ),
        key="historical_division"
    )


    # ========================================================
    # [06] DATE RANGE
    # ========================================================
    #
    # Allows the user to select:
    #
    #     Start Date → End Date
    #
    # Default:
    #     Entire available dataset period.
    #
    # format="DD/MM/YYYY":
    #     Controls how dates appear in the Streamlit UI.
    #
    # ========================================================

    dates = s3.date_input(
        "📅 Date Range",
        value=(
            min_date,
            max_date
        ),
        key="historical_date_range",
        format="DD/MM/YYYY"
    )


    # ========================================================
    # [07] CREATE FILTERED DATAFRAME
    # ========================================================
    #
    # A separate dataframe "x" is created.
    #
    # The original cleaned dataframe "df" remains unchanged.
    #
    # All filters are progressively applied to x.
    #
    # ========================================================

    x = df.copy()


    # ========================================================
    # [08] APPLY STATION FILTER
    # ========================================================
    #
    # If the user selects "All":
    #     No filtering happens.
    #
    # If a specific station is selected:
    #     Only matching Station values remain.
    #
    # ========================================================

    if station != "All":

        x = x[
            x["Station"].astype(str)
            == station
        ]


    # ========================================================
    # [09] APPLY DIVISION FILTER
    # ========================================================
    #
    # If the user selects "All":
    #     No filtering happens.
    #
    # Otherwise:
    #     Keep only rows belonging to the selected division.
    #
    # ========================================================

    if division != "All":

        x = x[
            x["Division"].astype(str)
            == division
        ]


    # ========================================================
    # [10] APPLY DATE FILTER
    # ========================================================
    #
    # Streamlit date_input normally returns a tuple when a
    # date range is selected.
    #
    # This section handles two cases:
    #
    #     Case 1 → Two dates selected
    #     Case 2 → One date selected
    #
    # ========================================================


    # --------------------------------------------------------
    # [10-A] DATE RANGE SELECTED
    # --------------------------------------------------------
    #
    # Example:
    #
    #     01/01/2025 → 31/01/2025
    #
    # The end date is increased by one day so that the entire
    # selected end date is included.
    #
    # The condition uses:
    #
    #     Date >= start_date
    #     Date < end_date + 1 day
    #
    # This avoids accidentally excluding records on the
    # selected end date.
    #
    # --------------------------------------------------------

    if isinstance(dates, (tuple, list)):

        if len(dates) == 2:

            start_date = pd.Timestamp(
                dates[0]
            ).normalize()

            end_date = (
                pd.Timestamp(
                    dates[1]
                ).normalize()
                + pd.Timedelta(days=1)
            )

            x = x[
                (x["Date"] >= start_date)
                &
                (x["Date"] < end_date)
            ]


    # --------------------------------------------------------
    # [10-B] SINGLE DATE SELECTED
    # --------------------------------------------------------
    #
    # If Streamlit returns a single date instead of a range,
    # only records matching that exact date are displayed.
    #
    # --------------------------------------------------------

    elif dates is not None:

        selected = pd.Timestamp(
            dates
        ).normalize()

        x = x[
            x["Date"] == selected
        ]


    # ========================================================
    # [11] DISPLAY FILTERED DATA
    # ========================================================
    #
    # At this point:
    #
    #     x = cleaned + filtered dataset
    #
    # The user sees:
    #
    #     1. Number of matching records
    #     2. Complete filtered dataframe
    #
    # ========================================================


    # --------------------------------------------------------
    # [11-A] FILTERED RECORD COUNT
    # --------------------------------------------------------
    #
    # Shows how many records remain after all selected filters.
    #
    # --------------------------------------------------------

    st.caption(
        f"Showing {len(x):,} records"
    )


    # --------------------------------------------------------
    # [11-B] DISPLAY DATA TABLE
    # --------------------------------------------------------
    #
    # width="stretch":
    #     Uses the available page width.
    #
    # height=480:
    #     Controls the visible table height.
    #
    # To change table height:
    #
    #     height=600
    #
    # To display only selected columns, the dataframe can be
    # changed to:
    #
    #     x[["Date", "Station", "Division", "rain_sum"]]
    #
    # --------------------------------------------------------

    st.dataframe(
        x,
        width="stretch",
        height=480
    )

