#!/usr/bin/env python3
import json
import time
import urllib.parse
import urllib.request

URL = "http://localhost:7125/printer/objects/query"

PARAMS = [
    "extruder",
    "heater_bed",
    "heater_generic chamber",
    "motion_report",
    "print_stats",
    "fan_generic auxiliary_cooling_fan",
    "fan_generic chamber_circulation_fan",
    "chamber_fan chamber_fan",
    "heater_fan hotend_fan",
    "heater_fan hotend_fan2",
    "heater_fan hotend_fan3",
    "fan_generic cooling_fan",
    "controller_fan board_fan",
    "filament_switch_sensor fila",
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


def flatten_fields(prefix, obj, out):
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


def fetch_metrics():
    query = "&".join(urllib.parse.quote(p) for p in PARAMS)
    query_url = f"{URL}?{query}"

    with urllib.request.urlopen(query_url) as response:
        data = json.loads(response.read().decode())

    status = data.get("result", {}).get("status", {})
    timestamp = int(time.time() * 1_000_000_000)

    for obj_name, values in status.items():
        measurement = f"klipper_{obj_name.replace(' ', '_')}"
        tags = f"object={obj_name.replace(' ', '_')}"

        fields = {}
        flatten_fields("", values, fields)

        if not fields:
            continue

        field_str = ",".join(f"{k}={v}" for k, v in fields.items())
        print(f"{measurement},{tags} {field_str} {timestamp}")


if __name__ == "__main__":
    while True:
        fetch_metrics()
        time.sleep(10)
