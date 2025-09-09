# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个股票数据分析和飞书表格同步工具，主要用于：
- 获取中国A股市场数据（价格、EPS预测等）
- 处理Excel文件中的股票投资数据
- 计算财务指标（PE比率、市值、潜在收益等）
- 同步数据到飞书多维表格

## 核心架构

### 数据获取层 (`get_data/`)
- `get_price.py`: 使用akshare获取所有A股实时价格数据，保存到 `data/all_stock_price.csv`
- `get_EPS.py`: 获取特定股票列表的预测年报每股收益数据，保存到 `data/股票代码_EPS.csv`

### 数据处理层
- `fill_excel_data.py`: 核心数据处理脚本，读取Excel文件并填充计算字段：
  - 从CSV数据中匹配当前价格和市值
  - 计算PE比率 (Current Price / EPS 2025E)
  - 计算中位目标价 ((Target Low + Target High) / 2)
  - 计算潜在收益率 (Mid Target / Current Price - 1)
  - 输出更新后的Excel文件到 `fromyouwei_updated.xlsx`

### 飞书集成层
- `feishu_config.py`: 飞书应用配置（APP_ID、APP_SECRET、BASE_URL、TABLE_ID）
- `feishu_auth.py`: 飞书API认证模块，处理token获取和管理
- `data_processor.py`: Excel数据处理器，转换为飞书API格式
- `sync_to_feishu.py`: 完整的飞书多维表格操作类，支持批量CRUD
- `import.json` / `export.json`: 飞书应用权限配置文件

### 自动化层
- `run_full_sync.py`: 完整的数据同步主脚本
- `.github/workflows/sync-to-feishu.yml`: GitHub Actions工作流配置
- `requirements.txt`: Python依赖列表
- `GITHUB_SETUP.md`: GitHub自动化设置指南

## 常用命令

### 数据获取
```bash
# 获取所有A股价格数据
cd get_data && python get_price.py

# 获取特定股票的EPS预测数据
cd get_data && python get_EPS.py
```

### 数据处理
```bash
# 处理Excel文件，计算财务指标
python fill_excel_data.py
```

### 飞书同步
```bash
# 测试飞书认证
python feishu_auth.py

# 测试数据格式转换
python data_processor.py

# 同步Excel数据到飞书（核心功能）
python sync_to_feishu.py

# 执行完整的数据获取和同步流程
python run_full_sync.py
```

### GitHub Actions自动化
```bash
# 安装依赖
pip install -r requirements.txt

# 查看工作流配置
cat .github/workflows/sync-to-feishu.yml
```

## 数据流程

### 手动执行流程
1. **数据收集**: 使用akshare库从东方财富等数据源获取股票数据
2. **数据整合**: 将价格、EPS数据与Excel中的投资标的匹配
3. **指标计算**: 自动计算PE比率、潜在收益率等投资决策指标
4. **数据转换**: 将Excel数据转换为飞书API兼容格式
5. **飞书同步**: 通过API将数据批量上传到飞书多维表格

### 自动化流程（GitHub Actions）
1. **定时触发**: 每个工作日早上9点和下午3点自动执行
2. **环境准备**: 自动安装Python依赖和配置环境变量
3. **数据获取**: 依次执行get_price.py和get_EPS.py获取最新数据
4. **数据处理**: 运行fill_excel_data.py计算财务指标
5. **飞书同步**: 运行sync_to_feishu.py上传到飞书表格
6. **日志归档**: 保存执行日志和生成文件供调试使用

## 关键依赖

- `akshare`: 中国股票数据获取
- `pandas`: 数据处理和分析
- `numpy`: 数值计算
- 飞书API: 表格同步功能

## 数据文件结构

- `fromyouwei.xlsx`: 原始投资标的Excel文件
- `fromyouwei_updated.xlsx`: 处理后的Excel文件
- `data/all_stock_price.csv`: 全市场股票价格数据
- `data/股票代码_EPS.csv`: 特定股票EPS预测数据

## 股票代码处理

- 所有股票代码统一格式为6位字符串（前导0补齐）
- Excel中的Ticker字段取前6位作为股票代码进行匹配