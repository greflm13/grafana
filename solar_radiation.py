#!/usr/bin/env python
import datetime
import time

import requests


def get_data():
    while True:
        req = requests.get(
            "https://api.open-meteo.com/v1/forecast?latitude=47.01778&longitude=15.441042&minutely_15=global_tilted_irradiance_instant&tilt=45&forecast_minutely_15=0&past_minutely_15=4"
        )
        res = req.json()
        if req.status_code in [200]:
            return res
        time.sleep(60)


def main() -> None:
    data = get_data()

    for idx, timestamp in enumerate(data["minutely_15"]["time"]):
        value = data["minutely_15"]["global_tilted_irradiance_instant"][idx]
        print(
            f"solar_radiation,latitude=47.01778,longitude=15.441042 value={value} {int(datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M').timestamp()) * 1000000000}"
        )


if __name__ == "__main__":
    main()
