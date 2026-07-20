import os
from elevenlabs import save
from elevenlabs.client import ElevenLabs
import subprocess
import platform
from dotenv import load_dotenv

load_dotenv()

def text_to_speech_with_elevenlabs(input_text, output_filepath):
    """
    Generate speech using ElevenLabs free tier voices.
    """
    try:
        client = ElevenLabs(api_key=os.environ.get("ELEVENLABS_API_KEY"))
        
        audio = client.text_to_speech.convert(
            text=input_text,
            voice_id="pNInz6obpgDQGcFmaJgB",  
            model_id="eleven_turbo_v2_5"  
        )
        
     
        save(audio, output_filepath)
        
   
        os_name = platform.system()
        subprocess.run(['afplay', output_filepath])
            
    except Exception as e:
        print(f" Error generating or playing audio: {e}")




# input_text = "Hi, I am doing fine, how are you? This is a test for AI generated speech using ElevenLabs."
# output_filepath = "test_text_to_speech.mp3"
# text_to_speech_with_elevenlabs(input_text, output_filepath)
