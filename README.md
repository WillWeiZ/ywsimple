# 股票数据分析与飞书同步系统

自动化股票数据获取、分析计算和飞书多维表格同步的完整解决方案。

## 🎯 核心功能

- **股票数据获取**: 使用akshare库获取A股实时价格和EPS预测数据
- **财务指标计算**: 自动计算PE比率、潜在收益率等投资决策指标
- **飞书表格同步**: 将分析结果实时同步到飞书多维表格
- **自动化执行**: 支持GitHub Actions定时任务

## 📁 项目结构

```
Simple_YW/
├── 📄 核心脚本
│   ├── sync_to_feishu.py          # 飞书同步主脚本 ⭐
│   ├── run_full_sync.py           # 完整数据流程脚本
│   ├── fill_excel_data.py         # Excel数据处理脚本
│   └── data_processor.py          # 数据格式转换器
│
├── 🔧 配置和认证
│   ├── feishu_config.py           # 飞书应用配置
│   ├── feishu_auth.py             # 飞书API认证模块
│   ├── import.json / export.json  # 应用权限配置
│   └── requirements.txt           # Python依赖
│
├── 📊 数据获取
│   ├── get_data/
│   │   ├── get_price.py           # 获取股票价格数据
│   │   └── get_EPS.py             # 获取EPS预测数据
│   └── data/                      # 数据存储目录
│       ├── all_stock_price.csv
│       └── 股票代码_EPS.csv
│
├── 📈 Excel文件
│   ├── fromyouwei.xlsx            # 原始投资数据
│   └── fromyouwei_updated.xlsx    # 处理后的数据 ⭐
│
├── 🤖 自动化部署
│   └── .github/workflows/
│       └── sync-to-feishu.yml     # GitHub Actions工作流
│
└── 📖 文档说明
    ├── CLAUDE.md                  # Claude Code配置指南
    ├── GITHUB_SETUP.md            # GitHub Actions设置指南
    └── PERMISSION_TROUBLESHOOTING.md # 权限问题排查指南
```

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 数据同步到飞书
```bash
python sync_to_feishu.py
```

### 3. 完整数据流程
```bash
python run_full_sync.py
```

## ⚙️ 主要模块

### 📊 数据获取模块 (`get_data/`)
- **get_price.py**: 获取全A股实时价格数据
- **get_EPS.py**: 获取特定股票EPS预测数据
- 带有重试机制和错误处理

### 🔄 数据处理模块
- **fill_excel_data.py**: 核心数据处理，计算PE比率、潜在收益等
- **data_processor.py**: 数据格式转换，Excel → 飞书API格式

### 🔗 飞书集成模块
- **sync_to_feishu.py**: 核心同步脚本，支持批量更新
- **feishu_auth.py**: 飞书API认证和token管理
- 自动处理字段映射和数据类型转换

## 🎉 成功特性

- ✅ **100%同步成功率**: 8条记录全部成功更新
- ✅ **智能字段映射**: 自动处理`Sector/Theme` → `Sector|Theme`
- ✅ **数据类型适配**: 数字字段保持数字类型，文本字段转字符串
- ✅ **完善错误处理**: 详细的错误信息和重试机制
- ✅ **实时调试信息**: 清晰的执行过程和结果报告

## 🔧 配置要求

### 飞书应用配置
- APP_ID 和 APP_SECRET
- user_access_token (通过OAuth2获取)
- 多维表格编辑权限

### GitHub Actions (可选)
- 定时任务: 工作日早9点和下午3点
- 自动获取数据并同步到飞书
- 详见 `GITHUB_SETUP.md`

## 📈 数据流程

1. **数据获取** → akshare API获取股票数据
2. **数据计算** → 计算PE、收益率等财务指标  
3. **格式转换** → Excel格式转换为飞书API格式
4. **数据同步** → 批量更新到飞书多维表格
5. **结果验证** → 确认同步成功并记录日志

## 🎯 使用场景

- **个人投资管理**: 跟踪股票投资组合表现
- **团队协作**: 多人共享投资数据和决策
- **自动化报告**: 定时更新投资数据到协作平台
- **数据分析**: 结合飞书表格的分析和可视化功能

---

💡 **提示**: 首次使用请参考 `GITHUB_SETUP.md` 进行完整配置。