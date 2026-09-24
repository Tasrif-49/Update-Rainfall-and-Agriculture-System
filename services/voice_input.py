
# VOICE_INPUT.PY — QUICK DEVELOPER INDEX

#
# [01] MODULE PURPOSE
#      → Agriculture page-এর optional Speech-to-Text input
#      → services.voice.py-এর TTS flow আলাদা রাখা
#
# [02] IMPORTS
#      → Audio processing, regex, date parsing
#      → Streamlit, microphone recorder, Speech Recognition
#
# [03] BANGLA DIGIT MAPPING
#      → Bangla digits → English digits
#
# [04] BANGLA MONTH MAPPING
#      → Bangla month name → month number
#
# [05] BANGLA NUMBER WORDS
#      → এক, দুই, তিন... → numeric value
#
# [06] ENGLISH NUMBER WORDS
#      → one, two, three... → numeric value
#
# [07] TEXT NORMALIZATION
#      → Voice transcript clean + normalize
#
# [08] NUMBER PARSING
#      → Spoken number → numeric value
#      → Decimal / দশমিক / point / hundred handling
#
# [09] NUMBER VALIDATION
#      → Minimum / maximum range check
#
# [10] OPTION SUGGESTION LABELS
#      → Voice ভুল option বললে available option-এর label
#
# [11] OPTION SUGGESTION VOICE
#      → ভুল option হলে valid options voice-এ জানানো
#
# [12] OPTION PARSING
#      → Voice transcript → matching Streamlit option
#      → Similarity / word matching
#
# [13] DATE PARSING
#      → Bangla/English month + day + year
#      → YYYY-MM-DD / DD-MM-YYYY / DD/MM/YYYY
#
# [14] GENERIC VALUE PARSER
#      → number / option / date / text আলাদা করা
#
# [15] APPLY PENDING VOICE INPUT
#      → Previous rerun-এর voice value widget-এ apply
#
# [16] VOICE INPUT WIDGET
#      → Microphone open
#      → Speech record
#      → Speech-to-Text
#      → Number / Option / Date parsing
#      → Validation + warning
#      → Pending value save
#      → Streamlit rerun
#      → Recognized speech display
#

# QUICK CHANGE GUIDE

#
# Number voice parsing       → [08], [09]
# Bangla number support      → [05]
# English number support     → [06]
# Month/date voice           → [13]
# Option matching            → [12]
# Wrong option suggestion    → [10], [11]
# Microphone settings        → [16]
# Speech recognition        → [16]
# Voice language             → [16] recognize_google()
# Voice button text          → [16] mic_recorder()
# Pending widget value       → [15]
# Recognized speech display  → [16]
# Voice input error handling → [16]
#

# IMPORTANT
#
# This file handles:
#     SPEECH → TEXT → VALUE
#
# services.voice.py handles:
#     TEXT → BANGLA AUDIO → BROWSER PLAYBACK
#
# Normal typing / manual selection should remain unchanged.



# [01] MODULE PURPOSE
# Agriculture page-এর optional Speech-to-Text input helper।
#
# এই module:
# Speech → Text → Parsed Value
# flow handle করে।
#
# এটি services.voice.py-এর existing TTS flow পরিবর্তন করে না.



# [02] IMPORTS

# Memory buffer-এর জন্য।
import io

# Text cleaning এবং pattern matching-এর জন্য।
import re

# Date object-এর জন্য।
from datetime import date

# Voice option matching-এর similarity calculation-এর জন্য।
from difflib import SequenceMatcher

# Streamlit session state এবং UI-এর জন্য।
import streamlit as st

# Browser microphone recording-এর জন্য।
from streamlit_mic_recorder import mic_recorder

# Speech-to-Text recognition-এর জন্য।
import speech_recognition as sr



# [03] BANGLA DIGIT MAPPING

# Bangla digits → English digits conversion।
BN_DIGITS = str.maketrans(
    "০১২৩৪৫৬৭৮৯",
    "0123456789"
)



