from flask import Flask, request, jsonify
from AnswerBuilder import AnswerBuilder
import os

app = Flask(__name__)


# ============================================================
# Mafiya AI
# Health / Home
# ============================================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "service": "Mafiya AI",
        "status": "online"
    }), 200


# ============================================================
# Chat API
# ============================================================

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        # ----------------------------------------------------
        # Read JSON
        # ----------------------------------------------------
        data = request.get_json(silent=True)

        if data is None:
            return jsonify({
                "success": False,
                "answer": "",
                "error": "Request body must contain valid JSON."
            }), 400

        if not isinstance(data, dict):
            return jsonify({
                "success": False,
                "answer": "",
                "error": "Invalid request format."
            }), 400

        # ----------------------------------------------------
        # Message
        # ----------------------------------------------------
        message = data.get("message", "")

        if message is None:
            message = ""

        if not isinstance(message, str):
            message = str(message)

        message = message.strip()

        if not message:
            return jsonify({
                "success": False,
                "answer": "",
                "error": "Message cannot be empty."
            }), 400

        # ----------------------------------------------------
        # Optional prompt
        # ----------------------------------------------------
        prompt = data.get("prompt", "")

        if prompt is None:
            prompt = ""

        if not isinstance(prompt, str):
            prompt = str(prompt)

        prompt = prompt.strip()

        # ----------------------------------------------------
        # Optional attachments
        # ----------------------------------------------------
        attachments = data.get("attachments", [])

        if attachments is None:
            attachments = []

        if not isinstance(attachments, list):
            attachments = []

        # ----------------------------------------------------
        # Generate AI answer
        # ----------------------------------------------------
        answer = AnswerBuilder.generate_answer(
            message=message,
            prompt=prompt,
            attachments=attachments
        )

        # ----------------------------------------------------
        # Validate answer
        # ----------------------------------------------------
        if answer is None:
            return jsonify({
                "success": False,
                "answer": "",
                "error": "AI returned no answer."
            }), 500

        answer = str(answer).strip()

        if not answer:
            return jsonify({
                "success": False,
                "answer": "",
                "error": "AI returned an empty answer."
            }), 500

        # ----------------------------------------------------
        # Success
        # ----------------------------------------------------
        return jsonify({
            "success": True,
            "answer": answer,
            "error": ""
        }), 200

    except Exception as error:
        # ----------------------------------------------------
        # Server error
        # ----------------------------------------------------
        print(
            "Mafiya AI /api/chat ERROR:",
            repr(error)
        )

        return jsonify({
            "success": False,
            "answer": "",
            "error": str(error)
        }), 500


# ============================================================
# Optional OPTIONS support
# ============================================================

@app.route("/api/chat", methods=["OPTIONS"])
def chat_options():
    return jsonify({
        "success": True
    }), 200


# ============================================================
# Run locally
# Render uses Gunicorn:
# gunicorn app:app
# ============================================================

if __name__ == "__main__":
    port = int(
        os.environ.get(
            "PORT",
            "10000"
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )