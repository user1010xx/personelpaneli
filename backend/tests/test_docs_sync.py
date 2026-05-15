from app.models import DocsLink, Personnel
from app.routes.personnel import docs_service


def test_sync_personnel_from_docs_updates_department_position_and_phone(client, db, admin_token_headers, admin_user, monkeypatch):
    existing = Personnel(
        name="Ali Veli",
        employee_id="ali.veli",
        username="ali.veli",
        department="Eski Departman",
        position="Eski Pozisyon",
        phone="0000",
    )
    db.add(existing)
    db.add(
        DocsLink(
            key="personnel",
            label="Personel",
            url="https://docs.google.com/spreadsheets/d/test-sheet/edit?gid=0#gid=0",
            spreadsheet_id="test-sheet",
            gid="0",
        )
    )
    db.commit()

    monkeypatch.setattr(
        docs_service,
        "get_sheet_rows_by_gid",
        lambda spreadsheet_id, gid: [
            {
                "PERSONEL ADI": "Ali Veli",
                "KULLANICI ADI": "ali.veli",
                "DEPARTMAN": "Operasyon",
                "POZISYON": "Takım Lideri",
                "TELEFON": "05551234567",
            }
        ],
    )

    response = client.post("/api/personnel/sync-docs", headers=admin_token_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["updated"] == 1
    assert payload["created"] == 0

    db.refresh(existing)
    assert existing.department == "Operasyon"
    assert existing.position == "Takım Lideri"
    assert existing.phone == "05551234567"