import pandas as pd
from datetime import datetime, timedelta, time
from sqlalchemy.orm import Session
from app.models import (
    Personnel, SalesData, AttendanceData, WarningData,
    TrainingData, CallMonitoring, WhatsAppData, User
)
from app.utils.auth import hash_password

def seed_database(db: Session):
    """Seed database with sample data for testing"""

    try:
        if db.query(User).first():
            print("Database already seeded")
            return

        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@personelpanel.com",
            full_name="Administrator",
            role="admin",
            hashed_password=hash_password("LocalDev123!"),
            is_active=True
        )
        db.add(admin_user)

        # Create test user
        test_user = User(
            username="testuser",
            email="test@personelpanel.com",
            full_name="Test User",
            role="user",
            hashed_password=hash_password("LocalDev123!"),
            is_active=True
        )
        db.add(test_user)

        # Create personnel
        personnel_data = [
            {"name": "Ahmet Yilmaz", "employee_id": "EMP001", "department": "Satis", "position": "Satis Danismani"},
            {"name": "Fatma Kara", "employee_id": "EMP002", "department": "Satis", "position": "Satis Danismani"},
            {"name": "Ali Demir", "employee_id": "EMP003", "department": "Musteri Hizmetleri", "position": "Musteri Temsilcisi"},
            {"name": "Zeynep Guzel", "employee_id": "EMP004", "department": "Satis", "position": "Satis Koordinatoru"},
            {"name": "Murat Kaya", "employee_id": "EMP005", "department": "Musteri Hizmetleri", "position": "Musteri Temsilcisi"},
        ]

        personnel_objects = []
        for p_data in personnel_data:
            p = Personnel(**p_data)
            db.add(p)
            personnel_objects.append(p)

        db.commit()

        db.refresh(admin_user)
        db.refresh(test_user)
        for p in personnel_objects:
            db.refresh(p)

        # Create sample sales data
        today = datetime.now().date()
        for i, person in enumerate(personnel_objects):
            for day_offset in range(1, 11):
                sale_date = today - timedelta(days=day_offset)
                sales = SalesData(
                    personnel_id=person.id,
                    sales_count=5 + (i + day_offset) % 10,
                    date=sale_date
                )
                db.add(sales)

        # Create sample attendance data
        current_month = datetime.now().month
        current_year = datetime.now().year

        for person in personnel_objects:
            attendance = AttendanceData(
                personnel_id=person.id,
                month=current_month,
                year=current_year,
                working_days=28.5,
                leave_days=1.5,
                salary_amount=15000 + (person.id * 1000)
            )
            db.add(attendance)

        # Create sample warnings
        warnings_data = [
            {"personnel_id": personnel_objects[0].id, "subject": "Gec gelme", "notes": "3 kez gec gelinmistir"},
            {"personnel_id": personnel_objects[1].id, "subject": "Musteri sikayeti", "notes": "Musteri hizmetinde eksiklik"},
        ]

        for w_data in warnings_data:
            w_data["date"] = today - timedelta(days=5)
            w = WarningData(**w_data)
            db.add(w)

        # Create sample training
        training_data = [
            {
                "personnel_id": personnel_objects[0].id,
                "subject": "Urun Egitimi",
                "date": today - timedelta(days=3),
                "start_time": time(9, 0),
                "end_time": time(11, 0),
                "trainer": "Egitmen Ali"
            },
            {
                "personnel_id": personnel_objects[2].id,
                "subject": "Musteri Iliskileri",
                "date": today - timedelta(days=2),
                "start_time": time(14, 0),
                "end_time": time(16, 0),
                "trainer": "Egitmen Ayse"
            },
        ]

        for t_data in training_data:
            t = TrainingData(**t_data)
            db.add(t)

        # Create sample call monitoring
        for i, person in enumerate(personnel_objects[:3]):
            for day_offset in range(1, 6):
                call = CallMonitoring(
                    personnel_id=person.id,
                    phone_number=f"+905{i:02d}{day_offset:03d}0000",
                    quality_score=70 + (day_offset * 3) % 30,
                    date=today - timedelta(days=day_offset)
                )
                db.add(call)

        # Create sample whatsapp data
        for person in personnel_objects:
            for day_offset in range(1, 6):
                whatsapp = WhatsAppData(
                    personnel_id=person.id,
                    unanswered_count=2 + (person.id + day_offset) % 5,
                    date=today - timedelta(days=day_offset)
                )
                db.add(whatsapp)

        db.commit()
        print("Database seeded successfully!")
        print("Test credentials:")
        print("  Admin: admin / LocalDev123!")
        print("  User: testuser / LocalDev123!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {str(e)}")
        raise

if __name__ == "__main__":
    from app.database import SessionLocal, engine, Base

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    seed_database(db)
    db.close()
