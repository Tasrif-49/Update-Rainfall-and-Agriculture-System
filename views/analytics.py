
# ============================================================
# ADVANCED ANALYTICS PAGE — DEVELOPER GUIDE
# ============================================================
#
# MAIN FUNCTION:
#     show_analytics(df)
#
# PURPOSE:
#     This page provides visual analysis of historical
#     Bangladesh weather and rainfall data.
#
# AVAILABLE ANALYSIS:
#
#     1. Station-wise filtering
#     2. Monthly average rainfall
#     3. Historical rainfall trend
#     4. Temperature vs rainfall
#     5. Wind speed vs rainfall
#     6. Rainfall distribution
#     7. Station-wise average rainfall
#
# ============================================================
#
# MAIN DATA FLOW
# ============================================================
#
#     Full Dataset (df)
#             ↓
#     Select Station
#             ↓
#     Filtered Dataset (x)
#             ↓
#     ┌──────────────────────────────────────────┐
#     │ Monthly Rainfall                        │
#     │ Historical Trend                        │
#     │ Temperature vs Rainfall                 │
#     │ Wind Speed vs Rainfall                  │
#     │ Rainfall Distribution                   │
#     └──────────────────────────────────────────┘
#
#     Full Dataset (df)
#             ↓
#     Station-wise Average
#             ↓
#     Top 20 Stations
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
# [03] Page Title
#
# [04] Station Selection
#      [04-A] Create station list
#      [04-B] Station selectbox
#      [04-C] "All" station logic
#      [04-D] Specific station filtering
#
# [05] Empty Dataset Check
#
# [06] Monthly Average Rainfall
#      [06-A] Extract month
#      [06-B] Calculate monthly average
#      [06-C] Create month names
#      [06-D] Monthly rainfall bar chart
#
# [07] Chart Configuration
#
# [08] Sample Dataset
#
# [09] Historical Rainfall Trend
#
# [10] Temperature vs Rainfall
#
# [11] Wind Speed vs Rainfall
#
# [12] Rainfall Distribution
#
# [13] Station Average Rainfall
#      [13-A] Calculate station average
#      [13-B] Sort stations
#      [13-C] Keep top 20
#      [13-D] Display station chart
#
# ============================================================
#
# QUICK CHANGE GUIDE
# ============================================================
#
# Change page title
#     → [03]
#
# Change station dropdown
#     → [04]
#
# Change monthly rainfall chart
#     → [06]
#
# Change historical trend range
#     → [09]
#        Current: last 1000 records
#
# Change scatter sample size
#     → [08]
#        Current: maximum 3000 records
#
# Change temperature variable
#     → [10]
#
# Change wind variable
#     → [11]
#
# Change rainfall histogram bins
#     → [12]
#        Current: 50 bins
#
# Change number of top stations
#     → [13-C]
#        Current: top 20
#
# ============================================================


# ============================================================
# [01] IMPORTS
# ============================================================
#
# streamlit:
#     Creates the Streamlit interface and displays charts.
#
# pandas:
#     Used for filtering, grouping, sampling and calculations.
#
# plotly.express:
#     Creates interactive analytics charts.
#
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# [02] MAIN FUNCTION
# ============================================================
#
# show_analytics(df)
#
# INPUT:
#     df = Complete weather dataset.
#
# IMPORTANT COLUMNS USED:
#
#     Station
#     Date
#     rain_sum
#     temperature_2m_mean
#     wind_speed_10m_max
#
# The function uses:
#
#     x  → station-filtered dataset
#     df → complete dataset
#
# This distinction is important:
#
#     Most charts use x.
#     Station Average chart uses the complete df.
#
# ============================================================

