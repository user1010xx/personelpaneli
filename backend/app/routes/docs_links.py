from urllib.parse import parse_qs, urlparse

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import DocsLink
from ..schemas.docs_link import DocsLinkResponse, DocsLinkUpdate
from ..utils.auth import get_admin_user
from ..utils.db import safe_commit

router = APIRouter(prefix="/api/docs-links", tags=["Docs Links"])

DOCS_LINK_DEFINITIONS = {
    "personnel": {
        "label": "Personel Guncel Link",
        "url": settings.DEFAULT_PERSONNEL_SHEET_URL or (
            f"https://docs.google.com/spreadsheets/d/{settings.PERSONNEL_SHEET_ID}/edit?gid=0#gid=0"
            if settings.PERSONNEL_SHEET_ID else ""
        ),
    },
    "attendance": {
        "label": "Puantaj Guncel Link",
        "url": settings.DEFAULT_ATTENDANCE_SHEET_URL or (
            f"https://docs.google.com/spreadsheets/d/{settings.DOCS_PUANTAJ_ID}/edit?gid=0#gid=0"
            if settings.DOCS_PUANTAJ_ID else ""
        ),
    },
    "warnings": {
        "label": "Uyari Kesinti Guncel Link",
        "url": settings.DEFAULT_WARNINGS_SHEET_URL or (
            f"https://docs.google.com/spreadsheets/d/{settings.WARNINGS_SHEET_ID}/edit?gid=0#gid=0"
            if settings.WARNINGS_SHEET_ID else ""
        ),
    },
    "whatsapp": {
        "label": "Whatsapp Guncel Link",
        "url": settings.DEFAULT_WHATSAPP_SHEET_URL or (
            f"https://docs.google.com/spreadsheets/d/{settings.DOCS_WHATSAPP_ID}/edit?gid=0#gid=0"
            if settings.DOCS_WHATSAPP_ID else ""
        ),
    },
}


def parse_google_sheet_url(url: str):
    parsed = urlparse(url.strip())
    parts = [part for part in parsed.path.split("/") if part]
    try:
        spreadsheet_id = parts[parts.index("d") + 1]
    except (ValueError, IndexError):
        raise HTTPException(status_code=400, detail="Google Sheets link format is invalid")

    query = parse_qs(parsed.query)
    gid = query.get("gid", [None])[0]
    if not gid and parsed.fragment:
        fragment_query = parse_qs(parsed.fragment.replace("#", "").replace("gid=", "gid="))
        gid = fragment_query.get("gid", [None])[0]
        if not gid and "gid=" in parsed.fragment:
            gid = parsed.fragment.split("gid=")[-1]
    if not gid:
        gid = "0"
    return spreadsheet_id, str(gid)


def ensure_default_links(db: Session):
    for key, payload in DOCS_LINK_DEFINITIONS.items():
        existing = db.query(DocsLink).filter(DocsLink.key == key).first()
        if existing:
            if existing.label != payload["label"]:
                existing.label = payload["label"]
            continue
        spreadsheet_id = ""
        gid = "0"
        if payload["url"]:
            spreadsheet_id, gid = parse_google_sheet_url(payload["url"])
        db.add(DocsLink(
            key=key,
            label=payload["label"],
            url=payload["url"],
            spreadsheet_id=spreadsheet_id,
            gid=gid,
        ))
    safe_commit(db, message="Default docs links could not be initialized")


def get_docs_link_config(db: Session, key: str, require_configured: bool = True):
    ensure_default_links(db)
    docs_link = db.query(DocsLink).filter(DocsLink.key == key).first()
    if not docs_link:
        raise HTTPException(status_code=404, detail="Docs link not found")
    if require_configured and (not docs_link.url or not docs_link.spreadsheet_id):
        raise HTTPException(
            status_code=400,
            detail=f"{docs_link.label} kullanici yonetiminde kaydedilmemis",
        )
    return docs_link


@router.get("", response_model=list[DocsLinkResponse])
def list_docs_links(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    ensure_default_links(db)
    return db.query(DocsLink).order_by(DocsLink.id.asc()).all()


@router.put("/{key}", response_model=DocsLinkResponse)
def update_docs_link(
    key: str,
    docs_link_update: DocsLinkUpdate,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    docs_link = get_docs_link_config(db, key, require_configured=False)
    spreadsheet_id, gid = parse_google_sheet_url(docs_link_update.url)
    docs_link.url = docs_link_update.url.strip()
    docs_link.spreadsheet_id = spreadsheet_id
    docs_link.gid = gid
    safe_commit(db, message="Docs link could not be updated")
    db.refresh(docs_link)
    return docs_link