# VOICE.PY — QUICK DEVELOPER INDEX

#
# [01] IMPORTS
#      → Required libraries and gTTS import
#
# [02] SESSION STATE INITIALIZATION
#      → Voice-related Streamlit session state
#
# [03] GLOBAL VOICE ON / OFF SWITCH
#      → Voice system enable / disable
#
# [04] BANGLA TEXT CLEANER
#      → HTML, URL, Email, English words and symbols remove
#
# [05] BANGLA NUMBER CONVERSION
#      → English digits → Bangla digits
#
# [06] PREPARE VOICE TEXT
#      → Final TTS-ready Bangla text preparation
#
# [07] FORMAT IRRIGATION TIME
#      → Decimal hours → ঘণ্টা + মিনিট
#
# [08] GENERATE MP3
#      → gTTS দিয়ে Bangla MP3 তৈরি
#
# [09] SPEAK SEQUENCE
#      → Multiple messages combine + duplicate check + audio generate
#
# [10] RESET VOICE HASH
#      → Duplicate voice detection reset
#
# [11] GROWTH STAGE VOICE
#      → Crop growth stage automatic voice
#
# [12] AGRICULTURE RESULT VOICE
#      → সেচ লাগবে কি না + পানি + সময় + বৃষ্টি না হলে প্রয়োজন
#
# [13] SMART RECOMMENDATION VOICE
#      → Smart Agriculture recommendation voice
#
# [14] SIMPLE SINGLE VOICE
#      → Single text voice shortcut
#
# [15] PLAY VOICE
#      → Simple voice wrapper
#
# [16] WELCOME VOICE
#      → Welcome instruction voice
#
# [17] SELECTION VOICE
#      → User selection-এর পর voice
#
# [18] SECTION VOICE
#      → New section instruction voice
#
# [19] PROCESS VOICE QUEUE
#      → Compatibility function for voice queue
#
# [20] BROWSER VOICE PLAYER
#      → Streamlit browser-এ audio autoplay
#
# [21] CANCEL CURRENT VOICE
#      → Current voice/audio cancel
#
# [22] RESET VOICE STATE
#      → Complete voice state reset
#

# QUICK CHANGE GUIDE
#
# Voice wording change       → [11], [12], [13], [16]-[18]
# Irrigation time format      → [07]
# English/Bangla text filter → [04]
# Number format               → [05]
# gTTS settings               → [08]
# Duplicate voice problem    → [09], [10]
# Audio not playing          → [20]
# Voice ON/OFF               → [03]
# Voice reset/cancel         → [21], [22]
#

# [01] IMPORTS
# Standard library: memory buffer, regular expression, hashing
import io
import re
import hashlib

# Streamlit UI and session state
import streamlit as st

# Google Text-to-Speech
from gtts import gTTS


# [02] SESSION STATE INITIALIZATION
# এই function voice system-এর প্রয়োজনীয় session state তৈরি করে।
def _init_voice_state():

    # Voice system-এর default state values
    defaults = {
        "voice_audio": None,
        "voice_version": 0,
        "voice_rendered_version": -1,
        "voice_hash": None,
        "voice_enabled": True,
    }

    # যেসব key আগে থেকে নেই, শুধু সেগুলো initialize করা হবে।
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# [03] GLOBAL VOICE ON / OFF SWITCH
# Voice বর্তমানে চালু আছে কি না তা check করে।
def is_voice_enabled():

    # Voice state নিশ্চিত করা হচ্ছে।
    _init_voice_state()

    # Voice enabled হলে True return করবে।
    return bool(
        st.session_state.get(
            "voice_enabled",
            True
        )
    )


# Voice system manually ON/OFF করার function।
def set_voice_enabled(enabled):

    # Voice state নিশ্চিত করা হচ্ছে।
    _init_voice_state()

    # User-এর selected voice status save করা হচ্ছে।
    st.session_state["voice_enabled"] = bool(
        enabled
    )


