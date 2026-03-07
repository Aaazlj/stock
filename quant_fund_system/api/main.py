"""FastAPI 服务。"""
from __future__ import annotations

from typing import Any
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from quant_fund_system.ai.service import AIService
from quant_fund_system.config import DATA_DIR
from quant_fund_system.data.data_fetcher import DataFetcher
from quant_fund_system.data.data_manager import DataManager
from quant_fund_system.paper_trading.simulator import PaperTrader
from quant_fund_system.scheduler.scheduler import DailyScheduler
from quant_fund_system.database.db import engine
from quant_fund_system.database.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="A股量化研究与交易系统")

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/frontend", StaticFiles(directory=frontend_dir), name="frontend")

fetcher = DataFetcher(DATA_DIR)
manager = DataManager(fetcher)
trader = PaperTrader()
scheduler = DailyScheduler(manager, trader)
ai_service = AIService()


class DailyReportRequest(BaseModel):
    portfolio: dict[str, Any] = Field(default_factory=dict)
    strategies: dict[str, Any] = Field(default_factory=dict)
    backtest: dict[str, Any] = Field(default_factory=dict)


class FactorAnalyzeRequest(BaseModel):
    factor_name: str
    ic: float | None = None
    quantile_returns: list[dict[str, Any]] = Field(default_factory=list)
    extra: dict[str, Any] = Field(default_factory=dict)


class RiskAlertRequest(BaseModel):
    account: dict[str, Any] = Field(default_factory=dict)
    constraints: dict[str, Any] = Field(default_factory=dict)
    breaches: list[str] = Field(default_factory=list)


@app.get("/stocks")
def stocks():
    return fetcher.get_stock_list().head(100).to_dict(orient="records")


@app.get("/stocks/summary")
def stocks_summary():
    stock_df = fetcher.get_stock_list().head(100)
    industry_counts = (
        stock_df["industry"].fillna("未知").value_counts().head(10).rename_axis("industry").reset_index(name="count")
    )
    return {
        "total": int(stock_df.shape[0]),
        "top_industries": industry_counts.to_dict(orient="records"),
    }


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


@app.post("/ai/report/daily")
def ai_daily_report(req: DailyReportRequest):
    report = ai_service.generate_daily_report(req.model_dump())
    return {"report": report}


@app.post("/ai/analyze/factor")
def ai_factor_report(req: FactorAnalyzeRequest):
    report = ai_service.analyze_factor(req.model_dump())
    return {"report": report}


@app.post("/ai/alert/risk")
def ai_risk_alert(req: RiskAlertRequest):
    report = ai_service.generate_risk_alert(req.model_dump())
    return {"report": report}


@app.get("/")
def index():
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Frontend not found", "hint": "请访问 API 文档 /docs"}
