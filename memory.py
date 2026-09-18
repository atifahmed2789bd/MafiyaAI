# backend/memory.py

import json
import os
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ============================================================
# MafiyaAI Memory System
# ============================================================
#
# No fixed message limit
# No fixed memory-entry limit
# No automatic deletion
#
# Memory is stored in a JSON file and grows as storage allows.
# ============================================================


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEMORY_FILE = os.path.join(
    BASE_DIR,
    "mafiyaai_memory.json"
)

_memory_lock = threading.RLock()


# ============================================================
# Internal Helpers
# ============================================================

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _empty_memory() -> Dict[str, Any]:
    return {
        "version": 1,
        "created_at": _now(),
        "updated_at": _now(),
        "conversations": []
    }


def _load_memory() -> Dict[str, Any]:

    with _memory_lock:

        if not os.path.exists(MEMORY_FILE):
            return _empty_memory()

        try:

            with open(
                MEMORY_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            if not isinstance(data, dict):
                return _empty_memory()

            if "conversations" not in data:
                data["conversations"] = []

            return data

        except (json.JSONDecodeError, OSError):

            # Do not destroy existing data.
            # Return a fresh in-memory structure if the file
            # cannot currently be read.
            return _empty_memory()


def _save_memory(data: Dict[str, Any]) -> None:

    with _memory_lock:

        data["updated_at"] = _now()

        directory = os.path.dirname(MEMORY_FILE)

        if directory:
            os.makedirs(
                directory,
                exist_ok=True
            )

        temporary_file = MEMORY_FILE + ".tmp"

        with open(
            temporary_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2
            )

        # Atomic replacement
        os.replace(
            temporary_file,
            MEMORY_FILE
        )


# ============================================================
# Create Conversation
# ============================================================

def create_conversation(
    title: Optional[str] = None
) -> str:

    import uuid

    conversation_id = str(uuid.uuid4())

    data = _load_memory()

    conversation = {
        "id": conversation_id,
        "title": title or "New Conversation",
        "created_at": _now(),
        "updated_at": _now(),
        "messages": []
    }

    data["conversations"].append(
        conversation
    )

    _save_memory(data)

    return conversation_id


# ============================================================
# Add Message
# ============================================================

def add_message(
    conversation_id: str,
    role: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:

    import uuid

    if not conversation_id:
        raise ValueError(
            "conversation_id is required."
        )

    if not role:
        raise ValueError(
            "role is required."
        )

    if content is None:
        content = ""

    data = _load_memory()

    conversation = None

    for item in data["conversations"]:

        if item.get("id") == conversation_id:
            conversation = item
            break

    if conversation is None:

        conversation_id = create_conversation()

        data = _load_memory()

        for item in data["conversations"]:

            if item.get("id") == conversation_id:
                conversation = item
                break

    message = {
        "id": str(uuid.uuid4()),
        "role": role,
        "content": str(content),
        "created_at": _now()
    }

    if metadata:
        message["metadata"] = metadata

    conversation["messages"].append(
        message
    )

    conversation["updated_at"] = _now()

    _save_memory(data)

    return message


# ============================================================
# Get One Conversation
# ============================================================

def get_conversation(
    conversation_id: str
) -> Optional[Dict[str, Any]]:

    data = _load_memory()

    for conversation in data["conversations"]:

        if conversation.get("id") == conversation_id:
            return conversation

    return None


# ============================================================
# Get All Conversations
# ============================================================

def get_all_conversations() -> List[Dict[str, Any]]:

    data = _load_memory()

    return data["conversations"]


# ============================================================
# Get Conversation Messages
# ============================================================

def get_messages(
    conversation_id: str
) -> List[Dict[str, Any]]:

    conversation = get_conversation(
        conversation_id
    )

    if not conversation:
        return []

    return conversation.get(
        "messages",
        []
    )


# ============================================================
# Build AI Context
# ============================================================

def build_context(
    conversation_id: str
) -> str:

    messages = get_messages(
        conversation_id
    )

    if not messages:
        return ""

    context_parts = []

    for message in messages:

        role = message.get(
            "role",
            "unknown"
        )

        content = message.get(
            "content",
            ""
        )

        if not content:
            continue

        context_parts.append(
            f"{role}: {content}"
        )

    return "\n\n".join(
        context_parts
    )


# ============================================================
# Search Memory
# ============================================================

def search_memory(
    query: str
) -> List[Dict[str, Any]]:

    if not query:
        return []

    query = query.lower()

    data = _load_memory()

    results = []

    for conversation in data["conversations"]:

        for message in conversation.get(
            "messages",
            []
        ):

            content = str(
                message.get(
                    "content",
                    ""
                )
            )

            if query in content.lower():

                results.append({
                    "conversation_id":
                        conversation.get("id"),

                    "message_id":
                        message.get("id"),

                    "role":
                        message.get("role"),

                    "content":
                        content,

                    "created_at":
                        message.get("created_at")
                })

    return results


# ============================================================
# Save Long-Term Memory
# ============================================================

def save_long_term_memory(
    key: str,
    value: Any
) -> None:

    data = _load_memory()

    if "long_term_memory" not in data:
        data["long_term_memory"] = {}

    data["long_term_memory"][key] = {
        "value": value,
        "updated_at": _now()
    }

    _save_memory(data)


# ============================================================
# Get Long-Term Memory
# ============================================================

def get_long_term_memory(
    key: Optional[str] = None
):

    data = _load_memory()

    memories = data.get(
        "long_term_memory",
        {}
    )

    if key is None:
        return memories

    memory = memories.get(key)

    if memory is None:
        return None

    return memory.get(
        "value"
    )


# ============================================================
# Delete Conversation
# ============================================================
#
# This function exists only for an explicit user action.
# Nothing is automatically deleted by the system.
# ============================================================

def delete_conversation(
    conversation_id: str
) -> bool:

    data = _load_memory()

    original_count = len(
        data["conversations"]
    )

    data["conversations"] = [
        conversation
        for conversation in data["conversations"]
        if conversation.get("id") != conversation_id
    ]

    changed = (
        len(data["conversations"])
        != original_count
    )

    if changed:
        _save_memory(data)

    return changed


# ============================================================
# Memory Statistics
# ============================================================

def get_memory_stats() -> Dict[str, int]:

    data = _load_memory()

    conversations = data.get(
        "conversations",
        []
    )

    conversation_count = len(
        conversations
    )

    message_count = 0

    for conversation in conversations:

        message_count += len(
            conversation.get(
                "messages",
                []
            )
        )

    long_term_count = len(
        data.get(
            "long_term_memory",
            {}
        )
    )

    return {
        "conversations":
            conversation_count,

        "messages":
            message_count,

        "long_term_memories":
            long_term_count
    }