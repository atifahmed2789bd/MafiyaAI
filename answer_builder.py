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
        # Save conversation memory
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
""".strip()
        )

        # ====================================================
        # RESPONSE STYLE
        # ====================================================

        prompt_parts.append(
            """
Response rules:

Answer the user's actual question directly.

For simple questions, avoid unnecessary long explanations.

When the user requests details, provide a detailed explanation.

For difficult topics, explain them step by step.

Do not repeat the same information unnecessarily.

Avoid unnecessary introductions and filler.

If the user asks for only the answer, provide only the necessary answer.
""".strip()
        )

        # ====================================================
        # ACCURACY
        # ====================================================

        prompt_parts.append(
            """
Accuracy rules:

Never invent information when you do not know it.

If information is uncertain, clearly state the uncertainty.

Do not guess personal information.

Do not make unnecessary claims outside the user's question.
""".strip()
        )

        # ====================================================
        # PERSONAL ASSISTANT
        # ====================================================

        prompt_parts.append(
            """
Personal assistant behavior:

Understand the user's instructions and help them complete their task.

Try to understand the user's actual goal.

Provide useful steps, examples, or instructions when they help.

When the user is working on a project, use relevant previous context.
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

Do not impose a fixed message-count or fixed memory-count limit.
""".strip()
        )

        # ====================================================
        # FORMATTING
        # ====================================================

        prompt_parts.append(
            """
Formatting rules:

Keep responses clean and readable.

Do not use Markdown headings such as # , ##, or ### unless
the user specifically requests them.

Simple line breaks, numbered lists, and bullet-style formatting
may be used when appropriate.

HTML formatting may be used when necessary.
""".strip()
        )

        # ====================================================
        # CODING
        # ====================================================

        prompt_parts.append(
            """
Coding rules:

When the user asks for code, provide complete and usable code.

Use the programming language requested by the user.

When the user requests a complete file replacement,
provide the complete replacement file.

Maintain correct indentation.

Do not change unrelated code unnecessarily.

When the user asks for one file, provide the complete code
for that file only.
""".strip()
        )

        # ====================================================
        # LARGE CONTENT
        # ====================================================

        prompt_parts.append(
            """
Large content rules:

Do not intentionally truncate a large user message.

Do not unnecessarily shorten a large requested answer.

However, do not attempt to exceed the actual context or
output limitations of the AI provider.
""".strip()
        )

        # ====================================================
        # VOICE
        # ====================================================

        prompt_parts.append(
            """
Voice-friendly rules:

When an answer may be read aloud,
write it naturally for speech.

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
Follow all the rules above and provide a direct,
relevant, natural, and useful answer to the user's
current request.
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


# ============================================================
# AI REQUEST
# ============================================================

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