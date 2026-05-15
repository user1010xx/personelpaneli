from datetime import date

from app.models import CallProcessData, Personnel
from app.routes.dashboard import build_summary


def test_build_summary_averages_by_days_with_data(db):
    personnel = Personnel(name="Ali Veli", employee_id="EMP001")
    db.add(personnel)
    db.commit()
    db.refresh(personnel)

    db.add_all(
        [
            CallProcessData(
                personnel_id=personnel.id,
                date=date(2024, 1, 1),
                call_count=10,
                talk_duration=600,
                average_ring_duration=10,
            ),
            CallProcessData(
                personnel_id=personnel.id,
                date=date(2024, 1, 3),
                call_count=20,
                talk_duration=1200,
                average_ring_duration=12,
            ),
        ]
    )
    db.commit()

    rows = build_summary(db, date(2024, 1, 1), date(2024, 1, 31))

    assert len(rows) == 1
    assert rows[0]["average_call_count"] == 15
    assert rows[0]["average_talk_duration"] == 900
    assert rows[0]["average_talk_duration_display"] == "00:15:00"


def test_build_summary_returns_zeroes_for_empty_dataset(db):
    personnel = Personnel(name="Ayşe", employee_id="EMP002")
    db.add(personnel)
    db.commit()

    rows = build_summary(db, date(2024, 2, 1), date(2024, 2, 29))

    assert len(rows) == 1
    assert rows[0]["membership_count"] == 0
    assert rows[0]["average_call_count"] == 0
    assert rows[0]["average_talk_duration"] == 0
    assert rows[0]["average_talk_duration_display"] == "00:00:00"
    assert rows[0]["average_call_score"] == 0
    assert rows[0]["average_whatsapp_unanswered"] == 0