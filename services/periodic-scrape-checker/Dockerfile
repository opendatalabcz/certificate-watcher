FROM python:3.11-slim-bookworm as builder

COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

ENV APP_DIR /app
RUN mkdir -p /app
ADD . /app

WORKDIR /app

CMD ["python", "./main.py", "-c", "/config/docker-env.cfg"]