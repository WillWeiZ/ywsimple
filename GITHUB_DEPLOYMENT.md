# GitHub Actions 部署指南

本指南将帮助你将股票数据同步脚本部署到GitHub Actions，实现每个工作日中午12点和下午5点的自动执行。

## 🕐 执行时间安排

- **中午12:00** (北京时间) = UTC 04:00
- **下午17:00** (北京时间) = UTC 09:00
- 仅在**工作日**（周一至周五）执行

## 📋 部署步骤

### 1. 推送代码到GitHub

首先确保你的代码已经推送到GitHub仓库。

### 2. 配置GitHub Secrets

在GitHub仓库页面，进入 **Settings** > **Secrets and variables** > **Actions**，添加以下secrets：

#### 必需的Secrets：

| Secret名称 | 值 | 说明 |
|-----------|-----|------|
| `FEISHU_APP_ID` | `cli_a8351c888cac9013` | 飞书应用ID |
| `FEISHU_APP_SECRET` | `gIcB8ViEFF478MsW0cJQ2efsLUtNrzZa` | 飞书应用密钥 |
| `FEISHU_BASE_URL` | `https://ydetzdeqyc.feishu.cn/base/U3iYbe8cGaBrLEso6jMctMVgnVb` | 飞书多维表格URL |
| `FEISHU_TABLE_ID` | `tbl29O0osz3dn74L` | 飞书表格ID |
| `FEISHU_USER_TOKEN` | `u-duMNU3i9FcGrxiU3yP9lc_gl06sw058hhgG010a80evD` | 飞书用户访问令牌 |

### 3. 配置步骤详解

1. **进入仓库设置**
   - 在你的GitHub仓库页面，点击 "Settings" 标签

2. **进入Secrets设置**
   - 在左侧菜单中找到 "Secrets and variables"
   - 点击 "Actions"

3. **添加Repository secrets**
   - 点击 "New repository secret"
   - 按照上表逐一添加所有5个secret

4. **验证配置**
   - 确保所有5个secret都已正确添加
   - 检查名称拼写是否准确

## 🚀 手动触发测试

配置完成后，你可以手动触发工作流进行测试：

1. 进入 **Actions** 标签页
2. 选择 "同步股票数据到飞书" 工作流
3. 点击 "Run workflow" 
4. 选择 "Run workflow" 按钮

## 📊 监控执行状态

### 自动执行时间
- **中午12:00** (北京时间，UTC+8)
- **下午17:00** (北京时间，UTC+8)
- 仅在工作日执行

### 查看执行日志
1. 进入 **Actions** 标签页
2. 点击相应的工作流运行
3. 查看详细执行步骤和日志

### 下载执行结果
执行完成后，可以下载以下文件：
- `complete_sync.log` - 执行日志
- `*.xlsx` - 更新后的Excel文件
- `data/*.csv` - 股票数据CSV文件

## 🔧 故障排除

### 常见问题

1. **Secret配置错误**
   - 检查所有secret名称是否正确
   - 确认secret值没有多余的空格

2. **飞书权限问题** 
   - 确认FEISHU_USER_TOKEN仍然有效
   - 检查飞书应用权限设置

3. **网络连接问题**
   - akshare数据源可能偶尔不稳定
   - 脚本有重试机制，通常会自动恢复

### 调试方法

1. **查看详细日志**
   - 在Actions页面查看每个步骤的执行日志
   - 特别关注错误信息和堆栈跟踪

2. **手动触发测试**
   - 使用workflow_dispatch进行手动测试
   - 可以在非工作时间进行调试

3. **本地测试**
   ```bash
   # 设置环境变量
   export FEISHU_USER_TOKEN="your_token_here"
   
   # 运行脚本
   python complete_sync.py
   ```

## 📈 预期执行流程

每次自动执行将按以下步骤进行：

1. **检查依赖** ✅
2. **获取股票价格数据** ✅ (或使用缓存数据)
3. **获取EPS预测数据** ✅ (或使用缓存数据) 
4. **处理Excel数据，计算财务指标** ✅
5. **同步数据到飞书** ✅
6. **上传执行日志** ✅

预计执行时间：2-10分钟（取决于网络状况）

## 📝 注意事项

- **数据时效性**: 脚本会优先使用现有数据文件，避免频繁的网络请求
- **飞书限流**: 飞书API有请求频率限制，脚本已做相应处理
- **日志保留**: 执行日志和结果文件保留7天
- **节假日**: 脚本仅在工作日执行，节假日自动跳过

## 🎯 部署完成

配置完成后，你的股票数据将在每个工作日中午12点和下午5点自动同步到飞书表格，无需人工干预！
