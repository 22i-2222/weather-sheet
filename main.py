import os
import json
import time
import logging
from datetime import datetime, timezone

import requests
import gspread
from google.oauth2.service_account import Credentials

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("weather")

LAT = os.environ["LAT"]
LON = os.environ["LON"]
SHEET_ID = os.environ["SHEET_ID"]
WORKSHEET = os.environ.get("WORKSHEET", "Sheet1")
INTERVAL = int(os.environ.get("INTERVAL_SECONDS", "30"))
# "append" = new row every time, "update" = keep overwriting row 2
MODE = os.environ.get("MODE", "append")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
HEADER = ["timestamp_utc", "lat", "lon", "temp_c", "feels_like_c", "humidity_pct",
          "pressure_hpa", "wind_kmh", "wind_dir_deg", "cloud_cover_pct", "precip_mm", "weather_code"]


def get_sheet():
    creds_info = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    ws = gspread.authorize(creds).open_by_key(SHEET_ID).worksheet(WORKSHEET)
    if ws.row_values(1) != HEADER:
        ws.insert_row(HEADER, 1)
    return ws


def get_weather():
    r = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": LAT,
            "longitude": LON,
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,"
                       "pressure_msl,wind_speed_10m,wind_direction_10m,"
                       "cloud_cover,precipitation,weather_code",
        },
        timeout=15,
    )
    r.raise_for_status()
    c = r.json()["current"]
    return [
        datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        LAT, LON,
        c["temperature_2m"], c["apparent_temperature"], c["relative_humidity_2m"],
        c["pressure_msl"], c["wind_speed_10m"], c["wind_direction_10m"],
        c["cloud_cover"], c["precipitation"], c["weather_code"],
    ]


def main():
    ws = None
    while True:
        start = time.time()
        try:
            if ws is None:
                ws = get_sheet()
            row = get_weather()
            if MODE == "update":
                ws.update(range_name="A2", values=[row])
            else:
                ws.append_row(row, value_input_option="USER_ENTERED")
            log.info("written: %s", row)
        except Exception as e:
            log.error("failed: %s", e)
            ws = None  # rebuild the connection on next loop
        time.sleep(max(0, INTERVAL - (time.time() - start)))


if __name__ == "__main__":
    main()
