import streamlit as st
import pandas as pd


def show_data_page(df):

    st.title(
        "📂 Historical Weather Dataset"
    )

    # ============================================================
    # DATASET SUMMARY
    # ============================================================

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Records",
        f"{len(df):,}"
    )

    c2.metric(
        "Stations",
        df.Station_ID.nunique()
    )

    c3.metric(
        "Period",
        f"{df.Date.min().date()} → {df.Date.max().date()}"
    )


    # ============================================================
    # FILTERS
    # ============================================================

    s1, s2, s3 = st.columns(3)

    station = s1.selectbox(
        "Station",
        ["All"] + sorted(
            df.Station.astype(str).unique()
        )
    )

    division = s2.selectbox(
        "Division",
        ["All"] + sorted(
            df.Division.astype(str).unique()
        )
    )

    dates = s3.date_input(
        "Date Range",
        value=(
            df.Date.min().date(),
            df.Date.max().date()
        ),
        key="historical_date_range"
    )


    # ============================================================
    # APPLY FILTERS
    # ============================================================

    x = df.copy()

    if station != "All":

        x = x[
            x.Station.astype(str) == station
        ]

    if division != "All":

        x = x[
            x.Division.astype(str) == division
        ]

    if (
        isinstance(dates, tuple)
        and len(dates) == 2
    ):

        x = x[
            (
                x.Date
                >=
                pd.Timestamp(dates[0])
            )
            &
            (
                x.Date
                <=
                pd.Timestamp(dates[1])
            )
        ]


    # ============================================================
    # DISPLAY FILTERED DATA
    # ============================================================

    st.dataframe(
        x,
        width="stretch",
        height=480
    )