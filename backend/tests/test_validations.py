import os
os.environ.setdefault('SECRET_KEY', 'test-secret-key-that-is-long-enough-12345')
os.environ.setdefault('DATABASE_URL', 'sqlite:///./test.db')

import pytest
from pydantic import ValidationError

from app.schemas.personnel import PersonnelCreate
from app.schemas.whatsapp import WhatsAppDataCreate
from app.schemas.attendance import AttendanceDataCreate, AttendanceDataUpdate
from app.utils.auth import create_access_token, decode_token


def test_token_decode_contains_access_type():
    token = create_access_token({'sub': 'admin', 'user_id': 1, 'role': 'admin'})
    payload = decode_token(token)
    assert payload['sub'] == 'admin'
    assert payload['type'] == 'access'


def test_personnel_validation_rejects_empty_name():
    with pytest.raises(ValidationError):
        PersonnelCreate(name=' ', employee_id='EMP001')


def test_personnel_validation_accepts_valid_phone():
    item = PersonnelCreate(name='Ali Veli', employee_id='EMP001', phone='05551234567')
    assert item.phone == '05551234567'


def test_whatsapp_rejects_negative_count():
    with pytest.raises(ValidationError):
        WhatsAppDataCreate(personnel_id=1, unanswered_count=-1, date='2024-01-01')


def test_attendance_total_days_cannot_exceed_month_days():
    with pytest.raises(ValidationError):
        AttendanceDataCreate(personnel_id=1, month=2, year=2024, working_days=29, leave_days=1)


def test_attendance_update_total_days_cannot_exceed_month_days():
    with pytest.raises(ValidationError):
        AttendanceDataUpdate(month=2, year=2024, working_days=29, leave_days=1)


def test_attendance_update_total_days_uses_existing_month_context():
    with pytest.raises(ValidationError):
        AttendanceDataUpdate(month=4, year=2024, working_days=29.5, leave_days=1.5)


def test_attendance_update_allows_valid_fractional_totals():
    item = AttendanceDataUpdate(month=4, year=2024, working_days=29.5, leave_days=0.5)
    assert item.working_days == 29.5
    assert item.leave_days == 0.5
