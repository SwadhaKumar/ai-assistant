import logging
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import os
from pydub import AudioSegment
from groq import Groq

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def record_audio(file_path, timeout=5, sample_rate=16000):
    """
    Record audio from the default microphone using sounddevice and save as MP3.
    """
    try:
        logging.info(f"Recording for {timeout} seconds...")
        audio = sd.rec(int(timeout * sample_rate), samplerate=sample_rate, channels=1, dtype=np.int16)
        sd.wait()
        # Save as temporary WAV file
        temp_wav = "temp_recording.wav"
        wav.write(temp_wav, sample_rate, audio)
        # Convert WAV to MP3
        audio_segment = AudioSegment.from_wav(temp_wav)
        audio_segment.export(file_path, format="mp3", bitrate="128k")
        os.remove(temp_wav)
        logging.info(f"Audio saved to {file_path}")
        return True
    except Exception as e:
        logging.error(f"An error occurred during recording: {e}")
        return False

def transcribe_with_groq(audio_filepath):
    GROQ_API_KEY=os.environ.get("GROQ_API_KEY")
    client=Groq(api_key=GROQ_API_KEY)
    stt_model="whisper-large-v3"
    audio_file=open(audio_filepath, "rb")
    transcription=client.audio.transcriptions.create(
        model=stt_model,
        file=audio_file,
        language="en"
    )

    return transcription.text