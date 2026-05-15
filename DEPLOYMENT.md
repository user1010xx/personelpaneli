# Personel Panel - Deployment Guide

## Production Deployment

### 1. Environment Setup

```bash
# Kopyala production env
cp .env.production .env

# Güvenli secret key oluştur
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Output değerini .env dosyasında SECRET_KEY'e kopyala
```

### 2. Database Migration

```bash
cd backend

# PostgreSQL oluştur (production database)
# Örnek: CREATE DATABASE personelpanel_prod;

# Environment'ı set et
export DATABASE_URL="postgresql://user:password@prod-host:5432/personelpanel_prod"

# Alembic migration çalıştır (hazırlandığında)
# alembic upgrade head
```

### 3. Backend Deployment

#### Option A: Gunicorn + Nginx

```bash
# Gunicorn kur
pip install gunicorn

# Backend'i çalıştır
cd backend
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app

# Nginx yapılandırması
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Option B: Docker Production

```bash
# Production image build
docker build -f Dockerfile.backend -t personelpanel-backend:prod .

# Registry'e push
docker tag personelpanel-backend:prod your-registry/personelpanel-backend:prod
docker push your-registry/personelpanel-backend:prod

# Container run
docker run -d \
  --name personelpanel-backend \
  -e DATABASE_URL=postgresql://... \
  -e SECRET_KEY=your-secret \
  -p 8000:8000 \
  personelpanel-backend:prod
```

### 4. Frontend Deployment

#### Option A: Static Hosting (Vercel, Netlify)

```bash
cd frontend

# Build for production
npm run build

# Output: dist/ klasörü
# Bunu static hosting'e deploy et
```

#### Option B: Nginx Static Server

```bash
# Frontend build
cd frontend
npm run build

# Nginx config
server {
    listen 80;
    server_name yourdomain.com;

    root /var/www/personelpanel/frontend/dist;
    index index.html;

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }
}
```

#### Option C: Docker Production

```bash
# Build image
docker build -f Dockerfile.frontend -t personelpanel-frontend:prod .

# Registry'e push
docker tag personelpanel-frontend:prod your-registry/personelpanel-frontend:prod
docker push your-registry/personelpanel-frontend:prod

# Container run
docker run -d \
  --name personelpanel-frontend \
  -e VITE_API_URL=https://api.yourdomain.com/api \
  -p 3000:3000 \
  personelpanel-frontend:prod
```

### 5. Docker Compose Production

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

`docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  backend:
    image: your-registry/personelpanel-backend:prod
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/personelpanel
      SECRET_KEY: your-production-secret
      DEBUG: "False"
    restart: always

  frontend:
    image: your-registry/personelpanel-frontend:prod
    environment:
      VITE_API_URL: https://api.yourdomain.com/api
    restart: always

  db:
    volumes:
      - postgres_data_prod:/var/lib/postgresql/data
    restart: always

volumes:
  postgres_data_prod:
```

### 6. SSL/TLS (HTTPS)

#### Let's Encrypt + Certbot

```bash
# Certbot kur
sudo apt-get install certbot python3-certbot-nginx

# Certificate al
sudo certbot certonly --nginx -d yourdomain.com -d api.yourdomain.com

# Auto-renew setup
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

#### Nginx SSL Config

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # ... rest of config
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### 7. Database Backup

```bash
# Regular backup
pg_dump personelpanel > backup_$(date +%Y%m%d).sql

# Automated backup (cron job)
0 2 * * * /usr/bin/pg_dump personelpanel | gzip > /backups/personelpanel_$(date +\%Y\%m\%d).sql.gz
```

### 8. Monitoring & Logging

#### Application Monitoring

```bash
# PM2 for process management
npm install -g pm2

# Backend start
pm2 start "python backend/main.py" --name personelpanel-api

# Monitoring
pm2 monit
pm2 logs
```

#### Log Aggregation

```bash
# Install ELK stack atau use cloud logging
# Example: Sentry for error tracking
pip install sentry-sdk

# In backend/app/main.py:
import sentry_sdk
sentry_sdk.init("https://your-sentry-dsn@sentry.io/project-id")
```

