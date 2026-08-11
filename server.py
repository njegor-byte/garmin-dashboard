import datetime
import os
from flask import Flask, jsonify
from flask_cors import CORS
from garminconnect import Garmin

app = Flask(__name__)
CORS(app)

GARMIN_EMAIL = os.getenv("GARMIN_EMAIL")
GARMIN_PASSWORD = os.getenv("GARMIN_PASSWORD")
TOKEN_DIR = "/tmp/.garminconnect"

client = None


def get_garmin_client():
  global client
  if client is not None:
    return client

  if not GARMIN_EMAIL or not GARMIN_PASSWORD:
    raise ValueError("Garmin credentials are not set in environment variables")

  garmin = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)

  try:
    garmin.login(TOKEN_DIR)
  except Exception:
    garmin.login()
    garmin.garth.dump(TOKEN_DIR)

  client = garmin
  return client


def get_garmin_data():
  try:
    garmin = get_garmin_client()
    today = datetime.date.today().isoformat()

    activities = garmin.get_activities_by_date(today, today, "")
    stats = garmin.get_user_summary(today)

    bmr = (
        stats.get("bmrCalories")
        or stats.get("restingCalories")
        or stats.get("bmrKilocalories")
        or 0
    )
    active = (
        stats.get("activeCalories")
        or stats.get("activeKilocalories")
        or stats.get("netCalorieGoal")
        or 0
    )
    total = stats.get("totalKilocalories") or stats.get("totalCalories") or 0

    if total == 0 and (bmr > 0 or active > 0):
      total = bmr + active

    parsed_activities = []
    for act in activities:
      parsed_activities.append({
          "name": act.get("activityName", "Workout"),
          "type": act.get("activityType", {}).get("typeKey", "workout"),
          "durationMin": round(act.get("duration", 0) / 60),
          "avgHr": round(act.get("averageHR", 0)),
          "calories": round(act.get("calories", 0)),
      })

    return {
        "bmrCalories": round(bmr),
        "activeCalories": round(active),
        "totalBurned": round(total),
        "activities": parsed_activities,
    }
  except Exception as e:
    print(f"Garmin error: {e}")
    global client
    client = None
    return None


@app.route("/api/garmin/today", methods=["GET"])
def garmin_today():
  data = get_garmin_data()
  if data:
    return jsonify(data)
  return jsonify({"error": "Failed to fetch Garmin data"}), 500


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)