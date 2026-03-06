"""FastAPI 服务。"""
from __future__ import annotations

from fastapi import FastAPI

from quant_fund_system.config import DATA_DIR
from quant_fund_system.data.data_fetcher import DataFetcher
from quant_fund_system.data.data_manager import DataManager
from quant_fund_system.paper_trading.simulator import PaperTrader
from quant_fund_system.scheduler.scheduler import DailyScheduler
from quant_fund_system.database.db import engine
from quant_fund_system.database.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="A股量化研究与交易系统")

fetcher = DataFetcher(DATA_DIR)
manager = DataManager(fetcher)
trader = PaperTrader()
scheduler = DailyScheduler(manager, trader)


@app.get("/stocks")
def stocks():
    return fetcher.get_stock_list().head(100).to_dict(orient="records")


@app.get("/portfolio")
def portfolio():
    return trader.account.__dict__


@app.get("/strategies")
def strategies():
    result = scheduler.run()
    return result


@app.get("/backtest")
def backtest():
    code = fetcher.get_stock_list().iloc[0]["code"]
    prices = fetcher.get_price_history(code)
    from quant_fund_system.backtest_engine.engine import BacktestEngine

    bt = BacktestEngine().run(prices)
    return {
        "total_return": bt.total_return,
        "annual_return": bt.annual_return,
        "max_drawdown": bt.max_drawdown,
        "sharpe": bt.sharpe,
        "calmar": bt.calmar,
    }
