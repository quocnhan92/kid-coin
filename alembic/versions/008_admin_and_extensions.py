"""admin and extensions

Revision ID: 008
Revises: 007
Create Date: 2026-04-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '008'
down_revision: Union[str, None] = '007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # 1. Create Admin Tables
    # -------------------------------------------------------------------------
    adminrole_enum = postgresql.ENUM(
        'SUPER_ADMIN', 'MODERATOR', 'SUPPORT',
        name='adminrole', create_type=True
    )
    adminrole_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'admin_users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('username', sa.String(100), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(100), nullable=False),
        sa.Column('role', postgresql.ENUM('SUPER_ADMIN', 'MODERATOR', 'SUPPORT', name='adminrole', create_type=False), server_default='MODERATOR'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # -------------------------------------------------------------------------
    # 2. Extend Existing Tables
    # -------------------------------------------------------------------------
    
    # Extend users
    op.add_column('users', sa.Column('charity_rate', sa.Numeric(5, 2), server_default='5.00'))
    op.add_column('users', sa.Column('is_teen_mode', sa.Boolean(), server_default='false'))

    # Extend families
    op.add_column('families', sa.Column('charity_rate', sa.Numeric(5, 2), server_default='5.00'))
    op.add_column('families', sa.Column('is_suspended', sa.Boolean(), server_default='false'))

    # -------------------------------------------------------------------------
    # 3. Update TransactionType Enum
    # -------------------------------------------------------------------------
    # Adding new types to TransactionType enum
    # PostgreSQL doesn't support ALTER TYPE ADD VALUE in a transaction easily before PG12 
    # and Alembic requires some work. But we can use op.execute.
    new_types = [
        'AVATAR_PURCHASE', 'SAVINGS_DEPOSIT', 'SAVINGS_WITHDRAW', 
        'LOAN_RECEIVE', 'LOAN_REPAY', 'CHARITY_DONATE', 
        'STREAK_BONUS', 'BID_REWARD', 'PROBLEM_REWARD', 
        'REFLECTION_BONUS', 'CONTRACT_SALARY', 'PROJECT_MILESTONE',
        'ADMIN_ADJUSTMENT'
    ]
    for t in new_types:
        op.execute(f"ALTER TYPE transactiontype ADD VALUE IF NOT EXISTS '{t}'")


def downgrade() -> None:
    # Reversing enum updates is hard in PG (no DROP VALUE), so we usually leave the values.
    
    # Remove extensions
    op.drop_column('families', 'is_suspended')
    op.drop_column('families', 'charity_rate')
    op.drop_column('users', 'is_teen_mode')
    op.drop_column('users', 'charity_rate')

    # Drop admin tables
    op.drop_table('admin_users')

    # Drop enum
    postgresql.ENUM(name='adminrole').drop(op.get_bind(), checkfirst=True)
