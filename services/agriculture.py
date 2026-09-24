# AGRICULTURE.PY — QUICK DEVELOPER INDEX
#
# [01] IMPORTS
#      → Path, date/datetime, Pandas
#      → Voice service
#
# [02] DATA PATH
#      → Agriculture reference CSV files-এর location
#
# [03] DISPLAY MAPS
#      → Growth Stage English ↔ Bangla display label
#
# [04] SOIL TYPES
#      → Soil information/advisory
#      → Irrigation calculation-এ arbitrary soil multiplier নেই
#
# [05] WATER DEPTH OPTIONS
#      → Existing field water depth → mm
#
# [06] BASIC HELPERS
#      → CSV read
#      → Safe numeric conversion
#      → MM-DD date parsing
#      → Growth stage calculation
#
# [07] CSV LOADING
#      → Crop reference
#      → Kc reference
#      → Crop calendar
#      → Location-wise IWR reference
#
# [08] CROP / SEASON LOOKUP
#      → Crop options
#      → Season options
#      → Crop reference details
#
# [09] CROP CALENDAR
#      → Crop + season calendar lookup
#      → Growing season interval
#      → Reference season resolution
#
# [10] GROWTH STAGE
#      → Initial / Development / Mid / Late
#      → Farmer actual planting date support
#      → Reference calendar support
#      → Out-of-season handling
#
# [11] Kc LOOKUP
#      → Crop + Growth Stage থেকে Kc
#
# [12] LOCATION-WISE IWR REFERENCE
#      → Location options
#      → Crop/season-specific IWR reference
#
# [13] AREA CONVERSION
#      → Decimal / Acre / Hectare / m² → m²
#
# [14] WATER DEPTH → MM
#      → Finger-based / custom depth → mm
#
# [15] EXISTING WATER VOLUME
#      → Existing water mm → Liter / m³
#
# [16] EFFECTIVE RAINFALL
#      → Predicted rainfall থেকে effective rainfall
#
# [17] MAIN IRRIGATION CALCULATION
#      → Area
#      → Kc
#      → ET0 × Kc
#      → Crop water need
#      → Effective rain
#      → Existing water
#      → Net irrigation
#      → Efficiency
#      → Gross irrigation
#      → Water volume
#      → Irrigation status
#
# [18] IRRIGATION METHOD WATER FLOW
#      → Shallow Pump
#      → Deep Tubewell
#      → Drip
#      → Sprinkler
#
# [19] IRRIGATION METHOD OPTIONS
#      → Available irrigation method list
#
# [20] IRRIGATION METHOD CONFIG
#      → Selected method-এর configuration
#
# [21] IRRIGATION TIME CALCULATION
#      → Required water + irrigation method
#      → Flow rate
#      → Number of drippers/sprinklers
#      → Approximate irrigation time
#
# QUICK CHANGE GUIDE
#
# Agriculture CSV file        → [02]
# Crop/season label           → [08]
# Soil information             → [04]
# Existing water options       → [05]
# Growth stage logic           → [10]
# Growth stage percentage      → [06] _stage_from_progress()
# Kc values                    → Kc reference CSV / [11]
# Area conversion              → [13]
# Water depth conversion       → [14]
# Effective rainfall           → [16]
# Main irrigation formula     → [17]
# Irrigation status thresholds → [17]
# Pump flow rate               → [18]
# Drip flow rate               → [18]
# Sprinkler flow input         → [21]
# Irrigation time              → [21]
#
# IMPORTANT:
#
# MAIN WATER CALCULATION:
#
#       ET0
#        ↓
#       Kc
#        ↓
#     Crop Water Need
#        ↓
# Rain + Existing Water
#        ↓
#   Net Water Needed
#        ↓
# Irrigation Efficiency
#        ↓
# Gross Water Requirement
#        ↓
# Liter / m³
#
# IRRIGATION TIME IS A SEPARATE CALCULATION.
#
# calculate_irrigation()
#        ↓
# final water_liters
#        ↓
# calculate_irrigation_time()
#        ↓
# approximate irrigation hours



# [01] IMPORTS

# Project file path handling-এর জন্য।
from pathlib import Path

# Date এবং datetime handling-এর জন্য।
from datetime import date, datetime

# CSV/reference data processing-এর জন্য।
import pandas as pd

# Agriculture result-এর সাথে voice output ব্যবহার করার জন্য।
from services.voice import speak


# [02] DATA PATH

# Project root directory বের করা।
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Agriculture data directory।
DATA_DIR = PROJECT_ROOT / "data"

# Crop water reference CSV।
CROP_REFERENCE_FILE = (
    DATA_DIR / "01_bangladesh_crop_water_reference.csv"
)

# Crop Kc reference CSV।
KC_REFERENCE_FILE = (
    DATA_DIR / "02_crop_kc_reference.csv"
)

# Crop calendar CSV।
CROP_CALENDAR_FILE = (
    DATA_DIR / "03_bangladesh_crop_calendar.csv"
)

# Location-wise irrigation reference CSV।
LOCATION_IWR_FILE = (
    DATA_DIR / "04_bangladesh_location_iwr_reference.csv"
)


# [03] BANGLA / ENGLISH DISPLAY MAPS

# Growth Stage-এর internal English value থেকে
# user-facing Bangla + English label।
STAGE_LABELS = {
    "Initial": "প্রাথমিক পর্যায় (Initial)",
    "Development": "বৃদ্ধি পর্যায় (Development)",
    "Mid": "মধ্য পর্যায় (Mid)",
    "Late": "শেষ পর্যায় (Late)"
}

# Display label → internal English stage conversion।
STAGE_FROM_LABEL = {
    value: key for key, value in STAGE_LABELS.items()
}


# [04] SOIL TYPES
# Soil information/advisory-এর জন্য ব্যবহার করা হয়।
#
# IMPORTANT:
# Soil অনুযায়ী এখানে কোনো arbitrary multiplier
# irrigation calculation-এ প্রয়োগ করা হয় না।

