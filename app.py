from flask import Flask, render_template
import requests
import os
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route("/")
def home():
    # Stockholm koordinater
    lat = 59.3293
    lon = 18.0686
    url = f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{lon}/lat/{lat}/data.json"

    response = requests.get(url)
    data = response.json()
    
    # Hämta morgondagens prognos (ungefär 24 timmar fram)
    now = datetime.utcnow()
    tomorrow_date = (now + timedelta(days=1)).date()
    
    temps = []
    precipitation_probs = []
    wind_speeds = []

    for entry in data["timeSeries"]:
        time = datetime.fromisoformat(entry["validTime"].replace("Z","+00:00"))
        if time.date() == tomorrow_date:
            for param in entry["parameters"]:
                if param["name"] == "t":  # temperatur
                    temps.append(param["values"][0])
                elif param["name"] == "pcat":  # nederbörd % probability
                    precipitation_probs.append(param["values"][0])
                elif param["name"] == "ws":  # vind hastighet m/s
                    wind_speeds.append(param["values"][0])

    if temps:
        temp_min = min(temps)
        temp_max = max(temps)
    else:
        temp_min = temp_max = "N/A"

    if precipitation_probs:
        prec_prob = max(precipitation_probs)
    else:
        prec_prob = "N/A"

    if wind_speeds:
        wind_max = max(wind_speeds)
    else:
        wind_max = "N/A"

    return render_template("index.html",
                           temp_min=temp_min,
                           temp_max=temp_max,
                           prec_prob=prec_prob,
                           wind_max=wind_max)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
