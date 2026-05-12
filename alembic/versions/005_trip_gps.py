# Trip GPS Points
# Fichier : alembic/versions/005_trip_gps.py

from alembic import op
import sqlalchemy as sa


revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "trip_gps_points",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("trip_id", sa.String(36), sa.ForeignKey("trips.id"), nullable=False, index=True),
        sa.Column("latitude", sa.Float, nullable=False),
        sa.Column("longitude", sa.Float, nullable=False),
        sa.Column("altitude", sa.Float, nullable=True),
        sa.Column("speed_kmh", sa.Float, nullable=True),
        sa.Column("heading", sa.Float, nullable=True),
        sa.Column("accuracy_meters", sa.Float, nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade():
    op.drop_table("trip_gps_points")