SOIL_TYPES = {

    # Bangla soil description।
    "বেলে মাটি (Sandy Soil)": {
        "description": (
            "বেলে মাটিতে পানি দ্রুত নিচে চলে যেতে পারে। "
            "প্রয়োজন হলে একবারে বেশি পানি না দিয়ে ভাগ করে সেচ দেওয়া যেতে পারে।"
        )
    },

    # Bangla soil description।
    "দোআঁশ মাটি (Loamy Soil)": {
        "description": (
            "দোআঁশ মাটির পানি ধারণক্ষমতা সাধারণত মাঝারি "
            "এবং ফসলের জন্য উপযোগী।"
        )
    },

    # Bangla soil description।
    "এঁটেল মাটি (Clay Soil)": {
        "description": (
            "এঁটেল মাটি পানি তুলনামূলক বেশি সময় ধরে রাখতে পারে। "
            "সেচের আগে জমিতে পানি জমে আছে কিনা দেখা প্রয়োজন।"
        )
    }

}

# [05] WATER DEPTH CONVERSION
# জমিতে বর্তমানে কত গভীর পানি আছে তা user-friendly
# option থেকে millimeter-এ convert করার জন্য।

WATER_DEPTH_OPTIONS = {

    # Bangla water-depth option।
    "পানি নেই (No Water)": 0,

    # Bangla water-depth option।
    "আধা আঙুল (Half Finger)": 8,

    # Bangla water-depth option।
    "১ আঙুল (One Finger)": 15,

    # Bangla water-depth option।
    "২ আঙুল (Two Fingers)": 30,

    # Bangla water-depth option।
    "৩ আঙুল (Three Fingers)": 45,

    # Bangla water-depth option।
    "৪ আঙুল (Four Fingers)": 60

}

# [06] BASIC HELPERS


# [06-A] READ CSV

# Required CSV read করে।
def _read_csv(path):

    # File না থাকলে clear error।
    if not path.exists():

        # Bangla নয়, developer-facing English error।
        raise FileNotFoundError(
            f"Required agriculture data file not found: {path}"
        )

    # CSV → DataFrame।
    return pd.read_csv(path)


# [06-B] SAFE FLOAT

# Invalid/null value থাকলে crash না করে None return করে।
def _safe_float(value):

    # None অথবা NaN হলে।
    if value is None or pd.isna(value):
        return None

    try:

        # Numeric float conversion।
        return float(value)

    except (TypeError, ValueError):

        # Invalid value হলে None।
        return None



# [06-C] MM-DD DATE PARSER

# "MM-DD" format এবং year থেকে date তৈরি করে।
def _parse_mm_dd(mm_dd, year):

    # Empty/NaN value হলে।
    if mm_dd is None or pd.isna(mm_dd):
        return None

    # String conversion।
    text = str(mm_dd).strip()

    # Empty string হলে।
    if not text:
        return None

    try:

        # Month এবং day আলাদা করা।
        month, day = map(
            int,
            text.split("-")
        )

        # Final date তৈরি।
        return date(
            year,
            month,
            day
        )

    except (TypeError, ValueError):

        # Invalid date হলে None।
        return None



# [06-D] STAGE FROM PROGRESS

# Crop progress percentage অনুযায়ী Growth Stage determine করে।
def _stage_from_progress(progress):

    # প্রথম 20% → Initial।
    if progress <= 0.20:
        return "Initial"

    # 20%-45% → Development।
    elif progress <= 0.45:
        return "Development"

    # 45%-80% → Mid।
    elif progress <= 0.80:
        return "Mid"

    # 80%-এর বেশি → Late।
    return "Late"


# [07] CSV LOADING




# [07-A] CROP REFERENCE
# Crop water reference CSV load করে।
def load_crop_reference():
    return _read_csv(
        CROP_REFERENCE_FILE
    )



# [07-B] KC REFERENCE

# Crop Kc reference CSV load করে।
def load_kc_reference():
    return _read_csv(
        KC_REFERENCE_FILE
    )


# [07-C] CROP CALENDAR

# Crop calendar CSV load করে।
def load_crop_calendar():
    return _read_csv(
        CROP_CALENDAR_FILE
    )



# [07-D] LOCATION IWR REFERENCE

# Location-wise IWR CSV optional।
def load_location_iwr_reference():

    # File না থাকলে empty DataFrame return।
    if not LOCATION_IWR_FILE.exists():

        return pd.DataFrame(
            columns=[
                "Crop_or_Season",
                "Location",
                "Net_Irrigation_Reference_mm",
                "Source_Type",
                "Source"
            ]
        )

    # File থাকলে CSV load।
    return pd.read_csv(
        LOCATION_IWR_FILE
    )



# [08] CROP / SEASON LOOKUP




# [08-A] CROP OPTIONS

# CSV থেকে available crop options তৈরি করে।
def get_crop_options():

    # Crop reference load।
    df = load_crop_reference()

    # Final option dictionary।
    options = {}

    # Duplicate crop remove করে iterate।
    for _, row in df.drop_duplicates(
        subset=["Crop"]
    ).iterrows():

        # English crop name।
        crop_en = str(
            row["Crop"]
        ).strip()

        # Bangla crop name থাকলে ব্যবহার।
        crop_bn = (
            str(row["Crop_Bangla"]).strip()
            if pd.notna(
                row.get("Crop_Bangla")
            )
            else crop_en
        )

        # User-facing label।
        label = (
            f"{crop_bn} ({crop_en})"
        )

        # Label → internal crop value।
        options[label] = crop_en

    # Crop options return।
    return options



# [08-B] SEASON OPTIONS

