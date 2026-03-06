"""全局配置。"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data_cache"
DATA_DIR.mkdir(exist_ok=True)

DB_URL = "sqlite:///quant_fund.db"
STARTING_CASH = 1_000_000.0
MAX_SINGLE_WEIGHT = 0.10
MAX_INDUSTRY_WEIGHT = 0.30
TRADING_DAYS_PER_YEAR = 252
