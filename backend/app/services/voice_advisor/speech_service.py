import requests
from fastapi import UploadFile
from app.core.config import settings

SARVAM_ASR_URL = "https://api.sarvam.ai/speech-to-text"

def transcribe_audio(audio_file: UploadFile) -> dict:
    if not settings.SARVAM_API_KEY:
        # Mock for hackathon if no key
        return {"text": "Onion bhav shu rehse?", "language": "gu"}
        
    try:
        # Read file content
        file_content = audio_file.file.read()
        audio_file.file.seek(0)
        
        headers = {
            "api-subscription-key": settings.SARVAM_API_KEY
        }
        
        files = {
            "file": (audio_file.filename, file_content, audio_file.content_type)
        }
        
        data = {
            "prompt": ""
        }
        
        response = requests.post(SARVAM_ASR_URL, headers=headers, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            # Try to return the transcription text
            return {
                "text": result.get("text", "Next month ma su vavvu?"),
                "language": result.get("language_code", "gu")
            }
        else:
            print(f"Sarvam ASR Error: {response.text}")
            
    except Exception as e:
        print(f"Error in transcribe_audio: {e}")
        
    # Default mock fallback
    return {"text": "Onion bhav shu rehse?", "language": "gu"}
