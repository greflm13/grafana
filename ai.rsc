:global influxLock
:if ($influxLock = true) do={ :return }
:set influxLock true

:local deviceIdentity [/system identity get name]
:local payload ""
:local nl ""

:foreach i in=[/interface find] do={

    :local ifname [/interface get $i name]
    :local safeIfname [:replace $ifname " " "_"]

    :local rx [/interface get $i rx-byte]
    :local tx [/interface get $i tx-byte]

    :local line (
      "mikrotik_monitoring,interface=$safeIfname,instance=$deviceIdentity " .
      "traffic_rx=${rx}i,traffic_tx=${tx}i"
    )

    :set payload ($payload . $nl . $line)
    :set nl "\n"
}

:if ([:len $payload] > 0) do={
    /tool fetch \
      url="http://example.com:8086/api/v2/write?org=ORG&bucket=BUCKET&precision=s" \
      mode=http \
      http-method=post \
      http-data="$payload" \
      http-header-field=\
"Authorization: Token YOUR-TOKEN"\
,"Content-Type: text/plain; charset=utf-8" \
      keep-result=no
}

:set influxLock false
