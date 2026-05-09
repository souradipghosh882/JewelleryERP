FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for psycopg2, Pillow, barcode
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
