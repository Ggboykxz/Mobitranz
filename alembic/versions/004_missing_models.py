# Notifications, Zones, Raspberry Pi Units
# Fichier : alembic/versions/004_missing_models.py

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("data", sa.Text, nullable=True),
        sa.Column("notification_type", sa.String(50), nullable=False),
        sa.Column(
            "sent_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_read", sa.Boolean, default=False, nullable=False),
        sa.Column("fcm_message_id", sa.String(200), nullable=True),
        sa.Column("error", sa.Text, nullable=True),
    )

    op.create_table(
        "zones",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("base_price", sa.Numeric(10, 0), nullable=False),
        sa.Column("keywords", sa.String(500), nullable=False),
        sa.Column("lat_min", sa.Numeric(10, 7), nullable=True),
        sa.Column("lat_max", sa.Numeric(10, 7), nullable=True),
        sa.Column("lon_min", sa.Numeric(10, 7), nullable=True),
        sa.Column("lon_max", sa.Numeric(10, 7), nullable=True),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("priority", sa.Integer, default=0),
    )

    op.create_table(
        "raspberry_pi_units",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("serial_number", sa.String(100), unique=True, nullable=False, index=True),
        sa.Column("vehicle_id", sa.String(36), nullable=True, index=True),
        sa.Column(
            "status",
            sa.Enum(
                "pending", "active", "offline", "error", "maintenance",
                name="raspberrypistatus",
            ),
            nullable=False,
        ),
        sa.Column("firmware_version", sa.String(20), nullable=True),
        sa.Column("last_heartbeat", sa.DateTime, nullable=True),
        sa.Column("camera_enabled", sa.Boolean, default=False),
        sa.Column("camera_device_id", sa.String(100), nullable=True),
        sa.Column("microphone_enabled", sa.Boolean, default=False),
        sa.Column("gps_enabled", sa.Boolean, default=False),
        sa.Column("encryption_key_encrypted", sa.String(500), nullable=True),
        sa.Column("tamper_detected", sa.Boolean, default=False),
        sa.Column("tamper_detected_at", sa.DateTime, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_table("raspberry_pi_units")
    op.execute("DROP TYPE IF EXISTS raspberrypistatus")
    op.drop_table("zones")
    op.drop_table("notifications")
