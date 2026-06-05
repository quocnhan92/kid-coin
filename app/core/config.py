from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "KidCoin"
    DATABASE_URL: str = "postgresql://kidcoin_user:kidcoin_password@localhost:5432/kidcoin_db"
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Dev/test: unlock English City/Boss + all reward arcade games (set false in production)
    PLAY_TEST_UNLOCK_ALL: bool = True

    # Dev/test: skip coin debit when launching reward games (set false in production)
    PLAY_SKIP_REWARD_SPEND: bool = True

    # G1-first rollout: max grade exposed on hub (1–5)
    PLAY_MAX_GRADE: int = 1

    # Daily play cap per kid (minutes)
    PLAY_DAILY_SCREEN_MINUTES: int = 60

    # Default market when no cookie / path hint (vn | en | my | ph)
    DEFAULT_MARKET: str = "vn"

    class Config:
        env_file = ".env"

settings = Settings()