# Selected crop অনুযায়ী available seasons তৈরি করে।
def get_season_options(crop):

    # Crop reference load।
    df = load_crop_reference()

    # Selected crop-এর rows filter।
    rows = df[
        df["Crop"]
        .astype(str)
        .str.strip()
        .str.lower()
        ==
        str(crop)
        .strip()
        .lower()
    ].copy()

    # Final season options।
    options = {}

    # প্রতিটি matching season process।
    for _, row in rows.iterrows():

        # English season।
        season_en = str(
            row["Season"]
        ).strip()

        # Bangla season থাকলে ব্যবহার।
        season_bn = (
            str(
                row["Season_Bangla"]
            ).strip()
            if pd.notna(
                row.get("Season_Bangla")
            )
            else season_en
        )

        # User-facing season label।
        label = (
            f"{season_bn} ({season_en})"
        )

        # Label → internal season।
        options[label] = season_en

    # Season options return।
    return options



# [08-C] CROP REFERENCE

# Crop + Season-এর complete reference information return করে।
def get_crop_reference(crop, season):

    # Crop reference load।
    df = load_crop_reference()

    # Crop + season filter।
    rows = df[
        (
            df["Crop"]
            .astype(str)
            .str.strip()
            .str.lower()
            ==
            str(crop)
            .strip()
            .lower()
        )
        &
        (
            df["Season"]
            .astype(str)
            .str.strip()
            .str.lower()
            ==
            str(season)
            .strip()
            .lower()
        )
    ]

    # Match না থাকলে None।
    if rows.empty:
        return None

    # প্রথম matching row।
    row = rows.iloc[0]

    # Structured crop reference return।
    return {

        "crop": row.get("Crop"),

        "crop_bangla": row.get(
            "Crop_Bangla"
        ),

        "season": row.get(
            "Season"
        ),

        "season_bangla": row.get(
            "Season_Bangla"
        ),

        "crop_group": row.get(
            "Crop_Group"
        ),

        "growing_period": row.get(
            "Growing_Period"
        ),

        "cultivar": row.get(
            "Cultivar"
        ),

        "start_mm_dd": row.get(
            "Start_MM_DD"
        ),

        "end_mm_dd": row.get(
            "End_MM_DD"
        ),

        "duration_days": _safe_float(
            row.get(
                "Reference_Duration_Days"
            )
        ),

        "cwr_mm": _safe_float(
            row.get(
                "Bangladesh_Study_CWR_mm"
            )
        ),

        "iwr_mm": _safe_float(
            row.get(
                "Bangladesh_Study_IWR_mm"
            )
        ),

        "source_type": row.get(
            "Source_Type"
        ),

        "source": row.get(
            "Source"
        ),

        "database_status": row.get(
            "Database_Status"
        )
    }


# [09] CROP CALENDAR


# [09-A] GET CROP CALENDAR RECORD

# Crop + Season অনুযায়ী calendar record return করে।
def get_crop_calendar_record(crop, season):

    # Calendar CSV load।
    df = load_crop_calendar()

    # Crop + season filter।
    rows = df[
        (
            df["Crop"]
            .astype(str)
            .str.strip()
            .str.lower()
            ==
            str(crop)
            .strip()
            .lower()
        )
        &
        (
            df["Season"]
            .astype(str)
            .str.strip()
            .str.lower()
            ==
            str(season)
            .strip()
            .lower()
        )
    ]

    # Match না থাকলে None।
    if rows.empty:
        return None

    # First matching record।
    row = rows.iloc[0]

    # Calendar information return।
    return {

        "crop": row.get(
            "Crop"
        ),

        "season": row.get(
            "Season"
        ),

        "cultivar": row.get(
            "Cultivar"
        ),

        "start_mm_dd": row.get(
            "Start_MM_DD"
        ),

        "end_mm_dd": row.get(
            "End_MM_DD"
        ),

        "duration_days": _safe_float(
            row.get(
                "Reference_Duration_Days"
            )
        ),

        "source_type": row.get(
            "Source_Type"
        ),

        "source": row.get(
            "Source"
        )
    }


# [09-B] MAKE REFERENCE INTERVAL

# Crop season-এর start/end date তৈরি করে।
def _make_reference_interval(
    start_mm_dd,
    end_mm_dd,
    start_year
):

    # Start date তৈরি।
    start_date = _parse_mm_dd(
        start_mm_dd,
        start_year
    )

    # Start date invalid হলে।
    if start_date is None:
        return None, None

    # একই year-এ end date তৈরি করার চেষ্টা।
    end_same_year = _parse_mm_dd(
        end_mm_dd,
        start_year
    )

    # End date invalid হলে শুধু start return।
    if end_same_year is None:
        return start_date, None

    # CROSS-YEAR SEASON

    # End month/day যদি start-এর আগে হয়,
    # তাহলে season next calendar year-এ শেষ হয়।
    if end_same_year < start_date:

        # Next year-এর end date।
        end_date = _parse_mm_dd(
            end_mm_dd,
            start_year + 1
        )

    else:

        # Same-year end date।
        end_date = end_same_year

    # Start + end return।
    return start_date, end_date


# [09-C] RESOLVE REFERENCE SEASON