# [04] BANGLA TEXT CLEANER
# TTS-এর জন্য English UI words বাদ দিয়ে
# Bangla-readable text তৈরি করে।
#
# Bangla text এবং Bangla/English digits রাখা হয়।
def clean_voice_text(text):

    # Empty input হলে empty string return।
    if text is None:
        return ""

    # যেকোনো input-কে string করা হচ্ছে।
    text = str(text)

    # [04-A] HTML / TAG REMOVE

    # HTML tag voice-এর মধ্যে পড়া বন্ধ করা হচ্ছে।
    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

  
    # [04-B] URL REMOVE
    # Website URL voice থেকে বাদ দেওয়া হচ্ছে।
    text = re.sub(
        r"https?://\S+|www\.\S+",
        " ",
        text,
        flags=re.IGNORECASE
    )


    # [04-C] EMAIL REMOVE
    # Email address voice থেকে বাদ দেওয়া হচ্ছে।
    text = re.sub(
        r"\S+@\S+\.\S+",
        " ",
        text
    )

    # [04-D] ENGLISH WORDS REMOVE
    # English alphabet-এর শব্দগুলো voice text থেকে বাদ দেওয়া হচ্ছে।
    text = re.sub(
        r"[A-Za-z]+",
        " ",
        text
    )

  
    # [04-E] COMMON SYMBOLS REMOVE
    # Underscore, slash, star, backslash ইত্যাদি বাদ দেওয়া হচ্ছে।
    text = re.sub(
        r"[_/*\\]+",
        " ",
        text
    )

  
    # [04-F] ALLOWED CHARACTERS KEEP

    # Bangla Unicode, Bangla digits, English digits,
    # spaces এবং প্রয়োজনীয় punctuation রাখা হচ্ছে।
    text = re.sub(
        r"[^\u0980-\u09FF\u09E6-\u09EF0-9\s।,!?;:%\-–—()]+",
        " ",
        text
    )

    
    # [04-G] REMOVE DASHES
  
    # Dash-গুলো space দিয়ে replace করা হচ্ছে।
    text = re.sub(
        r"[-–—]+",
        " ",
        text
    )

  
    # [04-H] REMOVE EMPTY BRACKETS
  
    # খালি bracket remove করা হচ্ছে।
    text = re.sub(
        r"\(\s*\)",
        " ",
        text
    )

  
    # [04-I] NORMALIZE SPACES

    # Multiple spaces একটিতে convert করা হচ্ছে।
    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    # Final cleaned text return।
    return text


# [05] BANGLA NUMBER CONVERSION
# English digits-কে Bangla digits-এ convert করে।
def _english_digits_to_bangla(text):

    # English 0-9 এবং Bangla ০-৯ mapping।
    table = str.maketrans(
        "0123456789",
        "০১২৩৪৫৬৭৮৯"
    )

    # Converted text return।
    return text.translate(table)



# [06] PREPARE VOICE TEXT

# TTS generate করার আগে final text preparation করা হয়।
def _prepare_voice_text(text):

    # প্রথমে unwanted content remove করা হচ্ছে।
    text = clean_voice_text(text)

    # Clean করার পরে text না থাকলে কিছু generate হবে না।
    if not text:
        return ""

    # English numbers-কে Bangla numbers-এ convert করা হচ্ছে।
    text = _english_digits_to_bangla(
        text
    )

    # Extra spaces আবার normalize করা হচ্ছে।
    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    # Final TTS-ready text return।
    return text



# [07] FORMAT IRRIGATION TIME

