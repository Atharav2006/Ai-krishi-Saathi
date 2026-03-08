import os
import requests
import uuid
import wave
import struct
import base64
from app.core.config import settings

SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"
AUDIO_OUTPUT_DIR = "static/audio"

os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

def generate_audio(text: str, language: str) -> str:
    filename = f"{uuid.uuid4()}.wav"
    filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)
    
    # Check for empty or no key
    if not settings.SARVAM_API_KEY:
        create_silent_wav(filepath)
        return f"/static/audio/{filename}"
        
    headers = {
        "api-subscription-key": settings.SARVAM_API_KEY,
        "Content-Type": "application/json"
    }
    
    sarvam_lang = "hi-IN" 
    if language == "gu":
        sarvam_lang = "gu-IN"
        
    payload = {
        "inputs": [text],
        "target_language_code": sarvam_lang,
        "speaker": "meera", 
        "pitch": 0,
        "pace": 1.0,
        "loudness": 1.5,
        "speech_sample_rate": 8000,
        "enable_preprocessing": True,
        "model": "v2-narration" 
    }
    
    try:
        response = requests.post(SARVAM_TTS_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if "audios" in result and len(result["audios"]) > 0:
                audio_data = base64.b64decode(result["audios"][0])
                with open(filepath, "wb") as f:
                    f.write(audio_data)
                return f"/static/audio/{filename}"
        else:
            print(f"Sarvam TTS Error: {response.text}")
            
    except Exception as e:
        print(f"Error in generate_audio: {e}")

    # Fallback to dummy
    create_silent_wav(filepath)
    return f"/static/audio/{filename}"

def create_silent_wav(filepath):
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(8000)
        # write 0.5s of silence
        for _ in range(4000):
            wav_file.writeframesraw(struct.pack('<h', 0))
