from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from ..database import Base


class DocsLink(Base):
    __tablename__ = "docs_links"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False, index=True)
    label = Column(String, nullable=False)
    url = Column(String, nullable=False)
    spreadsheet_id = Column(String, nullable=False)
    gid = Column(String, nullable=False, default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())