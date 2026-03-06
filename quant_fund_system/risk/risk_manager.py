"""风控模块。"""
from __future__ import annotations

import pandas as pd


class RiskManager:
    def __init__(self, max_single_weight: float = 0.1, max_drawdown: float = -0.2, max_industry_weight: float = 0.3):
        self.max_single_weight = max_single_weight
        self.max_drawdown = max_drawdown
        self.max_industry_weight = max_industry_weight

    def check_position_limit(self, weights: pd.Series) -> bool:
        return bool((weights <= self.max_single_weight + 1e-8).all())

    def check_drawdown_limit(self, drawdown_series: pd.Series) -> bool:
        if drawdown_series.empty:
            return True
        return float(drawdown_series.min()) >= self.max_drawdown

    def check_industry_concentration(self, weights: pd.Series, industry_map: dict[str, str]) -> bool:
        grouped = {}
        for code, w in weights.items():
            grouped[industry_map.get(code, "未知")] = grouped.get(industry_map.get(code, "未知"), 0) + float(w)
        return all(v <= self.max_industry_weight + 1e-8 for v in grouped.values())
