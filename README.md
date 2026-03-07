# quant_fund_system

A股量化研究与交易系统（工程化示例），包含：
- 数据管理（AkShare + 缓存 + 增量入库）
- 因子研究（价值/质量/动量/风险、IC、分层）
- 策略（小市值、动量、多因子）
- 回测（backtrader）
- 组合优化（等权、风险平价、Markowitz）
- 模拟交易与风控
- FastAPI接口与Plotly可视化
- AI日报/因子分析/风险告警（OpenAI兼容接口）

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m quant_fund_system.main
```

启动后访问：
- `GET /`（Vue可视化看板）
- `GET /stocks`
- `GET /portfolio`
- `GET /strategies`
- `GET /backtest`

AI相关接口：
- `POST /ai/report/daily`
- `POST /ai/analyze/factor`
- `POST /ai/alert/risk`

## Docker Compose 启动

1. 复制环境变量模板：

```bash
cp .env.example .env
```

2. 按需修改 `.env`。

3. 构建并启动：

```bash
docker compose up --build -d
```

4. 查看日志：

```bash
docker compose logs -f
```

5. 停止服务：

```bash
docker compose down
```

默认会映射 `8000` 端口，并将宿主机 `./data` 挂载到容器 `/app/data` 用于持久化缓存和数据库。

## 环境变量配置说明

支持通过环境变量覆盖默认配置：

| 变量名 | 默认值 | 说明 |
| --- | --- | --- |
| `QFS_DATA_DIR` | `quant_fund_system/data_cache` | 数据缓存目录 |
| `QFS_DB_URL` | `sqlite:///quant_fund.db` | SQLAlchemy 数据库连接串 |
| `QFS_STARTING_CASH` | `1000000` | 初始资金 |
| `QFS_MAX_SINGLE_WEIGHT` | `0.10` | 单只股票最大仓位 |
| `QFS_MAX_INDUSTRY_WEIGHT` | `0.30` | 单行业最大仓位 |
| `QFS_TRADING_DAYS_PER_YEAR` | `252` | 年化交易日数量 |
| `OPENAI_API_KEY` | 空 | OpenAI/兼容服务 API Key |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | OpenAI 兼容接口地址 |
| `OPENAI_MODEL` | `gpt-4o-mini` | 调用模型名称 |

> 建议使用 `.env` 管理本地配置（示例见 `.env.example`），避免将敏感信息直接写入代码。

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
