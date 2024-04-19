#!/bin/bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

bash clean.sh && go run main.go -p 9001 media >> ./log/dash_server_log.log 2>&1 >/dev/null &

./main -port 9001 -directory media

#bash ./gen_live_ingest.sh localhost 9001 ./ffmpeg ${1} 
