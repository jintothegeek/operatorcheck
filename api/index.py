import os
import requests
from fastapi import FastAPI, HTTPException

app = FastAPI()

DIALPAD_API_KEY = os.getenv("DIALPAD_API_KEY")

@app.api_route("/check-operator", methods=["GET", "POST"])
def check_operator():
    if not DIALPAD_API_KEY:
        raise HTTPException(status_code=500, detail="DIALPAD_API_KEY missing")

    response = requests.get(
        "https://dialpad.com",
        headers={
            "Authorization": f"Bearer {DIALPAD_API_KEY}",
            "Accept": "application/json"
        },
        timeout=10
    )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Dialpad API error")

    users = response.json().get("users", [])

    operator_available = any(
        user.get("do_not_disturb") is False
        and user.get("is_online") is False
        and (user.get("on_duty_status") or "").strip().lower() == "available"
        for user in users
    )

    return {"Operator_available": operator_available}
