#!/usr/bin/env python3
import os
import sys
import urllib3

import requests

from time import sleep
from typing import Generator

from apacheconfig import make_loader

urllib3.disable_warnings()


def get_vhosts(path: str = "/etc/apache2/sites-enabled") -> Generator[dict[str, str | None], str, None]:
    for file in os.listdir(path):
        with make_loader() as loader:
            data = loader.load(os.path.join(path, file))

            assert isinstance(data, dict)
            if "IfModule" in data:
                vhosts = data["IfModule"]["mod_ssl.c"].get("VirtualHost", {})
                for vhost in vhosts:
                    yield {
                        "url": vhost["*:443"].get("ServerName", None),
                        "proxy": vhost["*:443"].get("ProxyPass", None),
                    }


def try_host(vhost: dict[str, str | None]) -> dict[str, str | int]:
    ret = {}
    assert isinstance(vhost["url"], str)
    try:
        req = requests.get(
            "https://" + vhost["url"], verify=False, allow_redirects=True, proxies={"https": "https://195.192.209.130"}
        )
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
    while True:
        vhosts = get_vhosts()
        for vhost in vhosts:
            try:
                host = try_host(vhost)
                print(f"vhosts,vhost={host['url']} status={host['status']}i,proxy={host['proxy']}i")
                sys.stdout.flush()

            except Exception as e:
                print(f'vhosts,vhost={vhost['url']} error="{e}"')
                sys.stdout.flush()

        sleep(30)


if __name__ == "__main__":
    main()
