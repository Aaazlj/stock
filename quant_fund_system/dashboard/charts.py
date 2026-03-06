"""Plotly 可视化。"""
from __future__ import annotations

import pandas as pd
import plotly.express as px


def equity_curve_chart(equity: pd.Series):
    df = equity.reset_index()
    df.columns = ["date", "equity"]
    return px.line(df, x="date", y="equity", title="收益曲线")


def drawdown_chart(drawdown: pd.Series):
    df = drawdown.reset_index()
    df.columns = ["date", "drawdown"]
    return px.area(df, x="date", y="drawdown", title="回撤曲线")


def factor_distribution(df: pd.DataFrame, col: str):
    return px.histogram(df, x=col, nbins=30, title=f"{col} 分布")


def holdings_pie(positions: dict[str, float]):
    p = pd.DataFrame({"code": list(positions.keys()), "weight": list(positions.values())})
    return px.pie(p, names="code", values="weight", title="持仓结构")
