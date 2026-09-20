from typing import Any, Callable, Dict, List, Optional

from ai import generate_ai_response

from memory import (
    add_message,
    build_context,
    get_long_term_memory,
    save_long_term_memory,
)


class AnswerBuilder:
    pass


AnswerBuilder._initialized = False


def _initialize(
    cls,
    context: Any = None,
) -> None:
    if cls._initialized:
        return

    cls._initialized = True


def _build_text(
    cls,
    user_message: str,
    conversation_id: Optional[str] = None,
    callback: Optional[
        Callable[[Optional[str], Optional[str]], None]
    ] = None,
) -> Optional[str]:
    return cls.build(
        user_message=user_message,
        conversation_id=conversation_id,
        callback=callback,
    )


def _build(
    cls,
    user_message: str,
    conversation_id: Optional[str] = None,
    attachments: Optional[List[Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    callback: Optional[
        Callable[[Optional[str], Optional[str]], None]
    ] = None,
) -> Optional[str]:
    try:
        cls.initialize()

        user_message = str(
            user_message or ""
        ).strip()

        attachments = attachments or []
        metadata = metadata or {}

        if not user_message and not attachments:
            error = "User message and attachments are empty."

            cls._send_error(
                callback,
                error,
            )

            return None

        answer = cls.generate_answer(
            message=user_message,
            conversation_id=conversation_id,
            attachments=attachments,
            metadata=metadata,
        )

        cls._send_success(
            callback,
            answer,
        )

        return answer

    except Exception as error:
        error_message = cls.safe_error(
            error
        )

        cls._send_error(
            callback,
            error_message,
        )

        return None


def _generate_answer(
    cls,
    message: str = "",
    conversation_id: Optional[str] = None,
    prompt: str = "",
    attachments: Optional[List[Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    cls.initialize()

    message = str(
        message or ""
    ).strip()

    attachments = attachments or []
    metadata = metadata or {}

    conversation_context = ""

    if conversation_id:
        try:
            conversation_context = build_context(
                conversation_id
            )
        except Exception:
            conversation_context = ""

    if not prompt.strip():
        prompt = cls.build_prompt(
            message=message,
            conversation_context=conversation_context,
            attachments=attachments,
        )

    answer = generate_ai_response(
        message=message,
        conversation_context=prompt,
    )

    if answer is None:
        raise RuntimeError(
            "AI returned an empty answer."
        )

    answer = str(
        answer
    ).strip()

    if not answer:
        raise RuntimeError(
            "AI returned an empty answer."
        )

    if conversation_id:
        if message:
            input_metadata = {
                "input_type": "text"
            }

            input_metadata.update(
                metadata
            )

            add_message(
                conversation_id=conversation_id,
                role="user",
                content=message,
                metadata=input_metadata,
            )

        add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=answer,
        )

    return answer


def _build_prompt(
    cls,
    message: str,
    conversation_context: str = "",
    attachments: Optional[List[Any]] = None,
) -> str:
    attachments = attachments or []

    prompt_parts = []

    prompt_parts.append(
        """
You're MafiyaAI.

You are an intelligent multilingual personal AI assistant.
Always address the user as Boss when appropriate.
Be friendly, natural, respectful, and helpful.
Do not use romantic or sexual roleplay.
Do not use overly formal language.
Remember relevant conversation context and use it when useful.
If you are not sure about something, say clearly that you are unsure.
Keep short answers short.
For difficult requests, explain step by step.
Do not guess the user's personal information.
Do not overuse the word Boss.
""".strip()
    )

    prompt_parts.append(
        """
Language rules:

Reply in the same language used by the user whenever possible.

If the user writes in Bengali, reply naturally in Bengali.

If the user writes in English, reply naturally in English.

Bengali and English may be mixed naturally when useful.

Do not unnecessarily translate the user's language.
""".strip()
    )

    prompt_parts.append(
        """
Response rules:

Answer the user's actual question directly.

Avoid unnecessary introductions and filler.

Do not repeat information unnecessarily.

Use clear spacing between different parts of an answer.

For detailed requests, explain clearly and step by step.
""".strip()
    )

    prompt_parts.append(
        """
Accuracy rules:

Never intentionally invent information.

If information is uncertain, clearly say so.

Do not guess the user's personal information.

Do not make unsupported claims.
""".strip()
    )

    prompt_parts.append(
        """
Memory rules:

Use relevant conversation context when available.

Do not use unrelated old information.

Do not automatically delete conversation memory.

Do not impose an artificial fixed message-count limit.

Do not impose an artificial fixed memory-count limit.
""".strip()
    )

    prompt_parts.append(
        """
Rich text formatting rules:

Use **text** for bold.

Use __text__ for underline.

Use ==text== for highlight.

Use ~~text~~ for lowlight.

The application will process these markers into visual formatting.

Do not explain these markers to the user.

Use them naturally and sparingly.

Do not use Markdown headings unless specifically requested.
""".strip()
    )

    prompt_parts.append(
        """
Website rules:

When a website is relevant, provide its direct HTTPS URL.

Do not use Markdown link syntax.

The application will detect URLs and convert them into clickable
website names.
""".strip()
    )

    prompt_parts.append(
        """
Coding rules:

When the user asks for code, provide complete usable code.

Use the requested programming language.

Maintain correct indentation.

When the user asks for a complete file replacement,
provide the complete file.

Always use fenced code blocks for code.

Do not remove indentation from code.

Do not use rich-text markers inside code unless they are
actually part of the code.
""".strip()
    )

    prompt_parts.append(
        """
Large content rules:

Do not intentionally truncate large user messages.

Do not unnecessarily shorten requested answers.

Respect the actual context and output limits of the AI provider.
""".strip()
    )

    prompt_parts.append(
        """
Voice-friendly rules:

When an answer may be read aloud, write naturally for speech.

Avoid unnecessary decorative symbols.

Keep code formatting intact when providing code.
""".strip()
    )

    if attachments:
        prompt_parts.append(
            "Current attachment information:\n\n"
            + cls.format_attachments(
                attachments
            )
        )

    if conversation_context:
        prompt_parts.append(
            "Relevant conversation context:\n\n"
            + conversation_context
        )

    if message:
        prompt_parts.append(
            "Current user message:\n\n"
            + message
        )
    else:
        prompt_parts.append(
            "The user has provided an attachment without a text message."
        )

    prompt_parts.append(
        """
Provide a direct, relevant, natural, accurate, and useful
answer to the user's current request.
""".strip()
    )

    return "\n\n".join(
        prompt_parts
    )


def _format_attachments(
    attachments: List[Any],
) -> str:
    if not attachments:
        return ""

    result = []

    for index, attachment in enumerate(
        attachments,
        start=1,
    ):
        if isinstance(
            attachment,
            dict,
        ):
            attachment_type = attachment.get(
                "type",
                "unknown",
            )

            name = attachment.get(
                "name",
                "",
            )

            content = attachment.get(
                "content",
                "",
            )

            result.append(
                f"Attachment {index}:\n"
                f"type: {attachment_type}\n"
                f"name: {name}\n"
                f"content: {content}"
            )

        else:
            result.append(
                f"Attachment {index}:\n"
                f"{str(attachment)}"
            )

    return "\n\n".join(
        result
    )


def _save_memory(
    cls,
    key: str,
    value: Any,
) -> None:
    save_long_term_memory(
        key=key,
        value=value,
    )


def _get_memory(
    cls,
    key: Optional[str] = None,
):
    return get_long_term_memory(
        key
    )


def _send_success(
    callback,
    answer: str,
) -> None:
    if callback is None:
        return

    try:
        callback(
            answer,
            None,
        )
    except Exception:
        pass


def _send_error(
    callback,
    error: str,
) -> None:
    if callback is None:
        return

    try:
        callback(
            None,
            error,
        )
    except Exception:
        pass


def _safe_error(
    error: Exception,
) -> str:
    if error is None:
        return "Unknown error."

    message = str(
        error
    )

    if not message.strip():
        return type(error).__name__

    return message.strip()


AnswerBuilder.initialize = classmethod(
    _initialize
)

AnswerBuilder.build_text = classmethod(
    _build_text
)

AnswerBuilder.build = classmethod(
    _build
)

AnswerBuilder.generate_answer = classmethod(
    _generate_answer
)

AnswerBuilder.build_prompt = classmethod(
    _build_prompt
)

AnswerBuilder.format_attachments = staticmethod(
    _format_attachments
)

AnswerBuilder.save_memory = classmethod(
    _save_memory
)

AnswerBuilder.get_memory = classmethod(
    _get_memory
)

AnswerBuilder._send_success = staticmethod(
    _send_success
)

AnswerBuilder._send_error = staticmethod(
    _send_error
)

AnswerBuilder.safe_error = staticmethod(
    _safe_error
)


class AIRequest:
    pass


def _request_init(
    self,
    message: str = "",
    attachments: Optional[List[Any]] = None,
    conversation_id: Optional[str] = None,
):
    self._message = message or ""
    self._attachments = attachments or []
    self._conversation_id = conversation_id


def _request_get_message(
    self,
) -> str:
    return self._message


def _request_get_attachments(
    self,
) -> List[Any]:
    return self._attachments


def _request_get_conversation_id(
    self,
) -> Optional[str]:
    return self._conversation_id


def _request_get_attachment_payload(
    self,
) -> dict:
    return {
        "attachments": self._attachments
    }


AIRequest.__init__ = _request_init

AIRequest.get_message = _request_get_message

AIRequest.get_attachments = _request_get_attachments

AIRequest.get_conversation_id = _request_get_conversation_id

AIRequest.get_attachment_payload = (
    _request_get_attachment_payload
)
