from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

API_KEY = "ab1656fb0ada06bd9c272c79903577ad"   # <-- replace with your OpenWeatherMap API key
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    if request.method == "POST":
        city = request.form.get("city")
        if city:
            params = {
                "q": city,
                "appid": API_KEY,
                "units": "metric"  # Celsius
            }
            response = requests.get(BASE_URL, params=params)
            data = response.json()

            # ✅ Handle error responses safely
            if data.get("cod") == 200:  # Success
                # Get timezone offset in seconds
                timezone_offset = data.get("timezone", 0)
                
                # Calculate current time for the location (UTC + offset)
                utc_now = datetime.now(timezone.utc)
                city_time = utc_now + timedelta(seconds=timezone_offset)
                current_time = city_time.strftime("%I:%M %p")
                
                weather_data = {
                    "city": data.get("name"),
                    "country": data["sys"].get("country"),
                    "temperature": data["main"].get("temp"),
                    "description": data["weather"][0].get("description", "").title(),
                    "icon": data["weather"][0].get("icon"),
                    "humidity": data["main"].get("humidity"),
                    "wind_speed": data["wind"].get("speed"),
                    "feels_like": data["main"].get("feels_like"),
                    "pressure": data["main"].get("pressure"),
                    "visibility": data.get("visibility", 0) / 1000 if data.get("visibility") else 0,
                    # Calculate sunrise/sunset using the timezone offset
                    "sunrise": (datetime.fromtimestamp(data["sys"].get("sunrise"), timezone.utc) + timedelta(seconds=timezone_offset)).strftime("%I:%M %p") if data["sys"].get("sunrise") else "N/A",
                    "sunset": (datetime.fromtimestamp(data["sys"].get("sunset"), timezone.utc) + timedelta(seconds=timezone_offset)).strftime("%I:%M %p") if data["sys"].get("sunset") else "N/A",
                    "time": current_time
                }
            else:
                weather_data = {"error": data.get("message", "City not found!")}

    return render_template("index.html", weather=weather_data)


if __name__ == "__main__":
    app.run(debug=True, port=5010)