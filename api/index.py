import os
import requests
from fastapi import FastAPI, HTTPException, Request

app = FastAPI()

DIALPAD_API_KEY = os.getenv("DIALPAD_API_KEY")
TARGET_OFFICE_ID = "5927317992210432"

def run_operator_check():
    if not DIALPAD_API_KEY:
        raise HTTPException(status_code=500, detail="DIALPAD_API_KEY missing")

    url = f"https://dialpad.com{TARGET_OFFICE_ID}/operators"
    headers = {
        "Authorization": f"Bearer {DIALPAD_API_KEY}",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()

        users = data.get("users", [])
        available_operators = []

        for user in users:
            # Strict check: must be online AND not in Do Not Disturb
            if user.get("is_online") is True and user.get("do_not_disturb") is False:
                available_operators.append({
                    "id": user.get("id"),
                    "name": user.get("display_name")
                })

        return {
            "has_available_operator": len(available_operators) > 0,
            "available_count": len(available_operators),
            "first_available_name": available_operators["name"] if available_operators else "None"
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Dialpad API error: {str(e)}")

@app.api_route("/", methods=["GET", "POST"])
@app.api_route("/api", methods=["GET", "POST"])
@app.api_route("/check-operator", methods=["GET", "POST"])
@app.api_route("/api/check-operator", methods=["GET", "POST"])
def check_operator():
    return run_operator_check()

@app.api_route("/{full_path:path}", methods=["GET", "POST"])
def catch_all(full_path: str, request: Request):
    return run_operator_check()


