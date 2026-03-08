from fastapi import UploadFile
from .speech_service import transcribe_audio
from .intent_classifier import detect_intent
from .advisor_service import generate_advice
from .tts_service import generate_audio

def process_voice_query(audio_file: UploadFile, district: str, crops: list) -> dict:
    # 1. Transcribe Audio
    transcription_result = transcribe_audio(audio_file)
    text = transcription_result["text"]
    language = transcription_result["language"]
    
    # 2. Detect Intent
    intent_result = detect_intent(text)
    intent = intent_result["intent"]
    
    # 3. Generate Advice
    advice_result = generate_advice(intent, district, crops)
    response_text = advice_result["text"]
    
    # 4. Generate TTS Audio
    audio_url = generate_audio(response_text, language)
    
    return {
        "text": response_text,
        "audio_url": audio_url,
        "language": language,
        "intent": intent,
        "transcribed_text": text
    }
