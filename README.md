# 每日自动化基金信息 + 股票信息采集系统

> 🚀 基于 Python + OpenClaw 的金融数据自动化采集、分析与定投系统

## 📋 项目简介

本项目用于每日自动化采集中国 A 股市场、基金的行情数据，支持自动化定投策略执行，可通过 OpenClaw 实现智能调度。

## ✅ 核心功能

- [x] 基金净值数据每日采集 (AKShare)
- [x] A 股行情数据采集 (Tushare)
- [x] 定投策略信号分析 (均线偏离策略)
- [x] 股票技术指标分析 (MA/MACD/RSI/布林带/KDJ)
- [x] 消息推送通知 (Server酱/邮件)
- [x] OpenClaw Skills 集成

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/imwxc/daily-finance-auto.git
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

# 编辑配置文件，填入你的 Tushare Token 和监控列表
vim config.yaml
```

### 3. 初始化

```bash
# 初始化数据库
python -m src.main init

# 查看系统状态
python -m src.main status
```

### 4. 使用

```bash
# 采集数据
python -m src.main collect --type fund    # 采集基金数据
python -m src.main collect --type stock   # 采集股票数据
python -m src.main collect --type all     # 采集所有数据

# 查看数据
python -m src.main funds                  # 查看基金列表
python -m src.main stocks                 # 查看股票列表

# 定投分析
python -m src.main invest                 # 检查定投信号
python -m src.main invest --notify        # 检查并发送通知

# 股票分析
python -m src.main analyze 600519         # 分析贵州茅台技术指标

# 查看配置
python -m src.main config                 # 显示当前配置
```

## 📊 数据源选型

| 数据源 | 类型 | 费用 | 适用场景 |
|--------|------|------|----------|
| **Tushare Pro** | Python SDK | ¥500/年起 | 股票数据主力 |
| **AKShare** | Python SDK | 免费 | 基金数据 |

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI 入口 (src/main.py)                    │
├─────────────┬─────────────┬─────────────┬──────────────────┤
│   collect   │   invest    │   analyze   │     status       │
│   数据采集   │  定投信号    │  技术分析    │     系统状态      │
└──────┬──────┴──────┬──────┴──────┬──────┴────────┬─────────┘
       │             │             │               │
       ▼             ▼             ▼               ▼
┌─────────────────────────────────────────────────────────────┐
│                     核心模块层                                │
├─────────────┬─────────────┬─────────────┬──────────────────┤
│ Collectors  │ Strategies  │  Analyzers  │     Notify       │
│ 数据采集器   │ 定投策略     │ 技术指标     │    消息推送       │
├─────────────┼─────────────┼─────────────┼──────────────────┤
│ AKShare     │ 均线偏离策略  │ MA/EMA/MACD │    Server酱      │
│ Tushare     │ 估值分位策略  │ RSI/KDJ/BB  │    邮件          │
└─────────────┴─────────────┴─────────────┴──────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                     数据存储层 (SQLite)                       │
│  funds | fund_navs | stocks | stock_dailys | invest_signals │
└─────────────────────────────────────────────────────────────┘
```

## 📁 项目结构

```
daily-finance-auto/
├── src/
│   ├── __init__.py
│   ├── main.py              # CLI 入口
│   ├── config.py            # 配置加载
│   ├── models/              # Pydantic 数据模型
│   │   ├── fund.py          # 基金模型
│   │   ├── stock.py         # 股票模型
│   │   └── signal.py        # 信号模型
│   ├── collectors/          # 数据采集
│   │   ├── base.py          # 采集器基类
│   │   ├── akshare_collector.py
│   │   └── tushare_collector.py
│   ├── storage/             # 数据存储
│   │   ├── database.py      # SQLite 连接
│   │   ├── fund_repo.py     # 基金仓库
│   │   └── stock_repo.py    # 股票仓库
│   ├── strategies/          # 策略引擎
│   │   ├── base.py          # 策略基类
│   │   └── ma_deviation.py  # 均线偏离策略
│   ├── analyzers/           # 技术分析
│   │   └── indicators.py    # 技术指标
│   └── notify/              # 消息通知
│       ├── base.py
│       ├── wechat.py        # Server酱
│       └── email.py         # 邮件
├── skills/                  # OpenClaw Skills
│   ├── fund-dca/            # 基金定投 Skill
│   └── stock-portfolio/     # 股票分析 Skill
├── tests/                   # 测试
├── docs/                    # 文档
│   ├── plans/               # 实施计划
│   └── research/            # 调研文档
├── config.example.yaml      # 配置模板
├── pyproject.toml           # 项目配置
└── README.md
```

## 🎯 定投策略

### 均线偏离策略

根据当前净值相对于 60 日均线的偏离程度调整定投金额：

| 偏离度 | 信号 | 操作 |
|--------|------|------|
| ≤ -20% | 📉 强买入 | 2x 定投 |
| -20% ~ -10% | 📉 买入 | 1.5x 定投 |
| -10% ~ +10% | ✅ 正常 | 1x 定投 |
| +10% ~ +20% | 📈 减仓 | 0.5x 定投 |
| > +20% | ⏸️ 跳过 | 跳过本次 |

## 🤖 OpenClaw 集成

### 安装 Skills

```bash
# 将 skills 目录复制到 OpenClaw 配置目录
cp -r skills/* ~/.openclaw/skills/
```

### Heartbeat 调度

参考 `docs/heartbeat-config.yaml` 配置定时任务：

```yaml
heartbeats:
  - name: daily_fund_collect
    schedule: "0 16 * * 1-5"    # 工作日下午 4 点
    skill: fund-dca
```

## 📚 相关调研

详见 [docs/research/](docs/research/) 目录：

- [数据 API 对比](docs/research/data-apis.md)
- [量化平台对比](docs/research/quant-platforms.md)
- [OpenClaw + OpenCode 自动理财方案](docs/research/openclaw-opencode-finance-plan.md)

## ⚠️ 风险提示

1. **投资风险**：所有投资策略均存在亏损风险，历史收益不代表未来表现
2. **技术风险**：免费数据源可能随时失效，建议使用付费 API
3. **合规风险**：请严格遵守各平台服务条款，避免违规操作
4. **AI 延迟**：AI Agent 调用延迟 2-5 秒，不适合高频交易

## 📄 License

MIT License