# [04] BANGLA MONTH MAPPING

# Bangla month name → numeric month।
BN_MONTHS = {
    "জানুয়ারি": 1,
    "জানুয়ারি": 1,
    "ফেব্রুয়ারি": 2,
    "ফেব্রুয়ারি": 2,
    "মার্চ": 3,
    "এপ্রিল": 4,
    "মে": 5,
    "জুন": 6,
    "জুলাই": 7,
    "আগস্ট": 8,
    "সেপ্টেম্বর": 9,
    "অক্টোবর": 10,
    "নভেম্বর": 11,
    "ডিসেম্বর": 12,
}



# [05] BANGLA NUMBER WORDS

# Spoken Bangla number → numeric value।
NUMBER_WORDS = {
    "শূন্য": 0,
    "এক": 1,
    "দুই": 2,
    "দুইটা": 2,
    "দুটি": 2,
    "তিন": 3,
    "চার": 4,
    "পাঁচ": 5,
    "ছয়": 6,
    "ছয়": 6,
    "সাত": 7,
    "আট": 8,
    "নয়": 9,
    "নয়": 9,
    "দশ": 10,
    "এগারো": 11,
    "বারো": 12,
    "তেরো": 13,
    "চৌদ্দ": 14,
    "পনেরো": 15,
    "ষোল": 16,
    "সতেরো": 17,
    "আঠারো": 18,
    "উনিশ": 19,
    "বিশ": 20,
    "ত্রিশ": 30,
    "চল্লিশ": 40,
    "পঞ্চাশ": 50,
    "ষাট": 60,
    "সত্তর": 70,
    "আশি": 80,
    "নব্বই": 90,
    "একশ": 100,
    "একশো": 100,
}


# [06] ENGLISH NUMBER WORDS
# Spoken English number → numeric value।
EN_NUMBER_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
    "hundred": 100,
}



# [07] TEXT NORMALIZATION
# Voice transcript clean এবং normalize করে।
def _norm(text):

    # Empty/null input handle করে lowercase করা।
    text = str(text or "").strip().lower()

    # Bangla digits → English digits।
    text = text.translate(BN_DIGITS)

    # Common punctuation remove করে space দেওয়া।
    text = re.sub(
        r"[।,;:!?]+",
        " ",
        text
    )

    # Multiple spaces → single space।
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    # Final normalized text।
    return text



# [08] NUMBER PARSING
# Spoken number বা numeric text থেকে number বের করে।
def _number_from_words(text):

    # Input normalize করা।
    t = _norm(text)

 
    # [08-A] DIRECT DIGIT / DECIMAL

    # Arabic/Bangla converted digits এবং decimal detect।
    m = re.search(
        r"\d+(?:\.\d+)?",
        t
    )

    # Direct number পাওয়া গেলে সেটি return।
    if m:
        return float(m.group(0))

    # Text-কে individual words-এ ভাগ করা।
    words = t.split()

    # Recognized numeric values এখানে জমা হবে।
    values = []

    # প্রতিটি word number dictionary-এর সাথে match।
    for word in words:

        # Bangla number হলে।
        if word in NUMBER_WORDS:
            values.append(
                NUMBER_WORDS[word]
            )

        # English number হলে।
        elif word in EN_NUMBER_WORDS:
            values.append(
                EN_NUMBER_WORDS[word]
            )

    # কোনো number পাওয়া না গেলে।
    if not values:
        return None

    
    # [08-B] DECIMAL NUMBER
    
    # যেমন:
    # "দুই দশমিক পাঁচ"
    # "two point five"
    if "দশমিক" in words or "point" in words:

        # কোন decimal marker ব্যবহার হয়েছে তা detect।
        marker = (
            "দশমিক"
            if "দশমিক" in words
            else "point"
        )

        # Decimal marker-এর অবস্থান।
        i = words.index(marker)

        # Decimal-এর আগের values।
        left = values[:i]

        # Decimal-এর পরের words।
        right_words = words[i + 1:]

        # Decimal অংশের values।
        right = []

        # Decimal-এর পরের প্রতিটি word parse।
        for w in right_words:

            # Bangla number।
            if w in NUMBER_WORDS:
                right.append(
                    str(NUMBER_WORDS[w])
                )

            # English number।
            elif w in EN_NUMBER_WORDS:
                right.append(
                    str(EN_NUMBER_WORDS[w])
                )

            # Direct digit।
            elif w.isdigit():
                right.append(w)

        # Left এবং right দুই অংশ পাওয়া গেলে decimal তৈরি।
        if left and right:
            return float(
                f"{sum(left)}.{''.join(right)}"
            )

    
    # [08-C] HUNDRED FORM
    
    # যেমন:
    # "একশ"
    # "দুইশ"
    # ধরনের simple compound handling।
    if 100 in values and len(values) > 1:

        # Final total।
        total = 0

        # Current section।
        current = 0

        # প্রতিটি numeric value process।
        for v in values:

            # 100 পাওয়া গেলে multiplier হিসেবে কাজ করবে।
            if v == 100:

                # Minimum multiplier 1।
                current = max(
                    1,
                    current
                ) * 100

                # Total-এ যোগ।
                total += current

                # Current reset।
                current = 0

            # অন্য number হলে current-এ যোগ।
            else:
                current += v

        # Final result।
        return float(
            total + current
        )


    # [08-D] SIMPLE COMPOUND NUMBER

    # সাধারণ recognized values যোগ করা।
    return float(
        sum(values)
    )


