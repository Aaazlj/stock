"""动量策略。"""
import pandas as pd


def run_momentum_strategy(latest_factors: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """按60日收益排序选股。"""
    return latest_factors.sort_values("mom_60", ascending=False).head(top_n)