# Calculation date কোন reference crop season-এর মধ্যে পড়ে
# কি না determine করে।
def resolve_reference_season(
    crop,
    season,
    calculation_date
):

    # Crop calendar record।
    calendar = get_crop_calendar_record(
        crop,
        season
    )

    # Calendar না থাকলে।
    if not calendar:

        return {
            "available": False,
            "in_season": None,
            "start_date": None,
            "end_date": None,
            "calendar": None
        }

    # Raw start/end values।
    start_raw = calendar.get(
        "start_mm_dd"
    )

    end_raw = calendar.get(
        "end_mm_dd"
    )

    # Start/end missing হলে।
    if (
        start_raw is None
        or pd.isna(start_raw)
        or end_raw is None
        or pd.isna(end_raw)
    ):

        return {
            "available": False,
            "in_season": None,
            "start_date": None,
            "end_date": None,
            "calendar": calendar
        }

    # datetime → date conversion।
    if isinstance(
        calculation_date,
        datetime
    ):

        calculation_date = (
            calculation_date.date()
        )

    # Possible season intervals।
    candidate_intervals = []

    # Calculation year-এর আগের, current এবং পরের year check।
    for start_year in [
        calculation_date.year - 1,
        calculation_date.year,
        calculation_date.year + 1
    ]:

        # Reference interval তৈরি।
        start_date, end_date = (
            _make_reference_interval(
                start_raw,
                end_raw,
                start_year
            )
        )

        # Valid interval হলে।
        if start_date and end_date:

            # Candidate list-এ যোগ।
            candidate_intervals.append(
                (
                    start_date,
                    end_date
                )
            )

            # Calculation date season-এর ভিতরে হলে।
            if (
                start_date
                <= calculation_date
                <= end_date
            ):

                return {
                    "available": True,
                    "in_season": True,
                    "start_date": start_date,
                    "end_date": end_date,
                    "calendar": calendar
                }

    # [09-D] OUTSIDE SEASON

    # Date season-এর বাইরে হলে closest reference interval বের করা।
    if candidate_intervals:

        # Calculation date-এর সবচেয়ে কাছের interval।
        closest = min(
            candidate_intervals,
            key=lambda item: min(
                abs(
                    (
                        calculation_date
                        - item[0]
                    ).days
                ),
                abs(
                    (
                        calculation_date
                        - item[1]
                    ).days
                )
            )
        )

        # Closest interval return।
        return {
            "available": True,
            "in_season": False,
            "start_date": closest[0],
            "end_date": closest[1],
            "calendar": calendar
        }

    # কোনো valid interval পাওয়া না গেলে।
    return {
        "available": False,
        "in_season": None,
        "start_date": None,
        "end_date": None,
        "calendar": calendar
    }



# [10] GROWTH STAGE

# Crop calendar অথবা farmer-provided planting date ব্যবহার করে
# Growth Stage determine করে।
def determine_growth_stage(
    crop,
    season,
    calculation_date,
    planting_date=None,
    use_actual_planting_date=False
):

    # Crop calendar record।
    calendar = get_crop_calendar_record(
        crop,
        season
    )

    # Calendar না থাকলে।
    if not calendar:

        # Bangla status message।
        return {
            "status": "NO_CALENDAR",
            "available": False,
            "stage": None,
            "stage_label": None,
            "day_of_crop": None,
            "duration_days": None,
            "progress": None,
            "reference_start_date": None,
            "reference_end_date": None,
            "message": "এই ফসলের জন্য crop calendar data পাওয়া যায়নি।"
        }

    # Reference crop duration।
    duration_days = calendar.get(
        "duration_days"
    )

    # Duration invalid হলে।
    if not duration_days or duration_days <= 0:

        # Bangla error/status message।
        return {
            "status": "NO_DURATION",
            "available": False,
            "stage": None,
            "stage_label": None,
            "day_of_crop": None,
            "duration_days": duration_days,
            "progress": None,
            "reference_start_date": None,
            "reference_end_date": None,
            "message": "এই ফসলের জন্য reference duration পাওয়া যায়নি।"
        }

    # datetime → date conversion।
    if isinstance(
        calculation_date,
        datetime
    ):

        calculation_date = (
            calculation_date.date()
        )


    # [10-A] ACTUAL FARMER PLANTING DATE

    # Farmer actual planting/transplanting date ব্যবহার করতে চাইলে
    # এই branch কাজ করে।
    if use_actual_planting_date:

        # Planting date না থাকলে।
        if planting_date is None:

            return {
                "status": "INVALID_PLANTING_DATE",
                "available": False,
                "stage": None,
                "stage_label": None,
                "day_of_crop": None,
                "duration_days": duration_days,
                "progress": None,
                "reference_start_date": None,
                "reference_end_date": None,
                "message": "প্রকৃত রোপণ/বপনের তারিখ নির্বাচন করুন।"
            }

        # datetime → date conversion।
        if isinstance(
            planting_date,
            datetime
        ):

            planting_date = (
                planting_date.date()
            )

        # Future planting date invalid।
        if planting_date > calculation_date:

            return {
                "status": "FUTURE_PLANTING_DATE",
                "available": False,
                "stage": None,
                "stage_label": None,
                "day_of_crop": None,
                "duration_days": duration_days,
                "progress": None,
                "reference_start_date": None,
                "reference_end_date": None,
                "message": "রোপণ/বপনের তারিখ হিসাবের তারিখের পরে হতে পারে না।"
            }

        # Crop-এর বর্তমান day number।
        day_of_crop = (
            calculation_date
            - planting_date
        ).days + 1

        # Reference duration শেষ হয়ে গেলে।
        if day_of_crop > int(
            round(duration_days)
        ):

            return {
                "status": "CROP_CYCLE_COMPLETE",
                "available": False,
                "stage": None,
                "stage_label": None,
                "day_of_crop": day_of_crop,
                "duration_days": duration_days,
                "progress": (
                    day_of_crop
                    / float(duration_days)
                ),
                "reference_start_date": None,
                "reference_end_date": None,
                "message": (
                    "প্রকৃত রোপণ/বপনের তারিখ অনুযায়ী reference crop "
                    "duration শেষ হয়ে গেছে। তারিখগুলো আবার যাচাই করুন।"
                )
            }

        # Crop progress calculate।
        progress = (
            day_of_crop
            / float(duration_days)
        )

        # Progress → stage।
        stage = _stage_from_progress(
            progress
        )

        # Calculation date-এর reference season।
        reference = resolve_reference_season(
            crop,
            season,
            calculation_date
        )

        # Planting date reference season-এর মধ্যে কি না।
        planting_reference = (
            resolve_reference_season(
                crop,
                season,
                planting_date
            )
        )

        # Default warning।
        warning = None

        # Planting date reference season-এর বাইরে হলে।
        if (
            planting_reference.get(
                "available"
            )
            and
            planting_reference.get(
                "in_season"
            ) is False
        ):

            # Bangla warning।
            warning = (
                "প্রকৃত রোপণ/বপনের তারিখ reference crop calendar-এর বাইরে। "
                "তবুও farmer-provided date অনুযায়ী stage হিসাব করা হয়েছে।"
            )

        # Actual planting date ভিত্তিক result।
        return {
            "status": "IN_SEASON_ACTUAL_DATE",
            "available": True,
            "stage": stage,
            "stage_label": STAGE_LABELS[stage],
            "day_of_crop": day_of_crop,
            "duration_days": duration_days,
            "progress": progress,
            "reference_start_date": reference.get(
                "start_date"
            ),
            "reference_end_date": reference.get(
                "end_date"
            ),
            "message": (
                "কৃষকের দেওয়া প্রকৃত রোপণ/বপনের তারিখ অনুযায়ী "
                "Growth Stage নির্ধারণ করা হয়েছে।"
            ),
            "warning": warning,
            "planting_date": planting_date
        }


  
    # [10-B] REFERENCE CROP CALENDAR DATE

    # Actual planting date ব্যবহার না করলে reference calendar
    # অনুযায়ী stage determine করা হয়।
    reference = resolve_reference_season(
        crop,
        season,
        calculation_date
    )

    # Reference season available না হলে।
    if not reference.get(
        "available"
    ):

        return {
            "status": "NO_CALENDAR_DATES",
            "available": False,
            "stage": None,
            "stage_label": None,
            "day_of_crop": None,
            "duration_days": duration_days,
            "progress": None,
            "reference_start_date": None,
            "reference_end_date": None,
            "message": (
                "এই ফসলের জন্য automatic Growth Stage নির্ধারণের মতো "
                "reference start/end date পাওয়া যায়নি।"
            )
        }

    # Date reference season-এর বাইরে হলে।
    if not reference.get(
        "in_season"
    ):

        return {
            "status": "OUT_OF_SEASON",
            "available": False,
            "stage": None,
            "stage_label": None,
            "day_of_crop": None,
            "duration_days": duration_days,
            "progress": None,
            "reference_start_date": reference.get(
                "start_date"
            ),
            "reference_end_date": reference.get(
                "end_date"
            ),
            "message": (
                "নির্বাচিত তারিখটি এই ফসলের reference growing "
                "season-এর বাইরে।"
            )
        }

    # Reference season-এর start date।
    start_date = reference["start_date"]

    # Crop day calculate।
    day_of_crop = (
        calculation_date
        - start_date
    ).days + 1

    # Calendar end date এবং reference duration সামান্য
    # আলাদা হতে পারে; তাই stage reference duration দিয়ে calculate।
    progress = min(
        day_of_crop
        / float(duration_days),
        1.0
    )

    # Progress → Growth Stage।
    stage = _stage_from_progress(
        progress
    )

    # Final reference-calendar result।
    return {
        "status": "IN_SEASON_REFERENCE",
        "available": True,
        "stage": stage,
        "stage_label": STAGE_LABELS[stage],
        "day_of_crop": day_of_crop,
        "duration_days": duration_days,
        "progress": progress,
        "reference_start_date": reference.get(
            "start_date"
        ),
        "reference_end_date": reference.get(
            "end_date"
        ),
        "message": (
            "Reference crop calendar অনুযায়ী Growth Stage "
            "স্বয়ংক্রিয়ভাবে নির্ধারণ করা হয়েছে।"
        ),
        "warning": None,
        "planting_date": start_date
    }