#### Health Checks

```bash
# Cron job for health monitoring
0 * * * * curl https://api.yourdomain.com/health || alert-admin
```

### 9. Performance Optimization

#### Backend

```python
# In app/config.py
if not DEBUG:
    # Redis caching
    from fastapi_cache2 import FastAPICache2
    from fastapi_cache2.backends.redis import RedisBackend
    
    FastAPICache2.init(RedisBackend(url="redis://localhost:6379"), 
                       prefix="fastapi-cache")
```

#### Frontend

```bash
# Code splitting & lazy loading
# Already configured in Vite

# CDN setup
# Place dist/ files on CDN
# Update asset paths in index.html
```

#### Database

```sql
-- Index creation for better performance
CREATE INDEX idx_personnel_id ON sales_data(personnel_id);
CREATE INDEX idx_date ON sales_data(date);
CREATE INDEX idx_personnel_date ON attendance_data(personnel_id, month, year);

-- Query optimization
VACUUM ANALYZE;
```

### 10. Scaling Considerations

#### Horizontal Scaling

```yaml
# Multiple backend instances with load balancing
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

# Kubernetes deployment
# See kubernetes-deployment.yaml
```

#### Database Scaling

```bash
# Read replicas setup
# Backup & replication configuration
# Connection pooling with PgBouncer
```

### 11. Security Hardening

```bash
# Update dependencies
pip install --upgrade -r requirements.txt
npm update

# Security headers
# In Nginx config:
add_header X-Content-Type-Options nosniff;
add_header X-Frame-Options DENY;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000";

# CORS configuration
# Already configured in backend/app/config.py
```

### 12. Backup & Disaster Recovery

```bash
#!/bin/bash
# backup.sh

# Database backup
pg_dump personelpanel | gzip > /backups/db_$(date +%Y%m%d_%H%M%S).sql.gz

# Application backup
tar -czf /backups/app_$(date +%Y%m%d).tar.gz \
  /opt/personelpanel/backend \
  /opt/personelpanel/frontend

# Upload to S3
aws s3 cp /backups/ s3://my-backup-bucket/personelpanel/

# Cleanup old backups
find /backups -name "*.gz" -mtime +30 -delete
```

### 13. CI/CD Pipeline

#### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml

name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Backend
        run: docker build -f Dockerfile.backend -t personelpanel-backend:${{ github.sha }}
      
      - name: Build Frontend
        run: docker build -f Dockerfile.frontend -t personelpanel-frontend:${{ github.sha }}
      
      - name: Push to Registry
        run: |
          docker push your-registry/personelpanel-backend:${{ github.sha }}
          docker push your-registry/personelpanel-frontend:${{ github.sha }}
      
      - name: Deploy
        run: |
          ssh deploy@prod-server 'cd /opt/personelpanel && \
            docker-compose -f docker-compose.prod.yml pull && \
            docker-compose -f docker-compose.prod.yml up -d'
```

### 14. Maintenance Tasks

```bash
# Weekly database optimization
0 0 * * 0 psql personelpanel -c "VACUUM ANALYZE;"

# Monthly security updates
0 0 1 * * apt-get update && apt-get upgrade -y

# Quarterly certificate renewal check
0 0 1 */3 * certbot renew --quiet
```

## Troubleshooting

### 502 Bad Gateway
- Backend server kontrol et
- Database bağlantısını kontrol et
- Logs'ları kontrol et: `docker logs personelpanel-backend`

### CORS Errors
- Frontend ve Backend origins match et
- Production domain'i CORS_ORIGINS'e ekle

### Database Connection Issues
- Connection string kontrol et
- Firewall kurallarını kontrol et
- Database logs'unu kontrol et

## Support

Docs linklerini aldıktan sonra:
1. Google Docs API credentials ekle
2. Docs ID'lerini .env'ye ekle
3. services/docs_service.py'u tamamla
4. Scheduled sync tasks setup et

Başarıyla deploy edildiyseniz, Docs entegrasyonunu ekleyebilirsiniz!
