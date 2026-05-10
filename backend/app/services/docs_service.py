from google.oauth2 import service_account
from google.auth.transport.requests import Request
import googleapiclient.discovery
from ..config import settings
import json
import os

class DocsService:
    """Service for Google Docs API integration"""
    
    def __init__(self):
        self.service = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Google Docs API client"""
        try:
            if not os.path.exists(settings.GOOGLE_CREDENTIALS_PATH):
                # Try to load from environment variable
                if 'GOOGLE_CREDENTIALS_JSON' in os.environ:
                    credentials_dict = json.loads(os.environ['GOOGLE_CREDENTIALS_JSON'])
                else:
                    print(f"Warning: Credentials file not found at {settings.GOOGLE_CREDENTIALS_PATH}")
                    return
            
            credentials = service_account.Credentials.from_service_account_file(
                settings.GOOGLE_CREDENTIALS_PATH,
                scopes=['https://www.googleapis.com/auth/documents.readonly']
            )
            
            self.service = googleapiclient.discovery.build('docs', 'v1', credentials=credentials)
        except Exception as e:
            print(f"Error initializing Docs API: {str(e)}")
    
    def get_document_content(self, doc_id: str) -> dict:
        """Fetch document content from Google Docs"""
        try:
            if not self.service:
                return {"error": "Service not initialized"}
            
            doc = self.service.documents().get(documentId=doc_id).execute()
            return doc
        except Exception as e:
            return {"error": str(e)}
    
    def parse_puantaj_data(self, doc_id: str) -> list:
        """
        Parse attendance/puantaj data from Docs
        Expected format: Personnel Name | Working Days | Leave Days | Month/Year
        Returns list of attendance records
        """
        doc = self.get_document_content(doc_id)
        if "error" in doc:
            return []
        
        # TODO: Implement parsing logic based on actual Docs structure
        attendance_records = []
        return attendance_records
    
    def parse_warnings_data(self, doc_id: str) -> list:
        """
        Parse warnings/uyarılar data from Docs
        Expected format: Personnel Name | Subject | Date | Notes
        Returns list of warning records
        """
        doc = self.get_document_content(doc_id)
        if "error" in doc:
            return []
        
        # TODO: Implement parsing logic
        warning_records = []
        return warning_records
    
    def parse_whatsapp_data(self, doc_id: str) -> list:
        """
        Parse WhatsApp unanswered messages from Docs
        Expected format: Personnel Name | Unanswered Count | Date
        Returns list of WhatsApp records
        """
        doc = self.get_document_content(doc_id)
        if "error" in doc:
            return []
        
        # TODO: Implement parsing logic
        whatsapp_records = []
        return whatsapp_records
