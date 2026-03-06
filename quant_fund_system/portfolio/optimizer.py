"""组合优化模块。"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from quant_fund_system.config import MAX_INDUSTRY_WEIGHT, MAX_SINGLE_WEIGHT


class PortfolioOptimizer:
    """支持等权、风险平价、均值方差。"""

    @staticmethod
    def equal_weight(codes: list[str]) -> pd.Series:
        w = np.repeat(1 / len(codes), len(codes))
        return pd.Series(w, index=codes, name="weight")

    @staticmethod
    def risk_parity(returns: pd.DataFrame) -> pd.Series:
        cov = returns.cov().values
        n = cov.shape[0]

        def obj(w):
            port_var = w @ cov @ w
            mrc = cov @ w
            rc = w * mrc / np.sqrt(port_var + 1e-12)
            return ((rc - rc.mean()) ** 2).sum()

        cons = ({"type": "eq", "fun": lambda w: np.sum(w) - 1},)
        bounds = [(0, MAX_SINGLE_WEIGHT) for _ in range(n)]
        x0 = np.repeat(1 / n, n)
        res = minimize(obj, x0, method="SLSQP", bounds=bounds, constraints=cons)
        return pd.Series(res.x, index=returns.columns, name="weight")

    @staticmethod
    def markowitz(returns: pd.DataFrame, industry_map: dict[str, str] | None = None) -> pd.Series:
        mu = returns.mean().values
        cov = returns.cov().values
        n = len(mu)

        def obj(w):
            # 最大化夏普（无风险利率近似0）-> 最小化负值
            ret = w @ mu
            vol = np.sqrt(w @ cov @ w + 1e-12)
            return -ret / vol

        cons = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]

        if industry_map:
            industries = sorted(set(industry_map.values()))
            for ind in industries:
                idx = [i for i, c in enumerate(returns.columns) if industry_map.get(c) == ind]
                cons.append({"type": "ineq", "fun": lambda w, idx=idx: MAX_INDUSTRY_WEIGHT - np.sum(w[idx])})

        bounds = [(0, MAX_SINGLE_WEIGHT) for _ in range(n)]
        x0 = np.repeat(1 / n, n)
        res = minimize(obj, x0, method="SLSQP", bounds=bounds, constraints=cons)
        return pd.Series(res.x, index=returns.columns, name="weight")
