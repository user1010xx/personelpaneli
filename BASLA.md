# ğŸš€ Personel Panel - Baslangic Rehberi (Turkce)

## Hos Geldiniz!

Bu rehber, **Personel Panel** web uygulamasini yerel ortaminda calistirmanizi saglayacak.

---

## ğŸ“‹ Sistem Gereksinimleri

Baslamadan once bilgisayarinizda asagidakilerin kurulu olmasi gerekmektedir:

- **Python 3.11+** - [indir](https://www.python.org/downloads/)
- **Node.js 18+** - [indir](https://nodejs.org/)
- **PostgreSQL 15+** - [indir](https://www.postgresql.org/download/)
- **Git** - [indir](https://git-scm.com/)

### Kurulum Kontrolu

Terminalde su komutlari calistirarak versiyonlarini kontrol edin:

```bash
python --version      # 3.11 veya uzeri
node --version        # 18 veya uzeri
npm --version         # 9 veya uzeri
psql --version        # 15 veya uzeri
```

---

## ğŸ—ï¸ Proje Yapisi

```
personelpanel.py/
â”œâ”€â”€ backend/          # Python FastAPI sunucusu
â”œâ”€â”€ frontend/         # React web uygulamasi
â””â”€â”€ docker-compose.yml # Docker yapilandirmasi
```

---

## âš¡ Hizli Baslangic (5 Dakika)

### Adim 1: Docker ile Calistirma (Onerilen)

En kolay yol Docker kullanmaktir:

```bash
# Docker Desktop'i baslatin

# Terminal'de proje dizinine gidin
cd c:\projeler\personelpanel.py

# Docker konteynerlerini baslatin
docker-compose up -d

# Bekleme: 10-15 saniye (database baslansin)

# Test verilerini yukleyin
docker exec personelpanel_backend python seed.py
```

Ardindan tarayicinizda acin:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

Giris bilgileri:
- Kullanici: `admin`
- Sifre: `Railway INITIAL_ADMIN_PASSWORD`

---

## ğŸ”§ Manuel Kurulum (Adim Adim)

### Adim 1: Backend Setup

```bash
# Backend dizinine gidin
cd backend

# Python sanal ortami olusturun
python -m venv venv

# Sanal ortami aktiflestirin
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Gerekli paketleri yukleyin
pip install -r requirements.txt

# Cevre degiskenlerini ayarlayin
cp .env.example .env

# .env dosyasini acip duzenleyin:
# DATABASE_URL=postgresql://personelpanel:change_me@localhost:5432/personelpanel
```

### Adim 2: PostgreSQL Database Olusturma

```bash
# PostgreSQL acin
psql -U postgres

# Database olusturun
CREATE DATABASE personelpanel;
CREATE USER personelpanel WITH PASSWORD 'change_me';
ALTER ROLE personelpanel SET client_encoding TO 'utf8';
ALTER ROLE personelpanel SET default_transaction_isolation TO 'read committed';
ALTER ROLE personelpanel SET default_transaction_deferrable TO on;
ALTER ROLE personelpanel SET default_transaction_read_only TO off;
GRANT ALL PRIVILEGES ON DATABASE personelpanel TO personelpanel;

# Cikin
\q
```

### Adim 3: Backend Baslat

```bash
# Backend dizininde (sanal ortam aktif)
cd backend
python main.py
```

Basarili ise konsol ciktisi:
```
INFO: Application startup complete
INFO: Uvicorn running on http://0.0.0.0:8000
```

### Adim 4: Frontend Setup

Yeni terminal acin:

```bash
# Frontend dizinine gidin
cd frontend

# Npm paketlerini yukleyin
npm install

# Gelistirme sunucusunu baslatin
npm run dev
```

Basarili ise cikti:
```
âœ  Local:   http://localhost:3000
```

---

## ğŸŒ Uygulamaya Erisim

Tarayicinizda acin:

### Frontend (React)
```
http://localhost:3000
```

Giris yap:
- Kullanici: `admin`
- Sifre: `Railway INITIAL_ADMIN_PASSWORD`

### Backend API (FastAPI)
```
http://localhost:8000
```

API dokumantasyonu:
```
http://localhost:8000/docs
```

---

## ğŸ“š Ana Sayfalar Rehberi

### 1. Dashboard (Ana Sayfa)
- Personel sayisi
- Tarih araligi filtreleme
- Toplam satis ozeti
- Personel bazli satis gorunumu

**Kullanim**: Hizli ozet bilgileri gormek icin

### 2. Personel Yonetimi
- Tum personelleri listele
- Yeni personel ekle
- Personel sil

**Kullanim**: Personel kaydlari yonetimi

### 3. Satis Verisi
- Excel dosyasindan toplu yukle
- Satis verileri goruntule
- Tarih filtreleme
- Excel'e aktar

**Kullanim**:
```
Excel formati:
Personnel Name | Date       | Sales Count
Ahmet Yilmaz  | 2026-05-10 | 5
```

### 4. Puantaj (Calisma Saatleri)
- Aylik calisma saatleri
- Izin gun takibi
- Maas bilgileri

**Ornek**: 28.5 gun calisma + 1.5 gun izin = 30 gun

### 5. Uyari & Kesinti
- Personel uyarilarini listele
- Uyari ekle
- Tarih ve konu bilgileri

### 6. Egitim & Geribildirim
- Verilen egitimleri listele
- Egitim ekle (baslangic-bitis saati)
- Egitmen bilgisi

### 7. Dinlenen Cagrilar
- Cagri kalitesi puanlamasi
- Telefon numarasi takibi
- Istatistikler

### 8. WhatsApp Mesajlari
- Cevapsiz mesaj takibi
- Gunluk veriler
- Personel analizi

---

## ğŸ§ª Test Verileri

Seed scripti calistirilinca su veriler yuklenir:

- **5 Personel**
- **50 Satis Kaydi** (son 10 gun)
- **5 Puantaj Kaydi**
- **2 Uyari**
- **2 Egitim**
- **15 Cagri Kaydi**
- **25 WhatsApp Kaydi**

---

## ğŸ“ Excel Dosyasi Nasil Hazirlanir?

### Satis Verileri

Excel dosyasi su sutunlari icermelidir:

| Personnel Name | Date       | Sales Count |
|----------------|-----------|-------------|
| Ahmet Yilmaz   | 2026-05-09 | 40          |
| Ahmet Yilmaz   | 2026-05-10 | 48          |

**Onemli**:
- Tarih formati: YYYY-MM-DD
- Ilk satir baslik olmali
- Excel formati: .xlsx

**Inkremental Hesaplama Ornegi**:
- 1-9 Mayis: Ahmet 40 satis
- 1-10 Mayis: Ahmet 48 satis
- 10 Mayis filtrelendiginde: 8 satis gosterilir (48-40)

---

## ğŸ” Giris Hesaplari

Seed scripti yuklendikten sonra:

| Rol | Kullanici | Sifre | Yetki |
|-----|-----------|-------|-------|
| Admin | admin | Railway INITIAL_ADMIN_PASSWORD | Tum islemler + kullanici yonetimi |
| Kullanici | kullanici | Railway uzerinden olusturulur | Tum modulleri goruntuleme |

---

## ğŸ› ï¸ Sik Sorulan Problemler

### Problem: "Connection refused" hatasi
**Cozum**: PostgreSQL'in calisip calismadigini kontrol edin
```bash
# Windows
psql -U postgres -c "SELECT version();"

# Mac/Linux
sudo -u postgres psql -c "SELECT version();"
```

### Problem: Port 3000 veya 8000 zaten kullanimda
**Cozum**:
```bash
# Windows - Port 3000'i kullanan process bul
netstat -ano | findstr :3000

# Terminalde Frontend/Backend'i farkli porta baslat
# Frontend: npm run dev -- --port 3001
```

### Problem: CORS hatasi
**Cozum**: Backend'in CORS ayarlarini kontrol edin
```bash
# backend/.env dosyasini kontrol et:
CORS_ORIGINS=["http://localhost:3000"]
```

### Problem: Excel yuklemesi basarisiz
**Cozum**:
1. Sutun adlarini kontrol et: "Personnel Name", "Date", "Sales Count"
2. Tarih formati YYYY-MM-DD olmali
3. Satis adedi integer olmali

---

## ğŸ“Š Veritabani Kontrol

Veritabanina dogrudan baglan:

```bash
# Terminal
psql -U personelpanel -h localhost -d personelpanel

# SQL sorgulari
SELECT * FROM personnel;
SELECT * FROM sales_data LIMIT 10;
SELECT * FROM users;

# Cikis
\q
```

---

## ğŸš€ Production Deploy

Daha sonra production'a deploy etmek icin: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## ğŸ“ Iletisim & Destek

**Docs Entegrasyonu**:
Docs linklerini aldiginizda:
1. `.env` dosyasinda DOCS_PUANTAJ_ID, DOCS_UYARILAR_ID, DOCS_WHATSAPP_ID ekle
2. Backend otomatik olarak verileri cekmeye baslayacak

---

## âœ¨ Sonraki Adimlar

1. âœ… Backend calisiyor
2. âœ… Frontend calisiyor
3. âœ… Test verileriniz yuklu
4. â³ Docs linklerini ekle (beklenen)
5. ğŸ“ˆ Analiz ve raporlama ozellikleri

---

Basarilar! ğŸ‰

Herhangi bir sorunla karsilasirsaniz, lutfen logs'lari kontrol edin veya README.md dosyasina bakin.
