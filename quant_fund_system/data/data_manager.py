"""数据管理流程：更新 + 落库。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from quant_fund_system.data.data_fetcher import DataFetcher
from quant_fund_system.database.db import get_session
from quant_fund_system.database.models import DailyPrice, Financial, Stock


@dataclass
class DataManager:
    fetcher: DataFetcher

    def update_stock_universe(self) -> pd.DataFrame:
        """更新股票基础信息。"""
        df = self.fetcher.get_stock_list()
        with get_session() as session:
            for _, row in df.iterrows():
                obj = session.get(Stock, row["code"])
                if obj is None:
                    session.add(Stock(code=row["code"], name=row["name"], industry=row.get("industry", "未知")))
                else:
                    obj.name = row["name"]
                    obj.industry = row.get("industry", "未知")
            session.commit()
        return df

    def update_prices(self, symbols: Iterable[str]) -> None:
        """增量更新价格数据。"""
        with get_session() as session:
            for code in symbols:
                df = self.fetcher.get_price_history(code)
                for _, row in df.iterrows():
                    exists = (
                        session.query(DailyPrice)
                        .filter(DailyPrice.code == code, DailyPrice.date == pd.to_datetime(row["date"]).date())
                        .first()
                    )
                    if exists:
                        continue
                    session.add(
                        DailyPrice(
                            date=pd.to_datetime(row["date"]).date(),
                            code=code,
                            open=float(row["open"]),
                            high=float(row["high"]),
                            low=float(row["low"]),
                            close=float(row["close"]),
                            volume=float(row["volume"]),
                        )
                    )
            session.commit()

    def update_financials(self, symbols: Iterable[str]) -> None:
        """更新财务指标。"""
        with get_session() as session:
            for code in symbols:
                df = self.fetcher.get_financial_data(code)
                row = df.iloc[-1]
                exists = session.query(Financial).filter(Financial.code == code).first()
                payload = {
                    "code": code,
                    "roe": float(row.get("roe", 0.0)),
                    "roa": float(row.get("roa", 0.0)),
                    "pe": float(row.get("pe", 0.0)),
                    "pb": float(row.get("pb", 0.0)),
                    "ps": float(row.get("ps", 0.0)),
                    "revenue_growth": float(row.get("revenue_growth", 0.0)),
                    "market_cap": float(self.fetcher.get_market_cap(code)),
                }
                if exists is None:
                    session.add(Financial(**payload))
                else:
                    for k, v in payload.items():
                        setattr(exists, k, v)
            session.commit()

    def update_all(self, sample_size: int = 50) -> None:
        """每日更新流程入口。"""
        stocks = self.update_stock_universe().head(sample_size)
        symbols = stocks["code"].tolist()
        self.update_prices(symbols)
        self.update_financials(symbols)
