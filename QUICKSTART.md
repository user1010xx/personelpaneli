# Personel Panel - Test Referansi

## Rapid Test Adimlari

### 1. Veritabani Setup
```bash
cd backend
python seed.py  # Test verilerini yukle
```

### 2. Backend Baslat
```bash
cd backend
python main.py
```
Backend erisim: http://localhost:8000

### 3. Frontend Baslat (yeni terminal)
```bash
cd frontend
npm install
npm run dev
```
Frontend erisim: http://localhost:3000

## Test Hesaplari

| Kullanici | Sifre | Rol |
|-----------|-------|-----|
| admin | INITIAL_ADMIN_PASSWORD | Admin (kullanici yonetimi) |
| testuser | Railway uzerinden olusturulur | Standart Kullanici |

## Test Senaryolari

### 1. Giris Testi
- [ ] admin hesabi ile giris yap
- [ ] Dashboard acilmali
- [ ] Cikis yap ve testuser ile giris

### 2. Personel Yonetimi
- [ ] Personel sayfasina git
- [ ] Mevcut personelleri goruntule (5 test personeli)
- [ ] Yeni personel ekle
- [ ] Personel sil

### 3. Satis Yonetimi
- [ ] Satis sayfasina git
- [ ] Tarih araligi sec (1-10 Mayis)
- [ ] Personellerin satis verilerini goruntule
- [ ] Excel dosyasini indir
- [ ] Excel formatinda yeni dosya yukle (ornek format: Personnel Name | Date | Sales Count)

### 4. Puantaj Sistemi
- [ ] Puantaj sayfasina git
- [ ] Ay/yil sec
- [ ] Mevcut puantajlari goruntule (28.5 calisma + 1.5 izin = 30)
- [ ] Yeni puantaj kaydi ekle

### 5. Uyari Sistemi
- [ ] Uyarilar sayfasina git
- [ ] Tum uyarilari veya personel bazli filtrele
- [ ] Uyari ekle

### 6. Egitim & Geribildirim
- [ ] Egitim sayfasina git
- [ ] Personel bazli egitimleri filtreleme
- [ ] Yeni egitim kaydi ekle

### 7. Cagri Izleme
- [ ] Cagri izleme sayfasina git
- [ ] Cagri kayitlarini goruntule
- [ ] Kalite puanina gore renkli gosterim (>80 yesil, 60-80 sari, <60 kirmizi)
- [ ] Yeni cagri kaydi ekle

## API Dokumantasyonu

Swagger API docs: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

## Veritabani

### Connection String
```
postgresql://personelpanel:change_me@localhost:5432/personelpanel
```

### Tablolar
- users (5 test kaydi: 1 admin + 1 user)
- personnel (5 personel)
- sales_data (50 satis kaydi - son 10 gun)
- attendance_data (5 puantaj)
- warning_data (2 uyari)
- training_data (2 egitim)
- call_monitoring (15 cagri)
- whatsapp_data (25 WhatsApp kaydi)

## Docker ile Test

```bash
docker-compose up -d
# Bekleme (10 saniye icin veritabanin baslamasi)
sleep 10
# Backend'de seed'i calistir
docker exec personelpanel_backend python seed.py
```

Ardindan:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Swagger: http://localhost:8000/docs

## Sorun Giderme

### CORS hatasi
- Tarayici konsolunda kontrol et
- .env dosyasinda CORS_ORIGINS kontrol et

### Database baglanti hatasi
```bash
# PostgreSQL'i test et
psql -U personelpanel -h localhost -d personelpanel -c "SELECT version();"
```

### Excel yuklemesi hatasi
- Sutun adlarini kontrol et: "Personnel Name", "Date", "Sales Count"
- Tarih formati: YYYY-MM-DD (2026-05-10)
- Satis adedi: Integer

## Goz at

- [x] Backend API tam kurulu
- [x] Frontend tam kurulu
- [x] Database semasi olusturulmus
- [x] Test verileri hazirlanmis
- [x] Authentication sistemi calisiyor
- [x] 7 modulun tamami islevsel
- [ ] Docs API entegrasyonu (linkler gelince)
- [ ] Gelismis raporlama (export secenegi hazir)

## Sonraki Adimlar

Docs linklerini aldiktan sonra:
1. DOCS_PUANTAJ_ID, DOCS_UYARILAR_ID, DOCS_WHATSAPP_ID'leri .env'ye ekle
2. services/docs_service.py icinde parsing logic'ini tamamla
3. Scheduled tasks ile otomatik sync ekle (Celery veya APScheduler)
