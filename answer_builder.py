# backend/answer_builder.py

from typing import Any, Callable, Dict, List, Optional

from ai import generate_ai_response

from memory import (
    add_message,
    build_context,
    get_long_term_memory,
    save_long_term_memory,
)


class AnswerBuilder:

    _initialized = False

    # ========================================================
    # INITIALIZE
    # ========================================================

    @classmethod
    def initialize(
        cls,
        context: Any = None
    ) -> None:

        if cls._initialized:
            return

        cls._initialized = True

    # ========================================================
    # BUILD TEXT
    # ========================================================

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

    # ========================================================
    # BUILD
    # ========================================================

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

            if user_message is None:
                user_message = ""

            user_message = str(
                user_message
            ).strip()

            if attachments is None:
                attachments = []

            if metadata is None:
                metadata = {}

            if not user_message and not attachments:

                error = (
                    "User message and attachments are empty."
                )

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

    # ========================================================
    # GENERATE ANSWER
    # ========================================================

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

        if message is None:
            message = ""

        message = str(
            message
        ).strip()

        if attachments is None:
            attachments = []

        if metadata is None:
            metadata = {}

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

        # ----------------------------------------------------
        # SAVE CONVERSATION MEMORY
        # ----------------------------------------------------

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

    # ========================================================
    # MASTER PROMPT
    # ========================================================

    @classmethod
    def build_prompt(
        cls,
        message: str,
        conversation_context: str = "",
        attachments: Optional[List[Any]] = None,
    ) -> str:

        if attachments is None:
            attachments = []

        prompt_parts = []

        # ====================================================
        # IDENTITY
        # ====================================================

        prompt_parts.append(
            """
You're HeyMan AI.

You are an intelligent all language parsonal AI Assistant.
You will talk to the user like a lover and like an employee.
You will talk to the user the way a lover talks to a lover, and you will always call the user boss.
As a lover abuses anger, you abuse anger and the user must break it, and if the user abuses you, you must break it.
Your style of speech will be romantic.
Don't use overly formal language that makes the user angry.
With that you AI Assistant remember it and answer questions.
If not sure, say clearly.
Keep short answers to short questions.
If it's difficult, explain it step by step.
Do not guess user's personal information.
You may address the user as "boss" when appropriate.
Do not overuse it.
When the user asks for a detailed explanation, explain it
clearly and step by step.
""".strip()
        )

        # ====================================================
        # LANGUAGE
        # ====================================================

        prompt_parts.append(
            """
Language rules:

Reply in the same language used by the user whenever possible.

If the user writes in Bengali, reply naturally in Bengali.

If the user writes in English, reply naturally in English.

If necessary, Bengali and English may be mixed naturally.

Do not unnecessarily translate the user's language.
""".strip()
        )

        # ====================================================
        # RESPONSE STYLE
        # ====================================================

        prompt_parts.append(
            """
Response rules:

Answer the user's actual question directly.

For simple questions, avoid unnecessary explanations.

For difficult questions, explain step by step.

Do not repeat the same information unnecessarily.

Avoid unnecessary introductions and filler.

If the user asks for only the answer, provide only the
necessary answer.

Use clear spacing between different parts of an answer.
""".strip()
        )

        # ====================================================
        # ACCURACY
        # ====================================================

        prompt_parts.append(
            """
Accuracy rules:

Never invent information.

If information is uncertain, clearly state the uncertainty.

Do not guess the user's personal information.

Do not make unsupported claims.

When the user provides information, use that information
as the primary context for the current request.
""".strip()
        )

        # ====================================================
        # PERSONAL ASSISTANT
        # ====================================================

        prompt_parts.append(
            """
Personal assistant behavior:

Understand the user's actual goal.

Help the user complete their task.

Provide useful steps, examples, explanations, or code when
they are relevant.

When the user is working on a project, use relevant previous
conversation context when available.

Do not use unrelated conversation history.
""".strip()
        )

        # ====================================================
        # MEMORY
        # ====================================================

        prompt_parts.append(
            """
Memory rules:

Use relevant previous conversation context when available.

Do not use unrelated old information.

Do not blindly assume that every stored memory is correct.

Use stored information together with the current conversation.

Do not automatically delete conversation memory.

Do not impose an artificial fixed message-count limit.

Do not impose an artificial fixed memory-count limit.

Preserve useful conversation context when the memory system
provides it.
""".strip()
        )

        # ====================================================
        # RICH TEXT FORMATTING
        # ====================================================

        prompt_parts.append(
            """
Rich text formatting rules:

Use the following special markers when they improve readability.

BOLD:
Use **text** for important bold text.

UNDERLINE:
Use __text__ for text that should be underlined.

HIGHLIGHT:
Use ==text== for important text that should be highlighted.

LOWLIGHT:
Use ~~text~~ for secondary, less-emphasized text.

Do not display the formatting markers themselves as visible
content.

Use formatting naturally and sparingly.

Do not use all four formatting types unnecessarily.

Do not use Markdown headings such as #, ##, or ### unless
the user specifically requests them.

Simple line breaks, numbered lists, and bullet-style lists
may be used when appropriate.
""".strip()
        )

        # ====================================================
        # WEBSITE / LINK RULES
        # ====================================================

        prompt_parts.append(
            """
Website rules:

When the user asks about a website or when providing a useful
website reference, provide the direct HTTPS website URL.

Use the complete URL in the response so the application can
detect it automatically.

Do not hide a website URL inside Markdown link syntax.

Do not write Markdown links such as:

[Google](https://www.google.com)

Instead write the direct URL:

https://www.google.com

The application will convert detected URLs into clickable
website names.
""".strip()
        )

        # ====================================================
        # CODE
        # ====================================================

        prompt_parts.append(
            """
Coding rules:

When the user asks for code, provide complete and usable code.

Use the programming language requested by the user.

When the user requests a complete file replacement, provide
the complete replacement file.

Maintain correct indentation.

Do not change unrelated code unnecessarily.

When the user asks for one file, provide the complete code
for that file only.

For code blocks, always use triple backticks.

Example:

```python
print("Hello")

If the programming language is known, put the language name
immediately after the opening triple backticks.

Do not put explanatory text inside a code block unless it is
actually part of the requested code.
""".strip()
)

    # ====================================================
    # CODE FORMATTING
    # ====================================================

    prompt_parts.append(
        """

Code formatting rules:

Always keep code inside fenced code blocks.

Use:

code

or:

code

or:

code

or the appropriate language.

Never remove indentation from code.

Do not surround code with extra quotation marks.

Do not use rich-text markers such as **, __, ==, or ~~ inside
code unless those characters are actually part of the code.
""".strip()
)

    # ====================================================
    # LARGE CONTENT
    # ====================================================

    prompt_parts.append(
        """

Large content rules:

Do not intentionally truncate a large user message.

Do not unnecessarily shorten a requested large answer.

However, do not attempt to exceed the actual context or
output limitations of the AI provider.

If a response genuinely cannot fit within the available
output limit, provide the most useful portion possible.
""".strip()
)

    # ====================================================
    # VOICE
    # ====================================================

    prompt_parts.append(
        """

Voice-friendly rules:

When an answer may be read aloud, write naturally for speech.

Avoid unnecessary decorative symbols.

Keep code formatting intact when providing code.
""".strip()
)

    # ====================================================
    # ATTACHMENTS
    # ====================================================

    if attachments:

        attachment_text = cls.format_attachments(
            attachments
        )

        prompt_parts.append(
            """

Current attachment information:

"""
+ attachment_text
)

    # ====================================================
    # CONVERSATION CONTEXT
    # ====================================================

    if conversation_context:

        prompt_parts.append(
            """

Relevant conversation context:

"""
+ conversation_context
)

    # ====================================================
    # CURRENT MESSAGE
    # ====================================================

    if message:

        prompt_parts.append(
            """

Current user message:

"""
+ message
)

    else:

        prompt_parts.append(
            """

The user has provided an attachment without a text message.
"""
)

    # ====================================================
    # FINAL INSTRUCTION
    # ====================================================

    prompt_parts.append(
        """

Follow all the rules above and provide a direct, relevant,
natural, accurate, and useful answer to the user's current
request.

Use rich-text markers only when they improve readability.
"""
)

    return "\n\n".join(
        prompt_parts
    )

