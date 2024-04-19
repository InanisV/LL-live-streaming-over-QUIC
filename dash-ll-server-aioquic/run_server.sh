#!/bin/bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

# bash clean.sh && python3.10 dash_server.py -l 'ERROR' -p 9001 media
bash clean.sh && python3.10 dash_server-aio.py -l 'WARN' -p 9001 media >> ./log/dash_server_log.log 2>&1 >/dev/null &


bash ./gen_live_ingest.sh localhost 9001 ./ffmpeg ${1} 
