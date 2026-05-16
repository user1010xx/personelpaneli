# cSpell:disable
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN perl -i -pe 's/^\x{FEFF}//' alembic.ini

EXPOSE 8000

CMD ["python", "main.py"]
