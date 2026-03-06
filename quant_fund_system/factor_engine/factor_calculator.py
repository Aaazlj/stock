"""因子计算模块。"""
from __future__ import annotations

import numpy as np
import pandas as pd


class FactorCalculator:
    """计算常见横截面因子。"""

    @staticmethod
    def compute_momentum(price_df: pd.DataFrame) -> pd.DataFrame:
        df = price_df.sort_values(["code", "date"]).copy()
        for w in [20, 60, 120]:
            df[f"mom_{w}"] = df.groupby("code")["close"].pct_change(w)
        return df

    @staticmethod
    def compute_risk(price_df: pd.DataFrame) -> pd.DataFrame:
        df = price_df.sort_values(["code", "date"]).copy()
        ret = df.groupby("code")["close"].pct_change()
        df["volatility_20"] = ret.groupby(df["code"]).rolling(20).std().reset_index(level=0, drop=True)

        def rolling_max_drawdown(x: pd.Series) -> float:
            cummax = x.cummax()
            dd = x / cummax - 1
            return dd.min()

        df["max_drawdown_60"] = (
            df.groupby("code")["close"].rolling(60).apply(rolling_max_drawdown, raw=False).reset_index(level=0, drop=True)
        )
        return df

    @staticmethod
    def standardize_cross_section(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
        out = df.copy()
        for c in cols:
            s = out[c]
            out[c] = (s - s.mean()) / (s.std() + 1e-8)
        return out

    @staticmethod
    def combine_factors(latest_df: pd.DataFrame) -> pd.DataFrame:
        """组合多因子评分。"""
        needed = ["roe", "mom_60", "pe", "market_cap"]
        x = FactorCalculator.standardize_cross_section(latest_df, needed)
        x["score"] = 0.3 * x["roe"] + 0.3 * x["mom_60"] - 0.2 * x["pe"] - 0.2 * x["market_cap"]
        return x
