FROM python:3.9-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR /var/www/app

RUN apk --update add
RUN apk add gcc musl-dev
RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .

CMD gunicorn --bind 0.0.0.0:5001 app:app