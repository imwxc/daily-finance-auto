# OpenClaw + OpenCode 自动理财完整方案

> 基于 AI Agent 的全自动理财系统，支持基金定投、股票监控、量化交易、小红书内容发布

## 🦞 OpenClaw 是什么？

**OpenClaw**（原名 Clawdbot/Moltbot）是一个开源的个人 AI 助手，GitHub Stars **192,000+**，是目前最火爆的 AI Agent 项目之一。

### 核心特点

| 特性 | 说明 |
|------|------|
| **真正能做事** | 不只是聊天，可以执行实际任务 |
| **多平台支持** | WhatsApp、Telegram、飞书、钉钉、企业微信、Signal 等 13+ 平台 |
| **持久记忆** | 记住你的偏好、上下文，持续进化 |
| **Skills 系统** | 可安装各种技能扩展功能 |
| **自主执行** | 通过 Heartbeat 引擎主动执行定时任务 |
| **本地运行** | 数据完全掌握在自己手中 |

### 官方资源

- 官网：https://openclaw.ai
- 中文文档：https://openclaw.cc
- GitHub：https://github.com/openclaw/openclaw
- Skills 市场：https://clawdhub.com

---

## ⌨️ OpenCode 是什么？

**OpenCode** 是一个开源的终端 AI 编程助手，GitHub Stars **100,000+**，是 Claude Code 的开源替代品。

### 核心特点

- 终端 TUI 界面
- 支持多种 LLM（Claude、GPT、Gemini、Kimi、GLM 等）
- MCP 协议支持
- 可以执行代码、操作文件

### 安装

```bash
curl -fsSL https://opencode.ai/install | bash
```

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    OpenClaw + OpenCode 自动理财系统                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────────────────┐   │
│  │  用户交互层   │     │   大脑层    │     │        执行层           │   │
│  ├─────────────┤     ├─────────────┤     ├─────────────────────────┤   │
│  │             │     │             │     │                         │   │
│  │ 飞书/钉钉   │────▶│  OpenClaw   │────▶│  OpenCode (代码执行)    │   │
│  │ 企业微信    │     │  Gateway    │     │  - 基金数据采集         │   │
│  │ Telegram    │     │             │     │  - 股票分析             │   │
│  │ Signal      │     │  + Skills   │     │  - 策略回测             │   │
│  │             │     │             │     │  - 定投计算             │   │
│  └─────────────┘     └─────────────┘     └─────────────────────────┘   │
│         │                   │                       │                  │
│         │                   │                       │                  │
│         ▼                   ▼                       ▼                  │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────────────────┐   │
│  │  小红书 MCP  │     │  数据源     │     │     交易执行            │   │
│  │  自动发布   │     │  Tushare    │     │  - FMZ 量化平台         │   │
│  │             │     │  AKShare    │     │  - Hyperliquid (加密)   │   │
│  │             │     │  yfinance   │     │  - 券商 API             │   │
│  └─────────────┘     └─────────────┘     └─────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 安装配置指南

### Step 1: 安装 OpenClaw

**macOS/Linux:**
```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

**Windows (PowerShell 管理员模式):**
```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex
```

### Step 2: 配置 OpenClaw

```bash
# 运行配置向导
openclaw onboard

# 选择模型（推荐国产模型）
# - GLM（智谱）
# - Kimi（月之暗面）
# - DeepSeek

# 选择通道
# - 飞书 / 钉钉 / 企业微信 / Telegram

# 启动网关
openclaw gateway
```

### Step 3: 安装 OpenCode

```bash
# macOS/Linux
curl -fsSL https://opencode.ai/install | bash

# 或使用包管理器
brew install anomalyco/tap/opencode

# 验证安装
opencode --version
```

### Step 4: 配置 OpenCode MCP

```bash
# 添加小红书 MCP（之前已配置）
opencode mcp add --transport http xiaohongshu-mcp http://localhost:18060/mcp
```

---

## 🛠️ 创建理财 Skills

OpenClaw 的 Skills 是扩展功能的核心。以下是理财相关 Skills 的创建指南。

### Skill 1: 基金定投监控

**文件位置**: `~/.openclaw/skills/fund-dca/skill.yaml`

```yaml
name: fund-dca
version: 1.0.0
description: 基金定投监控和提醒
author: user
tools:
  - python
  - http
