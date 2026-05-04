:log info "InfluxDB exporter scheduler run started"
:local deviceIdentity [/system identity get name]
:local payload ""
:local nl ""

:foreach i in=[/interface find] do={
    :local ifname [/interface get $i name]

    :local rx [/interface get $i rx-byte]
    :local tx [/interface get $i tx-byte]

    :local line ("mikrotik_monitoring,interface=" . $ifname . ",instance=" . $deviceIdentity . " traffic_rx=" . $rx . "i,traffic_tx=" . $tx . "i")

    :set payload ($payload . $nl . $line)
    :set nl "\n"
}

:if ([:len $payload] > 0) do={
    :local url "http://influx.example.com:8086/api/v2/write?org=ORGANIZATION&bucket=BUCKET&precision=s"
    :local h1 "Authorization: Token YOUR-TOKEN"
    :local h2 "Content-Type: text/plain; charset=utf-8"

    /tool fetch url=$url mode=http http-method=post http-data="$payload" http-header-field=($h1,$h2) keep-result=no
}
:log info "InfluxDB exporter scheduler run finished"