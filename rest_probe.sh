#!/usr/bin/env bash
set -euo pipefail
mkdir -p out
: "${SAFE_MODE:=1}"
: "${TARGET_BASE:=https://example.lab}" # replace with your lab


curl -i -sS --http2 \
-H "Accept: application/json" \
"$TARGET_BASE/api/v6/check-license?data=Zm9v" \
-o out/check_license_body.txt -D out/check_license_headers.txt


awk '/HTTP/{print $0}' out/check_license_headers.txt
wc -c out/check_license_body.txt | awk '{print "body-bytes:",$1}'
