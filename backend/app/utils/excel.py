import pandas as pd
from io import BytesIO
from typing import List, Tuple
from datetime import datetime, date
from sqlalchemy.orm import Session
from ..models import Personnel, SalesData
from ..schemas.sales import SalesDataBulkUpload

class ExcelService:
    """Service for handling Excel file operations"""
    
    @staticmethod
    def parse_sales_excel(file_content: bytes) -> List[SalesDataBulkUpload]:
        """
        Parse Excel file for sales data
        Expected columns: Personnel Name, Date, Sales Count
        """
        try:
            df = pd.read_excel(BytesIO(file_content))
            
            # Normalize column names
            df.columns = df.columns.str.lower().str.strip()
            
            required_columns = ['personnel name', 'date', 'sales count']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            sales_data = []
            for _, row in df.iterrows():
                # Skip empty rows
                if pd.isna(row['personnel name']) or pd.isna(row['sales count']):
                    continue
                
                sales_data.append(SalesDataBulkUpload(
                    personnel_name=str(row['personnel name']).strip(),
                    date=pd.to_datetime(row['date']).date() if not pd.isna(row['date']) else None,
                    sales_count=int(row['sales count'])
                ))
            
            return sales_data
        except Exception as e:
            raise ValueError(f"Error parsing Excel file: {str(e)}")
    
    @staticmethod
    def export_personnel_analytics(
        db: Session,
        personnel_list: List[int],
        start_date: date,
        end_date: date
    ) -> bytes:
        """
        Export personnel analytics to Excel
        Includes: sales, attendance, warnings, training, calls, whatsapp
        """
        with pd.ExcelWriter(BytesIO()) as writer:
            buffer = BytesIO()
            
            for personnel_id in personnel_list:
                personnel = db.query(Personnel).filter(Personnel.id == personnel_id).first()
                if not personnel:
                    continue
                
                # Get all related data
                sales = db.query(SalesData).filter(
                    SalesData.personnel_id == personnel_id,
                    SalesData.date.between(start_date, end_date)
                ).all()
                
                # Create DataFrame
                df_data = {
                    'Personnel': [personnel.name] * len(sales),
                    'Date': [s.date for s in sales],
                    'Sales Count': [s.sales_count for s in sales],
                }
                
                df = pd.DataFrame(df_data)
                df.to_excel(writer, sheet_name=personnel.name[:31], index=False)
            
            buffer.seek(0)
            return buffer.getvalue()
    
    @staticmethod
    def generate_summary_report(
        sales_summary: dict,
        attendance_summary: dict,
        warnings_count: dict
    ) -> bytes:
        """Generate summary report Excel"""
        buffer = BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Sales Summary
            df_sales = pd.DataFrame([
                {
                    'Personnel': name,
                    'Total Sales': data['total'],
                    'Average Daily Sales': data['average']
                }
                for name, data in sales_summary.items()
            ])
            df_sales.to_excel(writer, sheet_name='Sales Summary', index=False)
            
            # Attendance Summary
            df_attendance = pd.DataFrame([
                {
                    'Personnel': name,
                    'Working Days': data['working_days'],
                    'Leave Days': data['leave_days'],
                    'Total': data['total']
                }
                for name, data in attendance_summary.items()
            ])
            df_attendance.to_excel(writer, sheet_name='Attendance', index=False)
            
            # Warnings Summary
            df_warnings = pd.DataFrame([
                {
                    'Personnel': name,
                    'Warning Count': count
                }
                for name, count in warnings_count.items()
            ])
            df_warnings.to_excel(writer, sheet_name='Warnings', index=False)
        
        buffer.seek(0)
        return buffer.getvalue()
