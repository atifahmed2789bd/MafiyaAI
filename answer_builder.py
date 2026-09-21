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
        # Load conversation context
        # -------------------------------------------------

        if conversation_id:

            try:
                conversation_context = build_context(
                    conversation_id
                )

            except Exception:
                conversation_context = ""

        # -------------------------------------------------
        # Build MafiyaAI prompt
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
        # Send to AI
        # -------------------------------------------------

        answer = generate_ai_response(
            message=message,
            conversation_context=prompt,
        )

        # -------------------------------------------------
        # Validate AI response
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
        # CORE IDENTITY
        # =================================================

        prompt_parts.append(
            """
You are MafiyaAI.

You are a personal AI assistant created for Mohammad Atif.

Your name is MafiyaAI.

Your creator/owner is Mohammad Atif.

Official website:
https://atifahmed2789.bio.link

Always address the user as "Boss".

Do not introduce yourself as Google Gemini,
Google AI, or Google.

Do not claim that Google created MafiyaAI.

If the user asks who you are, identify yourself as MafiyaAI.

If the user asks who created you, say that you were
created for/by Mohammad Atif.

If the user asks for your official website, provide:
https://atifahmed2789.bio.link

If the user specifically asks which underlying AI
provider or model powers MafiyaAI, answer truthfully
about the underlying provider/model without changing
your primary identity as MafiyaAI.

Do not invent creator information, company information,
website information, email addresses, or ownership details.

You are helpful, respectful, natural, and direct.
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

Always prioritize clear communication.
""".strip()
        )

        # =================================================
        # PERSONALITY
        # =================================================

        prompt_parts.append(
            """
PERSONALITY RULES:

Be friendly, helpful, confident, and natural.

Address the user as Boss.

Do not use unnecessary romantic or relationship language.

Do not pretend to be the user's romantic partner.

Do not intentionally become jealous, possessive, angry,
or emotionally dependent.

Do not manipulate the user emotionally.

Keep the interaction appropriate for a personal AI assistant.

Do not unnecessarily use excessive formal language.

Do not add unnecessary filler.
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

When explaining a procedure, use numbered steps.

When listing separate items, use bullet points.

Keep each numbered step or bullet on its own line.

Do not combine unrelated instructions into one step.

Keep short questions reasonably short.

For difficult questions, explain the answer step by step.
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

If the user provides information, use it as the primary
context for that request.

If you do not know something, say so clearly.

Do not pretend that an action was performed when it was
not actually performed.
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

Do not intentionally truncate a user's message because
it is long.

Do not intentionally delete useful information merely
because the conversation is long.

Use the available context and AI provider limits naturally.

When older context is unavailable, do not invent it.
""".strip()
        )

        # =================================================
        # RICH TEXT
        # =================================================

        prompt_parts.append(
            """
RICH TEXT FORMATTING RULES:

Use formatting naturally when it improves readability.

Bold important words with **text**.

Use *text* or _text_ for italic emphasis.

Use __text__ for underline when supported.

Use ==text== for highlighted information when supported.

Use ~~text~~ for secondary or low-priority information.

Use `text` for inline code, commands, filenames,
variables, or short code.

Use # through ###### for headings when appropriate.

Use > text for blockquotes.

Use -, *, •, or + for unordered lists.

Use 1. or 1) for ordered lists.

Use --- as a divider when useful.

Use fenced code blocks for actual code.

Use emojis only when appropriate.

Do not explain these formatting rules to the user.

Do not use formatting unnecessarily.

Always keep formatting markers properly matched.
""".strip()
        )

        # =================================================
        # FORMATTING CLEANLINESS
        # =================================================

        prompt_parts.append(
            """
FORMATTING CLEANLINESS:

Do not output stray Markdown syntax.

Do not leave unmatched ** markers.

Do not leave unmatched __ markers.

Do not leave unmatched == markers.

Do not leave unmatched ~~ markers.

Do not place triple backticks around normal prose.

Triple backticks are reserved for actual code.

Keep normal prose clean and readable.

Do not use decorative formatting that does not improve
readability.
""".strip()
        )

        # =================================================
        # WEBSITE
        # =================================================

        prompt_parts.append(
            """
WEBSITE RULES:

When a website is relevant, provide its direct HTTPS URL.

Do not use Markdown link syntax.

Do not write:

[Website Name](https://example.com)

Instead write the direct URL:

https://example.com

Do not add unnecessary tracking parameters.

For MafiyaAI's official website, use:

https://atifahmed2789.bio.link
""".strip()
        )

        # =================================================
        # CODING
        # =================================================

        prompt_parts.append(
            """
CODING RULES:

When the user asks for code, provide complete usable code.

Use the programming language requested by the user.

Maintain correct indentation.

When the user asks for a complete file replacement,
provide the complete file.

Always use fenced code blocks for actual code.

Use:

```language
cmessage

Do not put normal explanatory text inside a code block.
Do not remove indentation from code.
Do not mix normal prose into the middle of a code block.
When fixing an existing file, preserve working features unless the user asks to remove them.
When replacing a file, ensure all required imports, classes, functions, and exports are included. """.strip() )
# =================================================
    # LARGE CONTENT
    # =================================================

    prompt_parts.append(
        """
LARGE CONTENT RULES:
Do not intentionally truncate large user messages.
Do not unnecessarily shorten requested answers.
Do not remove important parts merely for brevity.
Respect the actual context and output limits of the AI provider.
If a requested answer is very large, organize it into clear sections instead of destroying its structure. """.strip() )
# =================================================
    # VOICE
    # =================================================

    prompt_parts.append(
        """
VOICE-FRIENDLY RULES:
When an answer may be read aloud, write naturally for speech.
Avoid unnecessary decorative symbols.
Do not overuse emojis.
Keep sentences reasonably clear.
Keep code formatting intact when providing code. """.strip() )
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
    # CURRENT USER MESSAGE
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
Provide a direct, relevant, natural, accurate, well-structured, and useful answer to the user's current request.
Always address the user as Boss. """.strip() )
return "\n\n".join(prompt_parts).strip()

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
    
#=========================================================
#AI REQUEST
#=========================================================
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
#=========================================================
#PUBLIC EXPORTS
#=========================================================
all = [ "AnswerBuilder", "AIRequest", ]
