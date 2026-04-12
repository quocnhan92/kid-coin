import sys
import os
from datetime import date, timedelta
from unittest.mock import MagicMock, patch
from uuid import uuid4

# Base path
BASE_DIR = os.getcwd()
sys.path.append(BASE_DIR)

# Mock DB and models before imports
mock_db = MagicMock()
sys.modules["app.core.database"] = MagicMock()

from app.models.gamification import UserLevel, UserStreak, AvatarItem, UserAvatarItem, ItemType
from app.models.user_family import User, Role
from app.services import gamification_service, streak_service

def test_level_logic():
    print("\n--- Testing Level Logic ---")
    db = MagicMock()
    user = User(total_earned_score=150) # Level 2 candidate
    
    # Mock UserLevel data
    lvl1 = UserLevel(level=1, name="Level 1", min_xp=0)
    lvl2 = UserLevel(level=2, name="Level 2", min_xp=100)
    lvl3 = UserLevel(level=3, name="Level 3", min_xp=300)
    
    # Configure mock for get_level_info
    # Inside get_level_info:
    # 1. current_level = db.query(UserLevel).filter(UserLevel.min_xp <= xp).order_by(UserLevel.level.desc()).first()
    # 2. next_level = db.query(UserLevel).filter(UserLevel.level > current_level.level).order_by(UserLevel.level.asc()).first()
    
    mock_query = db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_order = mock_filter.order_by.return_value
    mock_order.first.side_effect = [lvl2, lvl3] 
    
    info = gamification_service.get_level_info(db, user)
    print(f"User XP: 150 -> Level: {info['current_level']} ({info['level_name']})")
    assert info['current_level'] == 2
    assert info['xp_to_next_level'] == 150
    assert info['progress_percentage'] == 25.0
    print("✅ Level logic test passed.")

def test_streak_logic():
    print("\n--- Testing Streak Logic ---")
    db = MagicMock()
    user_id = str(uuid4())
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    mock_query = db.query.return_value
    mock_filter = mock_query.filter.return_value
    
    # 1. New streak
    mock_filter.first.return_value = None
    streak = streak_service.update_streak(db, user_id)
    assert streak.current_streak == 1
    
    # 2. Consecutive day
    existing_streak = UserStreak(user_id=user_id, current_streak=1, last_active_date=yesterday)
    mock_filter.first.return_value = existing_streak
    streak = streak_service.update_streak(db, user_id)
    assert streak.current_streak == 2
    
    # 3. Same day
    existing_streak.last_active_date = today
    streak = streak_service.update_streak(db, user_id)
    assert streak.current_streak == 2
    
    # 4. Broken streak
    long_ago = today - timedelta(days=5)
    existing_streak.last_active_date = long_ago
    streak = streak_service.update_streak(db, user_id)
    assert streak.current_streak == 1
    
    print("✅ Streak logic test passed.")

if __name__ == "__main__":
    try:
        test_level_logic()
        test_streak_logic()
        print("\n🎉 ALL PHASE 2 LOGIC TESTS PASSED!")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