# [11] Kc LOOKUP

# Crop + Growth Stage অনুযায়ী Kc value বের করে।
def get_kc(
    crop,
    growth_stage
):

    # Kc reference load।
    df = load_kc_reference()

    # Crop + Growth Stage filter।
    rows = df[
        (
            df["Crop"]
            .astype(str)
            .str.strip()
            .str.lower()
            ==
            str(crop)
            .strip()
            .lower()
        )
        &
        (
            df["Growth_Stage"]
            .astype(str)
            .str.strip()
            .str.lower()
            ==
            str(growth_stage)
            .strip()
            .lower()
        )
    ]

    # Match না থাকলে None।
    if rows.empty:
        return None

    # First matching Kc row।
    row = rows.iloc[0]

    # Kc + source information return।
    return {
        "kc": float(
            row["Kc"]
        ),
        "source_type": row.get(
            "Kc_Source_Type"
        ),
        "source": row.get(
            "Kc_Source"
        )
    }



# [12] LOCATION-WISE SEASONAL IWR REFERENCE




# [12-A] LOCATION REFERENCE KEY

# Rice-এর ক্ষেত্রে season দিয়ে reference key তৈরি।
# অন্যান্য crop-এর ক্ষেত্রে crop name ব্যবহার।
def _location_reference_key(
    crop,
    season
):

    # Rice হলে season key।
    if (
        str(crop)
        .strip()
        .lower()
        == "rice"
    ):

        return str(
            season
        ).strip()

    # Other crops-এর জন্য crop key।
    return str(
        crop
    ).strip()



# [12-B] LOCATION OPTIONS

