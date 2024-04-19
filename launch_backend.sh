#! /usr/bin/env bash

SERVER_PORT=""
uvicorn backend:app --host 0.0.0.0 --port $SERVER_PORT
