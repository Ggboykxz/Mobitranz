# ============================================================
# Alembic Migration: Database Indexes
# Fichier : alembic/versions/003_indexes.py
# Description : Ajout indexes performance
# ============================================================

from alembic import op


revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_users_status ON users(status)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)")
    
    op.execute("CREATE INDEX IF NOT EXISTS idx_drivers_status ON drivers(status)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_drivers_available ON drivers(is_available)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_drivers_on_trip ON drivers(is_on_trip)")
    
    op.execute("CREATE INDEX IF NOT EXISTS idx_vehicles_qr ON vehicles(qr_code)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_vehicles_active ON vehicles(is_active)")
    
    op.execute("CREATE INDEX IF NOT EXISTS idx_trips_driver ON trips(driver_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_trips_status ON trips(status)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_trips_created ON trips(created_at)")
    
    op.execute("CREATE INDEX IF NOT EXISTS idx_payments_trip ON payments(trip_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_payments_method ON payments(method)")
    
    op.execute("CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_incidents_type ON incidents(incident_type)")
    
    op.execute("CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read)")
    
    op.execute("CREATE INDEX IF NOT EXISTS idx_voice_proposals_trip ON voice_proposals(trip_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_voice_proposals_validated ON voice_proposals(is_validated)")


def downgrade():
    op.execute("DROP INDEX IF NOT EXISTS idx_users_phone")
    op.execute("DROP INDEX IF NOT EXISTS idx_users_status")
    op.execute("DROP INDEX IF NOT EXISTS idx_users_role")
    
    op.execute("DROP INDEX IF NOT EXISTS idx_drivers_status")
    op.execute("DROP INDEX IF NOT EXISTS idx_drivers_available")
    op.execute("DROP INDEX IF NOT EXISTS idx_drivers_on_trip")
    
    op.execute("DROP INDEX IF NOT EXISTS idx_vehicles_qr")
    op.execute("DROP INDEX IF NOT EXISTS idx_vehicles_active")
    
    op.execute("DROP INDEX IF NOT EXISTS idx_trips_driver")
    op.execute("DROP INDEX IF NOT EXISTS idx_trips_status")
    op.execute("DROP INDEX IF NOT EXISTS idx_trips_created")
    
    op.execute("DROP INDEX IF NOT EXISTS idx_payments_trip")
    op.execute("DROP INDEX IF NOT EXISTS idx_payments_status")
    op.execute("DROP INDEX IF NOT EXISTS idx_payments_method")
    
    op.execute("DROP INDEX IF NOT EXISTS idx_incidents_status")
    op.execute("DROP INDEX IF NOT EXISTS idx_incidents_type")
    
    op.execute("DROP INDEX IF NOT EXISTS idx_notifications_user")
    op.execute("DROP INDEX IF NOT EXISTS idx_notifications_is_read")
    
    op.execute("DROP INDEX IF NOT EXISTS idx_voice_proposals_trip")
    op.execute("DROP INDEX IF NOT EXISTS idx_voice_proposals_validated")