# [09] NUMBER VALIDATION

# Parsed number-এর minimum/maximum range check করে।
def parse_number(
    text,
    minimum=None,
    maximum=None
):

    # Spoken text থেকে number বের করা।
    value = _number_from_words(text)

    # Number detect না হলে Bangla error।
    if value is None:

        # Bangla error message।
        raise ValueError(
            "সংখ্যাটি বোঝা যায়নি। আবার বলুন।"
        )

    # Minimum limit check।
    if minimum is not None and value < minimum:

        # Bangla validation message।
        raise ValueError(
            f"মানটি {minimum} এর চেয়ে কম হতে পারবে না।"
        )

    # Maximum limit check।
    if maximum is not None and value > maximum:

        # Bangla validation message।
        raise ValueError(
            f"মানটি {maximum} এর চেয়ে বেশি হতে পারবে না।"
        )

    # Valid number return।
    return value


# [10] OPTION SUGGESTION LABELS

# ভুল option বললে কোন field-এর options জানানো হবে।
OPTION_SUGGESTION_LABELS = {

    "agriculture_weather_source":
        "বৃষ্টির তথ্যের উৎস",

    "agriculture_area_unit":
        "জমির একক",

    "agriculture_crop_select":
        "ফসল",

    "agriculture_season_select":
        "মৌসুম",

    "agriculture_growth_stage":
        "বৃদ্ধি পর্যায়",

    "agriculture_growth_stage_fallback":
        "বৃদ্ধি পর্যায়",

    "agriculture_out_of_season_stage":
        "বৃদ্ধি পর্যায়",

    "agriculture_soil_type":
        "মাটির ধরন",

    "agriculture_water_measurement":
        "পানির গভীরতার ধরন",

    "agriculture_water_requirement_method":
        "পানির চাহিদা নির্ধারণের পদ্ধতি",

    "agriculture_irrigation_method":
        "সেচ পদ্ধতি",

    "agriculture_reference_period":
        "সময়কাল",
}


# [11] CLEAN OPTION FOR VOICE

# Option-এর Bangla label রাখা এবং parentheses-এর
# English text remove করা।
def _clean_option_for_voice(option):

    # Option-কে string করা।
    text = str(option or "")

    # Parentheses-এর ভিতরের text remove।
    text = re.sub(
        r"\([^)]*\)",
        "",
        text
    )

    # Extra spaces এবং surrounding dash remove।
    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip(" -–—")

    # Clean option return।
    return text


