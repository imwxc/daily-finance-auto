# Daily-Finance-Auto 实施计划

> 创建日期: 2026-02-28
> 状态: 待确认
> 目标: 基金定投 + 股票监控/分析（只分析不自动交易）

---

## 1. 系统架构设计

### 1.1 整体架构图

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    Daily-Finance-Auto 系统架构                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                      OpenClaw Gateway (大脑层)                          │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────────┐  │  │
│  │  │  Telegram  │ │  Heartbeat │ │  DAG Skill │ │  Session Manager   │  │  │
│  │  │  用户入口   │ │  定时调度   │ │  任务编排   │ │    上下文复用      │  │  │
│  │  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────────┬──────────┘  │  │
│  └────────┼──────────────┼──────────────┼──────────────────┼─────────────┘  │
│           │              │              │                  │                 │
│           ▼              ▼              ▼                  ▼                 │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                      OpenCode CLI (执行层)                              │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────────┐  │  │
│  │  │ 数据采集    │ │ 策略分析    │ │ 报告生成    │ │    文件操作        │  │  │
│  │  │  Session   │ │  Session   │ │  Session   │ │                    │  │  │
│  │  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────────┬──────────┘  │  │
│  └────────┼──────────────┼──────────────┼──────────────────┼─────────────┘  │
│           │              │              │                  │                 │
│           ▼              ▼              ▼                  ▼                 │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                    daily-finance-auto (项目层)                          │  │
│  │                                                                        │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────────┐   │  │
│  │  │  collectors/ │  │  strategies/ │  │        storage/            │   │  │
│  │  │ ├─ base.py   │  │ ├─ dca.py    │  │ ├─ __init__.py             │   │  │
│  │  │ ├─ fund.py   │  │ ├─ ma.py     │  │ ├─ database.py             │   │  │
│  │  │ └─ stock.py  │  │ └─ signal.py │  │ ├─ models.py               │   │  │
│  │  └──────────────┘  └──────────────┘  │ └─ repositories/           │   │  │
│  │                                      │    ├─ fund_repo.py         │   │  │
│  │  ┌──────────────┐  ┌──────────────┐  │    └─ stock_repo.py        │   │  │
│  │  │   notify/    │  │   config/    │  └────────────────────────────┘   │  │
│  │  │ ├─ base.py   │  │ └─ config.py │                                    │  │
│  │  │ ├─ wechat.py │  └──────────────┘  ┌────────────────────────────┐   │  │
│  │  │ └─ email.py  │                    │        main.py             │   │  │
│  │  └──────────────┘                    │ ├─ collect 子命令          │   │  │
│  │                                      │ ├─ analyze 子命令          │   │  │
│  │  ┌──────────────┐                    │ └─ report 子命令           │   │  │
│  │  │  .claude/    │                    └────────────────────────────┘   │  │
│  │  │ └─ context/  │                                                     │  │
│  │  └──────────────┘                                                     │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 数据流架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  数据源      │────▶│  采集器      │────▶│  存储层      │────▶│  策略引擎    │
│             │     │  collectors │     │  storage    │     │  strategies │
├─────────────┤     ├─────────────┤     ├─────────────┤     ├─────────────┤
│ Tushare Pro │     │ fund.py     │     │ SQLite      │     │ dca.py      │
│ AKShare     │     │ stock.py    │     │ PostgreSQL  │     │ ma.py       │
│ (备用)      │     │             │     │             │     │ signal.py   │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                   │
                                                                   ▼
                                                            ┌─────────────┐
                                                            │  通知层      │
                                                            │  notify     │
                                                            ├─────────────┤
                                                            │ wechat.py   │
                                                            │ email.py    │
                                                            └─────────────┘
