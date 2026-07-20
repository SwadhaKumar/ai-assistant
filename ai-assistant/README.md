# AI Voice Assistant with Webcam Vision

A real-time voice assistant built with Gradio that can:
- listen from your microphone,
- transcribe speech with Groq Whisper,
- reason with a LangGraph ReAct agent,
- look through your webcam when needed,
- and reply using ElevenLabs text-to-speech.

## Features

- Voice-first interaction (record and ask)
- Live webcam preview in the UI
- Vision tool calling for camera-dependent questions
- Conversational memory in the chat panel
- Spoken responses with ElevenLabs

## Project Structure

- `main.py`: Gradio app, webcam stream, interaction orchestration
- `ai_agent.py`: LangGraph ReAct agent + system prompt + tool wiring
- `tools.py`: Camera capture and Groq vision analysis tool
- `speech_to_text.py`: Microphone recording + Groq transcription
- `text_to_speech.py`: ElevenLabs speech generation and playback
- `camera_state.py`: Shared camera object/state between UI and tools
- `pyproject.toml`: Project metadata and dependencies

## How It Works

1. Click **Record & Ask** in the Gradio UI.
2. Audio is recorded locally and saved as `audio_question.mp3`.
3. Groq Whisper transcribes your speech to text.
4. The agent processes your query:
   - for normal questions, it answers directly,
   - for visual questions, it calls `analyze_image_with_query`.
5. If needed, the tool captures a webcam frame and sends image + query to Groq vision.
6. The final response is spoken aloud and appended to chat.

## Requirements

- Python 3.13+
- macOS, Linux, or Windows
- Working microphone
- Webcam (for vision queries)
- FFmpeg installed (required by `pydub` for audio conversion)

### API Keys

Create a `.env` file in the project root with:

```env
GROQ_API_KEY=your_groq_key
ELEVENLABS_API_KEY=your_elevenlabs_key
```

## Installation

### Option 1: Using `uv` (recommended)

```bash
uv sync
```

### Option 2: Using `venv` + `pip`

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run

```bash
python main.py
```

The app starts on:
- `http://0.0.0.0:7860`

## Usage

1. Start the app.
2. Click **Start Camera** to begin webcam feed.
3. Click **Record & Ask** and speak your question.
4. Wait for transcription, agent reasoning, and spoken response.
5. Click **Stop Camera** when done.

## Notes

- If camera is not running, the vision tool attempts to open it temporarily.
- On macOS, audio playback uses `afplay`.
- `demo.launch(..., share=True)` creates a public Gradio share link while running.

## Troubleshooting

- Missing keys error:
  - Ensure `.env` exists and contains both required keys.
- No microphone input:
  - Check OS microphone permissions for Python/Terminal.
- Camera unavailable:
  - Ensure no other app is locking the webcam.
- MP3/audio conversion issues:
  - Install FFmpeg and verify it is available in your PATH.

## Development

Useful files to edit during development:
- Prompt/tool behavior: `ai_agent.py`
- Vision capture/model logic: `tools.py`
- STT tuning (duration, sample rate): `speech_to_text.py`
- Voice and model settings: `text_to_speech.py`

## License

No license file is currently included in this repository.
