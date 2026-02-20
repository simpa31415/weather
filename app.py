from flask import Flask, render_template
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route("/")
def home():
    lat = 59.3293
    lon = 18.0686
    url = f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{lon}/lat/{lat}/data.json"

    temps = []
    wind_speeds = []
    precip_hours = 0
    total_hours = 0

    stockholm_offset = 1  # UTC+1 (vintertid). Ändra till 2 för sommartid

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        now_utc = datetime.utcnow()
        tomorrow_date = (now_utc + timedelta(days=1)).date()

        for entry in data.get("timeSeries", []):
            time_utc = datetime.fromisoformat(entry["validTime"].replace("Z", "+00:00"))
            time_local = time_utc + timedelta(hours=stockholm_offset)

            if time_local.date() == tomorrow_date and 6 <= time_local.hour <= 22:
                total_hours += 1
                for param in entry["parameters"]:
                    if param["name"] == "t":  # temperatur
                        temps.append(param["values"][0])
                    elif param["name"] == "ws":  # vind m/s
                        wind_speeds.append(param["values"][0])
                    elif param["name"] == "pmean":  # nederbörd mm
                        if param["values"][0] > 0:
                            precip_hours += 1

    except Exception as e:
        print("Fel vid hämtning från SMHI:", e)

    temp_min = min(temps) if temps else "N/A"
    temp_max = max(temps) if temps else "N/A"
    wind_max = max(wind_speeds) if wind_speeds else "N/A"
    prec_prob = round(precip_hours / total_hours * 100, 1) if total_hours else "N/A"

    return render_template("index.html",
                           temp_min=temp_min,
                           temp_max=temp_max,
                           wind_max=wind_max,
                           prec_prob=prec_prob)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
