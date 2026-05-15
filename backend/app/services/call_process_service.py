from datetime import date
from typing import Dict, List, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import CallProcessData, Personnel


class CallProcessService:
    @staticmethod
    def get_all_personnel_summary(
        db: Session,
        start_date: date,
        end_date: date
    ) -> Dict[str, Dict]:
        personnel_list = db.query(Personnel).all()
        totals = {
            row.personnel_id: row
            for row in db.query(
                CallProcessData.personnel_id.label("personnel_id"),
                func.coalesce(func.sum(CallProcessData.call_count), 0).label("total_calls"),
                func.coalesce(func.sum(CallProcessData.talk_duration), 0).label("total_talk_duration"),
                func.coalesce(func.avg(CallProcessData.average_ring_duration), 0).label("average_ring_duration"),
            )
            .filter(CallProcessData.date.between(start_date, end_date))
            .group_by(CallProcessData.personnel_id)
            .all()
        }
        summary = {}

        for personnel in personnel_list:
            records = db.query(CallProcessData).filter(
                CallProcessData.personnel_id == personnel.id,
                CallProcessData.date.between(start_date, end_date)
            ).all()

            total_row = totals.get(personnel.id)
            total_calls = total_row.total_calls if total_row else 0
            total_talk_duration = total_row.total_talk_duration if total_row else 0
            average_ring_duration = total_row.average_ring_duration if total_row else 0

            summary[personnel.name] = {
                "total_calls": total_calls,
                "total_talk_duration": total_talk_duration,
                "average_ring_duration": average_ring_duration,
                "daily_data": [
                    (record.date, record.call_count, record.talk_duration, record.average_ring_duration)
                    for record in records
                ]
            }

        return summary

    @staticmethod
    def add_bulk_call_process_data(
        db: Session,
        records: List[Tuple[str, date, int, float, float]]
    ) -> Dict:
        result = {"success": 0, "failed": 0, "errors": []}

        for personnel_name, target_date, call_count, talk_duration, average_ring_duration in records:
            try:
                personnel = db.query(Personnel).filter(Personnel.name.ilike(personnel_name)).first()

                if not personnel:
                    result["failed"] += 1
                    result["errors"].append(f"Personnel not found: {personnel_name}")
                    continue

                existing = db.query(CallProcessData).filter(
                    CallProcessData.personnel_id == personnel.id,
                    CallProcessData.date == target_date
                ).first()

                if existing:
                    existing.call_count = call_count
                    existing.talk_duration = talk_duration
                    existing.average_ring_duration = average_ring_duration
                else:
                    db.add(CallProcessData(
                        personnel_id=personnel.id,
                        date=target_date,
                        call_count=call_count,
                        talk_duration=talk_duration,
                        average_ring_duration=average_ring_duration
                    ))

                db.flush()
                result["success"] += 1
            except Exception as exc:
                result["failed"] += 1
                result["errors"].append(f"Error processing {personnel_name}: {str(exc)}")

        return result