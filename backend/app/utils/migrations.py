import logging

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text

from ..database import engine

logger = logging.getLogger(__name__)


def ensure_schema_version():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if "users" in tables and "alembic_version" not in tables:
        with engine.begin() as connection:
            connection.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY)"))
            connection.execute(text("INSERT INTO alembic_version (version_num) VALUES (:version)"), {"version": "20260515_baseline_schema"})


def upgrade_database():
    if engine.url.get_backend_name() == "sqlite":
        return
    ensure_schema_version()
    config = Config("alembic.ini")
    command.upgrade(config, "head")