#!/bin/bash

if [ "$#" -gt 3 ]; then
    echo "Illegal number of parameters"
    echo "Usage: ./run.sh [MODE] [PORT]" 
    #exit 1
fi

DEFAULTVALUE=5000
MODE=${1}
PORT=${2:-$DEFAULTVALUE}

#echo $MODE
if [ "${MODE^^}" = "DATACENTER" ]; then
    case "$PORT" in
    '5000')
    python3 Main_Server.py
    ;;
    '5001')
    python3 Second_Server.py
    ;;
    '5002')
    python3 Third_Server.py
    ;;
    *) 
    echo "Invalid port"
    ;;
    esac
else 
    python3 Client.py localhost $PORT
fi
