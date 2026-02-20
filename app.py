from flask import Flask, render_template
import requests
from datetime import datetime, timedelta
import pytz  # behöver installeras: pip install pytz

app = Flask(__name__)

@app.route("/")
def home():
    lat = 59.3293
    lon = 18.0686
    url = f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{lon}/lat/{lat}/data.json"

    response = requests.get(url)
    data = response.json()

    # Stockholm-tid
    tz = pytz.timezone("Europe/Stockholm")
    now_local = datetime.now(tz)
    tomorrow_local_date = (now_local + timedelta(days=1)).date()

    temps = []
    precipitation_probs = []
    wind_speeds = []

    for entry in data["timeSeries"]:
        # SMHI tider är UTC
        time_utc = datetime.fromisoformat(entry["validTime"].replace("Z", "+00:00"))
        time_local = time_utc.astimezone(tz)  # konvertera till Stockholmstid

        if time_local.date() == tomorrow_local_date and 6 <= time_local.hour <= 22:
            for param in entry["parameters"]:
                if param["name"] == "t":  # temperatur
                    temps.append(param["values"][0])
                elif param["name"] == "pcat":  # nederbörd % probability
                    precipitation_probs.append(param["values"][0])
                elif param["name"] == "ws":  # vind m/s
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