# [12] OPTION SUGGESTION VOICE

# User ভুল option বললে valid options voice-এ জানায়।
def _speak_option_suggestion(
    key,
    transcript,
    options
):

    # Options না থাকলে stop।
    if not options:
        return

    try:

        # Existing TTS module lazily import করা হচ্ছে।
        # এতে voice_input.py import করার সময়
        # services.voice dependency আলাদা রাখা যায়।
        from services.voice import speak_sequence

        # Field-এর Bangla label নেওয়া হচ্ছে।
        label = OPTION_SUGGESTION_LABELS.get(
            key,
            "এই অংশে"
        )

        # সব valid option-এর voice-friendly version তৈরি।
        spoken_options = [
            _clean_option_for_voice(option)
            for option in options
            if _clean_option_for_voice(option)
        ]

        # কোনো valid option না থাকলে stop।
        if not spoken_options:
            return

        # User কী বলেছে সেটি clean করা।
        transcript_text = _clean_option_for_voice(
            transcript
        )

        # Bangla suggestion message তৈরি।
        message = (
            f"আপনি বলেছেন {transcript_text}। "
            f"{label} রয়েছে: "
            + ", ".join(spoken_options)
            + "। অনুগ্রহ করে তালিকা থেকে একটি নির্বাচন করুন।"
        )

        # Suggestion voice generate।
        speak_sequence(
            [message],
            delay=0.05
        )

    except Exception:

        # Suggestion voice fail করলেও
        # Agriculture page যেন crash না করে।
        pass



# [13] OPTION PARSING

# Voice transcript থেকে available option-এর সবচেয়ে কাছের
# option নির্বাচন করে।
def parse_option(
    text,
    options
):

    # Options না থাকলে error।
    if not options:
        raise ValueError(
            "এই field-এর option পাওয়া যায়নি।"
        )

    # User query normalize করা।
    query = _norm(text)

    # Best matching option track করা।
    best = None

    # Highest similarity score track করা।
    best_score = 0.0

    # প্রতিটি available option check।
    for option in options:

        # Option normalize।
        candidate = _norm(option)

        # Full text similarity।
        score = SequenceMatcher(
            None,
            query,
            candidate
        ).ratio()

       
        # WORD-BASED MATCHING

        # Bangla + English label-এর জন্য word matching।
        q_words = set(
            query.split()
        )

        c_words = set(
            candidate.split()
        )

        # দুই side-এ word থাকলে overlap score।
        if q_words and c_words:

            # Matching words-এর ratio।
            score = max(
                score,
                len(q_words & c_words)
                / len(q_words | c_words)
            )

        # Query candidate-এর ভিতরে থাকলে strong match।
        if query and query in candidate:
            score = max(
                score,
                0.90
            )

        # Highest score update।
        if score > best_score:
            best_score = score
            best = option

    # Minimum confidence threshold।
    if best is None or best_score < 0.34:

        # Match না হলে Bangla error।
        raise ValueError(
            "কথাটি কোনো option-এর সাথে মেলানো যায়নি।"
        )

    # Best matching option return।
    return best



