
# ============================================================
# HOME.PY — QUICK DEVELOPER INDEX
# ============================================================
#
# FILE PURPOSE
# ------------------------------------------------------------
# This file controls the Home page of the
# Bangladesh Smart Rainfall & Agriculture System.
#
# [01] IMPORTS
#      → Streamlit
#      → Pandas
#      → Plotly Express
#
# [02] SHOW HOME FUNCTION
#      → Main Home page controller
#
# [03] HERO SECTION
#      → Project title
#      → Project description
#      → Weather record count
#      → Weather station count
#      → Reserved empty statistic
#      → Smart irrigation label
#
# [04] QUICK ACCESS
#      → Rainfall Prediction
#      → Smart Agriculture
#      → Analytics
#      → Session-state based navigation
#
# [05] ANALYSIS LAYOUT
#      → Two-column chart layout
#
# [06] MONTHLY RAINFALL ANALYSIS
#      → Monthly average rainfall
#      → Month name conversion
#      → Area chart
#      → Y-axis
#      → Chart layout
#      → Chart display
#
# [07] RAINFALL DISTRIBUTION
#      → Latest 1000 records
#      → Histogram
#      → Chart layout
#      → Chart display
#
# ------------------------------------------------------------
# QUICK CHANGE GUIDE
# ------------------------------------------------------------
#
# Change Home title/description
#      → [03]
#
# Change record count
#      → [03-A]
#
# Change station count
#      → [03-B]
#
# Change Smart Irrigation text
#      → [03-D]
#
# Change Prediction navigation
#      → [04-A]
#
# Change Agriculture navigation
#      → [04-B]
#
# Change Analytics navigation
#      → [04-C]
#
# Change chart column ratio
#      → [05]
#
# Change monthly rainfall calculation
#      → [06-A]
#
# Change month labels
#      → [06-B]
#
# Change monthly chart type/title
#      → [06-C]
#
# Change monthly chart height/settings
#      → [06-D]
#
# Change monthly chart display/config
#      → [06-E]
#
# Change distribution sample size
#      → [07-A]
#
# Change histogram
#      → [07-B]
#
# Change distribution chart settings
#      → [07-C]
#
# Change distribution chart display/config
#      → [07-D]
#
# IMPORTANT
# ------------------------------------------------------------
# Developer comments/index labels are kept OUTSIDE all
# st.markdown() content strings.
#
# Therefore they will NOT appear on the Home page.
#
# Application behavior is unchanged.
#
# ============================================================


# ============================================================
# [01] IMPORTS
# ============================================================
#
# Streamlit
#     → UI and page navigation
#
# Pandas
#     → Data processing and monthly calculations
#
# Plotly Express
#     → Rainfall charts
#
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# [02] MAIN HOME PAGE FUNCTION
# ============================================================
#
# FUNCTION:
#     show_home(df)
#
# INPUT:
#     df
#     → Main weather/rainfall dataframe
#
# REQUIRED DATA:
#     Date
#     Station_ID
#     rain_sum
#
# MAIN FLOW:
#
#     Hero
#       ↓
#     Quick Access
#       ↓
#     Chart Layout
#       ↓
#     Monthly Rainfall
#       ↓
#     Rainfall Distribution
#
# ============================================================

