# Mafiya AI

Mafiya AI is a personal AI assistant powered by Google Gemini.

## Project Structure

- `AnswerBuilder.py` — Main AI answer system
- `app.py` — Flask server
- `config.py` — Gemini configuration
- `requirements.txt` — Python dependencies
- `.gitignore` — Ignored files

## AI System

Mafiya AI uses multiple Gemini models with automatic fallback.

If one Gemini model fails, the next configured model is tried automatically.

## Configuration

The Gemini API key is provided through the Render environment variable:

`GEMINI_API_KEY`

The API key must not be stored directly inside GitHub source files.

## Server

The project is designed to run on Render using Gunicorn.

## Application

Name: Mafiya AI