# [14] DATE PARSING
# Voice transcript থেকে date তৈরি করে।
def parse_date(text):

    # Transcript normalize।
    t = _norm(text)

    # [14-A] NUMERIC DATE

    # Supported examples:
    # YYYY-MM-DD
    # DD-MM-YYYY
    # DD/MM/YYYY
    nums = [
        int(x)
        for x in re.findall(
            r"\d+",
            t
        )
    ]

    # তিনটি numeric component পাওয়া গেলে।
    if len(nums) >= 3:

        # প্রথম number year হলে YYYY-MM-DD ধরে।
        if nums[0] >= 1900:

            return date(
                nums[0],
                nums[1],
                nums[2]
            )

        # শেষ number year হলে DD-MM-YYYY ধরে।
        if nums[2] >= 1900:

            return date(
                nums[2],
                nums[1],
                nums[0]
            )


    # [14-B] BANGLA MONTH
   
    # Month number এখানে রাখা হবে।
    month = None

    # Bangla month dictionary check।
    for name, number in BN_MONTHS.items():

        # Month name transcript-এ থাকলে।
        if name in t:
            month = number
            break

 
    # [14-C] ENGLISH MONTH

    # Bangla month না পাওয়া গেলে English month check।
    if month is None:

        # English month mapping।
        english_months = {
            "january": 1,
            "february": 2,
            "march": 3,
            "april": 4,
            "may": 5,
            "june": 6,
            "july": 7,
            "august": 8,
            "september": 9,
            "october": 10,
            "november": 11,
            "december": 12,
        }

        # English month match।
        for name, number in english_months.items():

            # Month পাওয়া গেলে।
            if name in t:
                month = number
                break

    # Month পাওয়া না গেলে error।
    if month is None:

        # Bangla example দিয়ে error।
        raise ValueError(
            "মাস বোঝা যায়নি। যেমন: ১৫ সেপ্টেম্বর ২০২৬ বলুন।"
        )

    
    # [14-D] YEAR
  
    # 1900 বা তার বেশি number-গুলো year হিসেবে নেওয়া।
    years = [
        n for n in nums
        if n >= 1900
    ]

    # First valid year।
    year = years[0] if years else None

 
    # [14-E] DAY
   
    # 1-31-এর মধ্যে number নিয়ে day candidate তৈরি।
    day_candidates = [
        n for n in nums
        if n != year and 1 <= n <= 31
    ]

    # Year বা day missing হলে error।
    if year is None or not day_candidates:

        # Bangla date error।
        raise ValueError(
            "তারিখটি সম্পূর্ণ বোঝা যায়নি। "
            "দিন, মাস ও বছর বলুন।"
        )

    # Final Python date object।
    return date(
        year,
        month,
        day_candidates[0]
    )



# [15] GENERIC VALUE PARSER

# Field type অনুযায়ী correct parser select করে।
def _parse(
    text,
    value_type,
    options=None,
    minimum=None,
    maximum=None
):

    # Number field হলে number parser।
    if value_type == "number":

        return parse_number(
            text,
            minimum,
            maximum
        )

    # Option field হলে option parser।
    if value_type == "option":

        return parse_option(
            text,
            options or []
        )

    # Date field হলে date parser।
    if value_type == "date":

        return parse_date(text)

    # অন্য type হলে সাধারণ text return।
    return str(text).strip()



# [16] APPLY PENDING VOICE INPUT

# Previous rerun-এ captured value current widget-এর
# আগে apply করার জন্য।
def prepare_voice_input(key):

    # Pending value-এর session-state key।
    pending_key = (
        f"voice_input_pending_{key}"
    )

    # Applied state-এর session-state key।
    applied_key = (
        f"voice_input_applied_{key}"
    )

    # Pending value না থাকলে কিছু করার নেই।
    if pending_key not in st.session_state:
        return False

    # Pending value এবং transcript বের করে remove।
    value, transcript = st.session_state.pop(
        pending_key
    )

    # Target widget-এর session state-এ parsed value বসানো।
    st.session_state[key] = value

    # Exact recognized transcript save করা।
    st.session_state[
        f"voice_input_transcript_{key}"
    ] = transcript

    # Applied status mark করা।
    st.session_state[applied_key] = True

    # Successfully applied।
    return True


# [17] MAIN VOICE INPUT WIDGET

