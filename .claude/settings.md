# 每日自动化基金信息 + 股票信息采集系统

配置完成后，使用以下命令运行：

```bash
# 安装依赖
uv sync

# 采集数据
uv run python main.py collect

# 执行定投检查
uv run python main.py invest

# 查看报告
uv run python main.py report
```

详细文档见 [docs/research/](docs/research/) 目录。