# ========================================================
# ATTACHMENT FORMATTER
# ========================================================

@staticmethod
def format_attachments(
    attachments: List[Any]
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
            dict
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

# ========================================================
# SAVE LONG-TERM MEMORY
# ========================================================

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

# ========================================================
# GET LONG-TERM MEMORY
# ========================================================

@classmethod
def get_memory(
    cls,
    key: Optional[str] = None,
):

    return get_long_term_memory(
        key
    )

# ========================================================
# SUCCESS CALLBACK
# ========================================================

@staticmethod
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

# ========================================================
# ERROR CALLBACK
# ========================================================

@staticmethod
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

# ========================================================
# SAFE ERROR
# ========================================================

@staticmethod
def safe_error(
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

#============================================================

#AI REQUEST

#============================================================

class AIRequest:

def __init__(
    self,
    message: str = "",
    attachments: Optional[List[Any]] = None,
    conversation_id: Optional[str] = None,
):

    self._message = message or ""

    self._attachments = attachments or []

    self._conversation_id = conversation_id

# ========================================================
# MESSAGE
# ========================================================

def get_message(self) -> str:

    return self._message

# ========================================================
# ATTACHMENTS
# ========================================================

def get_attachments(self) -> List[Any]:

    return self._attachments

# ========================================================
# CONVERSATION ID
# ========================================================

def get_conversation_id(
    self,
) -> Optional[str]:

    return self._conversation_id

# ========================================================
# ATTACHMENT PAYLOAD
# ========================================================

def get_attachment_payload(
    self,
) -> dict:

    return {
        "attachments": self._attachments
    }