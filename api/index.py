import os
import requests
from fastapi import FastAPI, HTTPException

app = FastAPI()

# Reads the key from Vercel's Environment Variables (never hardcode the key here)
DIALPAD_API_KEY = os.getenv("DIALPAD_API_KEY")

@app.api_route("/check-operator", methods=["GET", "POST"])
def check_operator():
    if not DIALPAD_API_KEY:
        raise HTTPException(status_code=500, detail="DIALPAD_API_KEY missing")

    url = "https://dialpad.com/api/v2/offices/5927317992210432/operators"
    headers = {
        "Authorization": f"Bearer {DIALPAD_API_KEY}",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Dialpad's External API step requires a valid JSON object back
        return {
            "status": "success",
            "operators": data.get("items", data)
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Dialpad API error: {str(e)}")
