#!/usr/bin/env python
import json
import argparse
import subprocess


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("user", type=str)
    parser.add_argument("expected", action="extend", nargs="+")
    return parser.parse_args()


def main() -> None:
    metrics = []
    args = parse_args()

    cmd = ["sudo", "-u", args.user, "ls", f"/run/screen/S-{args.user}"]
    output = subprocess.check_output(cmd, text=True)
    screens = [s.split(".")[1] for s in output.splitlines()]

    for screen in args.expected:
        if screen in screens:
            metrics.append({"screen": screen, "status": 1})
        else:
            metrics.append({"screen": screen, "status": 0})
    print(json.dumps({"measurement": "screen", "data": metrics}))


if __name__ == "__main__":
    main()
