"""全局配置。"""
from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"环境变量 {name} 必须是浮点数，当前值: {value}") from exc


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"环境变量 {name} 必须是整数，当前值: {value}") from exc


DATA_DIR = Path(os.getenv("QFS_DATA_DIR", str(BASE_DIR / "data_cache"))).resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_URL = os.getenv("QFS_DB_URL", "sqlite:///quant_fund.db")
STARTING_CASH = _env_float("QFS_STARTING_CASH", 1_000_000.0)
MAX_SINGLE_WEIGHT = _env_float("QFS_MAX_SINGLE_WEIGHT", 0.10)
MAX_INDUSTRY_WEIGHT = _env_float("QFS_MAX_INDUSTRY_WEIGHT", 0.30)
TRADING_DAYS_PER_YEAR = _env_int("QFS_TRADING_DAYS_PER_YEAR", 252)
