from sqlalchemy import Column, String, DateTime, BigInteger, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.core.database import Base


class PlayKidWallet(Base):
    """Ví học/chơi của bé — quỹ điểm giải trí + số dư từng loại game."""

    __tablename__ = "play_kid_wallets"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    available_balance = Column(BigInteger, server_default="0", nullable=False)
    accounts_json = Column(JSONB, server_default="{}", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PlayWalletLedgerEntry(Base):
    """Sổ cái append-only — mỗi dòng ghi nhận một bút toán."""

    __tablename__ = "play_wallet_ledger"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    account_code = Column(String(32), nullable=False, index=True)
    entry_type = Column(String(8), nullable=False)  # credit | debit
    amount = Column(BigInteger, nullable=False)
    balance_after = Column(BigInteger, nullable=False)
    ref_game_id = Column(String(32), nullable=True)
    ref_session_id = Column(UUID(as_uuid=True), ForeignKey("play_sessions.id"), nullable=True)
    ref_reward_game_id = Column(String(32), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
