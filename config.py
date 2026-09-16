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
    #
    # বর্তমানে ব্যবহারযোগ্য stable Gemini models
    #
    # 1. Gemini 2.5 Flash
    # 2. Gemini 2.5 Flash-Lite
    # 3. Gemini 2.5 Pro
    #
    # পুরোনো 1.5 / 2.0 models রাখা হয়নি।
    # =========================================

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