# Proje Yapısı

```
personelpanel.py/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py                 # Ayarlar
│   │   ├── database.py               # Database session
│   │   ├── main.py                   # FastAPI uygulaması
│   │   │
│   │   ├── models/                   # SQLAlchemy Models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── personnel.py
│   │   │   ├── sales.py
│   │   │   ├── attendance.py
│   │   │   ├── warning.py
│   │   │   ├── training.py
│   │   │   ├── call_monitoring.py
│   │   │   └── whatsapp.py
│   │   │
│   │   ├── schemas/                  # Pydantic Schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── personnel.py
│   │   │   ├── sales.py
│   │   │   ├── attendance.py
│   │   │   ├── warning.py
│   │   │   ├── training.py
│   │   │   ├── call_monitoring.py
│   │   │   └── whatsapp.py
│   │   │
│   │   ├── routes/                   # API Routes
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── personnel.py
│   │   │   ├── sales.py
│   │   │   ├── attendance.py
│   │   │   ├── warnings.py
│   │   │   ├── training.py
│   │   │   ├── call_monitoring.py
│   │   │   └── whatsapp.py
│   │   │
│   │   ├── services/                 # Business Logic
│   │   │   ├── __init__.py
│   │   │   ├── docs_service.py       # Google Docs Integration
│   │   │   └── sales_service.py      # Sales calculations
│   │   │
│   │   └── utils/                    # Utilities
│   │       ├── __init__.py
│   │       ├── auth.py               # Authentication & JWT
│   │       └── excel.py              # Excel processing
│   │
│   ├── migrations/                   # Alembic migrations (hazır)
│   ├── main.py                       # Entry point
│   ├── seed.py                       # Database seeding
│   ├── requirements.txt              # Python dependencies
│   └── .env.example                  # Environment example
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.js             # API client
│   │   │   └── index.js              # API endpoints
│   │   │
│   │   ├── components/
│   │   │   └── Navbar.jsx            # Navigation
│   │   │
│   │   ├── pages/
│   │   │   ├── Login.jsx             # Giriş sayfası
│   │   │   ├── Dashboard.jsx         # Ana sayfa
│   │   │   ├── Personnel.jsx         # Personel yönetimi
│   │   │   ├── Sales.jsx             # Satış yönetimi
│   │   │   ├── Attendance.jsx        # Puantaj
│   │   │   ├── Warnings.jsx          # Uyarılar
│   │   │   ├── Training.jsx          # Eğitim
│   │   │   └── CallMonitoring.jsx    # Çağrı izleme
│   │   │
│   │   ├── App.jsx                   # Main App
│   │   ├── main.jsx                  # React entry
│   │   └── index.css                 # Global styles
│   │
│   ├── index.html                    # HTML entry
│   ├── package.json                  # Node dependencies
│   ├── vite.config.js                # Vite config
│   ├── postcss.config.js             # PostCSS config
│   └── tailwind.config.js            # Tailwind config
│
├── Docker Files
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
│
├── Documentation
│   ├── README.md                     # Genel dokümantasyon
│   ├── QUICKSTART.md                 # Hızlı başlangıç
│   └── PROJECT_STRUCTURE.md          # Bu dosya
│
├── .env.production                   # Production env
├── .env.example                      # Env template
├── .gitignore
│
└── Configuration
    ├── requirements.txt
    ├── package.json
    └── docker-compose.yml
```

## Modül Açıklamaları

### Backend Modülleri

#### 1. Authentication (routes/auth.py)
- Kayıt, giriş, token yönetimi
- JWT-based authentication

#### 2. User Management (routes/users.py)
- Admin user CRUD operations
- Role-based access control

#### 3. Personnel (routes/personnel.py)
- Personel bilgileri yönetimi
- Departman, pozisyon, iletişim bilgileri

#### 4. Sales (routes/sales.py)
- Günlük satış verileri
- Excel bulk upload
- İnkremental veri hesaplama
- Satış analizi

#### 5. Attendance (routes/attendance.py)
- Aylık puantaj/çalışma saatleri
- İzin günleri takibi
- Maaş hesaplaması

#### 6. Warnings (routes/warnings.py)
- Uyarı ve kesinti kayıtları
- Docs senkronizasyonu
- Personel bazlı filtreleme

