# backend/chat.py

from typing import Any, Dict, Optional

from ai import generate_ai_response
from memory import (
    add_message,
    build_context,
    create_conversation,
    get_conversation,
)


# ============================================================
# MafiyaAI Chat Controller
# ============================================================
#
# Flow:
#
# User Message
#      ↓
# Memory
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

    # Create a new conversation automatically
    # if no valid conversation exists.
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

    message = str(message)

    if not message.strip():
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
    # Save user message
    # --------------------------------------------------------

    user_message = add_message(
        conversation_id=conversation_id,
        role="user",
        content=message,
        metadata=metadata
    )


    # --------------------------------------------------------
    # Build complete conversation context
    # --------------------------------------------------------

    context = build_context(
        conversation_id
    )


    # --------------------------------------------------------
    # Generate AI response
    # --------------------------------------------------------

    ai_response = generate_ai_response(
        message=message,
        conversation_context=context
    )


    # --------------------------------------------------------
    # Save AI response
    # --------------------------------------------------------

    assistant_message = add_message(
        conversation_id=conversation_id,
        role="assistant",
        content=ai_response
    )


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

        result = generate_ai_response(
            message="Reply with exactly: OK"
        )

        return {
            "success": True,
            "ai": True,
            "response": result
        }

    except Exception as error:

        return {
            "success": False,
            "ai": False,
            "error": str(error)
        }