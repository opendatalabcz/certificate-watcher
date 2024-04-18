FROM python:3.11-slim-bookworm as builder

COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

ENV APP_DIR=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN mkdir -p /app
ADD . /app

RUN apt-get update -y \
    && apt-get install -y libcairo2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install uvicorn[standard]

WORKDIR /app

EXPOSE 8000

#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["python", "./main.py", "-c", "/config/docker-env.cfg"]