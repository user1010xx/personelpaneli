from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import CallMonitoring, CallProcessData, Personnel, SalesData, WhatsAppData
from ..utils.auth import get_current_user
from ..utils.dates import validate_date_range

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


def format_duration(total_seconds: float) -> str:
    seconds_value = int(total_seconds or 0)
    hours = seconds_value // 3600
    minutes = (seconds_value % 3600) // 60
    seconds = seconds_value % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def top_three(rows, key, reverse=True):
    filtered = [row for row in rows if row.get(key, 0) is not None]
    return sorted(filtered, key=lambda item: item.get(key, 0), reverse=reverse)[:3]


def build_summary(db: Session, start_date: date, end_date: date):
    sales_subquery = (
        db.query(
            SalesData.personnel_id.label("personnel_id"),
            func.coalesce(func.sum(SalesData.sales_count), 0).label("membership_count"),
        )
        .filter(SalesData.date >= start_date, SalesData.date <= end_date)
        .group_by(SalesData.personnel_id)
        .subquery()
    )
    call_process_subquery = (
        db.query(
            CallProcessData.personnel_id.label("personnel_id"),
            func.coalesce(func.sum(CallProcessData.call_count), 0).label("total_call_count"),
            func.coalesce(func.sum(CallProcessData.talk_duration), 0).label("total_talk_duration"),
            func.coalesce(func.count(func.distinct(CallProcessData.date)), 0).label("call_process_days"),
        )
        .filter(CallProcessData.date >= start_date, CallProcessData.date <= end_date)
        .group_by(CallProcessData.personnel_id)
        .subquery()
    )
    call_monitoring_subquery = (
        db.query(
            CallMonitoring.personnel_id.label("personnel_id"),
            func.coalesce(func.avg(CallMonitoring.quality_score), 0).label("average_call_score"),
        )
        .filter(CallMonitoring.date >= start_date, CallMonitoring.date <= end_date)
        .group_by(CallMonitoring.personnel_id)
        .subquery()
    )
    whatsapp_subquery = (
        db.query(
            WhatsAppData.personnel_id.label("personnel_id"),
            func.coalesce(func.avg(WhatsAppData.unanswered_count), 0).label("average_whatsapp_unanswered"),
        )
        .filter(WhatsAppData.date >= start_date, WhatsAppData.date <= end_date)
        .group_by(WhatsAppData.personnel_id)
        .subquery()
    )

    rows = (
        db.query(
            Personnel.id.label("personnel_id"),
            Personnel.name.label("personnel_name"),
            func.coalesce(sales_subquery.c.membership_count, 0).label("membership_count"),
            func.coalesce(call_process_subquery.c.total_call_count, 0).label("total_call_count"),
            func.coalesce(call_process_subquery.c.total_talk_duration, 0).label("total_talk_duration"),
            func.coalesce(call_process_subquery.c.call_process_days, 0).label("call_process_days"),
            func.coalesce(call_monitoring_subquery.c.average_call_score, 0).label("average_call_score"),
            func.coalesce(whatsapp_subquery.c.average_whatsapp_unanswered, 0).label("average_whatsapp_unanswered"),
        )
        .outerjoin(sales_subquery, sales_subquery.c.personnel_id == Personnel.id)
        .outerjoin(call_process_subquery, call_process_subquery.c.personnel_id == Personnel.id)
        .outerjoin(call_monitoring_subquery, call_monitoring_subquery.c.personnel_id == Personnel.id)
        .outerjoin(whatsapp_subquery, whatsapp_subquery.c.personnel_id == Personnel.id)
        .order_by(Personnel.name.asc())
        .all()
    )

    table_rows = []
    for row in rows:
        average_call_count = (
            row.total_call_count / row.call_process_days if row.call_process_days else 0
        )
        average_talk_duration = (
            row.total_talk_duration / row.call_process_days if row.call_process_days else 0
        )
        table_rows.append({
            "personnel_id": row.personnel_id,
            "personnel_name": row.personnel_name,
            "membership_count": row.membership_count,
            "average_call_count": round(average_call_count, 2),
            "average_talk_duration": round(average_talk_duration, 2),
            "average_talk_duration_display": format_duration(average_talk_duration),
            "average_call_score": round(row.average_call_score or 0, 2),
            "average_whatsapp_unanswered": round(row.average_whatsapp_unanswered or 0, 2),
        })

    return table_rows


@router.get("/summary")
def dashboard_summary(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    validate_date_range(start_date, end_date)
    table_rows = build_summary(db, start_date, end_date)

    return {
        "start_date": str(start_date),
        "end_date": str(end_date),
        "rows": table_rows,
        "leaders": {
            "membership": top_three(table_rows, "membership_count", True),
            "call_score": top_three(table_rows, "average_call_score", True),
            "talk_duration": top_three(table_rows, "average_talk_duration", True),
            "call_count": top_three(table_rows, "average_call_count", True),
            "whatsapp_unanswered": top_three(table_rows, "average_whatsapp_unanswered", False),
        },
    }