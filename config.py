import os


class Config:

    # =========================================
    # GEMINI API KEY
    # =========================================

    GEMINI_API_KEY = os.environ.get(
        "GEMINI_API_KEY",
        ""
    )


    # =========================================
    # GEMINI MODELS
    # =========================================

    GEMINI_MODELS = [

        os.environ.get(
            "GEMINI_MODEL_1",
            "gemini-3.8-flash"
        ),

        os.environ.get(
            "GEMINI_MODEL_2",
            "gemini-3.7-flash"
        ),

        os.environ.get(
            "GEMINI_MODEL_3",
            "gemini-3.1-pro-preview"
        ),

        os.environ.get(
            "GEMINI_MODEL_4",
            "gemini-2.5-flash"
        ),

        os.environ.get(
            "GEMINI_MODEL_5",
            "gemini-2.5-flash-lite"
        )

    ]


    # =========================================
    # SERVER
    # =========================================

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


    # =========================================
    # APP
    # =========================================

    APP_NAME = "Mafiya AI"


# =============================================
# CONFIG INSTANCE
# =============================================

config = Config()