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
# Normal:
# User
#   ↓
# Chat Controller
#   ↓
# AnswerBuilder
#   ↓
# Complete Prompt
#   ↓
# Gemini
#   ↓
# Response
#   ↓
# Memory
#
#
# Streaming:
# User
#   ↓
# Chat Controller
#   ↓
# AnswerBuilder
#   ↓
# Complete Prompt
#   ↓
# Gemini Streaming
#   ↓
# Chunks
#   ↓
# App
#   ↓
# Complete Response
#   ↓
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
# Get Safe Conversation Context
# ============================================================

def _get_conversation_context(
    conversation_id: str
) -> str:

    try:

        context = build_context(
            conversation_id
        )

        if context is None:
            return ""

        return str(
            context
        ).strip()

    except Exception as error:

        # Context failure should not prevent a new message
        # from reaching AnswerBuilder.
        print(
            "MafiyaAI memory context warning:",
            str(error),
            flush=True
        )

        return ""


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
    # Metadata
    # --------------------------------------------------------

    if metadata is None:
        metadata = {}


    # --------------------------------------------------------
    # Ensure conversation
    # --------------------------------------------------------

    conversation_id = _ensure_conversation(
        conversation_id
    )


    # --------------------------------------------------------
    # Generate answer through AnswerBuilder
    #
    # AnswerBuilder is responsible for:
    #
    # - MafiyaAI identity
    # - Creator information
    # - Website
    # - Language
    # - Formatting
    # - Memory
    # - Complete prompt
    # - Gemini request
    # --------------------------------------------------------

    try:

        ai_response = AnswerBuilder.generate_answer(
            message=message,
            conversation_id=conversation_id,
            metadata=metadata
        )

    except Exception as error:

        raise RuntimeError(
            "MafiyaAI failed to generate an answer: "
            f"{error}"
        ) from error


    # --------------------------------------------------------
    # Validate AI response
    # --------------------------------------------------------

    if ai_response is None:

        raise RuntimeError(
            "AI server returned an empty response."
        )

    ai_response = str(
        ai_response
    ).strip()

    if not ai_response:

        raise RuntimeError(
            "AI server returned an empty response."
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

        if not isinstance(
            messages,
            list
        ):
            messages = []


        # ----------------------------------------------------
        # Find latest user + assistant messages
        # ----------------------------------------------------

        for item in reversed(
            messages
        ):

            if not isinstance(
                item,
                dict
            ):
                continue

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
        "conversation_id": conversation_id,
        "user_message": user_message,
        "assistant_message": assistant_message,
        "response": ai_response
    }


# ============================================================
# STREAM MESSAGE
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
    # Metadata
    # --------------------------------------------------------

    if metadata is None:
        metadata = {}


    # --------------------------------------------------------
    # Ensure conversation
    # --------------------------------------------------------

    conversation_id = _ensure_conversation(
        conversation_id
    )


    # --------------------------------------------------------
    # Import streaming AI engine
    # --------------------------------------------------------

    from ai import stream_ai_response


    # --------------------------------------------------------
    # Get memory context
    # --------------------------------------------------------

    conversation_context = (
        _get_conversation_context(
            conversation_id
        )
    )


    # --------------------------------------------------------
    # Build COMPLETE AnswerBuilder prompt
    #
    # IMPORTANT:
    #
    # build_prompt() accepts:
    #
    #   message
    #   conversation_context
    #   attachments
    #
    # Do NOT pass:
    #
    #   conversation_id
    #   metadata
    # --------------------------------------------------------

    try:

        prompt = AnswerBuilder.build_prompt(
            message=message,
            conversation_context=conversation_context,
            attachments=[]
        )

    except Exception as error:

        raise RuntimeError(
            "AnswerBuilder failed to build the AI prompt: "
            f"{error}"
        ) from error


    # --------------------------------------------------------
    # Validate prompt
    # --------------------------------------------------------

    if prompt is None:

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
    # Collect complete streamed response
    # --------------------------------------------------------

    complete_response_parts = []


    try:

        for chunk in stream_ai_response(
            message=message,
            conversation_context=prompt
        ):

            if chunk is None:
                continue

            chunk = str(
                chunk
            )

            if not chunk:
                continue

            complete_response_parts.append(
                chunk
            )

            # ------------------------------------------------
            # Immediately send chunk to app
            # ------------------------------------------------

            yield chunk


    except GeneratorExit:

        # ----------------------------------------------------
        # Client manually stopped/disconnected.
        #
        # Do not save incomplete response.
        # ----------------------------------------------------

        return

    except Exception:

        # Let app.py convert the exception into its
        # appropriate SSE error response.
        raise


    # --------------------------------------------------------
    # Build complete response
    # --------------------------------------------------------

    complete_response = "".join(
        complete_response_parts
    ).strip()


    if not complete_response:

        raise RuntimeError(
            "AI server returned an empty streaming response."
        )


    # --------------------------------------------------------
    # Save user message
    #
    # Only after successful AI streaming.
    # --------------------------------------------------------

    try:

        add_message(
            conversation_id=conversation_id,
            role="user",
            content=message,
            metadata=metadata
        )

    except TypeError:

        add_message(
            conversation_id,
            "user",
            message
        )


    # --------------------------------------------------------
    # Save assistant message
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

    return _get_conversation_context(
        conversation_id
    )


# ============================================================
# Chat Health Check
# ============================================================

def chat_health_check() -> Dict[str, Any]:

    try:

        from ai import generate_ai_response

        result = generate_ai_response(
            message="Reply with exactly: OK"
        )


        if result is None:

            return {
                "success": False,
                "ai": False,
                "response": None,
                "error":
                    "AI returned an empty response."
            }


        result = str(
            result
        ).strip()


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