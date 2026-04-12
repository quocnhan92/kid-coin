"""initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # 1. Create PostgreSQL Enum types (10 total)
    # -------------------------------------------------------------------------
    role_enum = postgresql.ENUM(
        'PARENT', 'KID',
        name='role', create_type=False
    )
    role_enum.create(op.get_bind(), checkfirst=True)

    category_enum = postgresql.ENUM(
        'Học tập', 'Việc nhà', 'Giải trí', 'Xã hội', 'Cá nhân', 'Kiếm tiền', 'Khác',
        name='category', create_type=False
    )
    category_enum.create(op.get_bind(), checkfirst=True)

    verificationtype_enum = postgresql.ENUM(
        'Tự động duyệt', 'Cần chụp ảnh', 'Bố mẹ kiểm tra trực tiếp',
        name='verificationtype', create_type=False
    )
    verificationtype_enum.create(op.get_bind(), checkfirst=True)

    taskstatus_enum = postgresql.ENUM(
        'PENDING_APPROVAL', 'APPROVED', 'REJECTED',
        name='taskstatus', create_type=False
    )
    taskstatus_enum.create(op.get_bind(), checkfirst=True)

    redemptionstatus_enum = postgresql.ENUM(
        'PENDING_DELIVERY', 'DELIVERED',
        name='redemptionstatus', create_type=False
    )
    redemptionstatus_enum.create(op.get_bind(), checkfirst=True)

    transactiontype_enum = postgresql.ENUM(
        'TASK_COMPLETION', 'REWARD_REDEMPTION', 'PENALTY', 'BONUS',
        name='transactiontype', create_type=False
    )
    transactiontype_enum.create(op.get_bind(), checkfirst=True)

    clubrole_enum = postgresql.ENUM(
        'ADMIN', 'MEMBER',
        name='clubrole', create_type=False
    )
    clubrole_enum.create(op.get_bind(), checkfirst=True)

    invitationstatus_enum = postgresql.ENUM(
        'PENDING', 'ACCEPTED', 'REJECTED',
        name='invitationstatus', create_type=False
    )
    invitationstatus_enum.create(op.get_bind(), checkfirst=True)

    notificationtype_enum = postgresql.ENUM(
        'SYSTEM', 'CLUB_INVITE', 'KID_CLUB_INVITE', 'TASK_ASSIGNED',
        name='notificationtype', create_type=False
    )
    notificationtype_enum.create(op.get_bind(), checkfirst=True)

    auditstatus_enum = postgresql.ENUM(
        'INIT', 'PROCESSING', 'SUCCESS', 'FAILED',
        name='auditstatus', create_type=False
    )
    auditstatus_enum.create(op.get_bind(), checkfirst=True)

    # -------------------------------------------------------------------------
    # 2. Create tables in dependency order
    # -------------------------------------------------------------------------

    # 2.1 families (no FK dependencies)
    op.create_table(
        'families',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('address', sa.String(255), nullable=True),
        sa.Column('extra_info', sa.String(500), nullable=True),
        sa.Column('parent_pin', sa.String(60), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_family_name', 'families', ['name'])

    # 2.2 master_tasks (no FK dependencies)
    op.create_table(
        'master_tasks',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('icon_url', sa.String(255), nullable=True),
        sa.Column('suggested_value', sa.BigInteger(), server_default='10'),
        sa.Column('min_age', sa.Integer(), server_default='3'),
        sa.Column('max_age', sa.Integer(), server_default='18'),
        sa.Column('category', sa.Enum('Học tập', 'Việc nhà', 'Giải trí', 'Xã hội', 'Cá nhân', 'Kiếm tiền', 'Khác', name='category', create_type=False, create_constraint=False), nullable=False),
        sa.Column('verification_type', sa.Enum('Tự động duyệt', 'Cần chụp ảnh', 'Bố mẹ kiểm tra trực tiếp', name='verificationtype', create_type=False, create_constraint=False), server_default='Cần chụp ảnh'),
    )
    op.create_index('idx_master_task_category', 'master_tasks', ['category'])

    # 2.3 master_rewards (no FK dependencies)
    op.create_table(
        'master_rewards',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('icon_url', sa.String(255), nullable=True),
        sa.Column('suggested_cost', sa.BigInteger(), server_default='50'),
        sa.Column('min_age', sa.Integer(), server_default='3'),
        sa.Column('max_age', sa.Integer(), server_default='18'),
    )

    # 2.4 users (FK → families)
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('families.id'), nullable=False, index=True),
        sa.Column('role', sa.Enum('PARENT', 'KID', name='role', create_type=False, create_constraint=False), nullable=False),
        sa.Column('username', sa.String(100), unique=True, nullable=True),
        sa.Column('display_name', sa.String(50), nullable=False),
        sa.Column('avatar_url', sa.String(255), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('current_coin', sa.BigInteger(), server_default='0'),
        sa.Column('total_earned_score', sa.BigInteger(), server_default='0'),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_user_family_role', 'users', ['family_id', 'role'])
    op.create_index('idx_user_username', 'users', ['username'])

    # 2.5 family_tasks (FK → families, master_tasks)
    op.create_table(
        'family_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('families.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('master_task_id', sa.Integer(), sa.ForeignKey('master_tasks.id', ondelete='SET NULL'), nullable=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('points_reward', sa.BigInteger(), nullable=False),
        sa.Column('category', sa.Enum('Học tập', 'Việc nhà', 'Giải trí', 'Xã hội', 'Cá nhân', 'Kiếm tiền', 'Khác', name='category', create_type=False, create_constraint=False), server_default='Khác'),
        sa.Column('verification_type', sa.Enum('Tự động duyệt', 'Cần chụp ảnh', 'Bố mẹ kiểm tra trực tiếp', name='verificationtype', create_type=False, create_constraint=False), server_default='Cần chụp ảnh'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_family_task_name', 'family_tasks', ['name'])
    op.create_index('idx_family_task_is_active', 'family_tasks', ['is_active'])

    # 2.6 family_rewards (FK → families, master_rewards)
    op.create_table(
        'family_rewards',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('families.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('master_reward_id', sa.Integer(), sa.ForeignKey('master_rewards.id', ondelete='SET NULL'), nullable=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('points_cost', sa.BigInteger(), nullable=False),
        sa.Column('stock_limit', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_family_reward_name', 'family_rewards', ['name'])
    op.create_index('idx_family_reward_is_active', 'family_rewards', ['is_active'])

    # 2.7 clubs (FK → families)
    op.create_table(
        'clubs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('creator_family_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('families.id'), nullable=False, index=True),
        sa.Column('invite_code', sa.String(20), unique=True, nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_club_name', 'clubs', ['name'])
    op.create_index('idx_club_invite_code', 'clubs', ['invite_code'])

    # 2.8 club_members (FK → clubs, users — both CASCADE)
    op.create_table(
        'club_members',
        sa.Column('club_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('clubs.id', ondelete='CASCADE'), primary_key=True, index=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True, index=True),
        sa.Column('role', sa.Enum('ADMIN', 'MEMBER', name='clubrole', create_type=False, create_constraint=False), server_default='MEMBER', nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )

    # 2.9 club_invitations (FK → clubs CASCADE, users CASCADE/SET NULL)
    op.create_table(
        'club_invitations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('club_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('clubs.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('invited_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('inviter_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'ACCEPTED', 'REJECTED', name='invitationstatus', create_type=False, create_constraint=False), server_default='PENDING', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('club_id', 'invited_user_id', 'status', name='uq_club_user_status'),
    )

    # 2.10 club_tasks (FK → clubs, families)
    op.create_table(
        'club_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('club_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('clubs.id'), nullable=False),
        sa.Column('creator_family_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('families.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('points_reward', sa.BigInteger(), nullable=False),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_club_task_club_id', 'club_tasks', ['club_id'])
    op.create_index('idx_club_task_is_active', 'club_tasks', ['is_active'])

    # 2.11 task_logs (FK → users, family_tasks SET NULL, club_tasks SET NULL + CheckConstraint)
    op.create_table(
        'task_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('kid_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('family_task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('family_tasks.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('club_task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('club_tasks.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('status', sa.Enum('PENDING_APPROVAL', 'APPROVED', 'REJECTED', name='taskstatus', create_type=False, create_constraint=False), server_default='PENDING_APPROVAL'),
        sa.Column('proof_image_url', sa.String(255), nullable=True),
        sa.Column('parent_comment', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint('num_nonnulls(family_task_id, club_task_id) = 1', name='chk_one_task_source'),
    )
    op.create_index('idx_task_log_status', 'task_logs', ['status'])
    op.create_index('idx_task_log_created_at', 'task_logs', ['created_at'])

    # 2.12 redemption_logs (FK → users, family_rewards)
    op.create_table(
        'redemption_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('kid_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('reward_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('family_rewards.id'), nullable=False, index=True),
        sa.Column('status', sa.Enum('PENDING_DELIVERY', 'DELIVERED', name='redemptionstatus', create_type=False, create_constraint=False), server_default='PENDING_DELIVERY'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_redemption_log_status', 'redemption_logs', ['status'])
    op.create_index('idx_redemption_log_created_at', 'redemption_logs', ['created_at'])

    # 2.13 transactions (FK → users)
    op.create_table(
        'transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('kid_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('amount', sa.BigInteger(), nullable=False),
        sa.Column('transaction_type', sa.Enum('TASK_COMPLETION', 'REWARD_REDEMPTION', 'PENALTY', 'BONUS', name='transactiontype', create_type=False, create_constraint=False), nullable=False),
        sa.Column('reference_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_transaction_type', 'transactions', ['transaction_type'])
    op.create_index('idx_transaction_created_at', 'transactions', ['created_at'])

    # 2.14 family_devices (FK → families)
    op.create_table(
        'family_devices',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('families.id'), nullable=False),
        sa.Column('device_name', sa.String(100), nullable=False),
        sa.Column('device_token', sa.String(255), unique=True, nullable=False),
        sa.Column('initial_ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('device_info', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_default', sa.Boolean(), server_default='false'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('last_active_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_device_family_id', 'family_devices', ['family_id'])
    op.create_index('idx_device_token', 'family_devices', ['device_token'])

    # 2.15 notifications (FK → users CASCADE)
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('type', sa.Enum('SYSTEM', 'CLUB_INVITE', 'KID_CLUB_INVITE', 'TASK_ASSIGNED', name='notificationtype', create_type=False, create_constraint=False), server_default='SYSTEM', nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.String(1000), nullable=True),
        sa.Column('reference_id', sa.String(36), nullable=True),
        sa.Column('action_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_read', sa.Boolean(), server_default='false', index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), index=True),
    )

    # 2.16 audit_logs (FK → users nullable, no ondelete)
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True, index=True),
        sa.Column('action', sa.String(100), nullable=False, index=True),
        sa.Column('status', sa.Enum('INIT', 'PROCESSING', 'SUCCESS', 'FAILED', name='auditstatus', create_type=False, create_constraint=False), server_default='INIT', nullable=False, index=True),
        sa.Column('resource_type', sa.String(50), nullable=False, index=True),
        sa.Column('resource_id', sa.String(36), nullable=True, index=True),
        sa.Column('request_id', sa.String(50), nullable=True, index=True),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('device_info', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), index=True),
    )


def downgrade() -> None:
    # Drop tables in reverse dependency order
    op.drop_table('audit_logs')
    op.drop_table('notifications')
    op.drop_table('family_devices')
    op.drop_table('transactions')
    op.drop_table('redemption_logs')
    op.drop_table('task_logs')
    op.drop_table('club_tasks')
    op.drop_table('club_invitations')
    op.drop_table('club_members')
    op.drop_table('clubs')
    op.drop_table('family_rewards')
    op.drop_table('family_tasks')
    op.drop_table('users')
    op.drop_table('master_rewards')
    op.drop_table('master_tasks')
    op.drop_table('families')

    # Drop all enum types
    postgresql.ENUM(name='auditstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='notificationtype').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='invitationstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='clubrole').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='transactiontype').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='redemptionstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='taskstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='verificationtype').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='category').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='role').drop(op.get_bind(), checkfirst=True)
