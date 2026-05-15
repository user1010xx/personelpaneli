import json
import logging
import os
import googleapiclient.discovery
from google.oauth2 import service_account

from ..config import settings

logger = logging.getLogger(__name__)


def rows_from_values(values: list[list[str]]) -> list[dict]:
    if not values:
        return []

    headers = [str(header).strip() for header in values[0]]
    rows = []
    for value_row in values[1:]:
        if not any(str(cell).strip() for cell in value_row):
            continue
        row = {}
        for index, header in enumerate(headers):
            row[header] = str(value_row[index]).strip() if index < len(value_row) else ""
        rows.append(row)
    return rows


class DocsService:
    """Service for Google Docs and Google Sheets API integration"""

    def __init__(self):
        self.service = None
        self.sheets_service = None

    def _initialize(self):
        try:
            credentials = None
            scopes = [
                "https://www.googleapis.com/auth/documents.readonly",
                "https://www.googleapis.com/auth/spreadsheets.readonly",
            ]

            if os.path.exists(settings.GOOGLE_CREDENTIALS_PATH):
                credentials = service_account.Credentials.from_service_account_file(
                    settings.GOOGLE_CREDENTIALS_PATH,
                    scopes=scopes,
                )
            elif settings.GOOGLE_CREDENTIALS_JSON:
                credentials_dict = json.loads(settings.GOOGLE_CREDENTIALS_JSON)
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_dict,
                    scopes=scopes,
                )
            else:
                logger.warning("Google credentials not found at %s", settings.GOOGLE_CREDENTIALS_PATH)
                return

            self.service = googleapiclient.discovery.build("docs", "v1", credentials=credentials)
            self.sheets_service = googleapiclient.discovery.build("sheets", "v4", credentials=credentials)
        except Exception as exc:
            logger.error("Error initializing Docs API: %s", str(exc))

    def _ensure_initialized(self):
        if not self.service or not self.sheets_service:
            self._initialize()

    def get_document_content(self, doc_id: str) -> dict:
        try:
            if not self.service:
                self._ensure_initialized()
            if not self.service:
                return {"error": "Service not initialized"}
            return self.service.documents().get(documentId=doc_id).execute()
        except Exception as exc:
            logger.error("Error fetching Google Docs document %s: %s", doc_id, str(exc))
            return {"error": str(exc)}

    def _extract_plain_text(self, doc: dict) -> str:
        text_parts = []
        for element in doc.get("body", {}).get("content", []):
            paragraph = element.get("paragraph")
            if not paragraph:
                continue
            for item in paragraph.get("elements", []):
                content = item.get("textRun", {}).get("content")
                if content:
                    text_parts.append(content)
        return "".join(text_parts)

    def _parse_pipe_table(self, doc_id: str, expected_columns: list[str]) -> list[dict]:
        doc = self.get_document_content(doc_id)
        if "error" in doc:
            logger.warning("Skipping Docs parse for %s: %s", doc_id, doc["error"])
            return []

        rows = []
        for line in self._extract_plain_text(doc).splitlines():
            values = [value.strip() for value in line.split("|")]
            if len(values) != len(expected_columns):
                continue
            if [value.lower() for value in values] == [column.lower() for column in expected_columns]:
                continue
            rows.append(dict(zip(expected_columns, values)))
        return rows

    def parse_puantaj_data(self, doc_id: str) -> list:
        return self._parse_pipe_table(doc_id, ["personnel_name", "working_days", "leave_days", "month_year"])

    def parse_warnings_data(self, doc_id: str) -> list:
        return self._parse_pipe_table(doc_id, ["personnel_name", "subject", "date", "notes"])

    def parse_whatsapp_data(self, doc_id: str) -> list:
        return self._parse_pipe_table(doc_id, ["personnel_name", "unanswered_count", "date"])

    def get_sheet_rows(self, sheet_id: str, sheet_name: str) -> list[dict]:
        try:
            if not self.sheets_service:
                self._ensure_initialized()
            if not self.sheets_service:
                raise ValueError("Google Sheets servisi baslatilamadi. credentials.json kontrol edin.")

            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=sheet_name,
            ).execute()
            values = result.get("values", [])

            return rows_from_values(values)
        except Exception as exc:
            logger.error("Error fetching Google Sheet %s: %s", sheet_id, str(exc))
            raise ValueError(f"Google Sheet okunamadi: {str(exc)}")

    def get_sheet_rows_by_gid(self, sheet_id: str, gid: str = "0") -> list[dict]:
        try:
            if not self.sheets_service:
                self._ensure_initialized()
            if not self.sheets_service:
                raise ValueError("Google Sheets servisi baslatilamadi. credentials.json kontrol edin.")

            spreadsheet = self.sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            target_title = None

            for sheet in spreadsheet.get("sheets", []):
                properties = sheet.get("properties", {})
                if str(properties.get("sheetId")) == str(gid):
                    target_title = properties.get("title")
                    break

            if not target_title:
                raise ValueError(f"Google Sheet gid bulunamadi: {gid}")

            return self.get_sheet_rows(sheet_id, target_title)
        except Exception as exc:
            logger.error("Error fetching Google Sheet by gid %s/%s: %s", sheet_id, gid, str(exc))
            if isinstance(exc, ValueError):
                raise
            raise ValueError(f"Google Sheet okunamadi: {str(exc)}")