# একটি microphone control তৈরি করে এবং
# voice transcript/value capture করে।
def voice_input_widget(
    key,
    prompt,
    value_type="text",
    options=None,
    minimum=None,
    maximum=None,
):

  
    # [17-A] MICROPHONE CONTROL
 
    # Browser microphone recorder তৈরি।
    result = mic_recorder(

        # Bangla microphone start button text।
        start_prompt="🎤 ভয়েসে বলুন",

        # Bangla recording stop button text।
        stop_prompt="⏹️ রেকর্ডিং বন্ধ করুন",

        # একবার recording নেওয়া হবে।
        just_once=True,

        # Container width automatic নয়।
        use_container_width=False,

        # Audio format WAV।
        format="wav",

        # প্রতিটি field-এর জন্য unique microphone key।
        key=f"voice_input_mic_{key}",
    )

    # Recording পাওয়া গেলে process শুরু।
    if result and result.get("bytes"):

        try:

     
            # [17-B] SPEECH RECOGNIZER
           
            # Speech Recognition engine তৈরি।
            recognizer = sr.Recognizer()

            # Recorded WAV bytes audio source হিসেবে open।
            with sr.AudioFile(
                io.BytesIO(result["bytes"])
            ) as source:

                # Audio record করা।
                audio = recognizer.record(
                    source
                )

           
            # [17-C] SPEECH → TEXT
          
            # Bangla-Bangladesh language recognition।
            transcript = recognizer.recognize_google(
                audio,
                language="bn-BD"
            )

            # [17-D] SAVE EXACT TRANSCRIPT
          
            # User যা বলেছেন তার exact recognized text save।
            st.session_state[
                f"voice_input_transcript_{key}"
            ] = transcript

            try:

             
                # [17-E] PARSE VALUE
               
                # Transcript থেকে required value তৈরি।
                value = _parse(
                    transcript,
                    value_type,
                    options=options,
                    minimum=minimum,
                    maximum=maximum
                )

            except ValueError as exc:

               
                # [17-F] OPTION ERROR
                
                # Option match না হলে available options voice-এ জানানো।
                if value_type == "option":

                    # Valid options suggestion voice।
                    _speak_option_suggestion(
                        key,
                        transcript,
                        options or []
                    )

                    # User-এর জন্য warning।
                    st.warning(
                        f"{exc} "
                        "অনুগ্রহ করে উপরের তালিকা থেকে "
                        "একটি option বলুন।"
                    )

                # Number/date validation error হলে।
                else:

                    # Original validation message দেখানো।
                    st.warning(
                        str(exc)
                    )

                # Invalid value হলে None।
                value = None

            
            # [17-G] SAVE PENDING VALUE
         
            # Valid value পাওয়া গেলে next rerun-এর জন্য save।
            if value is not None:

                # Parsed value + exact transcript save।
                st.session_state[
                    f"voice_input_pending_{key}"
                ] = (
                    value,
                    transcript
                )

                # Widget state safely update করার জন্য rerun।
                st.rerun()

        # [17-H] SPEECH NOT UNDERSTOOD
        
        except sr.UnknownValueError:

            # Bangla recognition error।
            st.warning(
                "কথাটি পরিষ্কারভাবে বোঝা যায়নি। "
                "আবার ভয়েস দিন।"
            )

     
        # [17-I] SPEECH SERVICE ERROR
    
        except sr.RequestError:

            # Google speech recognition service unavailable।
            st.error(
                "ভয়েসকে লেখায় রূপান্তর করার সেবা "
                "এই মুহূর্তে পাওয়া যাচ্ছে না।"
            )

   
        # [17-J] GENERAL ERROR
    
        except Exception as exc:

            # Unexpected voice-input error।
            st.warning(
                f"ভয়েস ইনপুট নেওয়া যায়নি: {exc}"
            )


    # [17-K] SHOW RECOGNIZED TRANSCRIPT
  
    # Saved transcript নেওয়া।
    transcript = st.session_state.get(
        f"voice_input_transcript_{key}"
    )

    # Transcript থাকলে user-কে দেখানো।
    if transcript:

        # Bangla transcript label।
        st.caption(
            f"ভয়েসে যা বলা হয়েছে: {transcript}"
        )

 
    # [17-L] RETURN APPLIED STATUS
  
    # Current rerun-এ voice value successfully apply হয়েছে
    # কি না return করা।
    return st.session_state.pop(
        f"voice_input_applied_{key}",
        False
    )