# Decimal hours-কে farmer-friendly
# ঘণ্টা + মিনিটে রূপান্তর করে।
#
# Example:
# 1.0  -> ১ ঘণ্টা
# 1.5  -> ১ ঘণ্টা ৩০ মিনিট
# 0.5  -> ৩০ মিনিট
# 1.75 -> ১ ঘণ্টা ৪৫ মিনিট
# 2.25 -> ২ ঘণ্টা ১৫ মিনিট
def _format_bangla_time(hours):

    # Invalid input handle করার চেষ্টা।
    try:
        total_minutes = round(
            float(hours) * 60
        )
    except (
        TypeError,
        ValueError
    ):
        return ""

    # Zero বা negative time হলে কিছু return করা হবে না।
    if total_minutes <= 0:
        return ""

    # Total minutes থেকে ঘণ্টা বের করা হচ্ছে।
    total_hours = total_minutes // 60

    # Remaining minutes বের করা হচ্ছে।
    minutes = total_minutes % 60

    # Final time parts এখানে রাখা হবে।
    parts = []

 
    # [07-A] HOURS

    if total_hours > 0:

        # Bangla digit-এ ঘণ্টার value তৈরি করা হচ্ছে।
        parts.append(
            f"{_english_digits_to_bangla(str(total_hours))} ঘণ্টা"
        )

  
    # [07-B] MINUTES
  
    if minutes > 0:

        # Bangla digit-এ মিনিটের value তৈরি করা হচ্ছে।
        parts.append(
            f"{_english_digits_to_bangla(str(minutes))} মিনিট"
        )

    # ঘণ্টা + মিনিট একসাথে return।
    return " ".join(parts)



# [08] GENERATE MP3

# Cleaned Bangla text থেকে MP3 audio তৈরি করে।
def _generate_audio(text):

    # TTS-ready text তৈরি করা হচ্ছে।
    clean_text = _prepare_voice_text(
        text
    )

    # Text না থাকলে audio generate করা হবে না।
    if not clean_text:
        return None

    try:

        # Memory-এর মধ্যে audio রাখার জন্য buffer তৈরি।
        audio_buffer = io.BytesIO()

        # Bangla Google TTS তৈরি।
        tts = gTTS(
            text=clean_text,
            lang="bn",
            slow=False
        )

        # Generated audio buffer-এ লেখা হচ্ছে।
        tts.write_to_fp(
            audio_buffer
        )

        # Buffer-এর শুরুতে ফিরে যাওয়া।
        audio_buffer.seek(0)

        # MP3 bytes return।
        return audio_buffer.getvalue()

    except Exception:

        # gTTS / Internet failure হলে
        # Streamlit app crash করবে না।
        return None



# [09] SPEAK SEQUENCE

# Multiple voice messages একসাথে একটি Bangla audio-তে
# convert করে।
def speak_sequence(
    messages,
    delay=0.0
):

    # Voice state initialize করা হচ্ছে।
    _init_voice_state()

  
    # [09-A] GLOBAL VOICE SWITCH
   
    # Voice OFF থাকলে এখানে stop।
    if not is_voice_enabled():
        return

    # Message list না থাকলে কিছু করার নেই।
    if not messages:
        return

  
    # [09-B] PREPARE ALL MESSAGES
   
    # প্রতিটি message clean করে list-এ রাখা হচ্ছে।
    prepared_messages = []

    for message in messages:

        # Individual message clean করা হচ্ছে।
        cleaned = _prepare_voice_text(
            message
        )

        # Empty message বাদ দেওয়া হচ্ছে।
        if cleaned:
            prepared_messages.append(
                cleaned
            )

    # কোনো valid message না থাকলে stop।
    if not prepared_messages:
        return

    
    # [09-C] COMBINE MESSAGES
  
    # Multiple message-এর মাঝে Bangla pause punctuation দেওয়া হচ্ছে।
    final_text = " । ".join(
        prepared_messages
    )

    
    # [09-D] CREATE TEXT HASH
    
    # একই text আবার generate না করার জন্য MD5 hash তৈরি।
    voice_hash = hashlib.md5(
        final_text.encode("utf-8")
    ).hexdigest()

    # [09-E] DUPLICATE CHECK
    
    # একই voice আগে generate হয়ে থাকলে নতুন audio তৈরি হবে না।
    if (
        st.session_state.get(
            "voice_hash"
        )
        == voice_hash
    ):
        return

  
    # [09-F] GENERATE AUDIO
  
    # Final combined text থেকে MP3 generate।
    audio = _generate_audio(
        final_text
    )

    # Audio generate fail করলে stop।
    if audio is None:
        return

 
    # [09-G] SAVE AUDIO

    # Generated audio session state-এ রাখা হচ্ছে।
    st.session_state[
        "voice_audio"
    ] = audio

    # Current text-এর hash save করা হচ্ছে।
    st.session_state[
        "voice_hash"
    ] = voice_hash

    # New audio version number বাড়ানো হচ্ছে।
    st.session_state[
        "voice_version"
    ] = (
        st.session_state.get(
            "voice_version",
            0
        )
        + 1
    )



