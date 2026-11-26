import os
import requests
from fastapi import FastAPI, HTTPException, Request

app = FastAPI()

DIALPAD_API_KEY = os.getenv("DIALPAD_API_KEY")

def run_operator_check():
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

        users = data.get("users", [])
        available_operators = []

        for user in users:
            is_online = user.get("is_online") is True
            is_dnd = user.get("do_not_disturb") is True

            # Operator is available ONLY if online is True AND do_not_disturb is False
            if is_online and not is_dnd:
                available_operators.append({
                    "id": user.get("id"),
                    "name": user.get("display_name")
                })

        first_name = available_operators[0]["name"] if len(available_operators) > 0 else "None"

        return {
            "has_available_operator": len(available_operators) > 0,
            "available_count": len(available_operators),
            "first_available_name": first_name
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