```

### 1.3 核心组件职责

| 组件 | 职责 | 技术实现 | 文件位置 |
|------|------|----------|----------|
| **OpenClaw Gateway** | 接收指令、定时触发、任务调度 | OpenClaw + Skills | `~/.openclaw/` |
| **OpenCode CLI** | 执行代码任务、操作项目 | OpenCode Sessions | 系统级 |
| **collectors/** | 基金/股票数据采集 | AKShare + Tushare | `src/collectors/` |
| **strategies/** | 定投策略、信号分析 | pandas + numpy | `src/strategies/` |
| **storage/** | 数据持久化 | SQLite/PostgreSQL | `src/storage/` |
| **notify/** | 消息推送 | Server酱/Email | `src/notify/` |

---

## 2. 技术选型

### 2.1 核心技术栈

| 层级 | 技术选择 | 理由 | 备选方案 |
|------|---------|------|----------|
| **运行时** | Python 3.12 | 类型系统完善、async 原生支持 | Python 3.11 |
| **包管理** | uv | 速度快、依赖解析可靠 | poetry |
| **数据采集** | AKShare (主力) + Tushare (备用) | 免费、接口丰富、中文文档 | 东财/新浪 API |
| **数据存储** | SQLite (开发) / PostgreSQL (生产) | 零配置 / 企业级时序支持 | MySQL |
| **数据验证** | Pydantic v2 | 严格的类型验证、性能优秀 | dataclasses |
| **任务调度** | APScheduler 3.x | 成熟稳定、支持持久化 | Celery |
| **异步 HTTP** | aiohttp | 连接池、并发控制完善 | httpx |
| **通知推送** | Server酱 (微信) | 免费、稳定、微信直达 | 钉钉/飞书 |

### 2.2 数据源选型详情

```
┌─────────────────────────────────────────────────────────────┐
│                     数据源架构                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────┐      ┌─────────────────┐             │
│   │  AKShare (主力)  │      │ Tushare (备用)   │             │
│   │  免费、无需注册   │      │ ¥500/5000积分    │             │
│   └────────┬────────┘      └────────┬────────┘             │
│            │                        │                       │
│            │   ┌────────────────────┘                       │
│            │   │                                            │
│            ▼   ▼                                            │
│   ┌─────────────────────────────────────┐                  │
│   │        DataProvider 抽象层           │                  │
│   │   统一接口、自动降级、重试机制         │                  │
│   └─────────────────────────────────────┘                  │
│                        │                                    │
│                        ▼                                    │
│   ┌─────────────────────────────────────┐                  │
│   │          存储层 (SQLite)             │                  │
│   └─────────────────────────────────────┘                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**数据源对比**：

| 特性 | AKShare | Tushare Pro |
|------|---------|-------------|
| **费用** | 完全免费 | ¥500 起 |
| **稳定性** | 中（基于爬虫） | 高（官方 API） |
| **延迟** | 不确定 | 可控 |
| **基金数据** | ✅ 完整 | ✅ 完整 |
| **股票数据** | ✅ 完整 | ✅ 完整 |
| **财务数据** | ⚠️ 部分 | ✅ 完整 |
| **推荐场景** | 开发/研究 | 生产环境 |

### 2.3 存储选型详情

| 场景 | 推荐存储 | 理由 |
|------|---------|------|
| **Phase 1-2 (开发)** | SQLite | 零配置、单文件、易备份 |
| **Phase 3-4 (生产)** | PostgreSQL | 并发写入、TimescaleDB 时序优化 |

**SQLite 配置（开发阶段）**：
```python
# 启用 WAL 模式提升并发
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA synchronous=NORMAL")
conn.execute("PRAGMA cache_size=-64000")  # 64MB
```

---

## 3. 分阶段实施计划

### 3.1 总体时间线

```
Week 1-2  │ Phase 1: 数据基础设施
          │ ├── 项目骨架
          │ ├── 数据采集模块
          │ ├── SQLite 存储层
          │ └── CLI 入口
          │
Week 3-4  │ Phase 2: 基金定投自动化
          │ ├── 定投策略引擎
          │ ├── 信号分析
          │ ├── 消息推送
          │ └── OpenClaw Skill
          │
Week 5-6  │ Phase 3: 股票分析系统
          │ ├── 股票数据采集
          │ ├── 技术指标计算
          │ ├── 持仓报告
          │ └── OpenClaw Skill
          │
Week 7-8  │ Phase 4: 集成与优化
          │ ├── Heartbeat 调度
          │ ├── DAG 编排
          │ ├── 错误恢复
          │ └── 监控告警
```

### 3.2 Phase 1: 数据基础设施 (Week 1-2)

**目标**: 建立可靠的数据采集和存储基础

**任务列表**:

