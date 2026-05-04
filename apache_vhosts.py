#!/usr/bin/env python3
import os
import json
import urllib3

import requests

from apacheconfig import make_loader

urllib3.disable_warnings()


def get_vhosts(path: str = "/etc/apache2/sites-enabled") -> list[dict[str, str | None]]:
    lsit = []
    for file in os.listdir(path):
        with make_loader() as loader:
            data = loader.load(os.path.join(path, file))

            assert isinstance(data, dict)
            if "IfModule" in data:
                vhosts = data["IfModule"]["mod_ssl.c"].get("VirtualHost", {})
                for vhost in vhosts:
                    lsit.append(
                        {
                            "url": vhost["*:443"].get("ServerName", None),
                            "proxy": vhost["*:443"].get("ProxyPass", None),
                        }
                    )
    return lsit


def try_host(vhost: dict[str, str | None]) -> dict[str, str | int]:
    ret = {}
    assert isinstance(vhost["url"], str)
    try:
        req = requests.get("https://" + vhost["url"], verify=False, allow_redirects=True)
        ret = {"url": vhost["url"], "status": req.status_code, "proxy": -1}
    except requests.ConnectionError as e:
        if e.response:
            ret = {"url": vhost["url"], "status": e.response.status_code, "proxy": -1}
        else:
            ret = {"url": vhost["url"], "status": 600, "proxy": -1}
    if "proxy" in vhost and vhost["proxy"] is not None:
        try:
            req = requests.get(vhost["proxy"].split()[1], verify=False, allow_redirects=True)
            return {"url": ret["url"], "status": ret["status"], "proxy": req.status_code}
        except requests.ConnectionError as e:
            if e.response:
                return {"url": ret["url"], "status": ret["status"], "proxy": e.response.status_code}
            else:
                return {"url": ret["url"], "status": ret["status"], "proxy": 600}
    return ret


def main() -> None:
    metrics = []
    vhosts = get_vhosts()
    for vhost in vhosts:
        host = try_host(vhost)
        data = {
            "vhost": str(host["url"]),
            "status": int(host["status"]),
            "proxy": int(host["proxy"]),
        }
        metrics.append(data)

    print(json.dumps({"measurement": "vhosts", "data": metrics}))


if __name__ == "__main__":
    main()
