#! /usr/bin/env bash

SCRIPT_PATH="$( cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

function handler_signal_int()
{
    echo "Exiting file-monitor"
    exit 0
}

trap handler_signal_int SIGINT

while true
do
    echo "Directory has changed!"
    find "{{data.journals_files_folder}}" -type f | entr -n -d "${SCRIPT_PATH}/file-monitor-action.sh" /_
done