# [10] RESET VOICE HASH
# Current voice-এর duplicate detection reset করে।
def reset_voice_hash():

    # Voice state initialize করা হচ্ছে।
    _init_voice_state()

    # Hash clear করা হচ্ছে।
    st.session_state[
        "voice_hash"
    ] = None


# [11] GROWTH STAGE VOICE

# Automatically detected crop growth stage-এর জন্য voice।
def growth_stage_auto_voice(
    stage_label,
    next_instruction="মাটির ধরন নির্বাচন করুন"
):

    # Stage না থাকলে voice generate হবে না।
    if not stage_label:
        return

    # Voice pause token।
    PAUSE_TOKEN = "।"

  
    # Bangla voice message:
    # ফসলের বর্তমান বৃদ্ধি পর্যায় জানানো হচ্ছে।

    messages = [
        (
            "স্বয়ংক্রিয়ভাবে আপনার ফসলের "
            f"পর্যায় নির্ধারণ করা হয়েছে {stage_label}।"
        ),

        # User চাইলে manually অন্য growth stage নির্বাচন করতে পারবে।
        (
            "আপনি চাইলে উপরের বৃদ্ধি পর্যায় "
            "থেকে অন্য পর্যায় নির্বাচন করতে পারেন।"
        )
    ]

    # পরবর্তী instruction থাকলে voice sequence-এর শেষে যোগ করা হবে।
    if next_instruction:

        # Extra pause যোগ করা হচ্ছে।
        messages.extend([
            PAUSE_TOKEN,
            PAUSE_TOKEN,
            PAUSE_TOKEN,

            # Bangla next instruction।
            next_instruction
        ])

    # Complete voice sequence generate।
    speak_sequence(
        messages,
        delay=0.10
    )