triggers:
  - schedule: "0 9 * * 1-5"  # 工作日早上9点
  - keyword: "基金定投"
```

**指令文件**: `~/.openclaw/skills/fund-dca/instructions.md`

```markdown
# 基金定投监控任务

## 任务目标
监控用户持有的基金，分析定投信号，生成报告。

## 执行步骤

### 1. 获取基金净值
调用 OpenCode 执行以下 Python 代码：
\`\`\`python
import akshare as ak
import json

funds = ["110020", "000962"]  # 基金代码
results = []
for code in funds:
    df = ak.fund_open_fund_info_em(fund=code, indicator="单位净值走势")
    latest = df.iloc[-1]
    results.append({
        "code": code,
        "nav": float(latest["单位净值"]),
        "change": float(latest["日增长率"]),
        "date": str(latest["净值日期"])
    })
print(json.dumps(results, ensure_ascii=False))
\`\`\`

### 2. 分析定投信号
- 日跌幅 > 2%: 大跌加仓信号 📉
- 日涨幅 > 3%: 大涨止盈信号 📈
- 其他: 正常定投 ✅

### 3. 生成报告并发送
将分析结果发送到用户的聊天通道。

### 4. 可选：发布到小红书
如果用户要求，调用小红书 MCP 发布理财笔记。
```

### Skill 2: 股票持仓分析

**文件位置**: `~/.openclaw/skills/stock-portfolio/skill.yaml`

```yaml
name: stock-portfolio
version: 1.0.0
description: 股票持仓分析和建议
author: user
tools:
  - python
  - browser
triggers:
  - schedule: "0 16 * * 1-5"  # 工作日下午4点（收盘后）
  - keyword: "股票分析"
```

**指令文件**: `~/.openclaw/skills/stock-portfolio/instructions.md`

```markdown
# 股票持仓分析任务

## 执行步骤

### 1. 获取持仓数据
调用 OpenCode 使用 Tushare 获取股票数据：
\`\`\`python
import tushare as ts
import os

pro = ts.pro_api(os.getenv("TUSHARE_TOKEN"))

# 获取持仓股票行情
stocks = ["600519.SH", "000001.SZ"]  # 茅台、平安银行
for code in stocks:
    df = pro.daily(ts_code=code, limit=5)
    print(df.to_string())
\`\`\`

### 2. 技术分析
分析以下指标：
- MA5、MA20 均线
- MACD
- RSI
- 成交量变化

### 3. 生成建议
- 买入建议
- 卖出建议
- 持有建议

### 4. 推送报告
发送到用户配置的聊天通道。
```

### Skill 3: 理财内容发布

**文件位置**: `~/.openclaw/skills/finance-content/skill.yaml`

```yaml
name: finance-content
version: 1.0.0
description: 自动生成理财内容并发布到小红书
author: user
tools:
  - python
  - http
triggers:
  - schedule: "0 20 * * *"  # 每天晚上8点
  - keyword: "发布理财笔记"
```

**指令文件**: `~/.openclaw/skills/finance-content/instructions.md`

```markdown
# 理财内容发布任务

## 执行步骤

### 1. 获取今日热点
浏览财经新闻，找到热门理财话题。

### 2. 生成小红书笔记
生成符合小红书风格的理财笔记：
- 标题：吸引眼球，不超过20字
- 正文：干货为主，不超过1000字
- 配图：使用 AI 生成

### 3. 调用小红书 MCP 发布
使用之前配置的小红书 MCP 服务发布笔记。

### 4. 确认发布
向用户确认发布结果。
```

---

## 🔗 OpenCode 集成方案

OpenClaw 作为"大脑"负责规划和决策，OpenCode 作为"手"负责执行具体任务。

### 集成方式 1: 命令行调用

在 OpenClaw 的 Skill 指令中，让 AI 执行：

