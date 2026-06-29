#!/usr/bin/env python3
import sys
import json
import time
import urllib.parse
import urllib.request

from typing import NoReturn
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = "http://localhost:7125/printer/objects/query"

PARAMS = [
    "box_heater_fan heater_fan_a_box1",
    "box_heater_fan heater_fan_a_box2",
    "box_heater_fan heater_fan_a_box3",
    "box_heater_fan heater_fan_a_box4",
    "box_heater_fan heater_fan_b_box1",
    "box_heater_fan heater_fan_b_box2",
    "box_heater_fan heater_fan_b_box3",
    "box_heater_fan heater_fan_b_box4",
    "chamber_fan chamber_fan",
    "controller_fan board_fan_box1",
    "controller_fan board_fan_box2",
    "controller_fan board_fan_box3",
    "controller_fan board_fan_box4",
    "controller_fan board_fan",
    "extruder",
    "fan_generic auxiliary_cooling_fan",
    "fan_generic chamber_circulation_fan",
    "fan_generic cooling_fan",
    "filament_switch_sensor fila",
    "heater_bed",
    "heater_fan hotend_fan",
    "heater_fan hotend_fan2",
    "heater_fan hotend_fan3",
    "heater_generic chamber",
    "heater_generic heater_box1",
    "heater_generic heater_box2",
    "heater_generic heater_box3",
    "heater_generic heater_box4",
    "motion_report",
    "print_stats",
]

PRINTER_NAME = "klipper"


def influx_escape(value: str) -> str:
    return value.replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")


def format_field_value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return v
    if v is None:
        return None
    return f'"{v}"'


def flatten_fields(prefix: str, obj: dict, out: dict) -> None:
    for k, v in obj.items():
        key = f"{prefix}_{k}" if prefix else k
        if isinstance(v, dict):
            flatten_fields(key, v, out)
        elif isinstance(v, list):
            continue
        else:
            fv = format_field_value(v)
            if fv is not None:
                out[key] = fv


def fetch_metric(param: str):
    query_url = f"{URL}?{urllib.parse.quote(param)}"

    with urllib.request.urlopen(query_url) as response:
        data = json.loads(response.read().decode())

    status = data.get("result", {}).get("status", {})
    timestamp = int(time.time() * 1_000_000_000)

    values = status[param]
    measurement = f"klipper_{param.replace(' ', '_')}"
    tags = f"object={param.replace(' ', '_')}"

    fields = {}
    flatten_fields("", values, fields)

    if not fields:
        return

    field_str = ",".join(f"{k}={v}" for k, v in fields.items())
    return measurement, tags, field_str, timestamp


def main() -> NoReturn:
    while True:
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(fetch_metric, v): v for v in PARAMS}

            for future in as_completed(futures):
                try:
                    metric = future.result()
                    if not metric:
                        raise Exception
                    print(f"{metric[0]},{metric[1]} {metric[2]} {metric[3]}")
                    sys.stdout.flush()
                except Exception:
                    pass

        time.sleep(5)


if __name__ == "__main__":
    main()
