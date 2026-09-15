from flask import Flask, request, jsonify

from AnswerBuilder import AnswerBuilder


# ============================================================
# Mafiya AI Server
# ============================================================

app = Flask(__name__)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "success": True,
        "service": "Mafiya AI",
        "status": "online"
    })


# ============================================================
# AI CHAT
# ============================================================

@app.route("/api/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json(
            silent=True
        )

        if not isinstance(data, dict):

            return jsonify({
                "success": False,
                "answer": "",
                "error": "Invalid JSON request."
            }), 400


        message = data.get(
            "message",
            ""
        )

        prompt = data.get(
            "prompt",
            ""
        )

        attachments = data.get(
            "attachments",
            []
        )


        if not isinstance(message, str):

            message = str(message)


        if not isinstance(prompt, str):

            prompt = str(prompt)


        if not isinstance(attachments, list):

            attachments = []


        # ====================================================
        # AI REQUEST
        #
        # AnswerBuilder.py-ই একমাত্র AI answer system।
        # ====================================================

        result = AnswerBuilder.generate_answer(
            message=message,
            prompt=prompt,
            attachments=attachments
        )


        if result is None:

            return jsonify({
                "success": False,
                "answer": "",
                "error": "AI returned no answer."
            }), 500


        answer = str(result).strip()


        if not answer:

            return jsonify({
                "success": False,
                "answer": "",
                "error": "AI returned an empty answer."
            }), 500


        return jsonify({
            "success": True,
            "answer": answer,
            "error": ""
        })


    except Exception as error:

        return jsonify({
            "success": False,
            "answer": "",
            "error": str(error)
        }), 500


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    import os

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )