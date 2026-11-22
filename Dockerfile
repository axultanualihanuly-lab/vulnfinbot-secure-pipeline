FROM python:3.12-slim

RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools \
    && pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY run.py .

ENV HOST=0.0.0.0
ENV PORT=5000

EXPOSE 5000

CMD ["python", "run.py"]