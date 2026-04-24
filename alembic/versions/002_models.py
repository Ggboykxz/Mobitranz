# Trips, Payments, Recordings, Voice Proposals, Incidents, Audit Logs
# Fichier : alembic/versions/002_models.py

from alembic import op
import sqlalchemy as sa


def upgrade():
    # Trips table
    op.create_table(
        'trips',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('driver_id', sa.String(36), sa.ForeignKey('drivers.id'), nullable=False),
        sa.Column('vehicle_id', sa.String(36), sa.ForeignKey('vehicles.id'), nullable=False),
        sa.Column('client_ids', sa.ARRAY(sa.String), nullable=False),
        sa.Column('origin_geo', sa.String(100), nullable=False),
        sa.Column('dest_geo', sa.String(100), nullable=True),
        sa.Column('origin_label', sa.String(200), nullable=False),
        sa.Column('dest_label', sa.String(200), nullable=False),
        sa.Column('amount', sa.Integer, nullable=False),
        sa.Column('seats_count', sa.Integer, default=1),
        sa.Column('status', sa.Enum('proposing', 'horn_pending', 'payment_pending', 'active', 'completed', 'cancelled', 'incident', name='tripstatus'), nullable=False),
        sa.Column('proposed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('horn_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('payment_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('qr_code_used', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
    )
    
    # Payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('trip_id', sa.String(36), sa.ForeignKey('trips.id'), nullable=False),
        sa.Column('client_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('amount', sa.Integer, nullable=False),
        sa.Column('currency', sa.String(3), default='XAF'),
        sa.Column('method', sa.Enum('moovmoney', 'airtelmoney', 'card', 'biometric', 'cash', name='paymentmethod'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', 'refunded', name='paymentstatus'), nullable=False),
        sa.Column('external_transaction_id', sa.String(255), nullable=True),
        sa.Column('provider_reference', sa.String(255), nullable=True),
        sa.Column('provider_response', sa.String(1000), nullable=True),
        sa.Column('phone_number', sa.String(20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failure_reason', sa.String(500), nullable=True),
    )
    
    # Recordings table
    op.create_table(
        'recordings',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('trip_id', sa.String(36), sa.ForeignKey('trips.id'), nullable=False),
        sa.Column('vehicle_id', sa.String(36), sa.ForeignKey('vehicles.id'), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('file_size', sa.Integer, nullable=True),
        sa.Column('duration_seconds', sa.Integer, nullable=True),
        sa.Column('encryption_key_id', sa.String(36), nullable=True),
        sa.Column('encryption_nonce', sa.String(50), nullable=True),
        sa.Column('is_encrypted', sa.String(10), default='false'),
        sa.Column('status', sa.Enum('recording', 'processing', 'ready', 'encrypted', 'deleted', name='recordingstatus'), nullable=False),
        sa.Column('mime_type', sa.String(50), default='video/mp4'),
        sa.Column('access_count', sa.Integer, default=0),
        sa.Column('last_access_by', sa.String(36), nullable=True),
        sa.Column('last_access_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Voice Proposals table
    op.create_table(
        'voice_proposals',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('trip_id', sa.String(36), sa.ForeignKey('trips.id'), nullable=False),
        sa.Column('client_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('audio_path', sa.String(500), nullable=True),
        sa.Column('audio_duration_seconds', sa.Integer, nullable=True),
        sa.Column('transcription', sa.String(2000), nullable=False),
        sa.Column('confidence_score', sa.Integer, nullable=True),
        sa.Column('extracted_destination', sa.String(200), nullable=True),
        sa.Column('extracted_amount', sa.Integer, nullable=True),
        sa.Column('extracted_seats', sa.Integer, nullable=True),
        sa.Column('is_validated', sa.String(10), default='false'),
        sa.Column('validated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('validation_source', sa.String(50), nullable=True),
        sa.Column('detected_language', sa.String(10), default='fr'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Incidents table
    op.create_table(
        'incidents',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('trip_id', sa.String(36), sa.ForeignKey('trips.id'), nullable=False),
        sa.Column('reporter_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('incident_type', sa.Enum('sos', 'accident', 'dispute', 'theft', 'harassment', 'other', name='incidenttype'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'acknowledged', 'escalated', 'resolved', 'closed', name='incidentstatus'), nullable=False),
        sa.Column('description', sa.String(2000), nullable=True),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('latitude', sa.String(20), nullable=True),
        sa.Column('longitude', sa.String(20), nullable=True),
        sa.Column('audio_path', sa.String(500), nullable=True),
        sa.Column('escalated_to', sa.String(200), nullable=True),
        sa.Column('escalated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('escalation_reason', sa.String(500), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution', sa.String(1000), nullable=True),
        sa.Column('resolved_by', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
    )
    
    # Audit Logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('action', sa.Enum('login', 'logout', 'payment_initiated', 'payment_completed', 'payment_failed', 'video_accessed', 'user_created', 'user_updated', 'user_suspended', 'driver_validated', 'driver_suspended', 'trip_created', 'trip_completed', 'trip_cancelled', 'incident_reported', 'incident_escalated', name='auditaction'), nullable=False),
        sa.Column('previous_hash', sa.String(64), nullable=False),
        sa.Column('current_hash', sa.String(64), nullable=False),
        sa.Column('details', sa.Text, nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade():
    op.drop_table('audit_logs')
    op.drop_table('incidents')
    op.drop_table('voice_proposals')
    op.drop_table('recordings')
    op.drop_table('payments')
    op.drop_table('trips')