# backend/ai.py

import time
from typing import Optional

import google.generativeai as genai

from config import (
    GEMINI_API_KEY,
    GEMINI_MODELS,
    AI_TEMPERATURE,
    AI_MAX_OUTPUT_TOKENS,
    RETRY_DELAY_SECONDS,
    MODEL_RETRY_COUNT,
)


# ============================================================
# MafiyaAI AI Engine
# ============================================================

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured."
    )


genai.configure(
    api_key=GEMINI_API_KEY
)


# ============================================================
# System Prompt
# ============================================================

SYSTEM_PROMPT = """
You are MafiyaAI, a personal AI assistant.

Core behavior:

- Be helpful, accurate, and natural.
- Understand Bengali and English.
- Reply in the user's language whenever practical.
- Maintain conversation context when context is provided.
- Do not intentionally limit the user's message length.
- Do not intentionally limit stored conversation memory.
- Never automatically delete conversation history.
- For very large input, process as much of the available content
  as the AI model's context capacity allows.
"""


# ============================================================
# Model Initialization
# ============================================================

MODELS = []


for model_name in GEMINI_MODELS:

    try:

        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=SYSTEM_PROMPT,
            generation_config={
                "temperature": AI_TEMPERATURE,
                "max_output_tokens": AI_MAX_OUTPUT_TOKENS,
            }
        )

        MODELS.append({
            "name": model_name,
            "model": model,
        })

    except Exception:
        # If a model cannot be initialized,
        # continue with the next model.
        continue


if not MODELS:

    raise RuntimeError(
        "No Gemini models could be initialized."
    )


# ============================================================
# Generate AI Response
# ============================================================

def generate_ai_response(
    message: str,
    conversation_context: Optional[str] = None,
) -> str:

    if message is None:

        raise ValueError(
            "Message cannot be None."
        )


    message = str(message)


    if not message.strip():

        raise ValueError(
            "Message cannot be empty."
        )


    # --------------------------------------------------------
    # Build Prompt
    # --------------------------------------------------------

    if conversation_context:

        prompt = (
            "Conversation history:\n\n"
            + conversation_context
            + "\n\n"
            "Current user message:\n\n"
            + message
        )

    else:

        prompt = message


    last_error = None


    # ========================================================
    # Model Fallback Chain
    # ========================================================

    for model_info in MODELS:

        model_name = model_info["name"]
        model = model_info["model"]


        # ----------------------------------------------------
        # Retry current model
        # ----------------------------------------------------

        for attempt in range(
            MODEL_RETRY_COUNT
        ):

            try:

                response = model.generate_content(
                    prompt
                )


                text = extract_response_text(
                    response
                )


                if text:

                    return text


                last_error = RuntimeError(
                    f"{model_name} returned an empty response."
                )


            except Exception as error:

                last_error = error


            # ------------------------------------------------
            # Very short retry delay
            # ------------------------------------------------

            if attempt < MODEL_RETRY_COUNT - 1:

                time.sleep(
                    RETRY_DELAY_SECONDS
                )


        # ----------------------------------------------------
        # Current model failed.
        #
        # Move to the next model immediately.
        # ----------------------------------------------------

        continue


    # ========================================================
    # All Models Failed
    # ========================================================

    if last_error:

        raise RuntimeError(
            "All MafiyaAI Gemini models failed. "
            f"Last error: {last_error}"
        )


    raise RuntimeError(
        "MafiyaAI could not generate a response."
    )


# ============================================================
# Extract Response Text
# ============================================================

def extract_response_text(
    response
) -> str:

    if response is None:

        return ""


    # --------------------------------------------------------
    # Standard SDK response
    # --------------------------------------------------------

    try:

        text = response.text

        if text:

            return str(text).strip()

    except Exception:
        pass


    # --------------------------------------------------------
    # Candidate fallback
    # --------------------------------------------------------

    try:

        candidates = getattr(
            response,
            "candidates",
            None
        )


        if not candidates:

            return ""


        parts = []


        for candidate in candidates:

            content = getattr(
                candidate,
                "content",
                None
            )


            if not content:

                continue


            candidate_parts = getattr(
                content,
                "parts",
                []
            )


            for part in candidate_parts:

                part_text = getattr(
                    part,
                    "text",
                    None
                )


                if part_text:

                    parts.append(
                        str(part_text)
                    )


        if parts:

            return "\n".join(
                parts
            ).strip()


    except Exception:
        pass


    return ""


# ============================================================
# AI Connection Test
# ============================================================

def check_ai_connection() -> bool:

    try:

        response = generate_ai_response(
            "Reply with exactly: OK"
        )

        return (
            response.strip().upper()
            == "OK"
        )

    except Exception:

        return False


# ============================================================
# Get Active Models
# ============================================================

def get_available_models():

    return [
        model["name"]
        for model in MODELS
    ]


# ============================================================
# AI Engine Status
# ============================================================

def get_ai_status():

    return {
        "configured": bool(
            GEMINI_API_KEY
        ),

        "models": get_available_models(),

        "model_count": len(
            MODELS
        ),

        "retry_delay_seconds":
            RETRY_DELAY_SECONDS,

        "retry_count":
            MODEL_RETRY_COUNT,

        "message_limit":
            None,

        "memory_limit":
            None,
    }