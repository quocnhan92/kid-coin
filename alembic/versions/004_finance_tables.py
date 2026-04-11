"""finance tables

Revision ID: 004
Revises: 003
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # 1. Create PostgreSQL Enum types
    # -------------------------------------------------------------------------
    goalstatus_enum = postgresql.ENUM(
        'ACTIVE', 'COMPLETED', 'CANCELLED',
        name='goalstatus', create_type=False
    )
    goalstatus_enum.create(op.get_bind(), checkfirst=True)

    savingsstatus_enum = postgresql.ENUM(
        'ACTIVE', 'MATURED', 'WITHDRAWN',
        name='savingsstatus', create_type=False
    )
    savingsstatus_enum.create(op.get_bind(), checkfirst=True)

    loanstatus_enum = postgresql.ENUM(
        'ACTIVE', 'REPAID', 'OVERDUE',
        name='loanstatus', create_type=False
    )
    loanstatus_enum.create(op.get_bind(), checkfirst=True)

    # -------------------------------------------------------------------------
    # 2. Create tables
    # -------------------------------------------------------------------------

    # saving_goals (FK → users)
    op.create_table(
        'saving_goals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('kid_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('target_amount', sa.BigInteger(), nullable=False),
        sa.Column('current_amount', sa.BigInteger(), server_default='0'),
        sa.Column('icon_url', sa.String(255), nullable=True),
        sa.Column('deadline', sa.Date(), nullable=True),
        sa.Column('status', postgresql.ENUM('ACTIVE', 'COMPLETED', 'CANCELLED', name='goalstatus', create_type=False), server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint('current_amount >= 0', name='chk_saving_goal_current_amount_non_negative'),
        sa.CheckConstraint('target_amount > 0', name='chk_saving_goal_target_amount_positive'),
    )

    # savings_accounts (FK → users)
    op.create_table(
        'savings_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('kid_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('principal', sa.BigInteger(), nullable=False),
        sa.Column('interest_rate', sa.Numeric(5, 2), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('early_withdraw_penalty', sa.Numeric(5, 2), server_default='50.00'),
        sa.Column('status', postgresql.ENUM('ACTIVE', 'MATURED', 'WITHDRAWN', name='savingsstatus', create_type=False), server_default='ACTIVE'),
        sa.Column('matured_amount', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.CheckConstraint('principal > 0', name='chk_savings_account_principal_positive'),
    )

    # loan_accounts (FK → users, families, users for approved_by)
    op.create_table(
        'loan_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('kid_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('families.id'), nullable=False),
        sa.Column('loan_amount', sa.BigInteger(), nullable=False),
        sa.Column('interest_rate', sa.Numeric(5, 2), server_default='10.00'),
        sa.Column('total_owed', sa.BigInteger(), nullable=False),
        sa.Column('repaid_amount', sa.BigInteger(), server_default='0'),
        sa.Column('status', postgresql.ENUM('ACTIVE', 'REPAID', 'OVERDUE', name='loanstatus', create_type=False), server_default='ACTIVE'),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.CheckConstraint('repaid_amount <= total_owed', name='chk_loan_repaid_lte_total_owed'),
        sa.CheckConstraint('loan_amount > 0', name='chk_loan_amount_positive'),
    )

    # charity_fund (FK → families, UNIQUE on family_id)
    op.create_table(
        'charity_fund',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('families.id'), unique=True, nullable=False),
        sa.Column('balance', sa.BigInteger(), server_default='0'),
        sa.Column('total_donated', sa.BigInteger(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.CheckConstraint('balance >= 0', name='chk_charity_fund_balance_non_negative'),
    )

    # charity_donations (FK → charity_fund, users)
    op.create_table(
        'charity_donations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('fund_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('charity_fund.id'), nullable=False, index=True),
        sa.Column('donor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('amount', sa.BigInteger(), nullable=False),
        sa.Column('message', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.CheckConstraint('amount > 0', name='chk_charity_donation_amount_positive'),
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('charity_donations')
    op.drop_table('charity_fund')
    op.drop_table('loan_accounts')
    op.drop_table('savings_accounts')
    op.drop_table('saving_goals')

    # Drop enum types
    postgresql.ENUM(name='loanstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='savingsstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='goalstatus').drop(op.get_bind(), checkfirst=True)
