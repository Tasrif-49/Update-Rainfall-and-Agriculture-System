from gtts import gTTS
import os
import hashlib
import playsound
import threading
import time
import re

VOICE_CACHE_DIR = "voice_cache"
os.makedirs(VOICE_CACHE_DIR, exist_ok=True)

_VOICE_FILE_CACHE = {}
_VOICE_GENERATION_LOCK = threading.Lock()
_VOICE_PLAY_LOCK = threading.Lock()

_WELCOME_LOCK = threading.Lock()
_WELCOME_PLAYING = False
_WELCOME_PLAYED = False

_VOICE_STATE_LOCK = threading.Lock()
_VOICE_TOKEN = 0

_SELECTION_LOCK = threading.Lock()
_LAST_SELECTION_TEXT = {}

_SECTION_LOCK = threading.Lock()
_LAST_SECTION_TEXT = {}

BANGLA_RANGE = r"\u0980-\u09FF"


def contains_bangla(text):
    if text is None:
        return False
    return re.search(f"[{BANGLA_RANGE}]", str(text)) is not None


def clean_voice_text(text):
    if text is None:
        return ""

    text = str(text).strip()
    if not text:
        return ""

    # Remove English UI words, while keeping Bangla text and numbers.
    english_patterns = [
        r"\bSelect\b", r"\bselected\b", r"\bselection\b",
        r"\bCrop\b", r"\bSeason\b", r"\bSoil\b", r"\bWater\b",
        r"\bRainfall\b", r"\bPrediction\b", r"\bPredicted\b",
        r"\bIrrigation\b", r"\bMethod\b",
        r"\bTraditional\b", r"\bSprinkler\b", r"\bDrip\b",
        r"\bCustom\b", r"\bMeasurement\b", r"\bCalculate\b",
        r"\bSmart\b", r"\bAgriculture\b", r"\bRecommendation\b",
        r"\bAutomatic\b", r"\bManual\b", r"\bOverride\b",
        r"\bRecommended\b", r"\bET0\b", r"\bETc\b", r"\bKc\b",
        r"\bmm\b", r"\bday\b", r"\bDaily\b", r"\bReference\b",
        r"\bEvapotranspiration\b", r"\bInformation\b", r"\bInput\b",
        r"\bOutput\b", r"\bResult\b", r"\bDetails\b", r"\bCurrent\b",
        r"\bStage\b", r"\bGrowth\b", r"\bInitial\b", r"\bDevelopment\b",
        r"\bMid\b", r"\bLate\b", r"\bArea\b", r"\bUnit\b",
        r"\bLand\b", r"\bExisting\b", r"\bEfficiency\b",
        r"\bPlanting\b", r"\bSowing\b", r"\bToday's\b",
        r"\bReference\b", r"\bWater\b"
    ]

    for pattern in english_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    text = re.sub(
        r"\([^()\u0980-\u09FF]*[A-Za-z][^()\u0980-\u09FF]*\)",
        "",
        text
    )
    text = re.sub(r"[A-Za-z]+", "", text)
    text = re.sub(r"[_|<>]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def get_voice_filename(text):
    text = str(text)
    text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
    return os.path.join(VOICE_CACHE_DIR, f"{text_hash}.mp3")


def generate_voice(text):
    text = clean_voice_text(text)
    if not text:
        return None

    cached = _VOICE_FILE_CACHE.get(text)
    if cached and os.path.exists(cached):
        return cached

    filename = get_voice_filename(text)

    if os.path.exists(filename):
        _VOICE_FILE_CACHE[text] = filename
        return filename

    try:
        with _VOICE_GENERATION_LOCK:
            if os.path.exists(filename):
                _VOICE_FILE_CACHE[text] = filename
                return filename

            tts = gTTS(text=text, lang="bn")
            tts.save(filename)

        _VOICE_FILE_CACHE[text] = filename
        return filename

    except Exception as e:
        print("Voice Generate Error:", e)
        return None


def _new_voice_token():
    global _VOICE_TOKEN

    with _VOICE_STATE_LOCK:
        _VOICE_TOKEN += 1
        return _VOICE_TOKEN


def _voice_token_valid(token):
    with _VOICE_STATE_LOCK:
        return token == _VOICE_TOKEN


def cancel_pending_voice():
    _new_voice_token()


def _play_file(filename, token=None):
    """
    Play only if the token is still current.
    The lock is acquired in short intervals so an obsolete pending
    voice never waits behind an old voice and then plays later.
    """
    if not filename:
        return False

    try:
        while True:
            if token is not None and not _voice_token_valid(token):
                return False

            acquired = _VOICE_PLAY_LOCK.acquire(timeout=0.05)

            if acquired:
                break

        try:
            if token is not None and not _voice_token_valid(token):
                return False

            playsound.playsound(filename)
            return True

        finally:
            _VOICE_PLAY_LOCK.release()

    except Exception as e:
        print("Voice Play Error:", e)
        return False


def play_welcome(text, delay=0.5):
    global _WELCOME_PLAYING
    global _WELCOME_PLAYED

    with _WELCOME_LOCK:
        if _WELCOME_PLAYED:
            return

        _WELCOME_PLAYED = True
        _WELCOME_PLAYING = True

    def run():
        global _WELCOME_PLAYING

        try:
            if delay > 0:
                time.sleep(delay)

            filename = generate_voice(text)

            if filename:
                _play_file(filename)

        except Exception as e:
            print("Welcome Voice Error:", e)

        finally:
            with _WELCOME_LOCK:
                _WELCOME_PLAYING = False

    threading.Thread(target=run, daemon=True).start()


def is_welcome_playing():
    with _WELCOME_LOCK:
        return _WELCOME_PLAYING


def reset_welcome_voice():
    global _WELCOME_PLAYING
    global _WELCOME_PLAYED

    with _WELCOME_LOCK:
        _WELCOME_PLAYING = False
        _WELCOME_PLAYED = False


def _wait_for_welcome(token):
    while is_welcome_playing():
        if not _voice_token_valid(token):
            return False
        time.sleep(0.08)

    return _voice_token_valid(token)


def _run_voice_sequence(texts, delay=0.10):
    """
    One token owns the entire sequence.
    A newer interaction cancels the whole old sequence.
    """
    clean_texts = []

    for text in texts:
        cleaned = clean_voice_text(text)
        if cleaned and cleaned not in clean_texts:
            clean_texts.append(cleaned)

    if not clean_texts:
        return

    token = _new_voice_token()

    def run():
        if delay > 0:
            time.sleep(delay)

        if not _wait_for_welcome(token):
            return

        for text in clean_texts:
            if not _voice_token_valid(token):
                return

            filename = generate_voice(text)

            if not filename:
                return

            if not _voice_token_valid(token):
                return

            if not _play_file(filename, token=token):
                return

    threading.Thread(target=run, daemon=True).start()


def speak_sequence(texts, delay=0.05):
    """
    Speak a short ordered sequence as ONE voice job.

    A newer job cancels any older pending job. This is the main
    Streamlit-friendly entry point for: selection -> next instruction.
    """
    if isinstance(texts, str):
        texts = [texts]
    _run_voice_sequence(list(texts), delay=delay)


def section_voice(text, key="general_section", delay=0.10):
    clean_text = clean_voice_text(text)

    if not clean_text:
        return

    with _SECTION_LOCK:
        previous_text = _LAST_SECTION_TEXT.get(key)

        if previous_text == clean_text:
            return

        _LAST_SECTION_TEXT[key] = clean_text

    _run_voice_sequence([clean_text], delay=delay)


def selection_voice(
    text,
    key="general",
    delay=0.10,
    intro_text=None
):
    """
    For the first real interaction of a field:
        intro_text -> selected value

    For later changes:
        selected value only

    The caller decides when this function should be invoked.
    """
    clean_text = clean_voice_text(text)

    if not clean_text:
        return

    with _SELECTION_LOCK:
        previous_text = _LAST_SELECTION_TEXT.get(key)

        if previous_text == clean_text:
            return

        _LAST_SELECTION_TEXT[key] = clean_text

    sequence = []

    if intro_text:
        sequence.append(intro_text)

    sequence.append(clean_text)

    _run_voice_sequence(sequence, delay=delay)


def reset_section_voice():
    global _LAST_SECTION_TEXT

    _new_voice_token()

    with _SECTION_LOCK:
        _LAST_SECTION_TEXT = {}


def reset_selection_voice():
    global _LAST_SELECTION_TEXT

    _new_voice_token()

    with _SELECTION_LOCK:
        _LAST_SELECTION_TEXT = {}


def reset_all_voice_states():
    global _LAST_SELECTION_TEXT
    global _LAST_SECTION_TEXT

    _new_voice_token()

    with _SELECTION_LOCK:
        _LAST_SELECTION_TEXT = {}

    with _SECTION_LOCK:
        _LAST_SECTION_TEXT = {}


def play_voice(text, delay=0.2):
    _run_voice_sequence([text], delay=delay)


def speak(text):
    play_voice(text, delay=0.2)