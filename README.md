# quant_fund_system

A股量化研究与交易系统（工程化示例），包含：
- 数据管理（AkShare + 缓存 + 增量入库）
- 因子研究（价值/质量/动量/风险、IC、分层）
- 策略（小市值、动量、多因子）
- 回测（backtrader）
- 组合优化（等权、风险平价、Markowitz）
- 模拟交易与风控
- FastAPI接口与Plotly可视化

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m quant_fund_system.main
```

启动后访问：
- `GET /stocks`
- `GET /portfolio`
- `GET /strategies`
- `GET /backtest`

## 示例策略执行

```python
from quant_fund_system.data.data_fetcher import DataFetcher
from quant_fund_system.config import DATA_DIR
from quant_fund_system.factor_engine.factor_calculator import FactorCalculator
from quant_fund_system.strategies.momentum import run_momentum_strategy

fetcher = DataFetcher(DATA_DIR)
code = fetcher.get_stock_list().iloc[0]["code"]
price = fetcher.get_price_history(code)
f = FactorCalculator.compute_momentum(price)
latest = f.sort_values("date").groupby("code").tail(1)
print(run_momentum_strategy(latest, top_n=1))
```

## 示例回测

```python
from quant_fund_system.backtest_engine.engine import BacktestEngine
from quant_fund_system.data.data_fetcher import DataFetcher
from quant_fund_system.config import DATA_DIR

fetcher = DataFetcher(DATA_DIR)
code = fetcher.get_stock_list().iloc[0]["code"]
price = fetcher.get_price_history(code)
res = BacktestEngine().run(price)
print(res)
```
