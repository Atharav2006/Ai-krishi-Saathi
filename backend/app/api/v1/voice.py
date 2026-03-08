from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import List
import json
from app.services.voice_advisor import process_voice_query
from app.api import deps

router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024 # 5 MB

@router.post("/query")
async def handle_voice_query(
    audio_file: UploadFile = File(...),
    district: str = Form(...),
    favorite_crops: str = Form(...),
    current_user = Depends(deps.get_current_active_user)
):
    # Validate file size
    file_bytes = await audio_file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Audio file too large. Max 5MB allowed.")
    await audio_file.seek(0)
    
    # Validate file type
    allowed_extensions = ('.wav', '.mp3', '.m4a')
    if not audio_file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(status_code=400, detail="Invalid audio type. Must be wav, mp3, or m4a.")
    
    # Parse crops list
    try:
        crops = json.loads(favorite_crops)
        if not isinstance(crops, list):
            crops = [favorite_crops]
    except Exception:
        crops = [c.strip() for c in favorite_crops.split(",") if c.strip()]
        
    result = process_voice_query(audio_file, district, crops)
    
    return result