| ID | 任务 | 时间 | 依赖 | 产出物 |
|----|------|------|------|--------|
| 1.1.1 | 创建项目目录结构 | 2h | - | `src/`, `tests/`, `config/` |
| 1.1.2 | 更新 pyproject.toml 依赖 | 1h | 1.1.1 | `pyproject.toml` |
| 1.1.3 | 编写配置加载模块 | 3h | 1.1.2 | `src/config/config.py` |
| 1.1.4 | 创建 Pydantic 数据模型 | 4h | 1.1.3 | `src/storage/models.py` |
| 1.2.1 | 实现 DataProvider 抽象基类 | 2h | 1.1.4 | `src/collectors/base.py` |
| 1.2.2 | 实现 AKShare 基金采集器 | 4h | 1.2.1 | `src/collectors/fund.py` |
| 1.2.3 | 实现 Tushare 股票采集器 | 4h | 1.2.1 | `src/collectors/stock.py` |
| 1.2.4 | 添加错误重试和降级逻辑 | 3h | 1.2.2, 1.2.3 | `src/collectors/retry.py` |
| 1.3.1 | 设计 SQLite Schema | 2h | 1.1.4 | `docs/schema.sql` |
| 1.3.2 | 实现数据库连接管理 | 3h | 1.3.1 | `src/storage/database.py` |
| 1.3.3 | 实现 Repository 层 | 4h | 1.3.2 | `src/storage/repositories/` |
| 1.4.1 | 实现 main.py CLI 入口 | 3h | 1.2, 1.3 | `main.py` |
| 1.4.2 | 添加 collect 子命令 | 2h | 1.4.1 | `main.py` |
| 1.4.3 | 编写单元测试 | 4h | 1.4.2 | `tests/` |

**里程碑**: `python main.py collect --type fund` 成功采集基金数据并存储

### 3.3 Phase 2: 基金定投自动化 (Week 3-4)

**目标**: 实现智能定投策略和自动提醒

**任务列表**:

| ID | 任务 | 时间 | 依赖 | 产出物 |
|----|------|------|------|--------|
| 2.1.1 | 设计策略接口 (BaseStrategy) | 2h | Phase 1 | `src/strategies/base.py` |
| 2.1.2 | 实现均线偏离策略 | 4h | 2.1.1 | `src/strategies/ma.py` |
| 2.1.3 | 实现估值分位策略 | 4h | 2.1.1 | `src/strategies/pe_pb.py` |
| 2.1.4 | 实现市值定投策略 | 3h | 2.1.1 | `src/strategies/value.py` |
| 2.2.1 | 定投信号计算引擎 | 4h | 2.1 | `src/strategies/signal.py` |
| 2.2.2 | 信号强度评分 (0-100) | 3h | 2.2.1 | `src/strategies/score.py` |
| 2.3.1 | 通知接口设计 | 2h | - | `src/notify/base.py` |
| 2.3.2 | Server酱推送实现 | 3h | 2.3.1 | `src/notify/wechat.py` |
| 2.3.3 | 邮件推送实现 | 2h | 2.3.1 | `src/notify/email.py` |
| 2.3.4 | 推送模板设计 | 2h | 2.3.2, 2.3.3 | `src/notify/templates/` |
| 2.4.1 | 创建 OpenClaw fund-dca Skill | 4h | 2.2, 2.3 | `~/.openclaw/skills/fund-dca/` |
| 2.4.2 | 编写 Skill 指令文档 | 2h | 2.4.1 | `SKILL.md` |

**里程碑**: OpenClaw 接收 "检查定投信号" 自动分析并推送结果

### 3.4 Phase 3: 股票分析系统 (Week 5-6)

**目标**: 股票监控、技术分析、持仓报告（只分析不交易）

**任务列表**:

