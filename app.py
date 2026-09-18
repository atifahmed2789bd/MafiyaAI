# backend/app.py

from flask import Flask, jsonify, request

from chat import (
    chat_health_check,
    new_chat,
    send_message,
    send_voice_message,
)
from memory import (
    get_all_conversations,
    get_conversation,
    get_memory_stats,
    get_long_term_memory,
    save_long_term_memory,
    search_memory,
)


# ============================================================
# MafiyaAI Backend Server
# ============================================================

app = Flask(__name__)


# ============================================================
# Basic Configuration
# ============================================================

app.config["JSON_AS_ASCII"] = False


# ============================================================
# Home / Server Status
# ============================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "success": True,
        "name": "MafiyaAI",
        "status": "online",
        "message": "MafiyaAI backend is running."
    })


# ============================================================
# Health Check
# ============================================================

@app.route("/health", methods=["GET"])
def health():

    result = chat_health_check()

    return jsonify({
        "success": result.get("success", False),
        "server": True,
        "ai": result.get("ai", False),
        "response": result.get("response"),
        "error": result.get("error")
    })


# ============================================================
# Create New Chat
# ============================================================

@app.route("/chat/new", methods=["POST"])
def create_new_chat():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        title = data.get(
            "title"
        )

        result = new_chat(
            title=title
        )

        return jsonify(result)

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# Send Text Message
# ============================================================

@app.route("/chat/message", methods=["POST"])
def chat_message():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        message = data.get(
            "message"
        )

        conversation_id = data.get(
            "conversation_id"
        )

        metadata = data.get(
            "metadata"
        )

        if message is None:

            return jsonify({
                "success": False,
                "error": "message is required."
            }), 400

        result = send_message(
            message=message,
            conversation_id=conversation_id,
            metadata=metadata
        )

        return jsonify(result)

    except ValueError as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 400

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# Send Voice Message
# ============================================================

@app.route("/chat/voice", methods=["POST"])
def chat_voice():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        recognized_text = data.get(
            "text"
        )

        conversation_id = data.get(
            "conversation_id"
        )

        if not recognized_text:

            return jsonify({
                "success": False,
                "error": "text is required."
            }), 400

        result = send_voice_message(
            recognized_text=recognized_text,
            conversation_id=conversation_id
        )

        return jsonify(result)

    except ValueError as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 400

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# Get All Conversations
# ============================================================

@app.route("/memory/conversations", methods=["GET"])
def conversations():

    try:

        result = get_all_conversations()

        return jsonify({
            "success": True,
            "conversations": result
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# Get One Conversation
# ============================================================

@app.route(
    "/memory/conversation/<conversation_id>",
    methods=["GET"]
)
def conversation(conversation_id):

    try:

        result = get_conversation(
            conversation_id
        )

        if result is None:

            return jsonify({
                "success": False,
                "error": "Conversation not found."
            }), 404

        return jsonify({
            "success": True,
            "conversation": result
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# Search Memory
# ============================================================

@app.route("/memory/search", methods=["GET"])
def memory_search():

    try:

        query = request.args.get(
            "q",
            ""
        )

        if not query.strip():

            return jsonify({
                "success": False,
                "error": "Search query is required."
            }), 400

        results = search_memory(
            query
        )

        return jsonify({
            "success": True,
            "query": query,
            "results": results
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# Memory Statistics
# ============================================================

@app.route("/memory/stats", methods=["GET"])
def memory_stats():

    try:

        stats = get_memory_stats()

        return jsonify({
            "success": True,
            "stats": stats
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# Get Long-Term Memory
# ============================================================

@app.route("/memory/long-term", methods=["GET"])
def get_long_term():

    try:

        key = request.args.get(
            "key"
        )

        result = get_long_term_memory(
            key
        )

        return jsonify({
            "success": True,
            "memory": result
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# Save Long-Term Memory
# ============================================================

@app.route(
    "/memory/long-term",
    methods=["POST"]
)
def save_long_term():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        key = data.get(
            "key"
        )

        value = data.get(
            "value"
        )

        if not key:

            return jsonify({
                "success": False,
                "error": "key is required."
            }), 400

        save_long_term_memory(
            key=key,
            value=value
        )

        return jsonify({
            "success": True,
            "message": "Long-term memory saved."
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# 404 Handler
# ============================================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({
        "success": False,
        "error": "Endpoint not found."
    }), 404


# ============================================================
# Global Error Handler
# ============================================================

@app.errorhandler(Exception)
def internal_error(error):

    return jsonify({
        "success": False,
        "error": str(error)
    }), 500


# ============================================================
# Start Server
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        threaded=True
    )