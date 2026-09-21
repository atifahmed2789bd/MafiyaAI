import json
import os

from flask import (
    Flask,
    Response,
    jsonify,
    request,
    stream_with_context,
)

from flask_cors import CORS

from chat import (
    chat_health_check,
    new_chat,
    send_message,
    stream_message,
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

app.config["JSON_AS_ASCII"] = False

CORS(app)


# ============================================================
# JSON Helper
# ============================================================

def json_data(data):
    return json.dumps(
        data,
        ensure_ascii=False,
        separators=(",", ":")
    )


# ============================================================
# SSE Helper
# ============================================================

def sse_event(
    event: str,
    data
) -> str:

    return (
        f"event: {event}\n"
        f"data: {json_data(data)}\n\n"
    )


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

    try:

        result = chat_health_check()

        return jsonify({
            "success": result.get(
                "success",
                False
            ),

            "server": True,

            "ai": result.get(
                "ai",
                False
            ),

            "response": result.get(
                "response"
            ),

            "error": result.get(
                "error"
            )
        })

    except Exception as error:

        print(
            "HEALTH ERROR:",
            repr(error),
            flush=True
        )

        return jsonify({
            "success": False,
            "server": True,
            "ai": False,
            "response": None,
            "error": str(error)
        }), 500


# ============================================================
# Create New Chat
# ============================================================

@app.route(
    "/chat/new",
    methods=["POST"]
)
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

        return jsonify(
            result
        )

    except Exception as error:

        print(
            "CHAT NEW ERROR:",
            repr(error),
            flush=True
        )

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# Send Text Message - SSE STREAMING
# ============================================================

@app.route(
    "/chat/message",
    methods=["POST"]
)
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


        # ----------------------------------------------------
        # Validate message
        # ----------------------------------------------------

        if message is None:

            return jsonify({
                "success": False,
                "error":
                    "message is required."
            }), 400


        message = str(
            message
        ).strip()


        if not message:

            return jsonify({
                "success": False,
                "error":
                    "message cannot be empty."
            }), 400


        # ----------------------------------------------------
        # Validate metadata
        # ----------------------------------------------------

        if metadata is None:

            metadata = {}

        elif not isinstance(
            metadata,
            dict
        ):

            return jsonify({
                "success": False,
                "error":
                    "metadata must be an object."
            }), 400


        # ----------------------------------------------------
        # Streaming generator
        # ----------------------------------------------------

        @stream_with_context
        def generate():

            stream_completed = False

            try:

                # =================================================
                # START
                # =================================================

                yield sse_event(
                    "start",
                    {
                        "success": True,
                        "streaming": True,
                    }
                )


                # =================================================
                # AI STREAM
                # =================================================

                for chunk in stream_message(
                    message=message,
                    conversation_id=conversation_id,
                    metadata=metadata
                ):

                    if chunk is None:
                        continue

                    chunk = str(
                        chunk
                    )

                    if not chunk:
                        continue


                    # ---------------------------------------------
                    # Send only actual AI text
                    # ---------------------------------------------

                    yield sse_event(
                        "chunk",
                        {
                            "text": chunk
                        }
                    )


                # =================================================
                # STREAM COMPLETED
                # =================================================

                stream_completed = True

                yield sse_event(
                    "done",
                    {
                        "success": True,
                        "streaming": False,
                    }
                )


            except GeneratorExit:

                # -------------------------------------------------
                # Client manually stopped/disconnected.
                # -------------------------------------------------

                return


            except Exception as error:

                print(
                    "CHAT STREAM ERROR:",
                    repr(error),
                    flush=True
                )


                # -------------------------------------------------
                # Send error to frontend
                # -------------------------------------------------

                try:

                    yield sse_event(
                        "error",
                        {
                            "success": False,
                            "error": str(
                                error
                            )
                        }
                    )

                except GeneratorExit:

                    return


            finally:

                if not stream_completed:

                    pass


        # --------------------------------------------------------
        # SSE HTTP Response
        # --------------------------------------------------------

        response = Response(
            generate(),
            status=200,
            content_type=(
                "text/event-stream; "
                "charset=utf-8"
            )
        )


        # --------------------------------------------------------
        # Streaming headers
        # --------------------------------------------------------

        response.headers[
            "Cache-Control"
        ] = "no-cache, no-store, must-revalidate"

        response.headers[
            "Pragma"
        ] = "no-cache"

        response.headers[
            "Expires"
        ] = "0"

        response.headers[
            "Connection"
        ] = "keep-alive"

        response.headers[
            "X-Accel-Buffering"
        ] = "no"

        response.headers[
            "Access-Control-Allow-Origin"
        ] = "*"


        return response


    except ValueError as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 400


    except Exception as error:

        print(
            "CHAT MESSAGE ERROR:",
            repr(error),
            flush=True
        )

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# Send Voice Message
# ============================================================

@app.route(
    "/chat/voice",
    methods=["POST"]
)
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


        if recognized_text is None:

            return jsonify({
                "success": False,
                "error":
                    "text is required."
            }), 400


        recognized_text = str(
            recognized_text
        ).strip()


        if not recognized_text:

            return jsonify({
                "success": False,
                "error":
                    "text cannot be empty."
            }), 400


        result = send_voice_message(
            recognized_text=recognized_text,
            conversation_id=conversation_id
        )


        return jsonify(
            result
        )


    except ValueError as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 400


    except Exception as error:

        print(
            "VOICE ERROR:",
            repr(error),
            flush=True
        )

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# Get All Conversations
# ============================================================

@app.route(
    "/memory/conversations",
    methods=["GET"]
)
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
def conversation(
    conversation_id
):

    try:

        result = get_conversation(
            conversation_id
        )

        if result is None:

            return jsonify({
                "success": False,
                "error":
                    "Conversation not found."
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

@app.route(
    "/memory/search",
    methods=["GET"]
)
def memory_search():

    try:

        query = request.args.get(
            "q",
            ""
        )


        if not query.strip():

            return jsonify({
                "success": False,
                "error":
                    "Search query is required."
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

@app.route(
    "/memory/stats",
    methods=["GET"]
)
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

@app.route(
    "/memory/long-term",
    methods=["GET"]
)
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


        if key is None:

            return jsonify({
                "success": False,
                "error":
                    "key is required."
            }), 400


        if not str(
            key
        ).strip():

            return jsonify({
                "success": False,
                "error":
                    "key cannot be empty."
            }), 400


        save_long_term_memory(
            key=key,
            value=value
        )


        return jsonify({
            "success": True,
            "message":
                "Long-term memory saved."
        })


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
# 404 Handler
# ============================================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({
        "success": False,
        "error":
            "Endpoint not found."
    }), 404


# ============================================================
# Global Error Handler
# ============================================================

@app.errorhandler(Exception)
def internal_error(error):

    print(
        "GLOBAL ERROR:",
        repr(error),
        flush=True
    )

    return jsonify({
        "success": False,
        "error": str(error)
    }), 500


# ============================================================
# Start Server
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        threaded=True
    )