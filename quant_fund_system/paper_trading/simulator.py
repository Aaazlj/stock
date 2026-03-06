"""模拟交易系统。"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PaperAccount:
    cash: float
    positions: dict[str, int] = field(default_factory=dict)
    total_value: float = 0.0


class PaperTrader:
    """支持买入/卖出/调仓。"""

    def __init__(self, starting_cash: float = 1_000_000):
        self.account = PaperAccount(cash=starting_cash, total_value=starting_cash)
        self.order_log: list[dict] = []

    def buy(self, code: str, price: float, size: int) -> None:
        cost = price * size
        if cost > self.account.cash:
            return
        self.account.cash -= cost
        self.account.positions[code] = self.account.positions.get(code, 0) + size
        self.order_log.append({"side": "buy", "code": code, "price": price, "size": size})

    def sell(self, code: str, price: float, size: int) -> None:
        pos = self.account.positions.get(code, 0)
        if pos < size:
            return
        self.account.positions[code] = pos - size
        if self.account.positions[code] == 0:
            del self.account.positions[code]
        self.account.cash += price * size
        self.order_log.append({"side": "sell", "code": code, "price": price, "size": size})

    def rebalance(self, target_weights: dict[str, float], latest_prices: dict[str, float]) -> None:
        self.update_total_value(latest_prices)
        target_values = {k: self.account.total_value * w for k, w in target_weights.items()}

        # 先卖
        for code, pos in list(self.account.positions.items()):
            tgt = target_values.get(code, 0.0)
            cur = pos * latest_prices.get(code, 0.0)
            if cur > tgt:
                sell_size = int((cur - tgt) / latest_prices[code])
                if sell_size > 0:
                    self.sell(code, latest_prices[code], min(sell_size, pos))

        # 再买
        for code, tgt in target_values.items():
            price = latest_prices[code]
            cur = self.account.positions.get(code, 0) * price
            if tgt > cur:
                buy_size = int((tgt - cur) / price)
                if buy_size > 0:
                    self.buy(code, price, buy_size)

        self.update_total_value(latest_prices)

    def update_total_value(self, latest_prices: dict[str, float]) -> float:
        holdings = sum(latest_prices.get(c, 0.0) * s for c, s in self.account.positions.items())
        self.account.total_value = self.account.cash + holdings
        return self.account.total_value
