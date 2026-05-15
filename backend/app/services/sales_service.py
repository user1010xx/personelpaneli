from sqlalchemy import func
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
        """Get total sales for personnel in date range"""
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
        """Get sales for specific date"""
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
        """Get sales summary for all personnel in date range"""
        personnel_list = db.query(Personnel).all()
        totals = {
            row.personnel_id: row
            for row in db.query(
                SalesData.personnel_id.label("personnel_id"),
                func.coalesce(func.sum(SalesData.sales_count), 0).label("total_sales"),
            )
            .filter(SalesData.date.between(start_date, end_date))
            .group_by(SalesData.personnel_id)
            .all()
        }
        sales_rows = db.query(SalesData).filter(
            SalesData.date.between(start_date, end_date)
        ).all()
        sales_by_personnel = {}
        for sales in sales_rows:
            sales_by_personnel.setdefault(sales.personnel_id, []).append(sales)

        summary = {}
        days = (end_date - start_date).days + 1
        
        for personnel in personnel_list:
            sales = sales_by_personnel.get(personnel.id, [])
            total_sales = totals.get(personnel.id).total_sales if personnel.id in totals else 0
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
        """Add bulk sales data from Excel"""
        result = {"success": 0, "failed": 0, "errors": []}
        
        for personnel_name, target_date, sales_count in sales_records:
            try:
                personnel = db.query(Personnel).filter(
                    Personnel.name.ilike(personnel_name)
                ).first()
                
                if not personnel:
                    result["failed"] += 1
                    result["errors"].append(f"Personnel not found: {personnel_name}")
                    continue
                
                existing = db.query(SalesData).filter(
                    SalesData.personnel_id == personnel.id,
                    SalesData.date == target_date
                ).first()
                
                if existing:
                    existing.sales_count = sales_count
                else:
                    new_record = SalesData(
                        personnel_id=personnel.id,
                        sales_count=sales_count,
                        date=target_date
                    )
                    db.add(new_record)
                
                db.flush()
                result["success"] += 1
            
            except Exception as e:
                result["failed"] += 1
                result["errors"].append(f"Error processing {personnel_name}: {str(e)}")
        
        return result
