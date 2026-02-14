# 每日自动化基金信息 + 股票信息采集系统

> 🚀 基于 Python 的金融数据自动化采集、分析与定投系统

## 📋 项目简介

本项目用于每日自动化采集中国 A 股市场、基金的行情数据，支持自动化定投策略执行。

## 🔧 核心功能

- [ ] 基金净值数据每日采集
- [ ] A 股行情数据采集
- [ ] 定投策略自动执行
- [ ] 数据可视化仪表板
- [ ] 消息推送通知

## 📊 数据源选型

### 推荐方案

| 数据源 | 类型 | 费用 | 适用场景 |
|--------|------|------|----------|
| **Tushare Pro** | Python SDK | ¥500/年起 | 生产环境主力 |
| **AKShare** | Python SDK | 免费 | 备用/开发 |
| **掘金量化** | API | 免费起 | 实盘交易 |

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                      数据采集层                               │
├─────────────────┬─────────────────┬─────────────────────────┤
│  实时行情采集   │   历史数据同步   │    基本面数据更新        │
│  (Tushare Pro)  │  (AKShare)      │    (每日盘后)            │
└────────┬────────┴────────┬────────┴──────────┬──────────────┘
         │                 │                    │
         └──────────┬──────┴────────────────────┘
                    ▼
         ┌──────────────────────┐
         │    数据处理/存储      │
         │  (SQLite/PostgreSQL) │
         └──────────┬───────────┘
                    ▼
         ┌──────────────────────┐
         │    策略引擎           │
         │  (定投/止盈止损逻辑)   │
         └──────────┬───────────┘
                    ▼
         ┌──────────────────────┐
         │    通知/展示层        │
         │  (微信/邮件/仪表板)   │
         └──────────────────────┘
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/your-username/daily-finance-auto.git
cd daily-finance-auto

# 创建虚拟环境
uv venv
source .venv/bin/activate

# 安装依赖
uv sync
```

### 2. 配置

```bash
# 复制配置文件模板
cp config.example.yaml config.yaml

# 编辑配置文件，填入你的 Tushare Token
vim config.yaml
```

### 3. 运行

```bash
# 采集数据
python main.py collect

# 执行定投检查
python main.py invest

# 查看报告
python main.py report
```

## 📁 项目结构

```
daily-finance-auto/
├── src/
│   ├── collectors/      # 数据采集模块
│   │   ├── fund.py      # 基金数据采集
│   │   └── stock.py     # 股票数据采集
│   ├── strategies/      # 策略模块
│   │   ├── invest.py    # 定投策略
│   │   └── rebalance.py # 再平衡策略
│   ├── storage/         # 数据存储
│   └── notify/          # 消息通知
├── tests/               # 测试
├── config.yaml          # 配置文件
├── main.py              # 入口文件
└── pyproject.toml       # 项目配置
```

## 📚 相关调研

### 自动化赚钱方案调研

详见 [docs/research/](docs/research/) 目录：

- [数据 API 对比](docs/research/data-apis.md)
- [量化平台对比](docs/research/quant-platforms.md)
- [自动化套利方法](docs/research/arbitrage.md)
- [内容变现自动化](docs/research/content-monetization.md)

### 推荐开源项目

| 项目 | Stars | 描述 |
|------|-------|------|
| [Hummingbot](https://github.com/hummingbot/hummingbot) | 8K+ | 加密货币套利机器人 |
| [AiToEarn](https://github.com/yikart/AiToEarn) | 10K+ | AI 内容变现自动化 |
| [Qbot](https://github.com/UFund-Me/Qbot) | 5K+ | AI 量化交易机器人 |
| [WonderTrader](https://github.com/wondertrader/wondertrader) | 5K+ | 量化交易框架 |

## ⚠️ 风险提示

1. **投资风险**：所有投资策略均存在亏损风险，历史收益不代表未来表现
2. **技术风险**：免费数据源可能随时失效，建议使用付费 API
3. **合规风险**：请严格遵守各平台服务条款，避免违规操作

## 📄 License

MIT License