| ID | 任务 | 时间 | 依赖 | 产出物 |
|----|------|------|------|--------|
| 3.1.1 | 扩展股票数据采集 | 3h | Phase 1 | `src/collectors/stock.py` |
| 3.1.2 | 历史K线数据同步 | 3h | 3.1.1 | `src/collectors/stock.py` |
| 3.1.3 | 股票基本面数据 (PE/PB) | 4h | 3.1.1 | `src/collectors/fundamental.py` |
| 3.2.1 | MA/EMA/布林带计算 | 3h | 3.1 | `src/analysis/indicators.py` |
| 3.2.2 | MACD/RSI/KDJ 计算 | 3h | 3.1 | `src/analysis/indicators.py` |
| 3.2.3 | 成交量分析 | 2h | 3.1 | `src/analysis/volume.py` |
| 3.3.1 | 持仓收益计算 | 3h | 3.1, 3.2 | `src/analysis/portfolio.py` |
| 3.3.2 | 风险评估报告 | 4h | 3.3.1 | `src/analysis/risk.py` |
| 3.3.3 | 周报/月报生成 | 3h | 3.3.2 | `src/reports/` |
| 3.4.1 | 创建 OpenClaw stock-portfolio Skill | 4h | 3.3 | `~/.openclaw/skills/stock-portfolio/` |

**里程碑**: "生成周报" 自动生成股票持仓分析报告

### 3.5 Phase 4: 集成与优化 (Week 7-8)

**目标**: 完整的自动化调度和错误恢复

**任务列表**:

| ID | 任务 | 时间 | 依赖 | 产出物 |
|----|------|------|------|--------|
| 4.1.1 | OpenClaw Heartbeat 配置 | 2h | Phase 2, 3 | `heartbeat.yaml` |
| 4.1.2 | 定时任务: 每日数据采集 | 2h | 4.1.1 | `schedules/` |
| 4.1.3 | 定时任务: 定投信号检查 | 2h | 4.1.1 | `schedules/` |
| 4.1.4 | 定时任务: 周报生成 | 2h | 4.1.1 | `schedules/` |
| 4.2.1 | 设计 DAG DSL 模板 | 3h | - | `dag-dsl.yaml` |
| 4.2.2 | 实现 DAG Executor | 4h | 4.2.1 | `~/.openclaw/skills/dag-executor/` |
| 4.2.3 | 任务依赖管理 | 3h | 4.2.2 | `dag-executor/` |
| 4.3.1 | 三级错误恢复策略 | 4h | 4.2 | `recovery.py` |
| 4.3.2 | 自动修复流程 | 4h | 4.3.1 | `auto_fix.py` |
| 4.3.3 | 人工介入交互 | 3h | 4.3.1 | `manual.py` |
| 4.4.1 | 健康检查端点 | 2h | - | `health.py` |
| 4.4.2 | 错误告警通知 | 2h | 4.4.1 | `alert.py` |

**里程碑**: 系统可无人值守运行，自动恢复错误

---

## 4. 项目目录结构

```
daily-finance-auto/
├── .claude/
│   ├── settings.md
│   └── context_md/              # 上下文文档
│       ├── architecture/
│       ├── database/
│       └── guides/
│
├── docs/
│   ├── plans/                   # 设计文档
│   │   ├── 2026-02-14-openclaw-opencode-automation-design.md
│   │   └── 2026-02-28-finance-automation-implementation.md
│   └── research/                # 调研文档
│       ├── data-apis.md
│       ├── quant-platforms.md
│       └── openclaw-opencode-finance-plan.md
│
├── src/
│   ├── __init__.py
│   ├── collectors/              # 数据采集
│   │   ├── __init__.py
│   │   ├── base.py              # DataProvider 抽象基类
│   │   ├── fund.py              # 基金数据采集
│   │   ├── stock.py             # 股票数据采集
│   │   └── retry.py             # 重试/降级逻辑
│   │
│   ├── strategies/              # 策略模块
│   │   ├── __init__.py
│   │   ├── base.py              # BaseStrategy 抽象基类
│   │   ├── dca.py               # 定投策略
│   │   ├── ma.py                # 均线策略
│   │   ├── pe_pb.py             # 估值策略
│   │   ├── signal.py            # 信号计算
│   │   └── score.py             # 信号评分
│   │
│   ├── analysis/                # 分析模块
│   │   ├── __init__.py
│   │   ├── indicators.py        # 技术指标
│   │   ├── volume.py            # 成交量分析
│   │   ├── portfolio.py         # 持仓分析
│   │   └── risk.py              # 风险评估
│   │
│   ├── storage/                 # 数据存储
│   │   ├── __init__.py
│   │   ├── database.py          # 数据库连接
│   │   ├── models.py            # Pydantic 模型
│   │   └── repositories/
│   │       ├── __init__.py
│   │       ├── fund_repo.py
│   │       └── stock_repo.py
│   │
│   ├── notify/                  # 消息通知
│   │   ├── __init__.py
│   │   ├── base.py              # Notifier 抽象基类
│   │   ├── wechat.py            # Server酱
│   │   ├── email.py             # 邮件
│   │   └── templates/           # 推送模板
│   │
│   ├── reports/                 # 报告生成
│   │   ├── __init__.py
│   │   ├── daily.py
│   │   └── weekly.py
│   │
│   └── config/                  # 配置模块
│       ├── __init__.py
│       └── config.py            # 配置加载
│
├── tests/                       # 测试
│   ├── __init__.py
│   ├── test_collectors/
│   ├── test_strategies/
│   └── test_storage/
│
├── data/                        # 数据目录 (gitignore)
│   └── finance.db               # SQLite 数据库
│
├── config.yaml                  # 配置文件
├── config.example.yaml          # 配置模板
├── main.py                      # 入口文件
├── pyproject.toml               # 项目配置
├── README.md
└── .gitignore
```

