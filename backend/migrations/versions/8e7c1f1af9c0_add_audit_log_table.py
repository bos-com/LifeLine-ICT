"""Add audit_logs table supporting activity tracking.

Revision ID: 8e7c1f1af9c0
Revises: 55dd87c04a97
Create Date: 2025-10-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8e7c1f1af9c0"
down_revision: Union[str, Sequence[str], None] = "55dd87c04a97"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the audit_logs table and supporting indexes."""

    action_enum = sa.Enum(
        "create",
        "update",
        "delete",
        "access",
        "status_change",
        "attachment",
        name="audit_action",
    )
    actor_enum = sa.Enum(
        "user",
        "system",
        "service",
        "admin",
        name="audit_actor_type",
    )
    entity_enum = sa.Enum(
        "project",
        "resource",
        "maintenance_ticket",
        "document",
        "location",
        "sensor_site",
        "notification",
        "user",
        "alert",
        name="audit_entity_type",
    )

    action_enum.create(op.get_bind(), checkfirst=True)
    actor_enum.create(op.get_bind(), checkfirst=True)
    entity_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("action", action_enum, nullable=False),
        sa.Column("entity_type", entity_enum, nullable=False),
        sa.Column("entity_id", sa.String(length=100), nullable=False),
        sa.Column("entity_name", sa.String(length=255), nullable=True),
        sa.Column("actor_type", actor_enum, nullable=False, server_default="system"),
        sa.Column("actor_id", sa.String(length=100), nullable=True),
        sa.Column("actor_name", sa.String(length=255), nullable=True),
        sa.Column("summary", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("context", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
    )

    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])
    op.create_index("ix_audit_logs_entity", "audit_logs", ["entity_type", "entity_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])


def downgrade() -> None:
    """Drop the audit_logs table."""

    op.drop_index("ix_audit_logs_action", table_name="audit_logs")
    op.drop_index("ix_audit_logs_entity", table_name="audit_logs")
    op.drop_index("ix_audit_logs_created_at", table_name="audit_logs")
    op.drop_table("audit_logs")

    action_enum = sa.Enum(name="audit_action")
    actor_enum = sa.Enum(name="audit_actor_type")
    entity_enum = sa.Enum(name="audit_entity_type")

    action_enum.drop(op.get_bind(), checkfirst=True)
    actor_enum.drop(op.get_bind(), checkfirst=True)
    entity_enum.drop(op.get_bind(), checkfirst=True)
