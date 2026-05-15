# Railway Deployment

## Backend service

Create a Railway service from this repository and use `Dockerfile.backend`.

Required variables:

```env
DATABASE_URL=<Railway PostgreSQL connection string>
SECRET_KEY=<random 32+ character secret>
CORS_ORIGINS=["https://your-frontend-domain"]
GOOGLE_CREDENTIALS_JSON=<one-line service account JSON>
DEBUG=False
```

The Google service account `client_email` must be shared as Viewer on every Google Sheet saved in the panel.

## Frontend service

Create a second Railway service from the same repository and use `frontend/Dockerfile`.

Required variable:

```env
VITE_API_URL=https://your-backend-domain/api
```

## Runtime flow

1. Add Google Sheet links in `Kullanici Yonetimi`.
2. Share each Sheet with the service account email from `GOOGLE_CREDENTIALS_JSON`.
3. Use `Docs Baglantisini Hazirla` in each page to sync data.
