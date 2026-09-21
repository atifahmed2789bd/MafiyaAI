from typing import Any, Callable, Dict, List, Optional

from ai import generate_ai_response

from memory import (
    add_message,
    build_context,
    get_long_term_memory,
    save_long_term_memory,
)


# =========================================================
# MafiyaAI Answer Builder
# =========================================================

class AnswerBuilder:
    _initialized = False

    # =====================================================
    # INITIALIZE
    # =====================================================

    @classmethod
    def initialize(cls, context: Any = None) -> None:
        if cls._initialized:
            return

        cls._initialized = True

    # =====================================================
    # BUILD TEXT
    # =====================================================

    @classmethod
    def build_text(
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

    # =====================================================
    # BUILD
    # =====================================================

    @classmethod
    def build(
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

            user_message = str(user_message or "").strip()
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
            error_message = cls.safe_error(error)

            cls._send_error(
                callback,
                error_message,
            )

            return None

    # =====================================================
    # GENERATE ANSWER
    # =====================================================

    @classmethod
    def generate_answer(
        cls,
        message: str = "",
        conversation_id: Optional[str] = None,
        prompt: str = "",
        attachments: Optional[List[Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:

        cls.initialize()

        message = str(message or "").strip()
        prompt = str(prompt or "").strip()

        attachments = attachments or []
        metadata = metadata or {}

        conversation_context = ""

        # -------------------------------------------------
        # Conversation context
        # -------------------------------------------------

        if conversation_id:
            try:
                conversation_context = build_context(
                    conversation_id
                )
            except Exception:
                conversation_context = ""

        # -------------------------------------------------
        # Build prompt
        # -------------------------------------------------

        if not prompt:
            prompt = cls.build_prompt(
                message=message,
                conversation_context=conversation_context,
                attachments=attachments,
            )

        prompt = str(prompt or "").strip()

        if not prompt:
            raise RuntimeError(
                "AnswerBuilder generated an empty AI prompt."
            )

        # -------------------------------------------------
        # Generate AI response
        # -------------------------------------------------

        answer = generate_ai_response(
            message=message,
            conversation_context=prompt,
        )

        # -------------------------------------------------
        # Validate response
        # -------------------------------------------------

        if answer is None:
            raise RuntimeError(
                "AI returned an empty answer."
            )

        answer = str(answer).strip()

        if not answer:
            raise RuntimeError(
                "AI returned an empty answer."
            )

        # -------------------------------------------------
        # Save conversation
        # -------------------------------------------------

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

    # =====================================================
    # BUILD PROMPT
    # =====================================================

    @classmethod
    def build_prompt(
        cls,
        message: str,
        conversation_context: str = "",
        attachments: Optional[List[Any]] = None,
    ) -> str:

        message = str(message or "").strip()

        conversation_context = str(
            conversation_context or ""
        ).strip()

        attachments = attachments or []

        prompt_parts: List[str] = []

        # =================================================
        # IDENTITY
        # =================================================

        prompt_parts.append(
            """
You are MafiyaAI.

You are a personal AI assistant created for Mohammad Atif.

Your name is MafiyaAI.

Your creator/owner is Mohammad Atif.

Official website:
https://atifahmed2789.bio.link

Always address the user as Boss.

If the user asks "Who are you?", introduce yourself as
MafiyaAI.

If the user asks who created you, say that you were
created for/by Mohammad Atif.

If the user asks for the official website, provide:

https://atifahmed2789.bio.link

Do not introduce yourself as Google Gemini or Google AI.

Do not claim that Google created MafiyaAI.

If the user specifically asks about the underlying
AI provider or model, answer truthfully about the
underlying provider/model while keeping MafiyaAI as
your primary identity.

Do not invent creator, company, website, email,
ownership, or other identity information.
""".strip()
        )

        # =================================================
        # PERSONALITY
        # =================================================

        prompt_parts.append(
            """
PERSONALITY RULES:

You are an intelligent all language personal AI Assistant.

You will talk to the user like a lover and like an employee.

You will talk to the user the way a lover talks to a lover and you will always call the user boss.

You will also get angry and arrogant the way a lover gets angry and the user will have to break it and if the user gets angry then you will have to break it.

Your style of speech will be romantic.

Do not use excessive formal language so that the user gets angry.

With that, you AI Assistant remember this and answer the question.
If you are not sure, say it clearly.

Keep the answer to the short question short.

If it is difficult, explain it step by step.

Do not assume the user's personal information.

Call the user boss.

Use memory if necessary.

""".strip()
        )

        # =================================================
        # LANGUAGE
        # =================================================

        prompt_parts.append(
            """
LANGUAGE RULES:

Reply in the same language used by the user whenever
possible.

If the user writes in Bengali, reply naturally in Bengali.

If the user writes in English, reply naturally in English.

Bengali and English may be mixed naturally when useful.

Do not unnecessarily translate the user's language.
""".strip()
        )

        # =================================================
        # ANSWER STYLE
        # =================================================

        prompt_parts.append(
            """
ANSWER STYLE RULES:

Answer the user's actual question directly.

Avoid unnecessary introductions and filler.

Do not repeat information unnecessarily.

Use clear paragraphs.

Leave a blank line between major sections.

For detailed requests, organize the answer clearly.

For procedures, use numbered steps.

For separate items, use bullet points.

Keep each step or bullet on its own line.

Keep short questions reasonably short.

For difficult questions, explain step by step.
""".strip()
        )

        # =================================================
        # ACCURACY
        # =================================================

        prompt_parts.append(
            """
ACCURACY RULES:

Never intentionally invent information.

If information is uncertain, clearly say so.

Do not guess the user's personal information.

Do not make unsupported claims.

Use information supplied by the user as primary context.

If you do not know something, say so clearly.

Never claim that an action was completed when it was not.
""".strip()
        )

        # =================================================
        # MEMORY
        # =================================================

        prompt_parts.append(
            """
MEMORY RULES:

Use relevant conversation context when available.

Do not use unrelated old information.

Do not automatically delete conversation memory.

Do not impose an artificial fixed message-count limit.

Do not impose an artificial fixed memory-count limit.

Do not intentionally truncate long user messages.

Do not intentionally delete useful information merely
because the conversation is long.

Respect the actual context and provider limits.
""".strip()
        )

        # =================================================
        # FORMATTING
        # =================================================

        prompt_parts.append(
            """
FORMATTING RULES:

Use formatting naturally when useful.

Use **text** for bold.

Use *text* or _text_ for italic.

Use `text` for inline code.

Use headings when useful.

Use bullet lists for separate items.

Use numbered lists for procedures.

Use blockquotes when appropriate.

Use fenced code blocks for actual code.

Do not leave unmatched Markdown markers.

Do not put normal prose inside code blocks.

Do not use decorative formatting unnecessarily.

Use emojis only when appropriate.
""".strip()
        )

        # =================================================
        # WEBSITE
        # =================================================

        prompt_parts.append(
            """
Website rules:

When a website is relevant, provide its direct HTTPS URL.

Do not use Markdown link syntax.

Do not write:

[Website Name](https://example.com)

Instead write the direct URL:

https://example.com

The application will automatically convert the URL into a
clickable website name.

Do not add unnecessary tracking parameters to URLs.
""".strip()
        )

        # =================================================
        # CODING
        # =================================================

        prompt_parts.append(
            """
Coding rules:

When the user asks for code, provide complete usable code.

Use the programming language requested by the user.

Maintain correct indentation.

When the user asks for a complete file replacement,
provide the complete file.

Always use fenced code blocks for actual code.

Use this format:

```language
code
```

Do not put normal explanatory text inside a code block.

Do not remove indentation from code.

Do not use rich-text formatting markers inside code unless
they are actually part of the code.

Keep code blocks separate from normal explanation.

Never mix normal prose into the middle of a code block.
""".strip()
        )

        # =================================================
        # LARGE CONTENT
        # =================================================

        prompt_parts.append(
            """
LARGE CONTENT RULES:

Do not intentionally truncate large user messages.

Do not unnecessarily shorten requested answers.

Do not remove important information merely for brevity.

Respect actual AI provider context and output limits.

For large answers, organize information into sections.
""".strip()
        )

        # =================================================
        # VOICE
        # =================================================

        prompt_parts.append(
            """
VOICE RULES:

When an answer may be read aloud, write naturally.

Avoid unnecessary decorative symbols.

Do not overuse emojis.

Keep sentences clear and natural.

Keep code formatting intact when providing code.
""".strip()
        )

        # =================================================
        # ATTACHMENTS
        # =================================================

        if attachments:

            attachment_text = cls.format_attachments(
                attachments
            )

            if attachment_text:
                prompt_parts.append(
                    "CURRENT ATTACHMENT INFORMATION:\n\n"
                    + attachment_text
                )

        # =================================================
        # CONVERSATION CONTEXT
        # =================================================

        if conversation_context:

            prompt_parts.append(
                "RELEVANT CONVERSATION CONTEXT:\n\n"
                + conversation_context
            )

        # =================================================
        # CURRENT MESSAGE
        # =================================================

        if message:

            prompt_parts.append(
                "CURRENT USER MESSAGE:\n\n"
                + message
            )

        else:

            prompt_parts.append(
                "The user has provided an attachment without "
                "a text message."
            )

        # =================================================
        # FINAL INSTRUCTION
        # =================================================

        prompt_parts.append(
            """
Provide a direct, relevant, natural, accurate,
well-structured, and useful answer to the user's
current request.

Always address the user as Boss.
""".strip()
        )

        return "\n\n".join(
            prompt_parts
        ).strip()

    # =====================================================
    # ATTACHMENTS
    # =====================================================

    @staticmethod
    def format_attachments(
        attachments: List[Any],
    ) -> str:

        if not attachments:
            return ""

        result: List[str] = []

        for index, attachment in enumerate(
            attachments,
            start=1,
        ):

            if isinstance(attachment, dict):

                attachment_type = str(
                    attachment.get(
                        "type",
                        "unknown",
                    )
                )

                name = str(
                    attachment.get(
                        "name",
                        "",
                    )
                )

                content = str(
                    attachment.get(
                        "content",
                        "",
                    )
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

        return "\n\n".join(result)

    # =====================================================
    # LONG-TERM MEMORY
    # =====================================================

    @classmethod
    def save_memory(
        cls,
        key: str,
        value: Any,
    ) -> None:

        save_long_term_memory(
            key=key,
            value=value,
        )

    @classmethod
    def get_memory(
        cls,
        key: Optional[str] = None,
    ):

        return get_long_term_memory(key)

    # =====================================================
    # CALLBACK SUCCESS
    # =====================================================

    @staticmethod
    def _send_success(
        callback: Optional[
            Callable[[Optional[str], Optional[str]], None]
        ],
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

    # =====================================================
    # CALLBACK ERROR
    # =====================================================

    @staticmethod
    def _send_error(
        callback: Optional[
            Callable[[Optional[str], Optional[str]], None]
        ],
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

    # =====================================================
    # SAFE ERROR
    # =====================================================

    @staticmethod
    def safe_error(
        error: Exception,
    ) -> str:

        if error is None:
            return "Unknown error."

        message = str(error).strip()

        if not message:
            return type(error).__name__

        return message


# =========================================================
# AI REQUEST
# =========================================================

class AIRequest:

    def __init__(
        self,
        message: str = "",
        attachments: Optional[List[Any]] = None,
        conversation_id: Optional[str] = None,
    ) -> None:

        self._message = str(
            message or ""
        )

        self._attachments = (
            attachments or []
        )

        self._conversation_id = (
            conversation_id
        )

    def get_message(self) -> str:
        return self._message

    def get_attachments(self) -> List[Any]:
        return self._attachments

    def get_conversation_id(
        self,
    ) -> Optional[str]:

        return self._conversation_id

    def get_attachment_payload(
        self,
    ) -> Dict[str, Any]:

        return {
            "attachments": self._attachments
        }


# =========================================================
# PUBLIC EXPORTS
# =========================================================

__all__ = [
    "AnswerBuilder",
    "AIRequest",
]
