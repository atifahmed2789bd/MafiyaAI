from typing import Any, Dict, Iterator, Optional

from answer_builder import AnswerBuilder

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
# Normal flow:
#
# User Message
#      ↓
# Chat Controller
#      ↓
# AnswerBuilder
#      ↓
# Complete Prompt
#      ↓
# AI
#      ↓
# Complete Response
#      ↓
# Memory
#
#
# Streaming flow:
#
# User Message
#      ↓
# Chat Controller
#      ↓
# Memory Context
#      ↓
# AnswerBuilder
#      ↓
# Complete Prompt
#      ↓
# Gemini Streaming
#      ↓
# Chunk 1 → App
# Chunk 2 → App
# Chunk 3 → App
# ...
#      ↓
# Complete Response
#      ↓
# Memory
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
# Send Normal Message
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
    # Ensure conversation exists
    # --------------------------------------------------------

    conversation_id = _ensure_conversation(
        conversation_id
    )


    # --------------------------------------------------------
    # Generate complete AI response
    #
    # AnswerBuilder handles:
    #
    # - Memory context
    # - System instructions
    # - Language rules
    # - Formatting rules
    # - User message
    # - Gemini request
    # --------------------------------------------------------

    ai_response = AnswerBuilder.generate_answer(
        message=message,
        conversation_id=conversation_id,
        metadata=metadata
    )


    # --------------------------------------------------------
    # Get updated conversation
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


        # Search backwards for latest
        # user + assistant messages.

        for item in reversed(
            messages
        ):

            role = item.get(
                "role"
            )


            if (
                user_message is None
                and role == "user"
            ):

                user_message = item


            elif (
                assistant_message is None
                and role == "assistant"
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
# STREAM MESSAGE
#
# IMPORTANT:
#
# The streaming path MUST use the exact same AnswerBuilder
# prompt construction as the normal path.
#
# We do NOT call build_prompt() with conversation_id or
# metadata because those are NOT parameters of build_prompt().
#
# Correct:
#
# build_context()
#       ↓
# AnswerBuilder.build_prompt()
#       ↓
# stream_ai_response()
#
# ============================================================

def stream_message(
    message: str,
    conversation_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Iterator[str]:

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
    # Ensure conversation exists
    # --------------------------------------------------------

    conversation_id = _ensure_conversation(
        conversation_id
    )


    # --------------------------------------------------------
    # Import streaming AI engine
    # --------------------------------------------------------

    from ai import stream_ai_response


    # --------------------------------------------------------
    # Get conversation context
    #
    # This is the same context used by
    # AnswerBuilder.generate_answer().
    # --------------------------------------------------------

    try:

        conversation_context = build_context(
            conversation_id
        )

    except Exception:

        conversation_context = ""


    # --------------------------------------------------------
    # Build COMPLETE AnswerBuilder prompt
    #
    # IMPORTANT:
    #
    # build_prompt() accepts:
    #
    # message
    # conversation_context
    # attachments
    #
    # It does NOT accept:
    #
    # conversation_id
    # metadata
    #
    # Therefore the previous implementation caused
    # TypeError and then silently bypassed AnswerBuilder.
    # --------------------------------------------------------

    prompt = AnswerBuilder.build_prompt(
        message=message,
        conversation_context=conversation_context,
        attachments=[]
    )


    # --------------------------------------------------------
    # Safety validation
    # --------------------------------------------------------

    if not prompt:

        raise RuntimeError(
            "AnswerBuilder returned an empty prompt."
        )

    prompt = str(
        prompt
    ).strip()

    if not prompt:

        raise RuntimeError(
            "AnswerBuilder returned an empty prompt."
        )


    # --------------------------------------------------------
    # Collect complete streamed response.
    #
    # Memory is saved only AFTER streaming finishes.
    # --------------------------------------------------------

    complete_response_parts = []


    try:

        for chunk in stream_ai_response(
            message=message,
            conversation_context=prompt
        ):

            if not chunk:
                continue


            chunk = str(
                chunk
            )


            complete_response_parts.append(
                chunk
            )


            # =================================================
            # IMPORTANT
            #
            # Send each Gemini chunk immediately.
            #
            # Do NOT wait for the complete response.
            # =================================================

            yield chunk


    except GeneratorExit:

        # ----------------------------------------------------
        # Client disconnected / stream cancelled.
        #
        # Do not save incomplete AI response.
        # ----------------------------------------------------

        return


    except Exception:

        # ----------------------------------------------------
        # Let app.py handle the streaming error.
        # ----------------------------------------------------

        raise


    # --------------------------------------------------------
    # Complete response
    # --------------------------------------------------------

    complete_response = "".join(
        complete_response_parts
    ).strip()


    if not complete_response:

        raise RuntimeError(
            "AI returned an empty streaming response."
        )


    # --------------------------------------------------------
    # Save user message AFTER successful stream
    # --------------------------------------------------------

    try:

        add_message(
            conversation_id=conversation_id,
            role="user",
            content=message,
            metadata=metadata
        )

    except TypeError:

        # Compatibility with memory.py implementations
        # that don't accept metadata.

        add_message(
            conversation_id,
            "user",
            message
        )


    # --------------------------------------------------------
    # Save assistant response AFTER successful stream
    # --------------------------------------------------------

    try:

        add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=complete_response
        )

    except TypeError:

        add_message(
            conversation_id,
            "assistant",
            complete_response
        )


# ============================================================
# Send Voice Message
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

    if not conversation_id:
        return ""

    return build_context(
        conversation_id
    )


# ============================================================
# Chat Health Check
# ============================================================

def chat_health_check() -> Dict[str, Any]:

    try:

        # ----------------------------------------------------
        # Health check directly uses the AI engine.
        #
        # This avoids storing "OK" inside user memory.
        # ----------------------------------------------------

        from ai import generate_ai_response

        result = generate_ai_response(
            message="Reply with exactly: OK"
        )


        if not result:

            return {
                "success": False,
                "ai": False,
                "response": None,
                "error":
                    "AI returned an empty response."
            }


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


# ============================================================
# Public Exports
# ============================================================

__all__ = [
    "new_chat",
    "send_message",
    "stream_message",
    "send_voice_message",
    "get_chat_context",
    "chat_health_check",
]