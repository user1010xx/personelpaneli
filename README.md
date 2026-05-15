# Personel Panel - Proje KonfigÃ¼rasyonu

## GeliÅŸtirme OrtamÄ± Kurulumu

### Sistem Gereksinimleri
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker & Docker Compose (opsiyonel)

### Backend Kurulumu

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
```

.env dosyasÄ±nda ayarlarÄ± gÃ¼ncelleyin:
```
DATABASE_URL=postgresql://user:password@localhost:5432/personelpanel
SECRET_KEY=your-secret-key-here
```

Database migration calistirin:
```bash
alembic upgrade head
```

Backend'i baÅŸlatÄ±n:
```bash
python main.py
```

Backend Swagger dÃ¶kÃ¼mentasyonuna eriÅŸin: http://localhost:8000/docs

### Frontend Kurulumu

```bash
cd frontend
npm install
npm run dev
```

Frontend eriÅŸimi: http://localhost:3000

### Docker ile Ã‡alÄ±ÅŸtÄ±rma

```bash
docker-compose up -d
```

Bu otomatik olarak:
- PostgreSQL veritabanÄ±nÄ± baÅŸlatÄ±r
- Backend API'sÄ±nÄ± (8000) baÅŸlatÄ±r
- Frontend'i (3000) baÅŸlatÄ±r

## API Endpoints

### Authentication
- `GET /api/auth/me` - Mevcut kullanÄ±cÄ± bilgisi
- `POST /api/auth/register` - Yeni kullanÄ±cÄ± kayÄ±t
- `POST /api/auth/login` - GiriÅŸ
- `POST /api/auth/refresh` - Access token yenile
- `POST /api/auth/logout` - Oturumu kapat

### User Management (Admin)
- `GET /api/users` - TÃ¼m kullanÄ±cÄ±larÄ± listele
- `POST /api/users` - Yeni kullanÄ±cÄ± oluÅŸtur
- `PUT /api/users/{id}` - KullanÄ±cÄ± gÃ¼ncelle
- `DELETE /api/users/{id}` - KullanÄ±cÄ± sil

### Personnel
- `GET /api/personnel` - TÃ¼m personeli listele
- `GET /api/personnel/{id}` - Personel detaylarÄ±
- `POST /api/personnel` - Yeni personel ekle
- `PUT /api/personnel/{id}` - Personel gÃ¼ncelle
- `DELETE /api/personnel/{id}` - Personel sil
- `POST /api/personnel/sync-docs` - Personel verilerini Docs'tan senkronize et

### Sales
- `GET /api/sales` - SatÄ±ÅŸ verileri (filtreli)
- `GET /api/sales/personnel/{id}/summary` - Personel satÄ±ÅŸ Ã¶zeti
- `GET /api/sales/summary` - TÃ¼m personel satÄ±ÅŸ Ã¶zeti
- `POST /api/sales/upload-excel` - Excel dosyasÄ±ndan toplu yÃ¼kle
- `POST /api/sales` - Tek satÄ±ÅŸ kaydÄ± ekle
- `PUT /api/sales/{id}` - SatÄ±ÅŸ kaydÄ± gÃ¼ncelle

### Attendance (Puantaj)
- `GET /api/attendance` - TÃ¼m puantaj kayÄ±tlarÄ±
- `GET /api/attendance/{personnel_id}/{month}/{year}` - AylÄ±k puantaj
- `POST /api/attendance` - Puantaj kaydÄ± ekle
- `PUT /api/attendance/{id}` - Puantaj gÃ¼ncelle
- `DELETE /api/attendance/{id}` - Puantaj sil
- `POST /api/attendance/sync-docs` - Puantaj verilerini Docs'tan senkronize et

### Warnings
- `GET /api/warnings` - TÃ¼m uyarÄ±lar
- `GET /api/warnings/personnel/{id}` - Personel uyarÄ±larÄ±
- `GET /api/warnings/personnel/{id}/summary` - UyarÄ± Ã¶zeti
- `POST /api/warnings` - UyarÄ± ekle
- `PUT /api/warnings/{id}` - UyarÄ± gÃ¼ncelle
- `DELETE /api/warnings/{id}` - UyarÄ± sil
- `POST /api/warnings/sync-docs` - UyarÄ±larÄ± Docs'tan senkronize et

### Training
- `GET /api/training` - TÃ¼m eÄŸitim kayÄ±tlarÄ±
- `GET /api/training/personnel/{id}` - Personel eÄŸitimleri
- `POST /api/training` - EÄŸitim ekle
- `PUT /api/training/{id}` - EÄŸitim gÃ¼ncelle
- `DELETE /api/training/{id}` - EÄŸitim sil

### Call Monitoring
- `GET /api/call-monitoring` - TÃ¼m Ã§aÄŸrÄ± kayÄ±tlarÄ±
- `GET /api/call-monitoring/personnel/{id}` - Personel Ã§aÄŸrÄ±larÄ±
- `GET /api/call-monitoring/personnel/{id}/summary` - Ã‡aÄŸrÄ± Ã¶zeti
- `POST /api/call-monitoring` - Ã‡aÄŸrÄ± kaydÄ± ekle
- `PUT /api/call-monitoring/{id}` - Ã‡aÄŸrÄ± kaydÄ± gÃ¼ncelle
- `DELETE /api/call-monitoring/{id}` - Ã‡aÄŸrÄ± kaydÄ± sil

### WhatsApp
- `GET /api/whatsapp` - TÃ¼m WhatsApp kayÄ±tlarÄ±
- `GET /api/whatsapp/personnel/{id}` - Personel WhatsApp verisi
- `GET /api/whatsapp/personnel/{id}/summary` - WhatsApp Ã¶zeti
- `POST /api/whatsapp` - WhatsApp kaydÄ± ekle
- `PUT /api/whatsapp/{id}` - WhatsApp kaydÄ± gÃ¼ncelle
- `DELETE /api/whatsapp/{id}` - WhatsApp kaydÄ± sil
- `POST /api/whatsapp/sync-docs` - WhatsApp verilerini Docs'tan senkronize et

### Call Process
- `GET /api/call-process` - Ã‡aÄŸrÄ± sÃ¼reÃ§ kayÄ±tlarÄ±nÄ± listele
- `GET /api/call-process/summary` - Ã‡aÄŸrÄ± sÃ¼reÃ§ Ã¶zetini getir
- `POST /api/call-process/upload-excel` - Excel ile Ã§aÄŸrÄ± sÃ¼reÃ§ verisi yÃ¼kle
- `POST /api/call-process` - Ã‡aÄŸrÄ± sÃ¼reÃ§ kaydÄ± ekle
- `PUT /api/call-process/{id}` - Ã‡aÄŸrÄ± sÃ¼reÃ§ kaydÄ± gÃ¼ncelle

### Docs Links
- `GET /api/docs-links` - Docs baÄŸlantÄ±larÄ±nÄ± listele
- `PUT /api/docs-links/{key}` - Docs baÄŸlantÄ±sÄ±nÄ± gÃ¼ncelle

### Dashboard
- `GET /api/dashboard/summary` - Dashboard Ã¶zet verilerini getir

### System
- `GET /health` - Uygulama saÄŸlÄ±k durumu
- `GET /api/docs` - Basit endpoint Ã¶zeti

## Excel FormatÄ± (SatÄ±ÅŸ DosyasÄ±)

Excel dosyasÄ± ÅŸu sÃ¼tunlarÄ± iÃ§ermelidir:
- `Personnel Name` - Personel AdÄ±
- `Date` - Tarih (YYYY-MM-DD format)
- `Sales Count` - SatÄ±ÅŸ Adedi

## Google Docs Entegrasyonu (Beklenen)

Docs linklerini iÃ§ine alacaÄŸÄ± yerler:
- Puantaj verisi: `DOCS_PUANTAJ_ID` (.env'de)
- UyarÄ± verisi: `DOCS_UYARILAR_ID` (.env'de)
- WhatsApp verisi: `DOCS_WHATSAPP_ID` (.env'de)

## VeritabanÄ± ÅemasÄ±

TÃ¼m tablolar otomatik olarak oluÅŸturulur. Ä°Ã§erik:
- users: KullanÄ±cÄ± hesaplarÄ±
- personnel: Personel bilgileri
- sales_data: GÃ¼nlÃ¼k satÄ±ÅŸ verileri
- attendance_data: AylÄ±k puantaj/Ã§alÄ±ÅŸma saatleri
- warning_data: UyarÄ±lar ve cezalar
- training_data: EÄŸitim kayÄ±tlarÄ±
- call_monitoring: Dinlenen Ã§aÄŸrÄ±lar
- whatsapp_data: WhatsApp cevapsÄ±z mesaj takibi

## YapÄ±lacaklar

- [ ] Docs API entegrasyonu (linkler gelince)
- [ ] Dashboard analitik grafikleri
- [ ] GeliÅŸmiÅŸ raporlama
- [ ] Mail notifikasyonlarÄ±
- [ ] Veri backup sistemi
- [ ] KullanÄ±cÄ± rolleri (detaylÄ± izinler)
- [ ] Audit logging

## Sorun Giderme

### Database baÄŸlantÄ± hatasÄ±
```bash
# PostgreSQL'in Ã§alÄ±ÅŸÄ±r durumda olduÄŸunu kontrol edin
psql -U personelpanel -h localhost -d personelpanel
```

### CORS hatasÄ±
- `.env` dosyasÄ±nda CORS_ORIGINS kontrol edin
- Backend ve Frontend'in doÄŸru portlarda Ã§alÄ±ÅŸtÄ±ÄŸÄ±nÄ± kontrol edin

### Excel yÃ¼klemeleri baÅŸarÄ±sÄ±z
- Excel sÃ¼tun adlarÄ±nÄ±n tam olarak eÅŸleÅŸtiÄŸini kontrol edin
- Dosya formatÄ±nÄ±n .xlsx olduÄŸunu kontrol edin
