"""基于 backtrader 的回测引擎。"""
from __future__ import annotations

import math
from dataclasses import dataclass

import pandas as pd

try:
    import backtrader as bt
except Exception:  # pragma: no cover
    bt = None

from quant_fund_system.config import TRADING_DAYS_PER_YEAR


class BuyHoldStrategy(bt.Strategy if bt else object):
    """示例策略：首日买入并持有。"""

    def __init__(self):
        self.ordered = False

    def next(self):
        if not self.ordered:
            size = int(self.broker.getcash() / self.data.close[0])
            if size > 0:
                self.buy(size=size)
                self.ordered = True


@dataclass
class BacktestResult:
    total_return: float
    annual_return: float
    max_drawdown: float
    sharpe: float
    calmar: float
    equity_curve: pd.Series
    drawdown_curve: pd.Series


class BacktestEngine:
    """回测引擎封装。"""

    def run(self, price_df: pd.DataFrame, cash: float = 1_000_000.0) -> BacktestResult:
        if bt is None:
            raise ImportError("backtrader 未安装")

        data = price_df.copy().sort_values("date")
        data = data.rename(columns=str.lower)
        data["openinterest"] = 0
        data = data.set_index("date")[["open", "high", "low", "close", "volume", "openinterest"]]

        cerebro = bt.Cerebro(stdstats=False)
        feed = bt.feeds.PandasData(dataname=data)
        cerebro.adddata(feed)
        cerebro.addstrategy(BuyHoldStrategy)
        cerebro.broker.setcash(cash)
        cerebro.addanalyzer(bt.analyzers.TimeReturn, _name="timereturn")
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
        cerebro.run()

        rets = cerebro.runstrats[0][0].analyzers.timereturn.get_analysis()
        equity_curve = pd.Series(rets)
        cum = (1 + equity_curve).cumprod()
        total_return = float(cum.iloc[-1] - 1) if not cum.empty else 0.0
        annual_return = float((1 + total_return) ** (TRADING_DAYS_PER_YEAR / max(len(cum), 1)) - 1)

        running_max = cum.cummax()
        dd = cum / running_max - 1
        max_dd = float(dd.min()) if not dd.empty else 0.0

        daily = equity_curve.dropna()
        sharpe = float((daily.mean() / (daily.std() + 1e-8)) * math.sqrt(TRADING_DAYS_PER_YEAR)) if not daily.empty else 0.0
        calmar = float(annual_return / abs(max_dd)) if max_dd < 0 else 0.0

        return BacktestResult(total_return, annual_return, max_dd, sharpe, calmar, cum, dd)
