def detect_intent(text: str) -> dict:
    text_lower = text.lower()
    
    if "bhav" in text_lower or "price" in text_lower or "rate" in text_lower:
        intent = "PRICE_FORECAST"
    elif "varsad" in text_lower or "temperature" in text_lower or "weather" in text_lower:
        intent = "WEATHER"
    elif "vavvu" in text_lower or "boya" in text_lower or "recommendation" in text_lower or "next" in text_lower:
        intent = "CROP_RECOMMENDATION"
    elif "daag" in text_lower or "disease" in text_lower or "paand" in text_lower:
        intent = "DISEASE_HELP"
    else:
        intent = "UNKNOWN"
        
    # Mock extracted crop
    crop = None
    if "onion" in text_lower or "dungli" in text_lower:
        crop = "onion"
    if "tameta" in text_lower or "tomato" in text_lower:
        crop = "tomato"
        
    return {
        "intent": intent,
        "crop": crop
    }
