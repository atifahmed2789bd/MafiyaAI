import os


# ============================================================
# Mafiya AI Configuration
# ============================================================

class Config:

    # --------------------------------------------------------
    # Gemini API Key
    # Render Environment Variable:
    #
    # GEMINI_API_KEY
    # --------------------------------------------------------

    GEMINI_API_KEY = os.environ.get(
        "GEMINI_API_KEY",
        ""
    )

    # --------------------------------------------------------
    # Gemini Models
    #
    # প্রথমটি কাজ না করলে পরেরটিতে যাবে।
    # --------------------------------------------------------

    GEMINI_MODELS = [

        os.environ.get(
            "GEMINI_MODEL_1",
            "gemini-2.5-flash"
        ),

        os.environ.get(
            "GEMINI_MODEL_2",
            "gemini-2.5-flash-lite"
        ),

        os.environ.get(
            "GEMINI_MODEL_3",
            "gemini-2.5-pro"
        ),

        os.environ.get(
            "GEMINI_MODEL_4",
            "gemini-2.0-flash"
        ),

        os.environ.get(
            "GEMINI_MODEL_5",
            "gemini-2.0-flash-lite"
        ),

        os.environ.get(
            "GEMINI_MODEL_6",
            "gemini-1.5-flash"
        )
    ]

    # --------------------------------------------------------
    # Server
    # --------------------------------------------------------

    HOST = os.environ.get(
        "HOST",
        "0.0.0.0"
    )

    PORT = int(
        os.environ.get(
            "PORT",
            "10000"
        )
    )

    # --------------------------------------------------------
    # Application
    # --------------------------------------------------------

    APP_NAME = "Mafiya AI"


# ============================================================
# Configuration Instance
# ============================================================

config = Config()