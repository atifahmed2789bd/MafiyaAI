# backend/config.py

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
# Gemini API
# ============================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
).strip()


# ============================================================
# Gemini Models
# ============================================================
#
# Primary → Secondary → Fallback
#
# যদি প্রথম model ব্যর্থ হয়, কোনো 1-second delay থাকবে না।
# পরের model-এ immediately চেষ্টা করা হবে।
# ============================================================

GEMINI_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
]


# Remove duplicates / empty values
GEMINI_MODELS = list(
    dict.fromkeys(
        model.strip()
        for model in GEMINI_MODELS
        if model and model.strip()
    )
)


# ============================================================
# AI Settings
# ============================================================

AI_TEMPERATURE = 0.7

AI_MAX_OUTPUT_TOKENS = 65536


# ============================================================
# Retry / Fallback
# ============================================================

# Retry-এর মাঝে মাত্র 1 millisecond delay
RETRY_DELAY_SECONDS = 0.001

# একটি model সর্বোচ্চ কতবার চেষ্টা করবে
MODEL_RETRY_COUNT = 2


# ============================================================
# Memory Settings
# ============================================================

MEMORY_ENABLED = True

# Automatic deletion সম্পূর্ণ বন্ধ
MEMORY_AUTO_DELETE = False

# কোনো fixed limit নেই
MEMORY_MAX_MESSAGES = None

MEMORY_MAX_CONVERSATIONS = None

MEMORY_MAX_ENTRIES = None


# ============================================================
# Message Settings
# ============================================================

# কোনো fixed message limit নেই
MESSAGE_LIMIT = None

MESSAGE_MAX_WORDS = None

MESSAGE_AUTO_TRUNCATE = False


# ============================================================
# Server Settings
# ============================================================

DEBUG = False

THREADED = True

CORS_ENABLED = True


# ============================================================
# Configuration Validation
# ============================================================

def validate_config():

    errors = []

    if not GEMINI_API_KEY:
        errors.append(
            "GEMINI_API_KEY is not configured."
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