"""baseline schema

Revision ID: 20260515_baseline_schema
Revises:
Create Date: 2026-05-15
"""

from alembic import op
import sqlalchemy as sa


revision = "20260515_baseline_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("role", sa.String(), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "personnel",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("employee_id", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("hire_date", sa.Date(), nullable=True),
        sa.Column("reference", sa.String(), nullable=True),
        sa.Column("department", sa.String(), nullable=True),
        sa.Column("position", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("promotion_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_personnel_id", "personnel", ["id"])
    op.create_index("ix_personnel_name", "personnel", ["name"])
    op.create_index("ix_personnel_employee_id", "personnel", ["employee_id"], unique=True)
    op.create_index("ix_personnel_username", "personnel", ["username"], unique=True)
    op.create_unique_constraint("uq_personnel_email", "personnel", ["email"])

    op.create_table(
        "docs_links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("spreadsheet_id", sa.String(), nullable=False),
        sa.Column("gid", sa.String(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_docs_links_id", "docs_links", ["id"])
    op.create_index("ix_docs_links_key", "docs_links", ["key"], unique=True)

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("replaced_by_token_id", sa.Integer(), sa.ForeignKey("refresh_tokens.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_refresh_tokens_id", "refresh_tokens", ["id"])
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"], unique=True)

    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("entity_type", sa.String(), nullable=False),
        sa.Column("entity_id", sa.String(), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_audit_log_id", "audit_log", ["id"])
    op.create_index("ix_audit_log_actor_user_id", "audit_log", ["actor_user_id"])
    op.create_index("ix_audit_log_action", "audit_log", ["action"])
    op.create_index("ix_audit_log_entity_type", "audit_log", ["entity_type"])
    op.create_index("ix_audit_log_created_at", "audit_log", ["created_at"])
    op.create_index("ix_audit_log_entity_lookup", "audit_log", ["entity_type", "entity_id"])

    op.create_table(
        "sales_data",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("personnel_id", sa.Integer(), sa.ForeignKey("personnel.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sales_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("uploaded_date", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("sales_count >= 0 AND sales_count <= 10000", name="sales_count_range"),
        sa.UniqueConstraint("personnel_id", "date", name="unique_personnel_sales_date"),
    )
    op.create_index("ix_sales_data_id", "sales_data", ["id"])
    op.create_index("ix_sales_data_personnel_id", "sales_data", ["personnel_id"])
    op.create_index("ix_sales_data_date", "sales_data", ["date"])

    op.create_table(
        "attendance_data",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("personnel_id", sa.Integer(), sa.ForeignKey("personnel.id", ondelete="CASCADE"), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("working_days", sa.Float(), server_default="0"),
        sa.Column("leave_days", sa.Float(), server_default="0"),
        sa.Column("leave_type", sa.String(), nullable=True),
        sa.Column("salary_amount", sa.Float(), nullable=True),
        sa.Column("docs_sync_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("month >= 1 AND month <= 12", name="attendance_month_range"),
        sa.CheckConstraint("working_days >= 0 AND working_days <= 31", name="attendance_working_days_range"),
        sa.CheckConstraint("leave_days >= 0 AND leave_days <= 31", name="attendance_leave_days_range"),
        sa.CheckConstraint("salary_amount IS NULL OR salary_amount >= 0", name="attendance_salary_non_negative"),
        sa.UniqueConstraint("personnel_id", "month", "year", name="unique_personnel_month_year"),
    )
    op.create_index("ix_attendance_data_id", "attendance_data", ["id"])
    op.create_index("ix_attendance_data_personnel_id", "attendance_data", ["personnel_id"])
    op.create_index("idx_personnel_month_year", "attendance_data", ["personnel_id", "month", "year"])

    op.create_table(
        "warning_data",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("personnel_id", sa.Integer(), sa.ForeignKey("personnel.id", ondelete="CASCADE"), nullable=False),
        sa.Column("deduction", sa.String(), nullable=True),
        sa.Column("subject", sa.String(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("docs_id", sa.String(), nullable=True),
        sa.Column("docs_sync_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_warning_data_id", "warning_data", ["id"])
    op.create_index("ix_warning_data_personnel_id", "warning_data", ["personnel_id"])
    op.create_index("ix_warning_data_date", "warning_data", ["date"])
    op.create_index("idx_warning_personnel_date", "warning_data", ["personnel_id", "date"])

    op.create_table(
        "training_data",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("personnel_id", sa.Integer(), sa.ForeignKey("personnel.id", ondelete="CASCADE"), nullable=False),
        sa.Column("subject", sa.String(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("trainer", sa.String(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("end_time > start_time", name="training_end_after_start"),
    )
    op.create_index("ix_training_data_id", "training_data", ["id"])
    op.create_index("ix_training_data_personnel_id", "training_data", ["personnel_id"])
    op.create_index("ix_training_data_date", "training_data", ["date"])
    op.create_index("idx_training_personnel_date", "training_data", ["personnel_id", "date"])

    op.create_table(
        "call_monitoring",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("personnel_id", sa.Integer(), sa.ForeignKey("personnel.id", ondelete="CASCADE"), nullable=False),
        sa.Column("phone_number", sa.String(), nullable=False),
        sa.Column("quality_score", sa.Float(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("quality_score >= 0 AND quality_score <= 100", name="call_monitoring_quality_score_range"),
    )
    op.create_index("ix_call_monitoring_id", "call_monitoring", ["id"])
    op.create_index("ix_call_monitoring_personnel_id", "call_monitoring", ["personnel_id"])
    op.create_index("ix_call_monitoring_date", "call_monitoring", ["date"])
    op.create_index("idx_call_monitoring_personnel_date", "call_monitoring", ["personnel_id", "date"])

    op.create_table(
        "whatsapp_data",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("personnel_id", sa.Integer(), sa.ForeignKey("personnel.id", ondelete="CASCADE"), nullable=False),
        sa.Column("whatsapp_count", sa.Integer(), server_default="0"),
        sa.Column("device_count", sa.Integer(), server_default="0"),
        sa.Column("average_unanswered_count", sa.Integer(), server_default="0"),
        sa.Column("unanswered_count", sa.Integer(), server_default="0"),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("docs_sync_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("whatsapp_count >= 0", name="whatsapp_count_non_negative"),
        sa.CheckConstraint("device_count >= 0", name="whatsapp_device_count_non_negative"),
        sa.CheckConstraint("average_unanswered_count >= 0", name="whatsapp_average_unanswered_non_negative"),
        sa.CheckConstraint("unanswered_count >= 0", name="whatsapp_unanswered_non_negative"),
        sa.UniqueConstraint("personnel_id", "date", name="unique_personnel_whatsapp_date"),
    )
    op.create_index("ix_whatsapp_data_id", "whatsapp_data", ["id"])
    op.create_index("ix_whatsapp_data_personnel_id", "whatsapp_data", ["personnel_id"])
    op.create_index("ix_whatsapp_data_date", "whatsapp_data", ["date"])
    op.create_index("idx_whatsapp_personnel_date", "whatsapp_data", ["personnel_id", "date"])

    op.create_table(
        "call_process_data",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("personnel_id", sa.Integer(), sa.ForeignKey("personnel.id", ondelete="CASCADE"), nullable=False),
        sa.Column("call_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("talk_duration", sa.Float(), nullable=False, server_default="0"),
        sa.Column("average_ring_duration", sa.Float(), nullable=False, server_default="0"),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("uploaded_date", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("call_count >= 0", name="call_process_count_non_negative"),
        sa.CheckConstraint("talk_duration >= 0", name="call_process_talk_non_negative"),
        sa.CheckConstraint("average_ring_duration >= 0", name="call_process_ring_non_negative"),
        sa.UniqueConstraint("personnel_id", "date", name="unique_personnel_call_process_date"),
    )
    op.create_index("ix_call_process_data_id", "call_process_data", ["id"])
    op.create_index("ix_call_process_data_personnel_id", "call_process_data", ["personnel_id"])
    op.create_index("ix_call_process_data_date", "call_process_data", ["date"])


def downgrade():
    for table_name in (
        "call_process_data",
        "whatsapp_data",
        "call_monitoring",
        "training_data",
        "warning_data",
        "attendance_data",
        "sales_data",
        "audit_log",
        "refresh_tokens",
        "docs_links",
        "personnel",
        "users",
    ):
        op.drop_table(table_name)