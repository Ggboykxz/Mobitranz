# A generic, single revision migration.
# ============================================================
# Revision ID: initial
# Revises: 
# Create Date: 2026-04-24
# ============================================================
from alembic import op
import sqlalchemy as sa

revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create all tables
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('phone', sa.String(20), unique=True, nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('client', 'driver', 'admin', 'ministry', name='userrole'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'active', 'suspended', 'deleted', name='userstatus'), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=True),
        sa.Column('birth_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('kyc_verified', sa.Boolean, default=False),
        sa.Column('kyc_documents', sa.String(500), nullable=True),
        sa.Column('biometric_hash', sa.String(255), nullable=True),
        sa.Column('totp_secret', sa.String(32), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer, default=0),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
    )
    
    op.create_table(
        'drivers',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'validated', 'suspended', 'inactive', name='driverstatus'), nullable=False),
        sa.Column('kyc_verified', sa.Boolean, default=False),
        sa.Column('kyc_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('license_number', sa.String(50), nullable=True),
        sa.Column('license_expiry', sa.DateTime(timezone=True), nullable=True),
        sa.Column('permit_number', sa.String(50), nullable=True),
        sa.Column('permit_expiry', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id_card_number', sa.String(50), nullable=True),
        sa.Column('vehicle_id', sa.String(36), nullable=True),
        sa.Column('current_lat', sa.Float, nullable=True),
        sa.Column('current_lon', sa.Float, nullable=True),
        sa.Column('last_location_update', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_available', sa.Boolean, default=False),
        sa.Column('is_on_trip', sa.Boolean, default=False),
        sa.Column('total_trips', sa.Integer, default=0),
        sa.Column('rating', sa.Float, default=5.0),
        sa.Column('total_earnings', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
    )
    
    op.create_table(
        'vehicles',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('plate_number', sa.String(20), unique=True, nullable=False),
        sa.Column('brand', sa.String(50), nullable=False),
        sa.Column('model', sa.String(50), nullable=False),
        sa.Column('year', sa.Integer, nullable=True),
        sa.Column('color', sa.String(30), nullable=True),
        sa.Column('qr_code', sa.String(255), nullable=True),
        sa.Column('qr_code_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('camera_enabled', sa.Boolean, default=False),
        sa.Column('camera_device_id', sa.String(100), nullable=True),
        sa.Column('camera_encryption_key', sa.String(255), nullable=True),
        sa.Column('total_seats', sa.Integer, default=4, nullable=False),
        sa.Column('available_seats', sa.Integer, default=4, nullable=False),
        sa.Column('status', sa.Enum('pending', 'active', 'maintenance', 'inactive', name='vehiclestatus'), nullable=False),
        sa.Column('driver_id', sa.String(36), nullable=True),
        sa.Column('current_lat', sa.String(20), nullable=True),
        sa.Column('current_lon', sa.String(20), nullable=True),
        sa.Column('last_update', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
    )


def downgrade():
    op.drop_table('vehicles')
    op.drop_table('drivers')
    op.drop_table('users')