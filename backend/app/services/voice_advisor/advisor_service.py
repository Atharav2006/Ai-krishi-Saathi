def generate_advice(intent: str, district: str, crops: list) -> dict:
    if intent == "PRICE_FORECAST":
        # Hackathon demo: Match requested script exactly
        return {"text": "આગામી સાત દિવસમાં ડુંગળીના ભાવ વધવાની સંભાવના છે."} 
    
    elif intent == "WEATHER":
        return {"text": "આજે હવામાન ચોખ્ખું રહેશે અને વરસાદ ની કોઈ શક્યતા નથી."}
        
    elif intent == "CROP_RECOMMENDATION":
        return {"text": "તમારા વિસ્તારમાં મકાઈ અને બાજરી વાવવી યોગ્ય રહેશે."}
        
    elif intent == "DISEASE_HELP":
        return {"text": "કૃપા કરીને રોગની ઓળખ માટે કૅમેરા સ્કેનરનો ઉપયોગ કરો."}
        
    else:
        return {"text": "માફ કરશો, હું તમારી વાત સમજી શક્યો નથી."}