def show_home(df):


    # ========================================================
    # [03] HERO SECTION
    # ========================================================
    #
    # Displays:
    #     Project title
    #     Project description
    #     Weather record count
    #     Weather station count
    #     Empty/reserved statistic
    #     Smart irrigation system
    #
    # IMPORTANT:
    # The HTML below must remain clean.
    # Do not put Python developer comments inside the
    # st.markdown() string.
    #
    # ========================================================

    st.markdown(

        f"""

        <div class='hero'>

        <h1>
        🌧️ Bangladesh Smart Rainfall & Agriculture System
        </h1>

        <p>
        Rainfall prediction, agricultural water calculation
        and smart irrigation recommendation system.
        </p>

        <div class='hero-stats'>

        <div class='hero-stat'>

        <div class='hero-num'>
        {len(df):,}
        </div>

        <div class='hero-label'>
        Weather Records
        </div>

        </div>


        <div class='hero-stat'>

        <div class='hero-num'>
        {df.Station_ID.nunique()}
        </div>

        <div class='hero-label'>
        Weather Stations
        </div>

        </div>


        <div class='hero-stat'>

        <div class='hero-num'>
        
        </div>

        <div class='hero-label'>
        
        </div>

        </div>


        <div class='hero-stat'>

        <div class='hero-num'>
        🌱 Smart
        </div>

        <div class='hero-label'>
        Irrigation System
        </div>

        </div>

        </div>

        </div>

        """,

        unsafe_allow_html=True

    )


    # ========================================================
    # [04] QUICK ACCESS SECTION
    # ========================================================
    #
    # Creates three navigation buttons:
    #
    #     Rainfall Prediction
    #     Smart Agriculture
    #     Analytics
    #
    # Navigation works through:
    #
    #     st.session_state.page
    #
    # followed by:
    #
    #     st.rerun()
    #
    # IMPORTANT:
    # Page names must match the main application router.
    #
    # ========================================================

    st.markdown(

        "<div class='section-title'>🚀 Quick Access</div>",

        unsafe_allow_html=True

    )


    a, b, c = st.columns(3)


    # ========================================================
    # [04-A] RAINFALL PREDICTION BUTTON
    # ========================================================
    #
    # Button text:
    #     🔮 Rainfall Prediction
    #
    # Route:
    #     🔮 Rain Prediction
    #
    # ========================================================

    if a.button(

        "🔮 Rainfall Prediction",

        width="stretch",

        type="primary"

    ):

        st.session_state.page = "🔮 Rain Prediction"

        st.rerun()


    # ========================================================
    # [04-B] SMART AGRICULTURE BUTTON
    # ========================================================
    #
    # Button text:
    #     🌱 Smart Agriculture (কৃষি সেচ ব্যবস্থা)
    #
    # CURRENT ROUTE VALUE:
    #     🌱 Agriculture
    #
    # IMPORTANT:
    # This exact value is preserved from the supplied code.
    # ========================================================

    if b.button(

        "🌱 Smart Agriculture (কৃষি সেচ ব্যবস্থা)",

       width="stretch",

        type="primary"

    ):

        st.session_state.page = "🌱 Agriculture "

        st.rerun()


    # ========================================================
    # [04-C] ANALYTICS BUTTON
    # ========================================================
    #
    # Button text:
    #     📊 Analytics
    #
    # Route:
    #     📊 Analytics
    #
    # ========================================================

    if c.button(

        "📊 Analytics",

       width="stretch",

        type="primary"

    ):

        st.session_state.page = "📊 Analytics"

        st.rerun()


    # ========================================================
    # [04-D] SECTION DIVIDER
    # ========================================================
    #
    # Separates Quick Access from the chart section.
    #
    # ========================================================

    st.divider()


    # ========================================================
    # [05] ANALYSIS LAYOUT
    # ========================================================
    #
    # Creates two chart columns.
    #
    # LEFT:
    #     Monthly Rainfall Pattern
    #
    # RIGHT:
    #     Rainfall Distribution
    #
    # CURRENT WIDTH:
    #     1.5 : 1
    #
    # ========================================================

    left, right = st.columns(

        [1.5, 1]

    )


    # ========================================================
    # [06] MONTHLY RAINFALL ANALYSIS
    # ========================================================
    #
    # Calculates average rainfall for each calendar month
    # and displays it as an area chart.
    #
    # ========================================================

    with left:


        # ====================================================
        # [06-A] MONTHLY AVERAGE CALCULATION
        # ====================================================
        #
        # Process:
        #
        #     Date
        #       ↓
        #     Month number
        #       ↓
        #     Group by Month
        #       ↓
        #     Mean rain_sum
        #
        # CURRENT CALCULATION:
        #     Average rainfall
        #
        # ====================================================

        monthly = (

            df

            .assign(

                Month=df["Date"].dt.month

            )

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


        # ====================================================
        # [06-B] MONTH NAME CONVERSION
        # ====================================================
        #
        # Converts month numbers into abbreviated month names:
        #
        #     1  → Jan
        #     2  → Feb
        #     ...
        #     12 → Dec
        #
        # ====================================================

        monthly["Month Name"] = (

            pd.to_datetime(

                monthly["Month"],

                format="%m"

            )

            .dt.strftime("%b")

        )


        # ====================================================
        # [06-C] MONTHLY AREA CHART
        # ====================================================
        #
        # X-axis:
        #     Month Name
        #
        # Y-axis:
        #     Average Rainfall
        #
        # Chart:
        #     Plotly Area Chart
        #
        # ====================================================

        fig = px.area(

            monthly,

            x="Month Name",

            y="Average Rainfall",

            title="Monthly Rainfall Pattern"

        )


        # ====================================================
        # [06-D] MONTHLY CHART SETTINGS
        # ====================================================
        #
        # Y-axis:
        #     Rainfall (mm)
        #
        # Layout:
        #     height = 400
        #     dragmode = False
        #     hovermode = closest
        #     uirevision = constant
        #
        # ====================================================

        fig.update_yaxes(

            title="Rainfall (mm)"

        )


        fig.update_layout(
            height=400,
            dragmode=False,
            hovermode="closest",
            uirevision="constant"
        )


        # ====================================================
        # [06-E] MONTHLY CHART DISPLAY
        # ====================================================
        #
        # Displays the Plotly chart in Streamlit.
        #
        # ====================================================

        st.plotly_chart(

            fig,

            use_container_width=True,

            config={
                "displayModeBar": True,
                "displaylogo": False,
                "scrollZoom": False,
                "doubleClick": "reset",
                "modeBarButtonsToRemove": [
                    "pan2d",
                    "select2d",
                    "lasso2d",
                    "zoomIn2d",
                    "zoomOut2d"
                ]
            },

            key="monthly_rainfall_fixed"

        )


    # ========================================================
    # [07] RAINFALL DISTRIBUTION ANALYSIS
    # ========================================================
    #
    # Displays rainfall distribution using a histogram.
    #
    # The chart uses only the latest 1000 rows after sorting
    # the dataframe by Date.
    #
    # ========================================================

    with right:


        # ====================================================
        # [07-A] SELECT LATEST 1000 RECORDS
        # ====================================================
        #
        # Process:
        #
        #     Sort by Date
        #          ↓
        #     Take last 1000 rows
        #
        # IMPORTANT:
        # This means latest 1000 rows, not necessarily
        # 1000 unique dates.
        #
        # ====================================================

        latest = (

            df

            .sort_values("Date")

            .tail(1000)

        )


        # ====================================================
        # [07-B] RAINFALL HISTOGRAM
        # ====================================================
        #
        # X-axis:
        #     rain_sum
        #
        # Number of bins:
        #     30
        #
        # ====================================================

        fig = px.histogram(

            latest,

            x="rain_sum",

            nbins=30,

            title="Rainfall Distribution"

        )


        # ====================================================
        # [07-C] DISTRIBUTION CHART SETTINGS
        # ====================================================
        #
        # height:
        #     400
        #
        # dragmode:
        #     False
        #
        # hovermode:
        #     closest
        #
        # uirevision:
        #     constant
        #
        # ====================================================

        fig.update_layout(
            height=400,
            dragmode=False,
            hovermode="closest",
            uirevision="constant"
        )


        # ====================================================
        # [07-D] DISTRIBUTION CHART DISPLAY
        # ====================================================
        #
        # Displays the rainfall histogram in Streamlit.
        #
        # ====================================================

        st.plotly_chart(

            fig,

            use_container_width=True,

            config={
                "displayModeBar": True,
                "displaylogo": False,
                "scrollZoom": False,
                "doubleClick": "reset",
                "modeBarButtonsToRemove": [
                    "pan2d",
                    "select2d",
                    "lasso2d",
                    "zoomIn2d",
                    "zoomOut2d"
                ]
            },

            key="rainfall_distribution_fixed"

        )


# ============================================================
# END OF FILE
# ============================================================
#
# FINAL DEVELOPER MAP
# ============================================================
#
# [01] Imports
#
# [02] show_home(df)
#       │
#       ├── [03] Hero Section
#       │
#       ├── [04] Quick Access
#       │    ├── [04-A] Rainfall Prediction
#       │    ├── [04-B] Smart Agriculture
#       │    ├── [04-C] Analytics
#       │    └── [04-D] Divider
#       │
#       ├── [05] Analysis Layout
#       │
#       ├── [06] Monthly Rainfall Analysis
#       │    ├── [06-A] Monthly Calculation
#       │    ├── [06-B] Month Names
#       │    ├── [06-C] Area Chart
#       │    ├── [06-D] Chart Settings
#       │    └── [06-E] Chart Display
#       │
#       └── [07] Rainfall Distribution
#            ├── [07-A] Latest 1000 Records
#            ├── [07-B] Histogram
#            ├── [07-C] Chart Settings
#            └── [07-D] Chart Display
#
# ============================================================
# IMPORTANT
# ============================================================
#
# This file:
#
#     DOES:
#       → Display Home page information
#       → Display rainfall analysis charts
#       → Provide quick navigation
#
#     DOES NOT:
#       → Perform rainfall ML prediction
#       → Perform irrigation calculations
#       → Train the ML model
#
# ============================================================