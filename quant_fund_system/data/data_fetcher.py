"""数据抓取模块（AkShare + 本地缓存）。"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

try:
    import akshare as ak
except Exception:  # pragma: no cover
    ak = None


class DataFetcher:
    """负责从 AkShare 拉取并缓存数据。"""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, name: str) -> Path:
        return self.cache_dir / f"{name}.csv"

    def _read_cache(self, name: str) -> Optional[pd.DataFrame]:
        p = self._cache_path(name)
        if p.exists():
            return pd.read_csv(p, parse_dates=True)
        return None

    def _write_cache(self, name: str, df: pd.DataFrame) -> None:
        self._cache_path(name).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(self._cache_path(name), index=False)

    def get_stock_list(self, force_refresh: bool = False) -> pd.DataFrame:
        """获取 A 股股票列表。"""
        cache_key = "stock_list"
        if not force_refresh:
            cached = self._read_cache(cache_key)
            if cached is not None:
                return cached

        if ak is None:
            # 离线兜底样例
            df = pd.DataFrame(
                {
                    "code": ["000001", "000002", "600000"],
                    "name": ["平安银行", "万科A", "浦发银行"],
                    "industry": ["银行", "房地产", "银行"],
                }
            )
        else:
            spot = ak.stock_zh_a_spot_em()
            cols = {"代码": "code", "名称": "name", "行业": "industry"}
            df = spot[list(cols.keys())].rename(columns=cols)

        self._write_cache(cache_key, df)
        return df

    def get_price_history(self, symbol: str, start_date: str = "20180101", end_date: str = "20991231") -> pd.DataFrame:
        """获取日线行情。"""
        cache_key = f"price_{symbol}"
        cached = self._read_cache(cache_key)

        if ak is None:
            if cached is not None:
                return cached
            dates = pd.bdate_range("2022-01-01", periods=300)
            base = 10 + pd.Series(range(len(dates))).mul(0.01)
            df = pd.DataFrame(
                {
                    "date": dates,
                    "code": symbol,
                    "open": base,
                    "high": base * 1.01,
                    "low": base * 0.99,
                    "close": base * (1 + ((pd.Series(range(len(dates))) % 7) - 3) / 100),
                    "volume": 1_000_000,
                }
            )
            self._write_cache(cache_key, df)
            return df

        remote = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
        cols = {
            "日期": "date",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "成交量": "volume",
        }
        df = remote[list(cols.keys())].rename(columns=cols)
        df["date"] = pd.to_datetime(df["date"])
        df["code"] = symbol

        if cached is not None and not cached.empty:
            merged = pd.concat([cached, df], ignore_index=True).drop_duplicates(subset=["date", "code"]).sort_values("date")
            self._write_cache(cache_key, merged)
            return merged

        self._write_cache(cache_key, df)
        return df

    def get_financial_data(self, symbol: str) -> pd.DataFrame:
        """获取财务数据（简化版）。"""
        cache_key = f"financial_{symbol}"
        cached = self._read_cache(cache_key)
        if cached is not None:
            return cached

        if ak is None:
            df = pd.DataFrame(
                {
                    "code": [symbol],
                    "roe": [0.12],
                    "roa": [0.05],
                    "pe": [12.0],
                    "pb": [1.4],
                    "ps": [2.0],
                    "revenue_growth": [0.18],
                }
            )
        else:
            indicator = ak.stock_financial_analysis_indicator(symbol=symbol)
            indicator = indicator.sort_values(indicator.columns[0]).tail(1)
            df = pd.DataFrame(
                {
                    "code": [symbol],
                    "roe": [float(indicator.get("净资产收益率(%)", pd.Series([0])).iloc[0]) / 100],
                    "roa": [float(indicator.get("总资产净利润率(%)", pd.Series([0])).iloc[0]) / 100],
                    "pe": [float(indicator.get("市盈率", pd.Series([0])).iloc[0])],
                    "pb": [float(indicator.get("市净率", pd.Series([0])).iloc[0])],
                    "ps": [float(indicator.get("市销率", pd.Series([0])).iloc[0])],
                    "revenue_growth": [float(indicator.get("主营业务收入增长率(%)", pd.Series([0])).iloc[0]) / 100],
                }
            )

        self._write_cache(cache_key, df)
        return df

    def get_market_cap(self, symbol: str) -> float:
        """获取市值。"""
        stock_list = self.get_stock_list()
        if ak is None:
            return float(5e9)
        spot = ak.stock_zh_a_spot_em()
        row = spot.loc[spot["代码"] == symbol]
        if row.empty:
            return float(0)
        return float(row["总市值"].iloc[0])