# [12] AGRICULTURE RESULT VOICE
#
# FARMER-FRIENDLY VOICE FLOW
#
# [12-A] সেচ লাগবে কিনা + কত পানি
# [12-B] কত ঘণ্টা + কত মিনিট
# [12-C] বৃষ্টি না হলে কত পানি + কত ঘণ্টা + কত মিনিট
#
# Technical calculation voice-এ বলা হবে না।
def agriculture_result_voice(
    irrigation_needed,
    water_liters=0,
    irrigation_time_hours=None,
    no_rain_water_liters=None,
    no_rain_time_hours=None,
):

    # Voice messages এখানে জমা হবে।
    messages = []

   
    # [12-A] MAIN DECISION + HOW MUCH WATER
 

    # যদি irrigation প্রয়োজন হয়।
    if irrigation_needed:

        # Water value numeric করার চেষ্টা।
        try:
            water_liters = float(
                water_liters
            )

        except (
            TypeError,
            ValueError
        ):
            water_liters = 0.0

        # Bangla farmer-friendly irrigation message।
        messages.append(
            f"আজ আপনার জমিতে সেচ প্রয়োজন। "
            f"প্রায় {water_liters:.0f} লিটার পানি "
            f"সেচ দিতে হবে।"
        )

    # যদি irrigation প্রয়োজন না হয়।
    else:

        # Bangla no-irrigation message।
        messages.append(
            "আজ আপনার জমিতে অতিরিক্ত সেচ দেওয়ার "
            "প্রয়োজন নেই। জমিতে থাকা পানি এবং "
            "বৃষ্টির পানি বর্তমান প্রয়োজন মেটাতে যথেষ্ট।"
        )


    # [12-B] IRRIGATION TIME

    # Irrigation প্রয়োজন এবং time available হলে।
    if (
        irrigation_needed
        and
        irrigation_time_hours is not None
    ):

        # Decimal hours → Bangla ঘণ্টা/মিনিট।
        time_text = _format_bangla_time(
            irrigation_time_hours
        )

        # Valid time পাওয়া গেলে voice message যোগ।
        if time_text:

            # Bangla irrigation duration message।
            messages.append(
                f"এতে প্রায় {time_text} "
                f"সময় লাগবে।"
            )


    # [12-C] NO RAIN SCENARIO

    # No-rain water value numeric করার চেষ্টা।
    try:
        no_rain_water_value = float(
            no_rain_water_liters
        )

    except (
        TypeError,
        ValueError
    ):
        no_rain_water_value = 0.0

    # No-rain scenario-তে irrigation water প্রয়োজন হলে।
    if no_rain_water_value > 0:

        # Bangla no-rain irrigation message।
        no_rain_line = (
            f"আজ যদি বৃষ্টি না হয়, তাহলে প্রায় "
            f"{no_rain_water_value:.0f} লিটার পানি "
            f"সেচ দিতে হবে।"
        )

        # No-rain irrigation time format করা হচ্ছে।
        no_rain_time_text = _format_bangla_time(
            no_rain_time_hours
        )

        # Time পাওয়া গেলে একই message-এর সাথে যোগ করা হবে।
        if no_rain_time_text:

            # Bangla duration message।
            no_rain_line += (
                f" এতে প্রায় "
                f"{no_rain_time_text} "
                f"সময় লাগবে।"
            )

        # Final no-rain message sequence-এ যোগ।
        messages.append(
            no_rain_line
        )

    # [12-D] FINAL VOICE


    # সব result message একসাথে voice করা হচ্ছে।
    speak_sequence(
        messages
    )


# [13] SMART RECOMMENDATION VOICE
# Agriculture recommendation-এর voice তৈরি করে।
def agriculture_recommendation_voice(
    recommendations
):

    # Recommendation না থাকলে stop।
    if not recommendations:
        return

    # যদি একটি single string হয়।
    if isinstance(
        recommendations,
        str
    ):

        # String-কে single-item list করা হচ্ছে।
        messages = [
            recommendations
        ]

    # যদি list / tuple / iterable হয়।
    else:

        # আলাদা message list তৈরি।
        messages = list(
            recommendations
        )

    # Recommendation voice generate।
    speak_sequence(
        messages
    )


# [14] SIMPLE SINGLE VOICE

# একটি সাধারণ text voice করার shortcut।
def speak(
    text,
    delay=0.0
):

    # Text না থাকলে stop।
    if not text:
        return

    # Single text-কে sequence হিসেবে পাঠানো হচ্ছে।
    speak_sequence(
        [text],
        delay=delay
    )


# [15] PLAY VOICE

# speak() function-এর simple wrapper।
def play_voice(
    text,
    delay=0.0
):

    # সাধারণ voice playback request।
    speak(
        text,
        delay=delay
    )


# [16] WELCOME VOICE

# Agriculture page বা অন্য page-এর welcome voice।
def play_welcome(text):

    # Welcome message voice করা হচ্ছে।
    speak_sequence(
        [text],
        delay=0.10
    )