```markdown
## 执行代码

调用 OpenCode 执行以下命令：

\`\`\`bash
opencode run "帮我分析沪深300指数的最新走势，给出投资建议"
\`\`\`

或者让 OpenCode 执行特定的 Python 脚本：

\`\`\`bash
opencode run "执行 ~/daily-finance-auto/src/dca/fund_monitor.py"
\`\`\`
```

### 集成方式 2: HTTP API

OpenClaw 可以通过 HTTP 调用 OpenCode 的服务：

```markdown
## 通过 API 调用 OpenCode

发送 POST 请求到 OpenCode 服务：

\`\`\`json
POST http://localhost:4096/api/execute
{
  "task": "分析基金 110020 的净值走势",
  "script": "fund_analysis.py"
}
\`\`\`
```

### 集成方式 3: 共享文件

OpenClaw 和 OpenCode 共享工作目录：

```markdown
## 共享工作目录

1. OpenClaw 将任务写入 `~/finance-tasks/pending/task_001.md`
2. OpenCode 监控该目录，执行任务
3. OpenCode 将结果写入 `~/finance-tasks/completed/task_001_result.json`
4. OpenClaw 读取结果并发送给用户
```

---

## 📱 小红书自动发布集成

### 前提条件

已完成小红书 MCP 配置（参考之前的配置步骤）。

### 自动发布流程

```
┌─────────────────────────────────────────────────────────────┐
│                    小红书自动发布流程                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. OpenClaw 获取理财热点                                    │
│          │                                                  │
│          ▼                                                  │
│  2. AI 生成小红书笔记内容                                    │
│     - 标题（≤20字）                                         │
│     - 正文（≤1000字）                                        │
│     - 配图（AI 生成）                                        │
│          │                                                  │
│          ▼                                                  │
│  3. 调用小红书 MCP 发布                                      │
│     POST http://localhost:18060/mcp                         │
│     {                                                       │
│       "title": "...",                                       │
│       "content": "...",                                     │
│       "images": ["..."]                                     │
│     }                                                       │
│          │                                                  │
│          ▼                                                  │
│  4. 确认发布结果                                             │
│     - 发布成功：通知用户                                     │
│     - 发布失败：记录日志，重试                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Skill 指令示例

```markdown
# 小红书理财笔记自动发布

## 任务
每天晚上 8 点自动发布一篇理财笔记到小红书。

## 步骤

### 1. 获取今日理财热点
浏览以下网站获取热点：
- 东方财富网
- 雪球
- 同花顺

### 2. 生成笔记内容
根据热点生成小红书风格的笔记：

**标题示例**：
- 今日基金操作｜大跌加仓的机会来了？
- 2026理财新思路｜普通人也能躺赚

**正文要求**：
- 使用 emoji 增加可读性
- 分段清晰
- 包含实用干货

### 3. 生成配图
使用 DALL-E 或其他 AI 工具生成配图。

### 4. 调用小红书 MCP 发布
\`\`\`
使用 xiaohongshu-mcp 发布笔记：
- title: [生成的标题]
- content: [生成的正文]
- images: [生成的图片路径]
\`\`\`

### 5. 确认发布
检查发布状态，通知用户结果。
```

---

## 🎯 实战使用场景

### 场景 1: 每日基金定投提醒

**在飞书中说**：
```
帮我检查今天的基金定投信号
```

**OpenClaw 自动**：
1. 调用 OpenCode 执行基金数据采集脚本
2. 分析净值变化
3. 判断是否需要加仓
4. 推送结果到飞书

### 场景 2: 股票持仓周报

**在钉钉中说**：
```
生成本周股票持仓周报
```

**OpenClaw 自动**：
1. 调用 Tushare 获取持仓股票数据
2. 计算周收益率
3. 分析技术指标
4. 生成周报并发送

### 场景 3: 发布理财笔记到小红书

**在 Telegram 中说**：
```
今天有什么理财热点？帮我写篇小红书笔记发出去
```