def show_analytics(df):


    # ========================================================
    # [03] PAGE TITLE
    # ========================================================
    #
    # Main heading of the Analytics page.
    #
    # ========================================================

    st.title(
        "📊 Advanced Analytics"
    )


    # ========================================================
    # [04] STATION SELECTION
    # ========================================================
    #
    # Allows the user to analyse:
    #
    #     All stations
    #
    # OR
    #
    #     One specific station
    #
    # ========================================================


    # --------------------------------------------------------
    # [04-A] CREATE STATION LIST
    # --------------------------------------------------------
    #
    # Converts Station values to strings and sorts them.
    #
    # astype(str):
    #     Keeps dropdown values consistent even if the original
    #     Station column contains mixed data types.
    #
    # --------------------------------------------------------

    stations = sorted(
        df.Station.astype(str).unique()
    )


    # --------------------------------------------------------
    # [04-B] STATION SELECTBOX
    # --------------------------------------------------------
    #
    # "All" is added as the first option.
    #
    # No key is specified here, so Streamlit uses its normal
    # widget identity.
    #
    # --------------------------------------------------------

    sel = st.selectbox(
        "Station for detailed analytics",
        ["All"] + stations
    )


    # --------------------------------------------------------
    # [04-C] ALL STATIONS
    # --------------------------------------------------------
    #
    # If "All" is selected:
    #
    #     x = complete dataset
    #
    # --------------------------------------------------------

    if sel == "All":

        x = df.copy()


    # --------------------------------------------------------
    # [04-D] SPECIFIC STATION
    # --------------------------------------------------------
    #
    # If a station is selected:
    #
    #     Only that station's records are copied into x.
    #
    # x is the dataset used by the detailed analytics charts.
    #
    # --------------------------------------------------------

    else:

        x = df[
            df.Station.astype(str)
            ==
            sel
        ].copy()


    # ========================================================
    # [05] EMPTY DATASET CHECK
    # ========================================================
    #
    # Safety check.
    #
    # If the selected station contains no records, the page
    # displays a warning and stops further processing.
    #
    # This prevents charts from being generated from an empty
    # dataframe.
    #
    # ========================================================

    if x.empty:

        st.warning(
            "No data available."
        )

        return


    # ========================================================
    # [06] MONTHLY AVERAGE RAINFALL
    # ========================================================
    #
    # PURPOSE:
    #     Calculate the average rainfall for each month.
    #
    # Example:
    #
    #     January → average rainfall
    #     February → average rainfall
    #     ...
    #     December → average rainfall
    #
    # This analysis uses the currently selected station dataset
    # "x".
    #
    # ========================================================


    # --------------------------------------------------------
    # [06-A] EXTRACT MONTH NUMBER
    # --------------------------------------------------------
    #
    # Date.dt.month converts:
    #
    #     2025-01-15 → 1
    #     2025-06-20 → 6
    #
    # The month number is temporarily stored as "Month".
    #
    # --------------------------------------------------------

    monthly = (
        x
        .assign(
            Month=x["Date"].dt.month
        )


        # ----------------------------------------------------
        # [06-B] CALCULATE MONTHLY AVERAGE
        # ----------------------------------------------------
        #
        # Group records by month and calculate the mean
        # rainfall.
        #
        # rain_sum = daily rainfall value.
        #
        # ----------------------------------------------------

        .groupby(
            "Month",
            as_index=False
        )["rain_sum"]

        .mean()

        .rename(
            columns={
                "rain_sum":
                "Average Rainfall"
            }
        )
    )


    # --------------------------------------------------------
    # [06-C] CONVERT MONTH NUMBER TO MONTH NAME
    # --------------------------------------------------------
    #
    # Example:
    #
    #     1  → Jan
    #     2  → Feb
    #     12 → Dec
    #
    # --------------------------------------------------------

    monthly["Month Name"] = (
        pd.to_datetime(
            monthly["Month"],
            format="%m"
        )
        .dt.strftime("%b")
    )


    # --------------------------------------------------------
    # [06-D] MONTHLY RAINFALL BAR CHART
    # --------------------------------------------------------
    #
    # X-axis:
    #     Month Name
    #
    # Y-axis:
    #     Average Rainfall
    #
    # --------------------------------------------------------

    fig = px.bar(
        monthly,
        x="Month Name",
        y="Average Rainfall",
        title="Monthly Average Rainfall"
    )


    # ========================================================
    # [07] MONTHLY CHART CONFIGURATION
    # ========================================================
    #
    # height:
    #     Chart height.
    #
    # dragmode=False:
    #     Prevents drag-based chart interaction.
    #
    # hovermode="closest":
    #     Shows information for the nearest data point.
    #
    # uirevision="constant":
    #     Helps preserve chart UI state during Streamlit
    #     reruns.
    #
    # ========================================================

    fig.update_layout(
        height=400,
        dragmode=False,
        hovermode="closest",
        uirevision="constant"
    )


    # --------------------------------------------------------
    # DISPLAY MONTHLY CHART
    # --------------------------------------------------------

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": True,
            "displaylogo": False,
            "scrollZoom": False,
            "doubleClick": False,
            "modeBarButtonsToRemove": [
                "pan2d",
                "select2d",
                "lasso2d",
                "zoomIn2d",
                "zoomOut2d"
            ]
        },
        key="analytics_chart_1"
    )


    # ========================================================
    # [08] SAMPLE DATASET
    # ========================================================
    #
    # Scatter plots can become slow when thousands of points
    # are rendered.
    #
    # Therefore, a maximum of 3000 records is randomly sampled.
    #
    # min(3000, len(x)):
    #     If x has fewer than 3000 rows, all rows are used.
    #
    # random_state=42:
    #     Makes the sample reproducible.
    #
    # IMPORTANT:
    #     This sampling is only used for scatter plots.
    #     It does NOT modify x or the original dataset.
    #
    # ========================================================

    sample = x.sample(
        min(
            3000,
            len(x)
        ),
        random_state=42
    )


    # ========================================================
    # [09] HISTORICAL RAINFALL TREND
    # ========================================================
    #
    # Shows rainfall values over time.
    #
    # Only the latest 1000 records are displayed.
    #
    # WHY:
    #     Limiting the number of points keeps the chart easier
    #     to render and view.
    #
    # ========================================================

    a, b = st.columns(2)


    with a:

        fig = px.line(
            x
            .sort_values("Date")
            .tail(1000),
            x="Date",
            y="rain_sum",
            title="Historical Rainfall Trend"
        )


        # ----------------------------------------------------
        # CHART CONFIGURATION
        # ----------------------------------------------------

        fig.update_layout(
            height=400,
            dragmode=False,
            hovermode="closest",
            uirevision="constant"
        )


        # ----------------------------------------------------
        # DISPLAY HISTORICAL TREND
        # ----------------------------------------------------

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": True,
                "displaylogo": False,
                "scrollZoom": False,
                "doubleClick": False,
                "modeBarButtonsToRemove": [
                    "pan2d",
                    "select2d",
                    "lasso2d",
                    "zoomIn2d",
                    "zoomOut2d"
                ]
            },
            key="analytics_chart_2"
        )


    # ========================================================
    # [10] TEMPERATURE VS RAINFALL
    # ========================================================
    #
    # Scatter plot showing the relationship between:
    #
    #     X-axis → Mean temperature
    #     Y-axis → Rainfall
    #
    # Uses "sample" rather than all records.
    #
    # IMPORTANT:
    #     This chart shows association visually.
    #     It does not by itself prove causation.
    #
    # ========================================================

    with b:

        fig = px.scatter(
            sample,
            x="temperature_2m_mean",
            y="rain_sum",
            title="Temperature vs Rainfall"
        )


        # ----------------------------------------------------
        # CHART CONFIGURATION
        # ----------------------------------------------------

        fig.update_layout(
            height=400,
            dragmode=False,
            hovermode="closest",
            uirevision="constant"
        )


        # ----------------------------------------------------
        # DISPLAY TEMPERATURE CHART
        # ----------------------------------------------------

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": True,
                "displaylogo": False,
                "scrollZoom": False,
                "doubleClick": False,
                "modeBarButtonsToRemove": [
                    "pan2d",
                    "select2d",
                    "lasso2d",
                    "zoomIn2d",
                    "zoomOut2d"
                ]
            },
            key="analytics_chart_3"
        )


    # ========================================================
    # [11] WIND SPEED VS RAINFALL
    # ========================================================
    #
    # Second relationship analysis.
    #
    # X-axis:
    #     Maximum wind speed at 10m.
    #
    # Y-axis:
    #     Rainfall.
    #
    # Uses the same 3000-record sample created in [08].
    #
    # ========================================================

    a, b = st.columns(2)


    with a:

        fig = px.scatter(
            sample,
            x="wind_speed_10m_max",
            y="rain_sum",
            title="Wind Speed vs Rainfall"
        )


        # ----------------------------------------------------
        # CHART CONFIGURATION
        # ----------------------------------------------------

        fig.update_layout(
            height=400,
            dragmode=False,
            hovermode="closest",
            uirevision="constant"
        )


        # ----------------------------------------------------
        # DISPLAY WIND CHART
        # ----------------------------------------------------

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": True,
                "displaylogo": False,
                "scrollZoom": False,
                "doubleClick": False,
                "modeBarButtonsToRemove": [
                    "pan2d",
                    "select2d",
                    "lasso2d",
                    "zoomIn2d",
                    "zoomOut2d"
                ]
            },
            key="analytics_chart_4"
        )


    # ========================================================
    # [12] RAINFALL DISTRIBUTION
    # ========================================================
    #
    # Displays how rainfall values are distributed.
    #
    # Unlike the scatter plots, this chart uses the complete
    # currently selected dataset "x".
    #
    # nbins=50:
    #     Divides rainfall values into 50 histogram bins.
    #
    # ========================================================

    with b:

        fig = px.histogram(
            x,
            x="rain_sum",
            nbins=50,
            title="Rainfall Distribution"
        )


        # ----------------------------------------------------
        # CHART CONFIGURATION
        # ----------------------------------------------------

        fig.update_layout(
            height=400,
            dragmode=False,
            hovermode="closest",
            uirevision="constant"
        )


        # ----------------------------------------------------
        # DISPLAY HISTOGRAM
        # ----------------------------------------------------

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": True,
                "displaylogo": False,
                "scrollZoom": False,
                "doubleClick": False,
                "modeBarButtonsToRemove": [
                    "pan2d",
                    "select2d",
                    "lasso2d",
                    "zoomIn2d",
                    "zoomOut2d"
                ]
            },
            key="analytics_chart_5"
        )


    # ========================================================
    # [13] STATION AVERAGE RAINFALL
    # ========================================================
    #
    # PURPOSE:
    #     Compare average rainfall across stations.
    #
    # IMPORTANT:
    #
    #     This section uses the ORIGINAL COMPLETE "df".
    #
    #     It does NOT use the station-filtered "x".
    #
    # Therefore, even if the user selects one station above,
    # this chart still calculates station averages across the
    # complete dataset.
    #
    # ========================================================


    # --------------------------------------------------------
    # [13-A] CALCULATE STATION AVERAGE
    # --------------------------------------------------------
    #
    # Groups the complete dataset by Station and calculates
    # mean rainfall for each station.
    #
    # --------------------------------------------------------

    station_avg = (
        df
        .groupby(
            "Station",
            as_index=False
        )["rain_sum"]

        .mean()


        # ----------------------------------------------------
        # [13-B] SORT BY AVERAGE RAINFALL
        # ----------------------------------------------------
        #
        # Highest average rainfall appears first.
        #
        # ----------------------------------------------------

        .sort_values(
            "rain_sum",
            ascending=False
        )


        # ----------------------------------------------------
        # [13-C] KEEP TOP 20 STATIONS
        # ----------------------------------------------------
        #
        # Only the first 20 stations are displayed.
        #
        # ----------------------------------------------------

        .head(20)
    )


    # --------------------------------------------------------
    # [13-D] CREATE STATION BAR CHART
    # --------------------------------------------------------

    fig = px.bar(
        station_avg,
        x="Station",
        y="rain_sum",
        title="Top 20 Stations by Average Rainfall"
    )


    # --------------------------------------------------------
    # STATION CHART CONFIGURATION
    # --------------------------------------------------------

    fig.update_layout(
        height=400,
        dragmode=False,
        hovermode="closest",
        uirevision="constant"
    )


    # --------------------------------------------------------
    # DISPLAY STATION CHART
    # --------------------------------------------------------

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": True,
            "displaylogo": False,
            "scrollZoom": False,
            "doubleClick": False,
            "modeBarButtonsToRemove": [
                "pan2d",
                "select2d",
                "lasso2d",
                "zoomIn2d",
                "zoomOut2d"
            ]
        },
        key="analytics_chart_6"
    )

### এই page-এর সবচেয়ে গুরুত্বপূর্ণ developer map

##| Section | কাজ                       | Data                              |
##| ------- | ------------------------- | --------------------------------- |
##| `[04]`  | Station selection         | `Station`                         |
##| `[06]`  | Monthly average rainfall  | filtered `x`                      |
##| `[08]`  | Scatter sampling          | max 3,000 rows                    |
##| `[09]`  | Historical rainfall trend | last 1,000 rows                   |
##| `[10]`  | Temperature vs rainfall   | `temperature_2m_mean`, `rain_sum` |
##| `[11]`  | Wind vs rainfall          | `wind_speed_10m_max`, `rain_sum`  |
##| `[12]`  | Rainfall distribution     | filtered `x`                      |
##| `[13]`  | Station comparison        | **full `df`**                     |

##**একটা গুরুত্বপূর্ণ logic point:** `[13] Station Average` ইচ্ছাকৃতভাবে `df` ব্যবহার করছে, #`x` না। তাই উপরের station dropdown-এ একটি station নির্বাচন করলেও **Top 20 Stations by Average Rainfall** chart পুরো dataset-এর stationগুলোর average দেখাবে। এটা যদি আপনার intended behavior হয়, তাহলে code ঠিক আছে।