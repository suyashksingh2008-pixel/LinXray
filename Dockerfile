FROM mcr.microsoft.com/playwright/python:v1.55.0-noble

WORKDIR /app

RUN python -m pip install --no-cache-dir playwright==1.55.0

COPY scanner_exec.py /app/scanner_exec.py
COPY validation.py /app/validation.py
COPY config.py /app/config.py

ENTRYPOINT [ "python", "/app/scanner_exec.py" ]