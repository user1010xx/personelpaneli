# 🚀 Personel Panel - Başlangıç Rehberi (Türkçe)

## Hoş Geldiniz!

Bu rehber, **Personel Panel** web uygulamasını yerel ortamında çalıştırmanızı sağlayacak.

---

## 📋 Sistem Gereksinimleri

Başlamadan önce bilgisayarınızda aşağıdakilerin kurulu olması gerekmektedir:

- **Python 3.11+** - [indir](https://www.python.org/downloads/)
- **Node.js 18+** - [indir](https://nodejs.org/)
- **PostgreSQL 15+** - [indir](https://www.postgresql.org/download/)
- **Git** - [indir](https://git-scm.com/)

### Kurulum Kontrolü

Terminalde şu komutları çalıştırarak versiyonlarını kontrol edin:

```bash
python --version      # 3.11 veya üzeri
node --version        # 18 veya üzeri
npm --version         # 9 veya üzeri
psql --version        # 15 veya üzeri
```

---

## 🏗️ Proje Yapısı

```
personelpanel.py/
├── backend/          # Python FastAPI sunucusu
├── frontend/         # React web uygulaması
└── docker-compose.yml # Docker yapılandırması
```

---

## ⚡ Hızlı Başlangıç (5 Dakika)

### Adım 1: Docker ile Çalıştırma (Önerilen)

En kolay yol Docker kullanmaktır:

```bash
# Docker Desktop'ı başlatın

# Terminal'de proje dizinine gidin
cd c:\projeler\personelpanel.py

# Docker konteynerlerini başlatın
docker-compose up -d

# Bekleme: 10-15 saniye (database başlansın)

# Test verilerini yükleyin
docker exec personelpanel_backend python seed.py
```

Ardından tarayıcınızda açın:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

Giriş bilgileri:
- Kullanıcı: `admin`
- Şifre: `admin123`

---

## 🔧 Manuel Kurulum (Adım Adım)

### Adım 1: Backend Setup

```bash
# Backend dizinine gidin
cd backend

# Python sanal ortamı oluşturun
python -m venv venv

# Sanal ortamı aktifleştirin
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Gerekli paketleri yükleyin
pip install -r requirements.txt

# Çevre değişkenlerini ayarlayın
cp .env.example .env

# .env dosyasını açıp düzenleyin:
# DATABASE_URL=postgresql://personelpanel:personelpanel_pass@localhost:5432/personelpanel
```

### Adım 2: PostgreSQL Database Oluşturma

```bash
# PostgreSQL açın
psql -U postgres

# Database oluşturun
CREATE DATABASE personelpanel;
CREATE USER personelpanel WITH PASSWORD 'personelpanel_pass';
ALTER ROLE personelpanel SET client_encoding TO 'utf8';
ALTER ROLE personelpanel SET default_transaction_isolation TO 'read committed';
ALTER ROLE personelpanel SET default_transaction_deferrable TO on;
ALTER ROLE personelpanel SET default_transaction_read_only TO off;
GRANT ALL PRIVILEGES ON DATABASE personelpanel TO personelpanel;

# Çıkın
\q
```

### Adım 3: Backend Başlat

```bash
# Backend dizininde (sanal ortam aktif)
cd backend
python main.py
```

Başarılı ise konsol çıktısı:
```
INFO: Application startup complete
INFO: Uvicorn running on http://0.0.0.0:8000
```

### Adım 4: Frontend Setup

Yeni terminal açın:

```bash
# Frontend dizinine gidin
cd frontend

# Npm paketlerini yükleyin
npm install

# Geliştirme sunucusunu başlatın
npm run dev
```

Başarılı ise çıktı:
```
➜  Local:   http://localhost:3000
```

---

## 🌐 Uygulamaya Erişim

Tarayıcınızda açın:

### Frontend (React)
```
http://localhost:3000
```

Giriş yap:
- Kullanıcı: `admin`
- Şifre: `admin123`

### Backend API (FastAPI)
```
http://localhost:8000
```

API dokümantasyonu:
```
http://localhost:8000/docs
```

---

## 📚 Ana Sayfalar Rehberi

### 1. Dashboard (Ana Sayfa)
- Personel sayısı
- Tarih aralığı filtreleme
- Toplam satış özeti
- Personel bazlı satış görünümü

**Kullanım**: Hızlı özet bilgileri görmek için

### 2. Personel Yönetimi
- Tüm personelleri listele
- Yeni personel ekle
- Personel sil

**Kullanım**: Personel kaydları yönetimi

### 3. Satış Verisi
- Excel dosyasından toplu yükle
- Satış verileri görüntüle
- Tarih filtreleme
- Excel'e aktar

**Kullanım**:
```
Excel formatı:
Personnel Name | Date       | Sales Count
Ahmet Yılmaz  | 2026-05-10 | 5
```

### 4. Puantaj (Çalışma Saatleri)
- Aylık çalışma saatleri
- İzin gün takibi
- Maaş bilgileri

**Örnek**: 28.5 gün çalışma + 1.5 gün izin = 30 gün

### 5. Uyarı & Kesinti
- Personel uyarılarını listele
- Uyarı ekle
- Tarih ve konu bilgileri

### 6. Eğitim & Geribildirim
- Verilen eğitimleri listele
- Eğitim ekle (başlangıç-bitiş saati)
- Eğitmen bilgisi

### 7. Dinlenen Çağrılar
- Çağrı kalitesi puanlaması
- Telefon numarası takibi
- İstatistikler

### 8. WhatsApp Mesajları
- Cevapsız mesaj takibi
- Günlük veriler
- Personel analizi

---

## 🧪 Test Verileri

Seed scripti çalıştırılınca şu veriler yüklenir:

- **5 Personel**
- **50 Satış Kaydı** (son 10 gün)
- **5 Puantaj Kaydı**
- **2 Uyarı**
- **2 Eğitim**
- **15 Çağrı Kaydı**
- **25 WhatsApp Kaydı**

---

## 📝 Excel Dosyası Nasıl Hazırlanır?

### Satış Verileri

Excel dosyası şu sütunları içermelidir:

| Personnel Name | Date       | Sales Count |
|----------------|-----------|-------------|
| Ahmet Yılmaz   | 2026-05-09 | 40          |
| Ahmet Yılmaz   | 2026-05-10 | 48          |

**Önemli**: 
- Tarih formatı: YYYY-MM-DD
- İlk satır başlık olmalı
- Excel formatı: .xlsx

**İnkremental Hesaplama Örneği**:
- 1-9 Mayıs: Ahmet 40 satış
- 1-10 Mayıs: Ahmet 48 satış
- 10 Mayıs filtrelendiğinde: 8 satış gösterilir (48-40)

---

## 🔐 Giriş Hesapları

Seed scripti yüklendikten sonra:

| Rol | Kullanıcı | Şifre | Yetki |
|-----|-----------|-------|-------|
| Admin | admin | admin123 | Tüm işlemler + kullanıcı yönetimi |
| Kullanıcı | testuser | test123 | Tüm modülleri görüntüleme |

---

## 🛠️ Sık Sorulan Problemler

### Problem: "Connection refused" hatası
**Çözüm**: PostgreSQL'in çalışıp çalışmadığını kontrol edin
```bash
# Windows
psql -U postgres -c "SELECT version();"

# Mac/Linux
sudo -u postgres psql -c "SELECT version();"
```

### Problem: Port 3000 veya 8000 zaten kullanımda
**Çözüm**:
```bash
# Windows - Port 3000'i kullanan process bul
netstat -ano | findstr :3000

# Terminalde Frontend/Backend'i farklı porta başlat
# Frontend: npm run dev -- --port 3001
```

### Problem: CORS hatası
**Çözüm**: Backend'in CORS ayarlarını kontrol edin
```bash
# backend/.env dosyasını kontrol et:
CORS_ORIGINS=["http://localhost:3000"]
```

### Problem: Excel yüklemesi başarısız
**Çözüm**:
1. Sütun adlarını kontrol et: "Personnel Name", "Date", "Sales Count"
2. Tarih formatı YYYY-MM-DD olmalı
3. Satış adedi integer olmalı

---

## 📊 Veritabanı Kontrol

Veritabanına doğrudan bağlan:

```bash
# Terminal
psql -U personelpanel -h localhost -d personelpanel

# SQL sorguları
SELECT * FROM personnel;
SELECT * FROM sales_data LIMIT 10;
SELECT * FROM users;

# Çıkış
\q
```

---

## 🚀 Production Deploy

Daha sonra production'a deploy etmek için: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 📞 İletişim & Destek

**Docs Entegrasyonu**:
Docs linklerini aldığınızda:
1. `.env` dosyasında DOCS_PUANTAJ_ID, DOCS_UYARILAR_ID, DOCS_WHATSAPP_ID ekle
2. Backend otomatik olarak verileri çekmeye başlayacak

---

## ✨ Sonraki Adımlar

1. ✅ Backend çalışıyor
2. ✅ Frontend çalışıyor
3. ✅ Test verileriniz yüklü
4. ⏳ Docs linklerini ekle (beklenen)
5. 📈 Analiz ve raporlama özellikleri

---

Başarılar! 🎉

Herhangi bir sorunla karşılaşırsanız, lütfen logs'ları kontrol edin veya README.md dosyasına bakın.
