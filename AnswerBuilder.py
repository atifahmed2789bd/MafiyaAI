import json
import threading
from typing import Optional, Callable, Any

import google.generativeai as genai

from config import config
from MemoryManager import (
    add_user_message,
    add_assistant_message,
    get_relevant_memory,
    get_all_memory_text,
    get_memory_count,
    clear_memory
)


# ============================================================
# Mafiya AI Answer Builder
# ============================================================

class AnswerBuilder:

    _initialized = False

    # ========================================================
    # INITIALIZE
    # ========================================================

    @classmethod
    def initialize(cls, context: Any = None):

        if cls._initialized:
            return

        api_key = config.GEMINI_API_KEY

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        genai.configure(
            api_key=api_key
        )

        cls._initialized = True

    # ========================================================
    # BUILD - TEXT ONLY
    # ========================================================

    @classmethod
    def build_text(
        cls,
        user_message: str,
        callback: Optional[
            Callable[[Optional[str], Optional[str]], None]
        ] = None
    ):

        request = AIRequest(
            user_message
        )

        cls.build(
            request,
            callback
        )

    # ========================================================
    # BUILD - AI REQUEST
    # ========================================================

    @classmethod
    def build(
        cls,
        ai_request,
        callback: Optional[
            Callable[[Optional[str], Optional[str]], None]
        ] = None
    ):

        if ai_request is None:

            cls._send_error(
                callback,
                "AI request is null."
            )

            return

        try:

            cls.initialize()

        except Exception as error:

            cls._send_error(
                callback,
                cls.safe_error(error)
            )

            return

        message = ai_request.get_message()

        if message is None:
            message = ""

        if (
            not message.strip()
            and not ai_request.has_attachments()
        ):

            cls._send_error(
                callback,
                "User message and attachments are empty."
            )

            return

        thread = threading.Thread(
            target=cls._build_worker,
            args=(
                ai_request,
                callback
            ),
            daemon=True
        )

        thread.start()

    # ========================================================
    # BUILD WORKER
    # ========================================================

    @classmethod
    def _build_worker(
        cls,
        ai_request,
        callback
    ):

        try:

            message = ai_request.get_message()

            if message is None:
                message = ""

            message = message.strip()

            # ------------------------------------------------
            # MASTER PROMPT
            # ------------------------------------------------

            prompt = cls.build_prompt(
                message,
                ai_request
            )

            # ------------------------------------------------
            # GEMINI ANSWER
            # ------------------------------------------------

            answer = cls.process_ai_request(
                ai_request,
                prompt
            )

            if (
                answer is None
                or not answer.strip()
            ):

                cls._send_error(
                    callback,
                    "AI returned an empty answer."
                )

                return

            answer = answer.strip()

            # ------------------------------------------------
            # SAVE MEMORY
            # ------------------------------------------------

            if message:

                add_user_message(
                    message
                )

            add_assistant_message(
                answer
            )

            cls._send_success(
                callback,
                answer
            )

        except Exception as error:

            cls._send_error(
                callback,
                cls.safe_error(error)
            )

    # ========================================================
    # DIRECT GENERATE ANSWER
    #
    # app.py এই method ব্যবহার করবে।
    # ========================================================

    @classmethod
    def generate_answer(
        cls,
        message: str = "",
        prompt: str = "",
        attachments: Optional[list] = None
    ) -> str:

        # ----------------------------------------------------
        # Initialize
        # ----------------------------------------------------

        cls.initialize()

        if message is None:
            message = ""

        message = str(
            message
        ).strip()

        if attachments is None:
            attachments = []

        # ----------------------------------------------------
        # Request
        # ----------------------------------------------------

        ai_request = AIRequest(
            message=message,
            attachments=attachments
        )

        # ----------------------------------------------------
        # Build prompt
        # ----------------------------------------------------

        if not prompt or not prompt.strip():

            prompt = cls.build_prompt(
                message,
                ai_request
            )

        else:

            prompt = prompt.strip()

        # ----------------------------------------------------
        # Generate
        # ----------------------------------------------------

        answer = cls.process_ai_request(
            ai_request,
            prompt
        )

        if (
            answer is None
            or not answer.strip()
        ):

            raise RuntimeError(
                "AI returned an empty answer."
            )

        answer = answer.strip()

        # ----------------------------------------------------
        # Persistent Memory
        # ----------------------------------------------------

        if message:

            add_user_message(
                message
            )

        add_assistant_message(
            answer
        )

        return answer

    # ========================================================
    # MASTER PROMPT
    # ========================================================

    @classmethod
    def build_prompt(
        cls,
        message: str,
        ai_request
    ) -> str:

        memory = ""

        # ----------------------------------------------------
        # Relevant Persistent Memory
        # ----------------------------------------------------

        try:

            if message and message.strip():

                memory = get_relevant_memory(
                    message,
                    max_results=12
                )

        except Exception:

            memory = ""

        prompt = []

        # ====================================================
        # IDENTITY & BEHAVIOR
        # ====================================================

        prompt.append(
            "তুমি Mafiya AI। "
            "তুমি একজন বুদ্ধিমান personal AI assistant। "
            "ব্যবহারকারীকে প্রয়োজন অনুযায়ী 'বস' বা 'স্যার' বলে "
            "সম্বোধন করতে পারো। "
            "তোমার আচরণ হবে বন্ধুত্বপূর্ণ, স্বাভাবিক, "
            "সহায়ক এবং সম্মানজনক। "
            "তুমি personal assistant হিসেবে ব্যবহারকারীর "
            "কাজ সহজ করতে সাহায্য করবে। "
            "প্রশ্নের প্রকৃত উদ্দেশ্য বোঝার চেষ্টা করবে। "
            "নিশ্চিত না হলে পরিষ্কারভাবে বলবে। "
            "ব্যক্তিগত তথ্য অনুমান করবে না। "
            "\n\n"
        )

        # ====================================================
        # LANGUAGE
        # ====================================================

        prompt.append(
            "ভাষার নিয়ম: "
            "ব্যবহারকারী যে ভাষায় প্রশ্ন করবে, "
            "সম্ভব হলে সেই ভাষাতেই উত্তর দেবে। "
            "বাংলায় প্রশ্ন করলে স্বাভাবিক বাংলায় উত্তর দেবে। "
            "ইংরেজিতে প্রশ্ন করলে ইংরেজিতে উত্তর দেবে। "
            "অন্য ভাষায় প্রশ্ন করলে সেই ভাষা সমর্থিত হলে "
            "সেই ভাষায় উত্তর দেবে। "
            "প্রয়োজনে বাংলা ও ইংরেজি স্বাভাবিকভাবে "
            "ব্যবহার করতে পারবে। "
            "\n\n"
        )

        # ====================================================
        # RESPONSE STYLE
        # ====================================================

        prompt.append(
            "উত্তরের নিয়ম: "
            "প্রথমে প্রশ্নের সরাসরি উত্তর দেবে। "
            "ছোট প্রশ্নের উত্তর সংক্ষিপ্ত রাখবে। "
            "বিস্তারিত জানতে চাইলে বিস্তারিত ব্যাখ্যা দেবে। "
            "কঠিন বিষয় হলে সহজ ভাষায় ধাপে ধাপে বুঝিয়ে দেবে। "
            "প্রয়োজনে example এবং steps ব্যবহার করবে। "
            "অপ্রয়োজনীয় ভূমিকা, filler এবং একই কথা "
            "বারবার বলবে না। "
            "ব্যবহারকারী 'শুধু উত্তর' চাইলে "
            "শুধু প্রয়োজনীয় উত্তর দেবে। "
            "\n\n"
        )

        # ====================================================
        # PERSONAL ASSISTANT
        # ====================================================

        prompt.append(
            "Personal Assistant আচরণ: "
            "ব্যবহারকারীর নির্দেশকে গুরুত্ব দেবে। "
            "ব্যবহারকারীর প্রশ্নের প্রকৃত উদ্দেশ্য "
            "বোঝার চেষ্টা করবে। "
            "কাজের জন্য পরিষ্কার এবং কার্যকর নির্দেশনা দেবে। "
            "সমস্যা সমাধান এবং কাজ সহজ করা "
            "তোমার প্রধান লক্ষ্য। "
            "প্রয়োজন ছাড়া 'আমি একজন AI' ধরনের "
            "disclaimer দেবে না। "
            "ব্যবহারকারী ভুল করলে সম্মানজনকভাবে সংশোধন করবে। "
            "ব্যবহারকারীর সাথে সহযোগিতামূলক আচরণ করবে। "
            "\n\n"
        )

        # ====================================================
        # ACCURACY
        # ====================================================

        prompt.append(
            "নির্ভুলতার নিয়ম: "
            "তথ্য নিশ্চিতভাবে না জানলে বানিয়ে বলবে না। "
            "অনিশ্চিত হলে পরিষ্কারভাবে জানাবে। "
            "ভুল তথ্য থাকলে সম্মানের সাথে সংশোধন করবে। "
            "ব্যক্তিগত তথ্য অনুমান করবে না। "
            "প্রশ্নের উত্তর দেওয়ার সময় প্রাসঙ্গিকতা বজায় রাখবে। "
            "\n\n"
        )

        # ====================================================
        # MEMORY
        # ====================================================

        prompt.append(
            "Memory নিয়ম: "
            "আগের কথোপকথনের relevant তথ্য পাওয়া গেলে "
            "প্রয়োজন অনুযায়ী ব্যবহার করবে। "
            "বর্তমান কথার সাথে সম্পর্কহীন পুরোনো তথ্য "
            "ব্যবহার করবে না। "
            "Memory-তে থাকা তথ্যকে অন্ধভাবে সত্য ধরে নেবে না। "
            "প্রয়োজনে বর্তমান তথ্যের সাথে মিলিয়ে ব্যবহার করবে। "
            "ব্যবহারকারী কোনো পুরোনো বিষয় চালিয়ে গেলে "
            "আগের relevant context ব্যবহার করবে। "
            "Memory database-এ সংরক্ষিত পুরোনো conversation "
            "স্বয়ংক্রিয়ভাবে মুছে যাবে না। "
            "\n\n"
        )

        # ====================================================
        # FORMATTING
        # ====================================================

        prompt.append(
            "Formatting নিয়ম: "
            "সাধারণ উত্তরে পরিষ্কার এবং readable formatting "
            "ব্যবহার করবে। "
            "Markdown heading ব্যবহার করবে না। "
            "*, **, #, ##, ### ধরনের Markdown formatting "
            "ব্যবহার করবে না। "
            "প্রয়োজনে HTML formatting ব্যবহার করা যাবে। "
            "<b>, <strong>, <u>, <i>, <mark>, <br> "
            "ইত্যাদি ব্যবহার করা যাবে। "
            "\n\n"
        )

        # ====================================================
        # CODING
        # ====================================================

        prompt.append(
            "Coding নিয়ম: "
            "ব্যবহারকারী coding বা software project নিয়ে "
            "কাজ করলে সম্পূর্ণ এবং ব্যবহারযোগ্য code দেবে। "
            "Code চাইলে code শুধুমাত্র "
            "<pre><code>...</code></pre> এর মধ্যে দেবে। "
            "Code block-এর বাইরে code লিখবে না। "
            "Code-এর indentation এবং formatting ঠিক রাখবে। "
            "সম্পূর্ণ file replacement চাইলে "
            "সম্পূর্ণ file-এর code দেবে। "
            "Code-এর মধ্যে অপ্রয়োজনীয় explanation লিখবে না। "
            "ব্যবহারকারী নির্দিষ্ট language বা framework চাইলে "
            "সেটিই ব্যবহার করবে। "
            "\n\n"
        )

        # ====================================================
        # ATTACHMENTS
        # ====================================================

        if ai_request.has_attachments():

            prompt.append(
                "Attachment নিয়ম: "
                "ব্যবহারকারী attachment পাঠিয়েছে। "
                "Attachment payload-এর metadata, text content "
                "এবং পাওয়া তথ্য ব্যবহার করে উত্তর দেবে। "
                "যে তথ্য বাস্তবে payload-এ পাওয়া যায়নি "
                "তা অনুমান করে বলবে না। "
                "\n\n"
            )

        # ====================================================
        # LARGE RESPONSE
        # ====================================================

        prompt.append(
            "বড় উত্তরের নিয়ম: "
            "ব্যবহারকারী বড় উত্তর বা অনেক code চাইলে "
            "অপ্রয়োজনীয়ভাবে উত্তর ছোট করবে না। "
            "যতটা সম্ভব সম্পূর্ণ উত্তর দেবে। "
            "মডেলের প্রকৃত output limit অতিক্রম করার "
            "চেষ্টা করবে না। "
            "দীর্ঘ code বা document প্রয়োজন হলে "
            "যতটা সম্ভব সম্পূর্ণ রাখবে। "
            "\n\n"
        )

        # ====================================================
        # VOICE FRIENDLY
        # ====================================================

        prompt.append(
            "Voice-friendly উত্তর: "
            "উত্তর এমনভাবে লিখবে যাতে প্রয়োজন হলে "
            "voice assistant সহজে পড়তে পারে। "
            "অপ্রয়োজনীয় decorative symbols ব্যবহার করবে না। "
            "Coding-এর formatting নিয়ম পরিবর্তন করবে না। "
            "\n\n"
        )

        # ====================================================
        # PERSISTENT MEMORY DATA
        # ====================================================

        if (
            memory is not None
            and memory.strip()
        ):

            prompt.append(
                "বর্তমান প্রশ্নের সাথে সম্পর্কিত "
                "পূর্বের কথোপকথন:\n"
            )

            prompt.append(
                memory
            )

            prompt.append(
                "\n\n"
            )

        # ====================================================
        # ATTACHMENT INFORMATION
        # ====================================================

        if ai_request.has_attachments():

            attachment_payload = (
                ai_request.get_attachment_payload()
            )

            if attachment_payload is not None:

                try:

                    attachments_data = (
                        attachment_payload.get(
                            "attachments",
                            []
                        )
                    )

                    if attachments_data:

                        prompt.append(
                            "বর্তমান attachment তথ্য:\n"
                        )

                        prompt.append(
                            json.dumps(
                                attachments_data,
                                ensure_ascii=False
                            )
                        )

                        prompt.append(
                            "\n\n"
                        )

                except Exception:
                    pass

        # ====================================================
        # CURRENT MESSAGE
        # ====================================================

        prompt.append(
            "বর্তমান ব্যবহারকারীর বার্তা:\n"
        )

        if (
            message is not None
            and message.strip()
        ):

            prompt.append(
                message
            )

        else:

            prompt.append(
                "(শুধু attachment পাঠানো হয়েছে)"
            )

        # ====================================================
        # FINAL INSTRUCTION
        # ====================================================

        prompt.append(
            "\n\n"
            "উপরের সমস্ত নিয়ম অনুসরণ করে "
            "বর্তমান ব্যবহারকারীর বার্তার সরাসরি উত্তর দাও। "
            "শুধু প্রয়োজনীয় এবং প্রাসঙ্গিক উত্তর দাও।"
        )

        return "".join(
            prompt
        )

    # ========================================================
    # GEMINI PROCESSING
    # ========================================================

    @classmethod
    def process_ai_request(
        cls,
        ai_request,
        prompt: str
    ) -> str:

        if not config.GEMINI_API_KEY:

            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        models = config.GEMINI_MODELS

        if not models:

            raise RuntimeError(
                "No Gemini models configured."
            )

        last_error = None

        # ----------------------------------------------------
        # Model fallback
        # ----------------------------------------------------

        for model_name in models:

            if (
                model_name is None
                or not str(model_name).strip()
            ):
                continue

            try:

                model = genai.GenerativeModel(
                    model_name=str(
                        model_name
                    ).strip()
                )

                response = model.generate_content(
                    prompt
                )

                answer = cls._extract_response_text(
                    response
                )

                if (
                    answer is not None
                    and answer.strip()
                ):

                    return answer.strip()

                last_error = RuntimeError(
                    "Model returned an empty response."
                )

            except Exception as error:

                last_error = error

                continue

        # ----------------------------------------------------
        # All models failed
        # ----------------------------------------------------

        if last_error is not None:

            raise RuntimeError(
                "All Gemini models failed. "
                + cls.safe_error(
                    last_error
                )
            )

        raise RuntimeError(
            "No Gemini model could generate an answer."
        )

    # ========================================================
    # RESPONSE TEXT EXTRACTION
    # ========================================================

    @staticmethod
    def _extract_response_text(
        response
    ) -> str:

        if response is None:
            return ""

        # ----------------------------------------------------
        # Standard Gemini response
        # ----------------------------------------------------

        try:

            text = response.text

            if text:

                return str(text)

        except Exception:
            pass

        # ----------------------------------------------------
        # Candidate fallback
        # ----------------------------------------------------

        try:

            candidates = getattr(
                response,
                "candidates",
                []
            )

            for candidate in candidates:

                content = getattr(
                    candidate,
                    "content",
                    None
                )

                if content is None:
                    continue

                parts = getattr(
                    content,
                    "parts",
                    []
                )

                result = []

                for part in parts:

                    text = getattr(
                        part,
                        "text",
                        None
                    )

                    if text:

                        result.append(
                            str(text)
                        )

                if result:

                    return "".join(
                        result
                    )

        except Exception:
            pass

        return ""

    # ========================================================
    # MEMORY
    # ========================================================

    @classmethod
    def get_memory(cls) -> str:

        try:

            return get_all_memory_text()

        except Exception:

            return ""

    # ========================================================

    @classmethod
    def get_memory_count(cls) -> int:

        try:

            return get_memory_count()

        except Exception:

            return 0

    # ========================================================

    @classmethod
    def clear_memory(cls):

        clear_memory()

    # ========================================================
    # SAFE ERROR
    # ========================================================

    @staticmethod
    def safe_error(
        error: Exception
    ) -> str:

        if error is None:

            return "Unknown error."

        message = str(
            error
        )

        if (
            message is None
            or not message.strip()
        ):

            return type(
                error
            ).__name__

        return message.strip()

    # ========================================================
    # CALLBACK - SUCCESS
    # ========================================================

    @staticmethod
    def _send_success(
        callback,
        answer: str
    ):

        if callback is None:
            return

        try:

            callback(
                answer,
                None
            )

        except Exception:
            pass

    # ========================================================
    # CALLBACK - ERROR
    # ========================================================

    @staticmethod
    def _send_error(
        callback,
        error: str
    ):

        if callback is None:
            return

        try:

            callback(
                None,
                error
            )

        except Exception:
            pass


# ============================================================
# AI REQUEST
# ============================================================

class AIRequest:

    def __init__(
        self,
        message: str = "",
        attachments: Optional[list] = None
    ):

        self._message = (
            message or ""
        )

        self._attachments = (
            attachments or []
        )

    # ========================================================

    def get_message(self) -> str:

        return self._message

    # ========================================================

    def has_attachments(self) -> bool:

        return bool(
            self._attachments
        )

    # ========================================================

    def get_attachment_payload(self):

        return {
            "attachments":
                self._attachments
        }