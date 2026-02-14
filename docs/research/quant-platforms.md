# 量化交易平台对比

## 一、Python 量化框架（2024 最新）

| 框架 | 推荐度 | 活跃度 | 核心特点 |
|------|--------|--------|----------|
| **VectorBT** | ⭐⭐⭐⭐⭐ | 🔥🔥🔥 极高 | 向量化回测、Numba 加速、秒级千策略 |
| **Backtrader** | ⭐⭐⭐⭐ | 🔥🔥 中 | 事件驱动、功能全面、文档完善 |
| **VNPY** | ⭐⭐⭐⭐⭐ | 🔥🔥🔥 高 | 中国本土、CTP 实盘、多接口支持 |
| **Backtesting.py** | ⭐⭐⭐ | 🔥 低 | 轻量级、API 简洁 |
| **QuantConnect Lean** | ⭐⭐⭐⭐ | 🔥🔥 高 | 开源、云原生、C#/Python |

---

## 二、中国 A 股实盘平台

### 第一梯队

| 平台 | 特点 | 实盘方式 |
|------|------|----------|
| **聚宽 (JoinQuant)** | 国内最早，数据丰富 | 对接券商 API |
| **VNPY** | 开源框架，直连 CTP/XTP | 直连交易接口 |
| **BigQuant** | AI-first 平台 | 自动化交易 |

### 券商级系统

| 系统 | 开发商 | 门槛 | 特点 |
|------|--------|------|------|
| **QMT** | 迅投 | 10-30 万资产 | 全内存交易<1ms |
| **PTrade** | 恒生电子 | 10-30 万资产 | 云端运行，多因子策略 |

---

## 三、技术选型建议

### 新手入门路线
```
Backtesting.py → VectorBT → Backtrader → VNPY 实盘
```

### 中国 A 股特化方案
```
数据获取: AKShare / Tushare
回测框架: VNPY / Backtrader
实盘接口: CTP (期货) / XTP (股票)
```

---

## 四、GitHub 热门项目

| 项目 | Stars | 描述 |
|------|-------|------|
| [backtrader](https://github.com/backtrader/backtrader) | 14K+ | 成熟回测框架 |
| [vnpy](https://github.com/vnpy/vnpy) | 25K+ | 中国量化交易框架 |
| [vectorbt](https://github.com/polakowo/vectorbt) | 7K+ | 快速向量化回测 |
| [qlib](https://github.com/microsoft/qlib) | 14K+ | 微软 AI 量化平台 |
| [FinRL](https://github.com/AI4Finance-Foundation/FinRL) | 9K+ | 深度强化学习交易 |

---

## 五、过时技术（避免使用）

- ~~Zipline (原版)~~ → 改用 **zipline-reloaded**
- ~~PyAlgoTrade~~ → 改用 **Backtesting.py**
- ~~PyFolio (原版)~~ → 改用 **QuantStats**