# Selected crop/season-এর available location list।
def get_location_options(
    crop,
    season
):

    # Location reference load।
    df = load_location_iwr_reference()

    # Empty হলে empty list।
    if df.empty:
        return []

    # Relevant lookup key।
    key = _location_reference_key(
        crop,
        season
    )

    # Crop/season key অনুযায়ী rows।
    rows = df[
        df["Crop_or_Season"]
        .astype(str)
        .str.strip()
        .str.lower()
        ==
        key.lower()
    ]

    # Unique sorted location list।
    return sorted(
        rows["Location"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )



# [12-C] LOCATION IWR REFERENCE

# Selected location-এর Net IWR reference return করে।
def get_location_iwr_reference(
    crop,
    season,
    location
):

    # Reference data load।
    df = load_location_iwr_reference()

    # Data অথবা location না থাকলে।
    if df.empty or not location:
        return None

    # Lookup key।
    key = _location_reference_key(
        crop,
        season
    )

    # Crop/season + location filter।
    rows = df[
        (
            df["Crop_or_Season"]
            .astype(str)
            .str.strip()
            .str.lower()
            ==
            key.lower()
        )
        &
        (
            df["Location"]
            .astype(str)
            .str.strip()
            .str.lower()
            ==
            str(location)
            .strip()
            .lower()
        )
    ]

    # Match না থাকলে।
    if rows.empty:
        return None

    # First matching row।
    row = rows.iloc[0]

    # Location IWR reference return।
    return {
        "crop_or_season": row.get(
            "Crop_or_Season"
        ),
        "location": row.get(
            "Location"
        ),
        "net_iwr_reference_mm": _safe_float(
            row.get(
                "Net_Irrigation_Reference_mm"
            )
        ),
        "source_type": row.get(
            "Source_Type"
        ),
        "source": row.get(
            "Source"
        )
    }


# [13] AREA CONVERSION

# User-এর selected land unit → square meter।
def convert_area_to_m2(
    land_area,
    area_unit
):

    # Decimal / শতক → m²।
    if area_unit == "শতক (Decimal)":

        return land_area * 40.4686

    # Acre → m²।
    elif area_unit == "একর (Acre)":

        return land_area * 4046.8564

    # Hectare → m²।
    elif area_unit == "হেক্টর (Hectare)":

        return land_area * 10000

    # Otherwise value already treated as m²।
    else:

        return land_area


# [14] WATER DEPTH → MM

# User-এর selected water depth → millimeter।
def convert_water_depth_to_mm(
    water_measurement,
    custom_depth_cm=0.0
):

    # Custom measurement হলে cm → mm।
    if (
        water_measurement
        ==
        "নিজে পরিমাপ দিন (Custom Measurement)"
    ):

        return custom_depth_cm * 10

    # Preset option থেকে mm নেওয়া।
    return WATER_DEPTH_OPTIONS.get(
        water_measurement,
        0
    )



# [15] CALCULATE EXISTING WATER VOLUME

# Existing water depth + area থেকে total water volume।
def calculate_existing_water_volume(
    area_m2,
    water_depth_mm
):

    # 1 mm water × 1 m² = 1 liter।
    water_liters = (
        area_m2
        * water_depth_mm
    )

    # Liter → cubic meter।
    water_m3 = (
        water_liters
        / 1000
    )

    # Both units return।
    return {
        "water_liters": water_liters,
        "water_m3": water_m3
    }



# [16] EFFECTIVE RAINFALL

# Predicted rainfall-এর পুরোটা irrigation planning-এ
# usable ধরে না নিয়ে simplified effective rainfall হিসাব।
def calculate_effective_rainfall(
    predicted_rain_mm
):

    # Negative rainfall prevent করা।
    predicted_rain_mm = max(
        float(predicted_rain_mm),
        0.0
    )

    # Simplified planning assumption।
    # এটি universal physical law হিসেবে দাবি করা হয়নি।
    if predicted_rain_mm <= 5:

        # Small rainfall-এর 90% effective ধরা।
        return predicted_rain_mm * 0.90

    elif predicted_rain_mm <= 20:

        # Medium rainfall-এর 80% effective ধরা।
        return predicted_rain_mm * 0.80

    else:

        # Higher rainfall-এর 65% effective ধরা।
        return predicted_rain_mm * 0.65



# [17] MAIN IRRIGATION CALCULATION

# Agriculture system-এর মূল irrigation water calculation।
def calculate_irrigation(

    land_area,

    area_unit,

    crop_name,

    crop_stage,

    soil_type,

    existing_water_mm,

    predicted_rain_mm,

    et0_value,

    irrigation_efficiency,

    manual_crop_water_need_mm=None

):


    # [17-A] AREA
  
    # User land area → square meter।
    area_m2 = convert_area_to_m2(
        land_area,
        area_unit
    )


    # [17-B] Kc

    # Crop + Growth Stage অনুযায়ী Kc।
    kc_record = get_kc(
        crop_name,
        crop_stage
    )

    # Kc পাওয়া না গেলে calculation বন্ধ।
    if kc_record is None:

        raise ValueError(
            f"Kc value পাওয়া যায়নি: Crop={crop_name}, "
            f"Stage={crop_stage}"
        )

    # Kc numeric value।
    kc = kc_record["kc"]



    # [17-C] AUTOMATIC CROP WATER REQUIREMENT

    # ET0 = reference evapotranspiration
    # Kc = crop coefficient
    #
    # ETc = ET0 × Kc
    et0_mm = max(
        float(et0_value),
        0.0
    )

    # Automatic crop evapotranspiration।
    automatic_etc_mm = (
        et0_mm
        * kc
    )


  
    # [17-D] WATER REQUIREMENT METHOD
  
    # Manual crop water need দেওয়া থাকলে সেটি ব্যবহার।
    if manual_crop_water_need_mm is not None:

        # Negative manual value prevent।
        crop_water_need = max(
            float(
                manual_crop_water_need_mm
            ),
            0.0
        )

        # Method label।
        water_requirement_method = "MANUAL"

    else:

        # Otherwise automatic ETc ব্যবহার।
        crop_water_need = (
            automatic_etc_mm
        )

        # Method label।
        water_requirement_method = (
            "AUTOMATIC_ETC"
        )


   
    # [17-E] EFFECTIVE RAINFALL

    # Predicted rainfall থেকে effective rainfall।
    effective_rain = (
        calculate_effective_rainfall(
            predicted_rain_mm
        )
    )


   
    # [17-F] AVAILABLE WATER
  
    # Existing field water negative হতে দেওয়া হবে না।
    available_water = max(
        float(existing_water_mm),
        0.0
    )


  
    # [17-G] NET IRRIGATION REQUIREMENT

    # Net water:
    #
    # Crop Water Need
    #       -
    # Effective Rain
    #       -
    # Existing Water
    #
    # Minimum 0।
    net_water_needed = max(
        crop_water_need
        -
        effective_rain
        -
        available_water,
        0
    )


   
    # [17-H] IRRIGATION EFFICIENCY
 
    # Percentage → decimal এবং valid range।
    efficiency = max(
        min(
            float(
                irrigation_efficiency
            ) / 100,
            1.0
        ),
        0.10
    )


    
    # [17-I] GROSS IRRIGATION REQUIREMENT
   
    # Gross water = net requirement / efficiency।
    gross_water_mm = (
        net_water_needed
        / efficiency
    )


    
    # [17-J] WATER VOLUME
    # 1 mm water over 1 m² = 1 liter।
    water_liters = (
        gross_water_mm
        * area_m2
    )

    # Liter → m³।
    water_m3 = (
        water_liters
        / 1000
    )


  
    # [17-K] IRRIGATION STATUS
    # Net requirement zero হলে irrigation প্রয়োজন নেই।
    if net_water_needed <= 0:

        # Internal status।
        status = "NO_IRRIGATION"

        # Bangla user-facing status।
        status_bn = "আজ সেচ প্রয়োজন নেই"

        # English status।
        status_en = "No irrigation needed today"

    # Small requirement।
    elif net_water_needed <= 3:

        status = "LOW"

        # Bangla status।
        status_bn = "অল্প পরিমাণ সেচ দিন"

        status_en = "Light irrigation recommended"

    # Medium requirement।
    elif net_water_needed <= 7:

        status = "MEDIUM"

        # Bangla status।
        status_bn = "মাঝারি পরিমাণ সেচ দিন"

        status_en = "Moderate irrigation recommended"

    # High requirement।
    else:

        status = "HIGH"

        # Bangla status।
        status_bn = "বেশি পরিমাণ সেচ প্রয়োজন"

        status_en = "High irrigation requirement"


    # [17-L] FINAL IRRIGATION RESULT
    # Calculation-এর সব important output dictionary হিসেবে return।
    return {

        # Land area in m²।
        "area_m2": area_m2,

        # ET0।
        "et0_mm": et0_mm,

        # Crop coefficient।
        "kc": kc,

        # Automatically calculated ETc।
        "automatic_etc_mm": automatic_etc_mm,

        # Compatibility / same ETc value।
        "etc_mm": automatic_etc_mm,

        # Final crop water requirement।
        "crop_water_need": crop_water_need,

        # Manual অথবা automatic method।
        "water_requirement_method": (
            water_requirement_method
        ),

        # Original predicted rainfall।
        "predicted_rain": max(
            float(predicted_rain_mm),
            0.0
        ),

        # Effective rainfall।
        "effective_rain": effective_rain,

        # Existing water।
        "existing_water": available_water,

        # Same existing water under another key।
        "available_water": available_water,

        # Net irrigation requirement।
        "net_water_needed": net_water_needed,

        # Efficiency-adjusted gross water।
        "gross_water_mm": gross_water_mm,

        # Efficiency as percentage।
        "irrigation_efficiency": (
            efficiency * 100
        ),

        # Required water in liters।
        "water_liters": water_liters,

        # Required water in cubic meters।
        "water_m3": water_m3,

        # Kc source type।
        "kc_source_type": (
            kc_record.get(
                "source_type"
            )
        ),

        # Kc source।
        "kc_source": (
            kc_record.get(
                "source"
            )
        ),

        # Selected soil type.
        "soil_type": soil_type,

        # Internal status।
        "status": status,

        # Bangla status.
        "status_bn": status_bn,

        # English status.
        "status_en": status_en
    }



# [18] IRRIGATION METHOD WATER FLOW
#
# IMPORTANT:
# এগুলো representative/default planning values।
# নির্দিষ্ট pump, dripper বা sprinkler-এর guaranteed discharge নয়।
# Actual field discharge ভিন্ন হতে পারে।
#
# এই section calculate_irrigation()-এর মূল calculation logic
# পরিবর্তন করে না।
#
# calculate_irrigation() থেকে পাওয়া final water_liters ব্যবহার করে
# selected irrigation method অনুযায়ী আনুমানিক সময় হিসাব করা হয়।

IRRIGATION_METHODS = {

    # Shallow pump-এর representative/default flow।
    "শ্যালো পাম্প দিয়ে সেচ (Shallow Pump)": {
        "type": "FIXED_FLOW",
        "default_flow_lph": 60000.0,
        "default_efficiency": 60
    },

    # Deep tubewell-এর representative/default flow।
    "ডিপ টিউবওয়েল দিয়ে সেচ (Deep Tubewell)": {
        "type": "FIXED_FLOW",
        "default_flow_lph": 180000.0,
        "default_efficiency": 60
    },

    # Drip system-এর per-dripper representative flow।
    "ড্রিপ/ফোঁটা ফোঁটা সেচ (Drip Irrigation)": {
        "type": "PER_DRIPPER",
        "default_flow_per_unit_lph": 3.4,
        "default_efficiency": 90
    },

    # Sprinkler-এর flow user input হিসেবে নেওয়া হয়।
    "স্প্রিংকলার সেচ (Sprinkler Irrigation)": {
        "type": "PER_SPRINKLER",
        "default_flow_per_unit_lph": None,
        "default_efficiency": 75
    }

}



# [19] IRRIGATION METHOD OPTIONS

# UI dropdown/selectbox-এর জন্য available method list।
def get_irrigation_method_options():

    # Dictionary keys = user-facing irrigation methods।
    return list(
        IRRIGATION_METHODS.keys()
    )


# [20] IRRIGATION METHOD CONFIG

# Selected method-এর configuration return করে।
def get_irrigation_method_config(
    method_label
):

    # Selected method config।
    return IRRIGATION_METHODS.get(
        method_label
    )



# [21] IRRIGATION TIME CALCULATION

# calculate_irrigation() থেকে পাওয়া final water_liters
# এবং selected irrigation method ব্যবহার করে approximate
# irrigation time হিসাব করে।
def calculate_irrigation_time(
    water_liters,
    irrigation_needed,
    method_label,
    num_drippers=None,
    num_sprinklers=None,
    flow_per_sprinkler_lph=None
):
    """
    calculate_irrigation()-এর final water_liters ব্যবহার করে
    selected irrigation method অনুযায়ী আনুমানিক irrigation time
    হিসাব করে।

    এখানে ET0, Kc, rainfall, existing water বা মূল irrigation
    calculation পরিবর্তন করা হয় না।
    """

   
    # [21-A] DEFAULT RESULT

    # শুরুতে calculation unavailable ধরা হচ্ছে।
    result = {
        "available": False,
        "total_flow_lph": None,
        "hours": None,
        "needs_flow_input": False,
        "method_type": None,
        "num_units": None,
        "flow_per_unit_lph": None
    }


    
    # [21-B] NO IRRIGATION
  
    # Irrigation দরকার না হলে irrigation time-ও দরকার নেই।
    if not irrigation_needed:

        # Default unavailable result return।
        return result


    
    # [21-C] VALIDATE WATER AMOUNT
   
    # Water amount numeric কি না check।
    try:

        # Float conversion।
        water_liters = float(
            water_liters
        )

    except (TypeError, ValueError):

        # Invalid value হলে default result।
        return result

    # Zero/negative water হলে time calculation প্রয়োজন নেই।
    if water_liters <= 0:

        return result


  
    # [21-D] GET METHOD CONFIG
 
    # Selected irrigation method configuration।
    config = IRRIGATION_METHODS.get(
        method_label
    )

    # Unknown method হলে।
    if config is None:

        return result

    # Method type।
    method_type = config.get(
        "type"
    )

    # Result-এ method type save।
    result["method_type"] = (
        method_type
    )



    # [21-E] FIXED FLOW METHODS
 
    # Shallow Pump / Deep Tubewell।
    if method_type == "FIXED_FLOW":

        # Default flow rate নেওয়া।
        total_flow_lph = _safe_float(
            config.get(
                "default_flow_lph"
            )
        )

        # Invalid flow হলে calculation unavailable।
        if (
            total_flow_lph is None
            or total_flow_lph <= 0
        ):

            return result


   
    # [21-F] DRIP
 
    # Drip-এর total flow =
    # number of drippers × flow per dripper।
    elif method_type == "PER_DRIPPER":

        # Number of drippers numeric করার চেষ্টা।
        try:

            num_drippers = float(
                num_drippers
            )

        except (
            TypeError,
            ValueError
        ):

            # Invalid হলে zero।
            num_drippers = 0

        # Dripper count missing হলে user input দরকার।
        if num_drippers <= 0:

            # Flow input requirement mark।
            result[
                "needs_flow_input"
            ] = True

            return result

        # Default per-dripper flow।
        flow_per_unit = _safe_float(
            config.get(
                "default_flow_per_unit_lph"
            )
        )

        # Invalid flow হলে।
        if (
            flow_per_unit is None
            or flow_per_unit <= 0
        ):

            return result

        # Total drip flow।
        total_flow_lph = (
            num_drippers
            * flow_per_unit
        )

        # Unit count save।
        result[
            "num_units"
        ] = num_drippers

        # Per-unit flow save।
        result[
            "flow_per_unit_lph"
        ] = flow_per_unit


   
    # [21-G] SPRINKLER
    # Sprinkler-এর flow user input থেকে আসে।
    elif method_type == "PER_SPRINKLER":

        # Number of sprinklers numeric করার চেষ্টা।
        try:

            num_sprinklers = float(
                num_sprinklers
            )

        except (
            TypeError,
            ValueError
        ):

            # Invalid হলে zero।
            num_sprinklers = 0

        # Flow per sprinkler numeric করার চেষ্টা।
        try:

            flow_per_sprinkler_lph = float(
                flow_per_sprinkler_lph
            )

        except (
            TypeError,
            ValueError
        ):

            # Invalid হলে zero।
            flow_per_sprinkler_lph = 0

        # Sprinkler count বা flow missing হলে।
        if (
            num_sprinklers <= 0
            or flow_per_sprinkler_lph <= 0
        ):

            # User input required।
            result[
                "needs_flow_input"
            ] = True

            return result

        # Total sprinkler flow।
        total_flow_lph = (
            num_sprinklers
            *
            flow_per_sprinkler_lph
        )

        # Number of sprinklers save।
        result[
            "num_units"
        ] = num_sprinklers

        # Per-sprinkler flow save।
        result[
            "flow_per_unit_lph"
        ] = (
            flow_per_sprinkler_lph
        )


    
    # [21-H] UNKNOWN METHOD
 
    # Supported method ছাড়া অন্য কিছু হলে।
    else:

        return result



    # [21-I] FINAL IRRIGATION TIME

    # Flow valid কি না।
    if total_flow_lph <= 0:

        return result

    # Time in hours:
    #
    # Water volume (Liter)
  
    # Flow (Liter/hour)
    #
    irrigation_hours = (
        water_liters
        /
        total_flow_lph
    )

    # Calculation available।
    result[
        "available"
    ] = True

    # Total flow save।
    result[
        "total_flow_lph"
    ] = total_flow_lph

    # Irrigation time in hours save।
    result[
        "hours"
    ] = irrigation_hours

    # Final irrigation-time result।
    return result