**OpenClaw 自动**：
1. 浏览财经新闻获取热点
2. AI 生成小红书风格笔记
3. 调用小红书 MCP 发布
4. 确认发布结果

### 场景 4: 定投策略自动执行

**配置定时任务**：
```bash
# OpenClaw Heartbeat 配置
openclaw heartbeat add --name "fund_dca" --schedule "0 9 * * 4" --skill fund-dca
```

**每周四自动**：
1. 检查基金净值
2. 分析定投信号
3. 推送建议到聊天
4. 可选：自动执行买入

---

## ⚙️ 配置文件示例

### OpenClaw 主配置

**文件**: `~/.openclaw/config.yaml`

```yaml
model:
  default: glm-4-flash
  fallback: deepseek-chat

channels:
  feishu:
    enabled: true
    app_id: your_app_id
    app_secret: your_secret
  telegram:
    enabled: true
    bot_token: your_token

skills:
  fund-dca:
    enabled: true
  stock-portfolio:
    enabled: true
  finance-content:
    enabled: true

heartbeats:
  - name: daily_fund_check
    schedule: "0 9 * * 1-5"
    skill: fund-dca
  - name: weekly_report
    schedule: "0 16 * * 5"
    skill: stock-portfolio
  - name: daily_content
    schedule: "0 20 * * *"
    skill: finance-content

integrations:
  opencode:
    enabled: true
    endpoint: http://localhost:4096
  xiaohongshu_mcp:
    enabled: true
    endpoint: http://localhost:18060/mcp
```

---

## 📊 效果展示

### 飞书中的交互

```
用户: 帮我检查今天的基金定投信号

OpenClaw: 
📊 基金定投信号报告 (2026-02-14)

1. 沪深300指数 (110020)
   - 最新净值: 1.2345
   - 日涨跌: -1.2%
   - 信号: 正常定投 ✅

2. 中证500指数 (000962)
   - 最新净值: 2.3456
   - 日涨跌: -2.5%
   - 信号: 大跌加仓信号 📉

💡 建议: 今天中证500跌幅较大，可考虑加倍定投

是否需要我帮您记录这次定投计划？
```

### 小红书发布的笔记

```
标题: 今日基金操作｜大跌就是加仓机会！

正文:
姐妹们！今天市场又跌了 😅

但是别慌！跌就是机会！

📊 今日操作:
- 沪深300: 正常定投
- 中证500: 加倍定投 💪

💡 为什么敢加仓？
1. 长期看好中国经济
2. 指数定投越跌越买
3. 坚持纪律最重要

你们今天操作了吗？评论区聊聊~

#基金定投 #理财 #投资 #基金
```

---

## ⚠️ 风险提示

1. **AI 分析仅供参考** - 投资决策需结合自身情况
2. **先模拟后实盘** - 新策略务必先测试
3. **控制仓位** - 不要把所有资金投入单一策略
4. **定期检查** - 至少每周检查一次系统运行状态
5. **数据安全** - API 密钥不要泄露，使用 vault 存储

---

## 📚 参考资源

- [OpenClaw 官方文档](https://openclaw.cc)
- [OpenCode 官方网站](https://opencode.ai)
- [ClawHub Skills 市场](https://clawdhub.com)
- [小红书 MCP 项目](https://github.com/xpzouying/xiaohongshu-mcp)
- [FMZ 量化平台](https://www.fmz.com)

---

## 🚀 快速开始

```bash
# 1. 安装 OpenClaw
curl -fsSL https://openclaw.ai/install.sh | bash

# 2. 配置向导
openclaw onboard

# 3. 安装 OpenCode
curl -fsSL https://opencode.ai/install | bash

# 4. 配置小红书 MCP（如需发布内容）
cd ~/Tools/xiaohongshu-mcp && ./xiaohongshu-mcp-darwin-arm64

# 5. 在 OpenCode 中添加 MCP
opencode mcp add --transport http xiaohongshu-mcp http://localhost:18060/mcp

# 6. 启动 OpenClaw 网关
openclaw gateway

# 7. 在聊天软件中开始使用！
```

---

<promise>{{COMPLETION_PROMISE}}</promise>
