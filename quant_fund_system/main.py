"""系统启动入口。"""
from __future__ import annotations

from quant_fund_system.config import DATA_DIR
from quant_fund_system.data.data_fetcher import DataFetcher
from quant_fund_system.data.data_manager import DataManager
from quant_fund_system.database.db import engine
from quant_fund_system.database.models import Base


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def bootstrap_data() -> None:
    manager = DataManager(DataFetcher(DATA_DIR))
    manager.update_all(sample_size=10)


if __name__ == "__main__":
    import uvicorn

    init_db()
    bootstrap_data()
    uvicorn.run("quant_fund_system.api.main:app", host="0.0.0.0", port=8000, reload=False)
