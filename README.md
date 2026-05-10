# Personel Panel - Proje Konfigürasyonu

## Geliştirme Ortamı Kurulumu

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

.env dosyasında ayarları güncelleyin:
```
DATABASE_URL=postgresql://user:password@localhost:5432/personelpanel
SECRET_KEY=your-secret-key-here
```

Database oluşturun:
```bash
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

Backend'i başlatın:
```bash
python main.py
```

Backend Swagger dökümentasyonuna erişin: http://localhost:8000/docs

### Frontend Kurulumu

```bash
cd frontend
npm install
npm run dev
```

Frontend erişimi: http://localhost:3000

### Docker ile Çalıştırma

```bash
docker-compose up -d
```

Bu otomatik olarak:
- PostgreSQL veritabanını başlatır
- Backend API'sını (8000) başlatır
- Frontend'i (3000) başlatır

## API Endpoints

### Authentication
- `POST /api/auth/register` - Yeni kullanıcı kayıt
- `POST /api/auth/login` - Giriş
- `GET /api/auth/me` - Mevcut kullanıcı bilgisi

### User Management (Admin)
- `GET /api/users` - Tüm kullanıcıları listele
- `POST /api/users` - Yeni kullanıcı oluştur
- `PUT /api/users/{id}` - Kullanıcı güncelle
- `DELETE /api/users/{id}` - Kullanıcı sil

### Personnel
- `GET /api/personnel` - Tüm personeli listele
- `GET /api/personnel/{id}` - Personel detayları
- `POST /api/personnel` - Yeni personel ekle
- `PUT /api/personnel/{id}` - Personel güncelle
- `DELETE /api/personnel/{id}` - Personel sil

### Sales
- `GET /api/sales` - Satış verileri (filtreli)
- `GET /api/sales/personnel/{id}/summary` - Personel satış özeti
- `GET /api/sales/summary` - Tüm personel satış özeti
- `POST /api/sales/upload-excel` - Excel dosyasından toplu yükle
- `POST /api/sales` - Tek satış kaydı ekle
- `PUT /api/sales/{id}` - Satış kaydı güncelle

### Attendance (Puantaj)
- `GET /api/attendance` - Tüm puantaj kayıtları
- `GET /api/attendance/{personnel_id}/{month}/{year}` - Aylık puantaj
- `POST /api/attendance` - Puantaj kaydı ekle
- `PUT /api/attendance/{id}` - Puantaj güncelle
- `DELETE /api/attendance/{id}` - Puantaj sil

### Warnings
- `GET /api/warnings` - Tüm uyarılar
- `GET /api/warnings/personnel/{id}` - Personel uyarıları
- `GET /api/warnings/personnel/{id}/summary` - Uyarı özeti
- `POST /api/warnings` - Uyarı ekle
- `PUT /api/warnings/{id}` - Uyarı güncelle
- `DELETE /api/warnings/{id}` - Uyarı sil

### Training
- `GET /api/training` - Tüm eğitim kayıtları
- `GET /api/training/personnel/{id}` - Personel eğitimleri
- `POST /api/training` - Eğitim ekle
- `PUT /api/training/{id}` - Eğitim güncelle
- `DELETE /api/training/{id}` - Eğitim sil

### Call Monitoring
- `GET /api/call-monitoring` - Tüm çağrı kayıtları
- `GET /api/call-monitoring/personnel/{id}` - Personel çağrıları
- `GET /api/call-monitoring/personnel/{id}/summary` - Çağrı özeti
- `POST /api/call-monitoring` - Çağrı kaydı ekle
- `PUT /api/call-monitoring/{id}` - Çağrı kaydı güncelle
- `DELETE /api/call-monitoring/{id}` - Çağrı kaydı sil

### WhatsApp
- `GET /api/whatsapp` - Tüm WhatsApp kayıtları
- `GET /api/whatsapp/personnel/{id}` - Personel WhatsApp verisi
- `GET /api/whatsapp/personnel/{id}/summary` - WhatsApp özeti
- `POST /api/whatsapp` - WhatsApp kaydı ekle
- `PUT /api/whatsapp/{id}` - WhatsApp kaydı güncelle
- `DELETE /api/whatsapp/{id}` - WhatsApp kaydı sil

## Excel Formatı (Satış Dosyası)

Excel dosyası şu sütunları içermelidir:
- `Personnel Name` - Personel Adı
- `Date` - Tarih (YYYY-MM-DD format)
- `Sales Count` - Satış Adedi

## Google Docs Entegrasyonu (Beklenen)

Docs linklerini içine alacağı yerler:
- Puantaj verisi: `DOCS_PUANTAJ_ID` (.env'de)
- Uyarı verisi: `DOCS_UYARILAR_ID` (.env'de)
- WhatsApp verisi: `DOCS_WHATSAPP_ID` (.env'de)

## Veritabanı Şeması

Tüm tablolar otomatik olarak oluşturulur. İçerik:
- users: Kullanıcı hesapları
- personnel: Personel bilgileri
- sales_data: Günlük satış verileri
- attendance_data: Aylık puantaj/çalışma saatleri
- warning_data: Uyarılar ve cezalar
- training_data: Eğitim kayıtları
- call_monitoring: Dinlenen çağrılar
- whatsapp_data: WhatsApp cevapsız mesaj takibi

## Yapılacaklar

- [ ] Docs API entegrasyonu (linkler gelince)
- [ ] Dashboard analitik grafikleri
- [ ] Gelişmiş raporlama
- [ ] Mail notifikasyonları
- [ ] Veri backup sistemi
- [ ] Kullanıcı rolleri (detaylı izinler)
- [ ] Audit logging

## Sorun Giderme

### Database bağlantı hatası
```bash
# PostgreSQL'in çalışır durumda olduğunu kontrol edin
psql -U personelpanel -h localhost -d personelpanel
```

### CORS hatası
- `.env` dosyasında CORS_ORIGINS kontrol edin
- Backend ve Frontend'in doğru portlarda çalıştığını kontrol edin

### Excel yüklemeleri başarısız
- Excel sütun adlarının tam olarak eşleştiğini kontrol edin
- Dosya formatının .xlsx olduğunu kontrol edin
