"""小市值策略。"""
import pandas as pd


def run_small_cap_strategy(universe: pd.DataFrame, top_n: int = 30) -> pd.DataFrame:
    """过滤 ST/停牌后按市值最小选择股票。"""
    df = universe.copy()
    if "name" in df.columns:
        df = df[~df["name"].str.contains("ST", na=False)]
    if "suspended" in df.columns:
        df = df[df["suspended"] == 0]
    return df.sort_values("market_cap", ascending=True).head(top_n)
