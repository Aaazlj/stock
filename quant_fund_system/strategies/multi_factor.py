"""多因子策略。"""
import pandas as pd


def run_multi_factor_strategy(scored_df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """按综合分数排序选股。"""
    return scored_df.sort_values("score", ascending=False).head(top_n)
