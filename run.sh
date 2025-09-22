#!/bin/bash

# local testing
# nohup uvicorn main:app --host 0.0.0.0 --port 6395 > log.txt 2>&1 &
uvicorn main:app --host 0.0.0.0 --port 6395
# dev server testing
# nohup gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:10000 app.main:app > log.txt 2>&1 &
