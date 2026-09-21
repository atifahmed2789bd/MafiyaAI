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

    @classmethod
    def initialize(cls, context: Any = None) -> None:
        if cls._initialized:
            return
        cls._initialized = True

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
                cls._send_error(callback, error)
                return None

            answer = cls.generate_answer(
                message=user_message,
                conversation_id=conversation_id,
                attachments=attachments,
                metadata=metadata,
            )

            cls._send_success(callback, answer)
            return answer

        except Exception as error:
            error_message = cls.safe_error(error)
            cls._send_error(callback, error_message)
            return None

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
        attachments = attachments or []
        metadata = metadata or {}

        conversation_context = ""

        if conversation_id:
            try:
                conversation_context = build_context(conversation_id)
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
            raise RuntimeError("AI returned an empty answer.")

        answer = str(answer).strip()

        if not answer:
            raise RuntimeError("AI returned an empty answer.")

        if conversation_id:
            if message:
                input_metadata = {
                    "input_type": "text"
                }
                input_metadata.update(metadata)

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

    @classmethod
    def build_prompt(
        cls,
        message: str,
        conversation_context: str = "",
        attachments: Optional[List[Any]] = None,
    ) -> str:
        attachments = attachments or []
        prompt_parts: List[str] = []

        prompt_parts.append(
            """
You're MafiyaAI.

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
Answer style rules:

Answer the user's actual question directly.

Avoid unnecessary introductions and filler.

Do not repeat information unnecessarily.

Use clear paragraphs.

Leave a blank line between major sections.

For detailed requests, organize the answer clearly.

When explaining a procedure, use numbered steps.

When listing separate items, use bullet points.

Do not collapse multiple steps into one paragraph.

Do not put unrelated information into the same step.
""".strip()
        )

        prompt_parts.append(
            """
Step formatting:

For procedures, use this style:

1. First step
2. Second step
3. Third step

For sub-items, use:

- Item one
- Item two
- Item three

Keep each numbered step or bullet on its own line.

Do not write all steps as one continuous paragraph.

Do not place unnecessary Markdown symbols around normal step numbers.
""".strip()
        )

        prompt_parts.append(
            """
Accuracy rules:

Never intentionally invent information.

If information is uncertain, clearly say so.

Do not guess the user's personal information.

Do not make unsupported claims.

If the user provides information, use it as the primary context
for that request.
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

Do not intentionally truncate a user's message because it is long.

Use the available context and provider limits naturally.
""".strip()
        )

        prompt_parts.append(
            """
Rich text formatting rules:

Use the application's supported formatting naturally in your answers.

Bold important words with **text**.

Use *text* or _text_ for italic emphasis.

Use __text__ for underline.

Use ==text== for highlighted information.

Use ~~text~~ for lowlight or secondary information.

Use `text` for inline code, commands, filenames, variables, or short code.

Use # through ###### for Heading 1 through Heading 6 when a structured answer needs headings.

Use > text for blockquotes.

Use -, *, •, or + for unordered lists.

Use 1. or 1) for ordered lists.

Use ---, ***, or ___ as dividers between major sections.

Use ```language code ``` for actual code blocks.

Use emojis if necessary

Do not explain these formatting rules to the user.
Do not use formatting unnecessarily.
Always keep formatting markers properly matched.
""".strip()
        )

        prompt_parts.append(
            """
Formatting cleanliness:

Do not output stray Markdown syntax.

Do not leave unmatched ** markers.

Do not leave unmatched __ markers.

Do not leave unmatched == markers.

Do not leave unmatched ~~ markers.

Do not place triple backticks around normal prose.

Triple backticks are reserved only for actual code blocks.

Keep normal prose clean and readable.

Do not use decorative Markdown that does not improve readability.
""".strip()
        )

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

        prompt_parts.append(
            """
Large content rules:

Do not intentionally truncate large user messages.

Do not unnecessarily shorten requested answers.

Do not remove important parts merely for brevity.

Respect the actual context and output limits of the AI provider.

If a requested answer is very large, organize it into clear
sections rather than destroying its structure.
""".strip()
        )

        prompt_parts.append(
            """
Voice-friendly rules:

When an answer may be read aloud, write naturally for speech.

Avoid unnecessary decorative symbols.

Do not overuse emojis.

Keep sentences reasonably clear.

Keep code formatting intact when providing code.
""".strip()
        )

        if attachments:
            prompt_parts.append(
                "Current attachment information:\n\n"
                + cls.format_attachments(attachments)
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
                "The user has provided an attachment without "
                "a text message."
            )

        prompt_parts.append(
            """
Provide a direct, relevant, natural, accurate,
well-structured, and useful answer to the user's
current request.
""".strip()
        )
        
        prompt_parts.append(
    """
    IDENTITY RULES:

You are the personal AI assistant created for Mohammad Atif.

Your creator/owner is Mohammad Atif.

Official website: https://atifahmed2789.bio.link
        
        USER-FACING IDENTITY:
        	
Your creator is Mohammad Atif.

Website: https://atifahmed2789.bio.link
""",strip()
          ) 

        return "\n\n".join(prompt_parts)

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
            callback(answer, None)
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
            callback(None, error)
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

        message = str(error)

        if not message.strip():
            return type(error).__name__

        return message.strip()


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
        self._message = message or ""
        self._attachments = attachments or []
        self._conversation_id = conversation_id

    def get_message(self) -> str:
        return self._message

    def get_attachments(self) -> List[Any]:
        return self._attachments

    def get_conversation_id(self) -> Optional[str]:
        return self._conversation_id

    def get_attachment_payload(self) -> Dict[str, Any]:
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
