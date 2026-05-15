import re
import unicodedata
from datetime import date, datetime as datetime_type, time as time_type, timedelta
from io import BytesIO
from typing import List

import pandas as pd
from sqlalchemy.orm import Session

from ..models import Personnel, SalesData
from ..schemas.call_process import CallProcessDataBulkUpload
from ..schemas.sales import SalesDataBulkUpload


def normalize_header(value) -> str:
    # Map Turkish/Latin-Extended characters that do not decompose under NFKD
    # to their ASCII equivalents before normalization.
    _TR_MAP = str.maketrans(
        "\u0131\u0130\u015f\u015e\u011f\u011e\u00e7\u00c7\u00f6\u00d6\u00fc\u00dc",
        "iisSgGcCoOuU",
    )
    text = str(value or "").strip()
    text = text.translate(_TR_MAP)
    text = text.casefold()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


class ExcelService:
    MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS = {".xlsx", ".xls"}
    ALLOWED_MIME_TYPES = {
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        "application/octet-stream",
    }
    SALES_COLUMN_ALIASES = {
        "personnel name": "personnel_name",
        "personel adi": "personnel_name",
        "personel adi": "personnel_name",
        "personel ad i": "personnel_name",
        "personnel": "personnel_name",
        "personel": "personnel_name",
        "date": "date",
        "tarih": "date",
        "sales count": "sales_count",
        "uye adedi": "sales_count",
        "uye sayisi": "sales_count",
        "satis adedi": "sales_count",
        "sati adedi": "sales_count",
        "sat i adedi": "sales_count",
        "satis": "sales_count",
    }

    CALL_PROCESS_COLUMN_ALIASES = {
        "personnel name": "personnel_name",
        "personel adi": "personnel_name",
        "personel ad i": "personnel_name",
        "personel": "personnel_name",
        "personnel": "personnel_name",
        "date": "date",
        "tarih": "date",
        "arama adedi": "call_count",
        "cagri adedi": "call_count",
        "iagri adedi": "call_count",
        "i a r i adedi": "call_count",
        "konusma suresi": "talk_duration",
        "konu ma suresi": "talk_duration",
        "ortalama caldirma suresi": "average_ring_duration",
        "ortalama ialdirma suresi": "average_ring_duration",
        "ortalama i ald irma suresi": "average_ring_duration",
    }

    @staticmethod
    def _default_excel_date() -> date:
        return date.today() - timedelta(days=1)

    @staticmethod
    def validate_excel_upload(filename: str | None, content_type: str | None, file_size: int) -> None:
        normalized_name = (filename or "").strip().lower()
        if not any(normalized_name.endswith(extension) for extension in ExcelService.ALLOWED_EXTENSIONS):
            raise ValueError("Only Excel files with .xlsx or .xls extension are allowed")
        if content_type and content_type not in ExcelService.ALLOWED_MIME_TYPES:
            raise ValueError("Invalid file type. Only Excel uploads are allowed")
        if file_size <= 0:
            raise ValueError("Uploaded file is empty")
        if file_size > ExcelService.MAX_FILE_SIZE_BYTES:
            raise ValueError(f"Excel file size exceeds {ExcelService.MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB limit")

    @staticmethod
    def _parse_excel_date(value):
        if pd.isna(value):
            return None
        if isinstance(value, datetime_type):
            return value.date()
        if isinstance(value, date):
            return value
        parsed = pd.to_datetime(value, errors="coerce")
        if pd.isna(parsed):
            return None
        return parsed.date()

    @staticmethod
    def _parse_duration_value(value) -> float:
        if pd.isna(value):
            return 0.0
        if isinstance(value, timedelta):
            return value.total_seconds()
        if isinstance(value, datetime_type):
            return value.hour * 3600 + value.minute * 60 + value.second + value.microsecond / 1_000_000
        if isinstance(value, time_type):
            return value.hour * 3600 + value.minute * 60 + value.second + value.microsecond / 1_000_000
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return 0.0
            if ":" in text:
                parts = text.split(":")
                try:
                    if len(parts) == 3:
                        hours, minutes, seconds = parts
                        return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
                    if len(parts) == 2:
                        minutes, seconds = parts
                        return float(minutes) * 60 + float(seconds)
                except ValueError:
                    pass
            return float(text.replace(",", "."))
        return float(value)

    @staticmethod
    def parse_sales_excel(file_content: bytes) -> List[SalesDataBulkUpload]:
        try:
            df = pd.read_excel(BytesIO(file_content))
            df.columns = [
                ExcelService.SALES_COLUMN_ALIASES.get(normalize_header(col), normalize_header(col))
                for col in df.columns
            ]

            required_columns = ["personnel_name", "sales_count"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")

            sales_data = []
            for _, row in df.iterrows():
                if pd.isna(row["personnel_name"]) or pd.isna(row["sales_count"]):
                    continue
                sales_data.append(SalesDataBulkUpload(
                    personnel_name=str(row["personnel_name"]).strip(),
                    date=(
                        ExcelService._parse_excel_date(row["date"])
                        if "date" in df.columns
                        else None
                    ) or ExcelService._default_excel_date(),
                    sales_count=int(row["sales_count"]),
                ))
            return sales_data
        except Exception as exc:
            raise ValueError(f"Error parsing Excel file: {str(exc)}")

    @staticmethod
    def parse_call_process_excel(file_content: bytes) -> List[CallProcessDataBulkUpload]:
        try:
            df = pd.read_excel(BytesIO(file_content))
            df.columns = [
                ExcelService.CALL_PROCESS_COLUMN_ALIASES.get(normalize_header(col), normalize_header(col))
                for col in df.columns
            ]

            required_columns = ["personnel_name", "call_count", "talk_duration", "average_ring_duration"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")

            call_process_data = []
            for _, row in df.iterrows():
                if pd.isna(row["personnel_name"]):
                    continue
                call_process_data.append(CallProcessDataBulkUpload(
                    personnel_name=str(row["personnel_name"]).strip(),
                    date=(
                        ExcelService._parse_excel_date(row["date"])
                        if "date" in df.columns
                        else None
                    ) or ExcelService._default_excel_date(),
                    call_count=int(float(row["call_count"])) if not pd.isna(row["call_count"]) else 0,
                    talk_duration=ExcelService._parse_duration_value(row["talk_duration"]),
                    average_ring_duration=ExcelService._parse_duration_value(row["average_ring_duration"]),
                ))
            return call_process_data
        except Exception as exc:
            raise ValueError(f"Error parsing Excel file: {str(exc)}")

    @staticmethod
    def export_personnel_analytics(
        db: Session,
        personnel_list: List[int],
        start_date: date,
        end_date: date,
    ) -> bytes:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            for personnel_id in personnel_list:
                personnel = db.query(Personnel).filter(Personnel.id == personnel_id).first()
                if not personnel:
                    continue

                sales = db.query(SalesData).filter(
                    SalesData.personnel_id == personnel_id,
                    SalesData.date.between(start_date, end_date),
                ).all()

                df = pd.DataFrame({
                    "Personnel": [personnel.name] * len(sales),
                    "Date": [sale.date for sale in sales],
                    "Sales Count": [sale.sales_count for sale in sales],
                })
                df.to_excel(writer, sheet_name=personnel.name[:31], index=False)

        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def generate_summary_report(
        sales_summary: dict,
        attendance_summary: dict,
        warnings_count: dict,
    ) -> bytes:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            pd.DataFrame([
                {"Personnel": name, "Total Sales": data["total"], "Average Daily Sales": data["average"]}
                for name, data in sales_summary.items()
            ]).to_excel(writer, sheet_name="Sales Summary", index=False)

            pd.DataFrame([
                {
                    "Personnel": name,
                    "Working Days": data["working_days"],
                    "Leave Days": data["leave_days"],
                    "Total": data["total"],
                }
                for name, data in attendance_summary.items()
            ]).to_excel(writer, sheet_name="Attendance", index=False)

            pd.DataFrame([
                {"Personnel": name, "Warning Count": count}
                for name, count in warnings_count.items()
            ]).to_excel(writer, sheet_name="Warnings", index=False)

        buffer.seek(0)
        return buffer.getvalue()