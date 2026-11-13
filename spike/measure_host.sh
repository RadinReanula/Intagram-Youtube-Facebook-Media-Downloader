#!/bin/sh
# Run on the Debian VPS before choosing concurrency defaults.
# Prints free CPU, memory, disk and a one-shot bandwidth sample.

set -eu

echo "== cpu =="
nproc
uptime
if [ -r /proc/loadavg ]; then
  cat /proc/loadavg
fi

echo "== memory =="
free -h

echo "== disk =="
df -h /

echo "== bandwidth quota =="
echo "Check the provider panel. This host cannot see the monthly quota from inside the VM."

echo "== link sample (10 MB, metadata only) =="
if command -v curl >/dev/null 2>&1; then
  curl -o /dev/null -s -w "http_code=%{http_code} speed=%{speed_download} bytes/s time=%{time_total}s\n" \
    --max-time 20 "https://speed.cloudflare.com/__down?bytes=10000000" || echo "bandwidth sample failed"
else
  echo "curl is not installed"
fi
