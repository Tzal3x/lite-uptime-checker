#!/bin/bash

DB="/var/lib/uptime-checker/uptime.db"
URL="${UPTIME_CHECK_URL:-https://example.com}"
INTERVAL="${UPTIME_CHECK_INTERVAL:-300}"
NTFY_TOPIC="${NTFY_TOPIC}"

LAST_STATUS=0

init_db() {
  mkdir -p "$(dirname "$DB")"
  sqlite3 "$DB" "CREATE TABLE IF NOT EXISTS checks (
    timestamp INTEGER PRIMARY KEY,
    status INTEGER,
    response_time INTEGER
  );"
}

notify() {
  curl -d "$1" "ntfy.sh/$NTFY_TOPIC"
}

check() {
  local start=$(date +%s%N)
  local http_code=$(curl -s -w "%{http_code}" -o /dev/null "$URL" 2>/dev/null)
  local end=$(date +%s%N)
  local response_time=$(( (end - start) / 1000000 ))
  
  local status=0
  [[ "$http_code" == "200" ]] || status=1
  
  sqlite3 "$DB" "INSERT INTO checks (timestamp, status, response_time) VALUES ($(date +%s), $status, $response_time);"
  sqlite3 "$DB" "DELETE FROM checks WHERE timestamp < $(($(date +%s) - 1209600));"

  if [[ $status -eq 1 && $LAST_STATUS -eq 0 ]]; then
    notify "🔴 Downtime detected!"
  elif [[ $status -eq 0 && $LAST_STATUS -eq 1 ]]; then
    notify "🟢 Service recovered"
  fi

  LAST_STATUS=$status
}

init_db
while true; do
  check
  sleep "$INTERVAL"
done