---

## 5. 风险点与缓解措施

### 5.1 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| **AKShare 接口不稳定** | 数据采集中断 | 中 | 实现 Tushare 降级机制，本地缓存历史数据 |
| **SQLite 并发写入锁** | 数据丢失 | 低 | 启用 WAL 模式，单写者模式 |
| **OpenCode Session 上下文不足** | 任务执行失败 | 中 | 注入 AGENTS.md 静态上下文 |
| **定时任务错过执行** | 数据不完整 | 低 | Heartbeat 的 on_missed 通知机制 |

### 5.2 业务风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| **策略信号误判** | 错误的投资建议 | 中 | 多信号交叉验证，人工确认机制 |
| **数据延迟** | 决策滞后 | 中 | 明确标记数据时间戳，提醒用户 |
| **推送服务故障** | 通知丢失 | 低 | 多通道备份 (微信 + 邮件) |

### 5.3 合规风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| **API 密钥泄露** | 账户被盗用 | 低 | 使用环境变量，不提交到 git |
| **高频请求被封** | IP 被封禁 | 中 | 限制并发，添加延迟，使用备用源 |
| **自动交易违规** | 法律风险 | N/A | 本系统仅分析不交易 |

### 5.4 错误恢复策略

```
任务执行失败
      │
      ▼
┌─────────────────┐
│  Level 1: 重试   │  最多 2 次，间隔 5 秒
│  (自动)          │  
└────────┬────────┘
         │ 仍然失败
         ▼
┌─────────────────┐
│ Level 2: 降级    │  切换备用数据源
│ (自动)           │  AKShare → Tushare
└────────┬────────┘
         │ 仍然失败
         ▼
┌─────────────────┐
│ Level 3: 通知    │  Telegram 通知用户
│ (人工介入)       │  等待用户指令
└─────────────────┘
```

---

## 6. OpenClaw Skills 设计

### 6.1 fund-dca Skill

**文件位置**: `~/.openclaw/skills/fund-dca/SKILL.md`

```markdown
# 基金定投监控 Skill

## 触发方式
- 关键词: "基金定投", "定投信号", "检查定投"
- 定时: 每周四 09:00 (可配置)

## 执行步骤

### 1. 数据采集
调用 OpenCode 执行：
\`\`\`bash
cd ~/projects/daily-finance-auto
opencode run "采集今日所有基金的净值数据"
\`\`\`

### 2. 信号分析
分析每只基金的：
- 日涨跌幅
- 5日/20日均线偏离度
- 近期波动率

### 3. 生成信号
| 涨跌幅 | 信号 | 建议操作 |
|--------|------|----------|
| < -3% | 📉 大跌加仓 | 1.5x 定投 |
| -3% ~ -1% | ⬇️ 小跌 | 1.2x 定投 |
| -1% ~ 1% | ✅ 正常 | 1.0x 定投 |
| 1% ~ 3% | ⬆️ 小涨 | 0.8x 定投 |
| > 3% | 📈 大涨止盈 | 0.5x 定投 |

### 4. 推送通知
将分析结果推送到用户配置的通道。
```

### 6.2 stock-portfolio Skill

**文件位置**: `~/.openclaw/skills/stock-portfolio/SKILL.md`

