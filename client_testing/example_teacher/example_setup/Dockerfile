FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir pytest pytest-timeout

RUN mkdir src output

COPY test_lab01.py .

CMD python -m pytest -v --no-header -rA > /app/output/score.txt
