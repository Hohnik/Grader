FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt pytest pytest-timeout

RUN mkdir -p src tests

COPY src/ ./src/
COPY tests/ ./tests/

RUN touch src/__init__.py tests/__init__.py
RUN touch score.txt
RUN echo "17/100" > score.txt

ENV PYTHONPATH=/app
ENV PYTEST_TIMEOUT=30

CMD ["sh", "-c", "python -m pytest tests/ -v --no-header -rA --timeout=30 > score.txt"]
