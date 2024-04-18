#! /usr/bin/env bash

source config_ports.sh
uvicorn backend:app --host 0.0.0.0 --port $SERVER_PORT
