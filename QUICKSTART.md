# Personel Panel - Test Referansı

## Rapid Test Adımları

### 1. Veritabanı Setup
```bash
cd backend
python seed.py  # Test verilerini yükle
```

### 2. Backend Başlat
```bash
cd backend
python main.py
```
Backend erişim: http://localhost:8000

### 3. Frontend Başlat (yeni terminal)
```bash
cd frontend
npm install
npm run dev
```
Frontend erişim: http://localhost:3000

## Test Hesapları

| Kullanıcı | Şifre | Rol |
|-----------|-------|-----|
| admin | admin123 | Admin (kullanıcı yönetimi) |
| testuser | test123 | Standart Kullanıcı |

## Test Senaryoları

### 1. Giriş Testi
- [ ] admin hesabı ile giriş yap
- [ ] Dashboard açılmalı
- [ ] Çıkış yap ve testuser ile giriş

### 2. Personel Yönetimi
- [ ] Personel sayfasına git
- [ ] Mevcut personelleri görüntüle (5 test personeli)
- [ ] Yeni personel ekle
- [ ] Personel sil

### 3. Satış Yönetimi
- [ ] Satış sayfasına git
- [ ] Tarih aralığı seç (1-10 Mayıs)
- [ ] Personellerin satış verilerini görüntüle
- [ ] Excel dosyasını indir
- [ ] Excel formatında yeni dosya yükle (örnek format: Personnel Name | Date | Sales Count)

### 4. Puantaj Sistemi
- [ ] Puantaj sayfasına git
- [ ] Ay/yıl seç
- [ ] Mevcut puantajları görüntüle (28.5 çalışma + 1.5 izin = 30)
- [ ] Yeni puantaj kaydı ekle

### 5. Uyarı Sistemi
- [ ] Uyarılar sayfasına git
- [ ] Tüm uyarıları veya personel bazlı filtrele
- [ ] Uyarı ekle

### 6. Eğitim & Geribildirim
- [ ] Eğitim sayfasına git
- [ ] Personel bazlı eğitimleri filtreleme
- [ ] Yeni eğitim kaydı ekle

### 7. Çağrı İzleme
- [ ] Çağrı izleme sayfasına git
- [ ] Çağrı kayıtlarını görüntüle
- [ ] Kalite puanına göre renkli gösterim (>80 yeşil, 60-80 sarı, <60 kırmızı)
- [ ] Yeni çağrı kaydı ekle

## API Dokümantasyonu

Swagger API docs: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

## Veritabanı

### Connection String
```
postgresql://personelpanel:personelpanel_pass@localhost:5432/personelpanel
```

### Tablolar
- users (5 test kaydı: 1 admin + 1 user)
- personnel (5 personel)
- sales_data (50 satış kaydı - son 10 gün)
- attendance_data (5 puantaj)
- warning_data (2 uyarı)
- training_data (2 eğitim)
- call_monitoring (15 çağrı)
- whatsapp_data (25 WhatsApp kaydı)

## Docker ile Test

```bash
docker-compose up -d
# Bekleme (10 saniye için veritabanın başlaması)
sleep 10
# Backend'de seed'i çalıştır
docker exec personelpanel_backend python seed.py
```

Ardından:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Swagger: http://localhost:8000/docs

## Sorun Giderme

### CORS hatası
- Tarayıcı konsolunda kontrol et
- .env dosyasında CORS_ORIGINS kontrol et

### Database bağlantı hatası
```bash
# PostgreSQL'i test et
psql -U personelpanel -h localhost -d personelpanel -c "SELECT version();"
```

### Excel yüklemesi hatası
- Sütun adlarını kontrol et: "Personnel Name", "Date", "Sales Count"
- Tarih formatı: YYYY-MM-DD (2026-05-10)
- Satış adedi: Integer

## Göz at

- [x] Backend API tam kurulu
- [x] Frontend tam kurulu
- [x] Database şeması oluşturulmuş
- [x] Test verileri hazırlanmış
- [x] Authentication sistemi çalışıyor
- [x] 7 modülün tamamı işlevsel
- [ ] Docs API entegrasyonu (linkler gelince)
- [ ] Gelişmiş raporlama (export seçeneği hazır)

## Sonraki Adımlar

Docs linklerini aldıktan sonra:
1. DOCS_PUANTAJ_ID, DOCS_UYARILAR_ID, DOCS_WHATSAPP_ID'leri .env'ye ekle
2. services/docs_service.py içinde parsing logic'ini tamamla
3. Scheduled tasks ile otomatik sync ekle (Celery veya APScheduler)