# [17] SELECTION VOICE
# User কোনো selection করলে voice instruction দেওয়ার জন্য।
def selection_voice(
    text,
    value=None,
    key=None,
    delay=0.12
):

    # Text না থাকলে stop।
    if not text:
        return

    # Selected instruction voice করা হচ্ছে।
    speak_sequence(
        [text],
        delay=delay
    )


# [18] SECTION VOICE

# কোনো নতুন UI section শুরু হলে voice instruction দেওয়ার জন্য।
def section_voice(
    text,
    key=None,
    delay=0.10
):

    # Text না থাকলে stop।
    if not text:
        return

    # Section instruction voice করা হচ্ছে।
    speak_sequence(
        [text],
        delay=delay
    )



# [19] PROCESS VOICE QUEUE

# বর্তমানে আলাদা queue/thread ব্যবহার করা হচ্ছে না।
#
# Functionটি compatibility বজায় রাখার জন্য রাখা হয়েছে।
def process_voice_queue():

    # Voice state initialize করা হচ্ছে।
    _init_voice_state()



# [20] BROWSER VOICE PLAYER

# Browser-এর ভিতরে Bangla audio play করবে।
#
# Streamlit Cloud compatible।
# Server-side playsound ব্যবহার করা হচ্ছে না।
def render_voice_player():

    # Voice state initialize করা হচ্ছে।
    _init_voice_state()

   
    # [20-A] GLOBAL VOICE SWITCH
  
    # Voice OFF থাকলে player render হবে না।
    if not is_voice_enabled():
        return

 
    # [20-B] GET AUDIO STATE

    # Current generated audio নেওয়া হচ্ছে।
    audio = st.session_state.get(
        "voice_audio"
    )

    # Current audio version নেওয়া হচ্ছে।
    version = st.session_state.get(
        "voice_version",
        0
    )

    # সর্বশেষ browser-এ render করা version নেওয়া হচ্ছে।
    rendered_version = st.session_state.get(
        "voice_rendered_version",
        -1
    )

    # Audio না থাকলে কিছু render হবে না।
    if not audio:
        return

  
    # [20-C] SAME AUDIO SHOULD NOT PLAY AGAIN
  
    # একই version ইতিমধ্যে render হয়ে থাকলে পুনরায় play নয়।
    if version == rendered_version:
        return

    # Current version-কে rendered হিসেবে mark করা হচ্ছে।
    st.session_state[
        "voice_rendered_version"
    ] = version

  
    # [20-D] BROWSER AUDIO PLAYER
    
    # Browser-side audio player ব্যবহার করা হচ্ছে।
    st.audio(
        audio,
        format="audio/mp3",
        autoplay=True
    )



# [21] CANCEL CURRENT VOICE

# Current audio এবং hash cancel করে।
def cancel_pending_voice():

    # Voice state initialize করা হচ্ছে।
    _init_voice_state()

    # Current audio remove করা হচ্ছে।
    st.session_state[
        "voice_audio"
    ] = None

    # Duplicate hash clear করা হচ্ছে।
    st.session_state[
        "voice_hash"
    ] = None

    # Version বাড়ানো হচ্ছে যাতে পুরনো audio version আর valid না থাকে।
    st.session_state[
        "voice_version"
    ] = (
        st.session_state.get(
            "voice_version",
            0
        )
        + 1
    )



# [22] RESET VOICE STATE

# সম্পূর্ণ voice state reset করার জন্য।
def reset_voice_state():

    # Voice state initialize করা হচ্ছে।
    _init_voice_state()

    # Current audio clear।
    st.session_state[
        "voice_audio"
    ] = None

    # Current hash clear।
    st.session_state[
        "voice_hash"
    ] = None

    # Voice version reset।
    st.session_state[
        "voice_version"
    ] = 0

    # Rendered version আবার initial অবস্থায় নেওয়া হচ্ছে।
    st.session_state[
        "voice_rendered_version"
    ] = -1