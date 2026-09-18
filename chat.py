# backend/chat.py

from typing import Any, Dict, Optional

from answer_builder import AnswerBuilder

from memory import (
    build_context,
    create_conversation,
    get_conversation,
)


# ============================================================
# MafiyaAI Chat Controller
# ============================================================

# Flow:
#
# User Message
#      ↓
# Chat Controller
#      ↓
# Answer Builder
#      ↓
# Conversation Context
#      ↓
# AI
#      ↓
# AI Response
#      ↓
# Memory
#      ↓
# Response
#
# Answer Builder remains in a separate file.
#
# No fixed message limit.
# No automatic conversation deletion.
# ============================================================


# ============================================================
# Create New Chat
# ============================================================

def new_chat(
    title: Optional[str] = None
) -> Dict[str, Any]:

    conversation_id = create_conversation(
        title=title
    )

    return {
        "success": True,
        "conversation_id": conversation_id,
        "title": title or "New Conversation"
    }


# ============================================================
# Validate Conversation
# ============================================================

def _ensure_conversation(
    conversation_id: Optional[str]
) -> str:

    if conversation_id:

        conversation = get_conversation(
            conversation_id
        )

        if conversation:
            return conversation_id

    return create_conversation(
        title="New Conversation"
    )


# ============================================================
# Send Message
# ============================================================

def send_message(
    message: str,
    conversation_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:

    # --------------------------------------------------------
    # Validate message
    # --------------------------------------------------------

    if message is None:

        raise ValueError(
            "Message cannot be empty."
        )

    message = str(
        message
    ).strip()

    if not message:

        raise ValueError(
            "Message cannot be empty."
        )

    # --------------------------------------------------------
    # Conversation
    # --------------------------------------------------------

    conversation_id = _ensure_conversation(
        conversation_id
    )

    # --------------------------------------------------------
    # Generate AI response
    # --------------------------------------------------------

    ai_response = AnswerBuilder.generate_answer(
        message=message,
        conversation_id=conversation_id,
        metadata=metadata
    )

    # --------------------------------------------------------
    # Get saved conversation
    # --------------------------------------------------------

    conversation = get_conversation(
        conversation_id
    )

    user_message = None
    assistant_message = None

    if conversation:

        messages = conversation.get(
            "messages",
            []
        )

        # Find the latest user and assistant messages.
        for item in reversed(messages):

            if (
                user_message is None
                and item.get("role") == "user"
            ):

                user_message = item

            elif (
                assistant_message is None
                and item.get("role") == "assistant"
            ):

                assistant_message = item

            if (
                user_message is not None
                and assistant_message is not None
            ):

                break

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {
        "success": True,

        "conversation_id":
            conversation_id,

        "user_message":
            user_message,

        "assistant_message":
            assistant_message,

        "response":
            ai_response
    }


# ============================================================
# Send Message From Voice
# ============================================================

def send_voice_message(
    recognized_text: str,
    conversation_id: Optional[str] = None
) -> Dict[str, Any]:

    if recognized_text is None:

        raise ValueError(
            "Recognized voice text is empty."
        )

    recognized_text = str(
        recognized_text
    ).strip()

    if not recognized_text:

        raise ValueError(
            "Recognized voice text is empty."
        )

    return send_message(
        message=recognized_text,
        conversation_id=conversation_id,
        metadata={
            "input_type": "voice"
        }
    )


# ============================================================
# Get Chat Context
# ============================================================

def get_chat_context(
    conversation_id: str
) -> str:

    return build_context(
        conversation_id
    )


# ============================================================
# Chat Health Check
# ============================================================

def chat_health_check() -> Dict[str, Any]:

    try:

        result = AnswerBuilder.generate_answer(
            message="Reply with exactly: OK"
        )

        return {
            "success": True,
            "ai": True,
            "response": result,
            "error": None
        }

    except Exception as error:

        return {
            "success": False,
            "ai": False,
            "response": None,
            "error": str(error)
        }