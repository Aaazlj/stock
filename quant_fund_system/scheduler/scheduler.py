"""每日调度流程。"""
from __future__ import annotations

from quant_fund_system.data.data_manager import DataManager
from quant_fund_system.factor_engine.factor_calculator import FactorCalculator
from quant_fund_system.paper_trading.simulator import PaperTrader
from quant_fund_system.strategies.multi_factor import run_multi_factor_strategy


class DailyScheduler:
    """串联更新、计算、选股、模拟交易。"""

    def __init__(self, data_manager: DataManager, trader: PaperTrader):
        self.data_manager = data_manager
        self.trader = trader

    def run(self) -> dict:
        self.data_manager.update_all(sample_size=30)

        # 这里为了简化演示，直接从 fetcher cache 读取
        stocks = self.data_manager.fetcher.get_stock_list().head(30)
        snapshots = []
        latest_prices = {}

        for code in stocks["code"]:
            price = self.data_manager.fetcher.get_price_history(code)
            fin = self.data_manager.fetcher.get_financial_data(code).iloc[-1].to_dict()
            enriched = price[["date", "code", "close"]].copy()
            for k, v in fin.items():
                if k != "code":
                    enriched[k] = v
            enriched["market_cap"] = self.data_manager.fetcher.get_market_cap(code)
            snapshots.append(enriched)
            latest_prices[code] = float(price.iloc[-1]["close"])

        all_df = FactorCalculator.compute_momentum(
            __import__("pandas").concat(snapshots, ignore_index=True).rename(columns={"close": "close"})
        )
        latest = all_df.sort_values("date").groupby("code").tail(1)
        scored = FactorCalculator.combine_factors(latest)
        picks = run_multi_factor_strategy(scored, top_n=20)

        weight = 1 / len(picks)
        target = {c: weight for c in picks["code"].tolist()}
        self.trader.rebalance(target, latest_prices)

        return {"picked": picks["code"].tolist(), "account": self.trader.account.__dict__}
