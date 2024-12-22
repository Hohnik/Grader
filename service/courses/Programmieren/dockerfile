FROM python:alpine

WORKDIR /app

COPY requirements.txt .
COPY tests/* .
COPY src/* .

RUN pip install -r requirements.txt
RUN pip install pytest

CMD ["pytest", ">", "score.txt"]
