#!/usr/bin/env python3
import sys

from time import sleep
from typing import NoReturn

import qbittorrentapi


def main() -> NoReturn:
    while True:
        client = qbittorrentapi.Client(
            host="", port=0, username="", password="", VERIFY_WEBUI_CERTIFICATE=False
        )
        client.auth_log_in()

        torrentlist = client.torrents.info(sort="added_on")
        count = client.torrents.count()
        print(f"torrents count={count}i")
        sys.stdout.flush()

        for torrent in torrentlist:
            print(
                f"torrents,name={torrent.name.replace(' ', '\\ ')}"
                + f",category={torrent.category.replace(' ', '\\ ')}"
                + f",added_on={torrent.added_on}"
                + f",hash={torrent.hash}"
                + f",size={torrent.size}"
                + f" amount_left={torrent.amount_left}i"
                + f",downloaded={torrent.downloaded}i"
                + f",last_activity={torrent.last_activity}"
                + f",num_leechs={torrent.num_leechs}i"
                + f",num_seeds={torrent.num_seeds}i"
                + f",popularity={torrent.popularity}"
                + f",progress={torrent.progress}"
                + f",ratio={torrent.ratio}"
                + f",seeding_time={torrent.seeding_time}i"
                + f',state="{torrent.state}"'
                + f",time_active={torrent.time_active}i"
                + f",uploaded={torrent.uploaded}"
            )
            sys.stdout.flush()
        client.auth_log_out()

        sleep(60)


if __name__ == "__main__":
    main()
