# Mafiya AI

Mafiya AI is a personal AI assistant powered by Google Gemini.

## Project Structure

- `AnswerBuilder.py` — Main AI answer system
- `MemoryManager.py` — Persistent conversation memory system
- `app.py` — Flask server and Chat API
- `config.py` — Gemini configuration
- `requirements.txt` — Python dependencies
- `.gitignore` — Ignored files

## AI System

Mafiya AI uses multiple Gemini models with automatic fallback.

If one Gemini model fails, the next configured model is tried automatically.

All AI answer-generation logic is handled by `AnswerBuilder.py`.

## Memory System

Mafiya AI uses `MemoryManager.py` for persistent conversation memory.

The memory system stores:

- User messages
- AI responses
- Conversation timestamps

The SQLite database is:

`mafiya_memory.db`

There is no automatic message deletion or fixed message-count storage limit.

The database file is excluded from Git using `.gitignore`.

## Configuration

The Gemini API key is provided through the Render environment variable:

`GEMINI_API_KEY`

The API key must not be stored directly inside GitHub source files.

Gemini model names can also be configured through Render environment variables:

- `GEMINI_MODEL_1`
- `GEMINI_MODEL_2`
- `GEMINI_MODEL_3`
- `GEMINI_MODEL_4`
- `GEMINI_MODEL_5`
- `GEMINI_MODEL_6`

## Server

The project is designed to run on Render using Gunicorn.

Start command:

`gunicorn app:app`

## Chat API

Endpoint:

`POST /api/chat`

The API accepts a JSON request containing:

- `message`
- `prompt`
- `attachments`

The response contains:

- `success`
- `answer`
- `error`

## Application

Name: Mafiya AI