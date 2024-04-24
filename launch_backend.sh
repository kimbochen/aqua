#! /usr/bin/env bash

SERVER_PORT="8000"
uvicorn backend:app --host 0.0.0.0 --port $SERVER_PORT
