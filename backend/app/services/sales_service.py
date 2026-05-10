from sqlalchemy.orm import Session
from datetime import date, timedelta
from ..models import SalesData, Personnel
from typing import Dict, List, Tuple

class SalesService:
    """Service for sales data operations"""
    
    @staticmethod
    def get_sales_by_personnel_and_date_range(
        db: Session,
        personnel_id: int,
        start_date: date,
        end_date: date
    ) -> int:
        """
        Get total sales for personnel in date range
        Supports incremental calculation (e.g., 1-9 May vs 1-10 May)
        """
        sales = db.query(SalesData).filter(
            SalesData.personnel_id == personnel_id,
            SalesData.date.between(start_date, end_date)
        ).all()
        
        total_sales = sum(s.sales_count for s in sales)
        return total_sales
    
    @staticmethod
    def get_daily_sales_for_date(
        db: Session,
        personnel_id: int,
        target_date: date
    ) -> int:
        """
        Get sales for specific date (single day sales)
        Useful for understanding daily increment
        """
        sales = db.query(SalesData).filter(
            SalesData.personnel_id == personnel_id,
            SalesData.date == target_date
        ).first()
        
        return sales.sales_count if sales else 0
    
    @staticmethod
    def get_all_personnel_sales_summary(
        db: Session,
        start_date: date,
        end_date: date
    ) -> Dict[str, Dict]:
        """
        Get sales summary for all personnel in date range
        Returns: {personnel_name: {total: int, average: float, daily_data: []}}
        """
        personnel_list = db.query(Personnel).all()
        summary = {}
        
        for personnel in personnel_list:
            sales = db.query(SalesData).filter(
                SalesData.personnel_id == personnel.id,
                SalesData.date.between(start_date, end_date)
            ).all()
            
            total_sales = sum(s.sales_count for s in sales)
            days = (end_date - start_date).days + 1
            average = total_sales / days if days > 0 else 0
            
            summary[personnel.name] = {
                'total': total_sales,
                'average': average,
                'daily_data': [(s.date, s.sales_count) for s in sales]
            }
        
        return summary
    
    @staticmethod
    def add_bulk_sales_data(
        db: Session,
        sales_records: List[Tuple[str, date, int]]
    ) -> Dict:
        """
        Add bulk sales data from Excel
        Records format: [(personnel_name, date, sales_count), ...]
        Returns: {success: int, failed: int, errors: []}
        """
        result = {"success": 0, "failed": 0, "errors": []}
        
        for personnel_name, target_date, sales_count in sales_records:
            try:
                # Find personnel by name
                personnel = db.query(Personnel).filter(
                    Personnel.name.ilike(personnel_name)
                ).first()
                
                if not personnel:
                    result["failed"] += 1
                    result["errors"].append(f"Personnel not found: {personnel_name}")
                    continue
                
                # Check if record exists for this date
                existing = db.query(SalesData).filter(
                    SalesData.personnel_id == personnel.id,
                    SalesData.date == target_date
                ).first()
                
                if existing:
                    # Update existing record
                    existing.sales_count = sales_count
                else:
                    # Create new record
                    new_record = SalesData(
                        personnel_id=personnel.id,
                        sales_count=sales_count,
                        date=target_date
                    )
                    db.add(new_record)
                
                result["success"] += 1
            
            except Exception as e:
                result["failed"] += 1
                result["errors"].append(f"Error processing {personnel_name}: {str(e)}")
        
        db.commit()
        return result