```markdown
# 股票持仓分析 Skill

## 触发方式
- 关键词: "股票分析", "持仓报告", "周报"
- 定时: 每周五 16:30 (收盘后)

## 执行步骤

### 1. 数据采集
\`\`\`bash
cd ~/projects/daily-finance-auto
opencode run "采集持仓股票的今日行情和历史K线"
\`\`\`

### 2. 技术分析
计算并分析：
- MA5, MA20, MA60 均线
- MACD 金叉/死叉
- RSI 超买/超卖
- 成交量变化

### 3. 持仓评估
- 每只股票的周/月收益率
- 持仓总市值变化
- 风险敞口分析

### 4. 生成报告
输出 Markdown 格式的周报，包含：
- 本周市场概况
- 持仓收益汇总
- 个股技术分析
- 下周操作建议

### 5. 推送
将报告推送到配置的通道。
```

---

## 7. 配置文件规范

### 7.1 config.yaml 完整结构

```yaml
# 数据源配置
data_sources:
  primary: akshare
  fallback: tushare
  
  tushare:
    token: "${TUSHARE_TOKEN}"  # 从环境变量读取
    rate_limit: 200  # 每分钟请求上限

# 数据库配置
database:
  type: sqlite  # sqlite | postgresql
  
  sqlite:
    path: "./data/finance.db"
    pragmas:
      journal_mode: WAL
      synchronous: NORMAL
      cache_size: -64000
      
  postgresql:
    host: localhost
    port: 5432
    database: finance
    user: "${DB_USER}"
    password: "${DB_PASSWORD}"

# 基金监控列表
funds:
  - code: "110020.OF"
    name: "易方达沪深300ETF联接"
    amount: 1000  # 每期定投金额
    strategy: ma   # 策略: ma | pe_pb | value
    
  - code: "000962.OF"
    name: "天弘中证500ETF联接"
    amount: 500
    strategy: pe_pb

# 股票监控列表
stocks:
  watch_list:
    - code: "000001.SZ"
      name: "平安银行"
      position: 1000  # 持仓股数
      cost: 12.50     # 成本价
      
    - code: "600519.SH"
      name: "贵州茅台"
      position: 10
      cost: 1800.00

# 定投策略配置
strategies:
  ma:
    short_period: 5
    long_period: 20
    deviation_threshold: 0.05
    
  pe_pb:
    low_threshold: 0.2   # 估值分位 < 20% 加仓
    high_threshold: 0.8  # 估值分位 > 80% 减仓

# 通知配置
notify:
  channels:
    - type: wechat
      enabled: true
      send_key: "${SERVERCHAN_KEY}"
      
    - type: email
      enabled: false
      smtp_server: "smtp.qq.com"
      smtp_port: 465
      sender: "${EMAIL_SENDER}"
      password: "${EMAIL_PASSWORD}"
      receiver: "${EMAIL_RECEIVER}"

# 调度配置
schedule:
  collect_time: "16:30"  # 数据采集时间
  signal_time: "09:00"   # 信号检查时间
  report_time: "17:00"   # 报告生成时间
  report_day: 5          # 周报日 (1=周一, 5=周五)
```

---

## 8. 下一步行动

### 8.1 立即可执行

1. **确认设计**: 用户确认本设计文档
2. **启动 Phase 1**: 创建项目骨架
3. **安装依赖**: `uv sync`

### 8.2 等待确认

- [ ] Tushare API Token 是否已有？
- [ ] Server酱 SendKey 是否已有？
- [ ] 基金监控列表确定？
- [ ] 股票监控列表确定？

---

## 附录

### A. 相关文档

- [OpenClaw + OpenCode 自动化设计](./2026-02-14-openclaw-opencode-automation-design.md)
- [数据 API 选型](../research/data-apis.md)
- [量化平台对比](../research/quant-platforms.md)
- [OpenClaw + OpenCode 理财方案](../research/openclaw-opencode-finance-plan.md)

### B. 参考项目

| 项目 | 描述 |
|------|------|
| [TradingAgents-CN](https://github.com/xxx) | 多 Agent A 股量化框架 |
| [Hummingbot](https://github.com/hummingbot/hummingbot) | 加密货币套利机器人 |
| [Qbot](https://github.com/UFund-Me/Qbot) | AI 量化交易机器人 |
