from flask import Flask, render_template
import requests
import os
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route("/")
def home():
    lat = 59.3293
    lon = 18.0686
    url = f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{lon}/lat/{lat}/data.json"

    response = requests.get(url)
    data = response.json()

    now = datetime.utcnow()
    tomorrow_date = (now + timedelta(days=1)).date()

    temps = []
    precipitation_probs = []
    wind_speeds = []

    for entry in data["timeSeries"]:
        time = datetime.fromisoformat(entry["validTime"].replace("Z", "+00:00"))
        if time.date() == tomorrow_date:
            hour = time.hour
            if 6 <= hour <= 22:  # mellan 06:00 och 22:00
                for param in entry["parameters"]:
                    if param["name"] == "t":
                        temps.append(param["values"][0])
                    elif param["name"] == "pcat":  # nederbördssannolikhet
                        precipitation_probs.append(param["values"][0])
                    elif param["name"] == "ws":
                        wind_speeds.append(param["values"][0])

    temp_min = min(temps) if temps else "N/A"
    temp_max = max(temps) if temps else "N/A"
    prec_prob = round(sum(precipitation_probs)/len(precipitation_probs), 1) if precipitation_probs else "N/A"
    wind_max = max(wind_speeds) if wind_speeds else "N/A"

    return render_template("index.html",
                           temp_min=temp_min,
                           temp_max=temp_max,
                           prec_prob=prec_prob,
                           wind_max=wind_max)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
