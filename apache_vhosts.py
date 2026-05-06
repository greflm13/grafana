#!/usr/bin/env python3
import os
import sys
import urllib3

import requests

from time import sleep
from typing import Generator
from concurrent.futures import ThreadPoolExecutor, as_completed

from apacheconfig import make_loader

urllib3.disable_warnings()


def get_vhosts(path: str = "/etc/apache2/sites-enabled") -> Generator[dict[str, str | None], None, None]:
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
    assert isinstance(vhost["url"], str)
    try:
        req = requests.get(
            "https://" + vhost["url"],
            verify=False,
            allow_redirects=True,
            timeout=10,
            proxies={"https": "https://195.192.209.130"},
        )
        status = req.status_code
    except requests.RequestException as e:
        status = e.response.status_code if e.response else 600

    proxy_status = -1

    if vhost["proxy"]:
        try:
            proxy_url = vhost["proxy"].split()[1]
            req = requests.get(
                proxy_url,
                verify=False,
                allow_redirects=True,
                timeout=10,
            )
            proxy_status = req.status_code
        except requests.RequestException as e:
            proxy_status = e.response.status_code if e.response else 600

    return {"url": vhost["url"], "status": status, "proxy": proxy_status}


def main() -> None:
    while True:
        vhosts = list(get_vhosts())

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(try_host, v): v for v in vhosts}

            for future in as_completed(futures):
                vhost = futures[future]
                try:
                    host = future.result()
                    print(f"vhosts,vhost={host['url']} status={host['status']}i,proxy={host['proxy']}i")
                except Exception as e:
                    print(f'vhosts,vhost={vhost["url"]} error="{e}"')

                sys.stdout.flush()

        sleep(30)


if __name__ == "__main__":
    main()
