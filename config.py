# config.py

import os


# ============================================================
# MafiyaAI Configuration
# ============================================================

APP_NAME = "MafiyaAI"

HOST = os.getenv(
    "MAFIYA_HOST",
    "0.0.0.0"
)

PORT = int(
    os.getenv(
        "MAFIYA_PORT",
        "5000"
    )
)


# ============================================================
# Gemini API Keys
# ============================================================
#
# GEMINI_API_KEY_1
# GEMINI_API_KEY_2
# ...
# GEMINI_API_KEY_100
#
# Empty variables are ignored.
# ============================================================

GEMINI_API_KEYS = [
    os.getenv(
        f"GEMINI_API_KEY_{index}",
        ""
    ).strip()
    for index in range(1, 101)
]


# Remove empty and duplicate keys.
GEMINI_API_KEYS = list(
    dict.fromkeys(
        key
        for key in GEMINI_API_KEYS
        if key
    )
)


# ============================================================
# Legacy API Key Support
# ============================================================

LEGACY_GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
).strip()


if (
    LEGACY_GEMINI_API_KEY
    and LEGACY_GEMINI_API_KEY
    not in GEMINI_API_KEYS
):

    GEMINI_API_KEYS.insert(
        0,
        LEGACY_GEMINI_API_KEY
    )


# ============================================================
# Gemini Models
# ============================================================

GEMINI_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
]


GEMINI_MODELS = list(
    dict.fromkeys(
        str(model).strip()
        for model in GEMINI_MODELS
        if model
        and str(model).strip()
    )
)


# ============================================================
# AI Generation Settings
# ============================================================

AI_TEMPERATURE = 0.7

AI_MAX_OUTPUT_TOKENS = 65536


# ============================================================
# API Key Failover
# ============================================================

API_KEY_FAILOVER_DELAY_SECONDS = 0.01

MODEL_RETRY_COUNT = 1


# ============================================================
# Memory
# ============================================================

MEMORY_ENABLED = True

MEMORY_AUTO_DELETE = False

MEMORY_MAX_MESSAGES = None

MEMORY_MAX_CONVERSATIONS = None

MEMORY_MAX_ENTRIES = None

MESSAGE_LIMIT = None

MESSAGE_MAX_WORDS = None

MESSAGE_AUTO_TRUNCATE = False


# ============================================================
# Flask
# ============================================================

DEBUG = False

THREADED = True

CORS_ENABLED = True


# ============================================================
# Configuration Validation
# ============================================================

def validate_config():

    errors = []


    if not GEMINI_API_KEYS:

        errors.append(
            "No Gemini API key is configured."
        )


    if not GEMINI_MODELS:

        errors.append(
            "No Gemini models are configured."
        )


    if PORT <= 0 or PORT > 65535:

        errors.append(
            "Invalid server port."
        )


    if errors:

        raise RuntimeError(
            "MafiyaAI configuration error:\n"
            + "\n".join(
                f"- {error}"
                for error in errors
            )
        )


    return True