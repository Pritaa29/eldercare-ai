FROM python:3.11

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

# This script runs migrations, collects static files, then starts Daphne
CMD python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    daphne -b 0.0.0.0 -p $PORT eldercare.asgi:application
