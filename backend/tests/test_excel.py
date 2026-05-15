import os
os.environ.setdefault('SECRET_KEY', 'test-secret-key-that-is-long-enough-12345')
os.environ.setdefault('DATABASE_URL', 'sqlite:///./test.db')

from io import BytesIO
import pandas as pd
import pytest

from app.utils.excel import ExcelService


def test_parse_sales_excel_supports_turkish_columns():
    buffer = BytesIO()
    df = pd.DataFrame([
        {'Personel Adı': 'Ali Veli', 'Tarih': '2024-01-01', 'Satış Adedi': 5}
    ])
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    records = ExcelService.parse_sales_excel(buffer.getvalue())
    assert len(records) == 1
    assert records[0].personnel_name == 'Ali Veli'
    assert records[0].sales_count == 5
    assert str(records[0].date) == '2024-01-01'


def test_parse_sales_excel_falls_back_to_previous_day_when_date_missing():
    buffer = BytesIO()
    df = pd.DataFrame([
        {'Personel Adı': 'Ali Veli', 'Satış Adedi': 5}
    ])
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    records = ExcelService.parse_sales_excel(buffer.getvalue())
    assert len(records) == 1
    assert records[0].personnel_name == 'Ali Veli'
    assert records[0].sales_count == 5


def test_parse_call_process_excel_uses_excel_date():
    buffer = BytesIO()
    df = pd.DataFrame([
        {
            'Personel Adı': 'Ayşe',
            'Tarih': '2024-02-03',
            'Çağrı Adedi': 8,
            'Konuşma Süresi': '00:10:00',
            'Ortalama Çaldırma Süresi': '00:00:15',
        }
    ])
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    records = ExcelService.parse_call_process_excel(buffer.getvalue())
    assert len(records) == 1
    assert records[0].personnel_name == 'Ayşe'
    assert str(records[0].date) == '2024-02-03'


def test_parse_call_process_excel_falls_back_to_previous_day_when_date_missing():
    buffer = BytesIO()
    df = pd.DataFrame([
        {
            'Personel Adı': 'Ayşe',
            'Çağrı Adedi': 8,
            'Konuşma Süresi': '00:10:00',
            'Ortalama Çaldırma Süresi': '00:00:15',
        }
    ])
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    records = ExcelService.parse_call_process_excel(buffer.getvalue())
    assert len(records) == 1
    assert records[0].personnel_name == 'Ayşe'


def test_validate_excel_upload_rejects_invalid_extension():
    with pytest.raises(ValueError, match='Only Excel files with .xlsx or .xls extension are allowed'):
        ExcelService.validate_excel_upload('veri.csv', 'text/csv', 10)


def test_validate_excel_upload_rejects_invalid_mime_type():
    with pytest.raises(ValueError, match='Invalid file type. Only Excel uploads are allowed'):
        ExcelService.validate_excel_upload('veri.xlsx', 'text/plain', 10)


def test_validate_excel_upload_rejects_oversized_files():
    with pytest.raises(ValueError, match='Excel file size exceeds 5 MB limit'):
        ExcelService.validate_excel_upload('veri.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', ExcelService.MAX_FILE_SIZE_BYTES + 1)
