"""因子分析模块：IC + 分层回测。"""
from __future__ import annotations

import pandas as pd


class FactorAnalyzer:
    """评估因子有效性。"""

    @staticmethod
    def information_coefficient(df: pd.DataFrame, factor_col: str, future_ret_col: str) -> float:
        tmp = df[[factor_col, future_ret_col]].dropna()
        if tmp.empty:
            return 0.0
        return float(tmp[factor_col].corr(tmp[future_ret_col], method="spearman"))

    @staticmethod
    def quantile_backtest(df: pd.DataFrame, factor_col: str, future_ret_col: str, q: int = 5) -> pd.DataFrame:
        tmp = df[[factor_col, future_ret_col]].dropna().copy()
        tmp["bucket"] = pd.qcut(tmp[factor_col], q=q, labels=False, duplicates="drop")
        grouped = tmp.groupby("bucket")[future_ret_col].mean().reset_index()
        grouped.rename(columns={future_ret_col: "avg_future_ret"}, inplace=True)
        return grouped
