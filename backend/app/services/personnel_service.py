from sqlalchemy.orm import Session

from ..models import Personnel


TRANSLATION_TABLE = str.maketrans(
    "\u00e7\u00c7\u011f\u011e\u0131\u0130\u00f6\u00d6\u015f\u015e\u00fc\u00dc",
    "cCgGiIoOsSuU",
)


class PersonnelService:
    @staticmethod
    def normalize_text(value: str) -> str:
        return (value or "").strip().translate(TRANSLATION_TABLE)

    @staticmethod
    def normalize_personnel_name(value: str) -> str:
        return PersonnelService.normalize_text(value).lower()

    @staticmethod
    def normalize_cell_value(value: str) -> str:
        return PersonnelService.normalize_text(value).upper()

    @staticmethod
    def get_personnel_or_404(db: Session, personnel_id: int) -> Personnel:
        personnel = db.query(Personnel).filter(Personnel.id == personnel_id).first()
        if not personnel:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Personnel not found")
        return personnel

    @staticmethod
    def resolve_personnel(db: Session, personnel_name: str, include_username: bool = False):
        cleaned_name = (personnel_name or "").strip()
        if not cleaned_name:
            return None

        exact_match = db.query(Personnel).filter(Personnel.name.ilike(cleaned_name)).first()
        if exact_match:
            return exact_match

        if include_username:
            username_match = db.query(Personnel).filter(Personnel.username.ilike(cleaned_name)).first()
            if username_match:
                return username_match

        normalized_target = PersonnelService.normalize_personnel_name(cleaned_name)
        query = db.query(Personnel).order_by(Personnel.id.asc()).yield_per(200)
        for personnel in query:
            if PersonnelService.normalize_personnel_name(personnel.name) == normalized_target:
                return personnel
        return None

    @staticmethod
    def iter_personnel(db: Session, chunk_size: int = 200):
        return db.query(Personnel).order_by(Personnel.id.asc()).yield_per(chunk_size)
