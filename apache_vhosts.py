#!/usr/bin/env python

import os
import time

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

token = os.environ.get("INFLUXDB_TOKEN")
org = "sorogon"
bucket = "devices"
url = "https://influxdb.sorogon.eu"

client = InfluxDBClient(url=url, token=token, org=org)

write_api = client.write_api(write_options=SYNCHRONOUS)

for value in range(5):
    point = Point("apache_vhost").tag("tagname1", "tagvalue1").field("field1", value)
    write_api.write(bucket=bucket, org="sorogon", record=point)
    time.sleep(1)  # separate points by 1 second