#### 7. Training (routes/training.py)
- Eğitim kayıtları
- Eğitmen, konu, tarih-saat bilgileri
- Geribildirim notları

#### 8. Call Monitoring (routes/call_monitoring.py)
- Dinlenen çağrılar
- Kalite puanı
- Telefon numarası takibi

#### 9. WhatsApp (routes/whatsapp.py)
- Cevapsız mesaj takibi
- Günlük veriler
- Docs senkronizasyonu

### Frontend Sayfaları

#### Login
- Kullanıcı adı/şifre girişi
- Token yönetimi
- Automatic redirect

#### Dashboard
- Özet bilgiler
- Personel sayısı
- Toplam satışlar
- Tarih filtreleme

#### Personnel
- Personel listesi
- Yeni personel ekleme
- Silme işlemi

#### Sales
- Excel yükleme
- Satış tablosu
- Tarih aralığı filtreleme
- Excel export

#### Attendance
- Ay/yıl seçimi
- Puantaj listesi
- Yeni kayıt ekleme

#### Warnings
- Personel filtresi
- Uyarı listesi
- Uyarı ekleme

#### Training
- Personel filtresi
- Eğitim listesi
- Yeni eğitim ekleme

#### Call Monitoring
- Çağrı listesi
- Kalite puanı görselleme
- Yeni çağrı kaydı

## Veri Akışı

```
Client (React)
    ↓
Vite Dev Server (3000)
    ↓
API Client (axios)
    ↓
Backend API (FastAPI - 8000)
    ↓
Routes (API endpoints)
    ↓
Services (Business Logic)
    ↓
Models (SQLAlchemy ORM)
    ↓
Database (PostgreSQL)
    ↓
Google Docs API (Opsiyonel - Docs linklerini bekliyor)
```

## Teknoloji Stack

### Backend
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL
- **Auth**: JWT + Passlib
- **Excel**: Pandas + openpyxl
- **API Docs**: Swagger/OpenAPI

### Frontend
- **Framework**: React 18
- **Bundler**: Vite
- **Styling**: Tailwind CSS
- **HTTP Client**: Fetch API
- **Router**: React Router v6

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Package Managers**: pip, npm

## Veritabanı Şeması

```
USERS
├── id (PK)
├── username (UNIQUE)
├── email (UNIQUE)
├── hashed_password
├── role (admin/user)
└── is_active

PERSONNEL
├── id (PK)
├── name
├── employee_id (UNIQUE)
├── department
└── position

SALES_DATA
├── id (PK)
├── personnel_id (FK)
├── sales_count
├── date
└── UNIQUE(personnel_id, date)

ATTENDANCE_DATA
├── id (PK)
├── personnel_id (FK)
├── month
├── year
├── working_days
├── leave_days
└── UNIQUE(personnel_id, month, year)

WARNING_DATA
├── id (PK)
├── personnel_id (FK)
├── subject
└── date

TRAINING_DATA
├── id (PK)
├── personnel_id (FK)
├── subject
├── date
├── start_time
└── end_time

CALL_MONITORING
├── id (PK)
├── personnel_id (FK)
├── phone_number
├── quality_score
└── date

WHATSAPP_DATA
├── id (PK)
├── personnel_id (FK)
├── unanswered_count
├── date
└── UNIQUE(personnel_id, date)
```

## Güvenlik Özellikleri

✅ JWT Token Authentication
✅ Password Hashing (bcrypt)
✅ Role-Based Access Control
✅ CORS Protection
✅ Input Validation (Pydantic)
✅ SQL Injection Prevention (SQLAlchemy ORM)
✅ Environment Variable Management

## Scalability Hazırlıkları

- Database Connection Pooling
- API Caching Yapısı
- Async Request Handling
- Docker Containerization
- Microservices Ready Architecture

## Gelecek Geliştirmeler

- [ ] Google Docs API Integration (linkler gelince)
- [ ] Scheduled Sync Tasks (Celery/APScheduler)
- [ ] Advanced Analytics Dashboard
- [ ] Email Notifications
- [ ] Database Backup System
- [ ] Audit Logging
- [ ] Performance Metrics
- [ ] Multi-language Support
- [ ] Mobile App
