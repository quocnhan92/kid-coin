"""teen tables

Revision ID: 007
Revises: 006
Create Date: 2026-04-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '007'
down_revision: Union[str, None] = '006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # 1. Create PostgreSQL Enum types
    # -------------------------------------------------------------------------
    periodtype_enum = postgresql.ENUM(
        'WEEKLY', 'MONTHLY',
        name='periodtype', create_type=True
    )
    periodtype_enum.create(op.get_bind(), checkfirst=True)

    contractstatus_enum = postgresql.ENUM(
        'DRAFT', 'ACTIVE', 'COMPLETED', 'BREACHED',
        name='contractstatus', create_type=True
    )
    contractstatus_enum.create(op.get_bind(), checkfirst=True)

    checkinstatus_enum = postgresql.ENUM(
        'PENDING', 'VERIFIED', 'MISSED',
        name='checkinstatus', create_type=True
    )
    checkinstatus_enum.create(op.get_bind(), checkfirst=True)

    projectstatus_enum = postgresql.ENUM(
        'ACTIVE', 'COMPLETED', 'PAUSED',
        name='projectstatus', create_type=True
    )
    projectstatus_enum.create(op.get_bind(), checkfirst=True)

    milestonestatus_enum = postgresql.ENUM(
        'PENDING', 'VERIFIED', 'REJECTED',
        name='milestonestatus', create_type=True
    )
    milestonestatus_enum.create(op.get_bind(), checkfirst=True)

    # -------------------------------------------------------------------------
    # 2. Create tables
    # -------------------------------------------------------------------------

    # teen_contracts
    op.create_table(
        'teen_contracts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('kid_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('families.id'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('period_type', postgresql.ENUM('WEEKLY', 'MONTHLY', name='periodtype', create_type=False), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('salary_coins', sa.BigInteger(), nullable=False),
        sa.Column('milestones', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', postgresql.ENUM('DRAFT', 'ACTIVE', 'COMPLETED', 'BREACHED', name='contractstatus', create_type=False), server_default='DRAFT'),
        sa.Column('signed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # contract_checkins
    op.create_table(
        'contract_checkins',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('contract_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('teen_contracts.id'), nullable=False, index=True),
        sa.Column('kid_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('checkin_date', sa.Date(), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('proof_url', sa.String(255), nullable=True),
        sa.Column('verified_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('status', postgresql.ENUM('PENDING', 'VERIFIED', 'MISSED', name='checkinstatus', create_type=False), server_default='PENDING'),
    )

    # personal_projects
    op.create_table(
        'personal_projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('kid_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('families.id'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('total_budget', sa.BigInteger(), nullable=False),
        sa.Column('milestones', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('status', postgresql.ENUM('ACTIVE', 'COMPLETED', 'PAUSED', name='projectstatus', create_type=False), server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # project_milestone_logs
    op.create_table(
        'project_milestone_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('personal_projects.id'), nullable=False, index=True),
        sa.Column('milestone_index', sa.Integer(), nullable=False),
        sa.Column('proof_url', sa.String(255), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('verified_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('coins_released', sa.BigInteger(), nullable=False),
        sa.Column('status', postgresql.ENUM('PENDING', 'VERIFIED', 'REJECTED', name='milestonestatus', create_type=False), server_default='PENDING'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('project_milestone_logs')
    op.drop_table('personal_projects')
    op.drop_table('contract_checkins')
    op.drop_table('teen_contracts')

    # Drop enum types
    postgresql.ENUM(name='milestonestatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='projectstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='checkinstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='contractstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='periodtype').drop(op.get_bind(), checkfirst=True)
