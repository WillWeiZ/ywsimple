# GitHub Actions 自动化设置指南

## 🔧 GitHub Secrets 配置

在您的GitHub仓库中设置以下Secrets：

### 1. 进入仓库设置
- 进入GitHub仓库页面
- 点击 Settings -> Secrets and variables -> Actions
- 点击 "New repository secret"

### 2. 添加以下Secrets

| Secret名称 | 值 | 说明 |
|-----------|-----|------|
| `FEISHU_APP_ID` | `cli_a8351c888cac9013` | 飞书应用ID |
| `FEISHU_APP_SECRET` | `gIcB8ViEFF478MsW0cJQ2efsLUtNrzZa` | 飞书应用密钥 |
| `FEISHU_BASE_URL` | `https://ydetzdeqyc.feishu.cn/base/U3iYbe8cGaBrLEso6jMctMVgnVb` | 飞书多维表格URL |
| `FEISHU_TABLE_ID` | `tbl29O0osz3dn74L` | 表格ID |

## 📅 定时任务说明

工作流将在以下时间自动执行：
- **每个工作日早上9点**（北京时间）- 获取开盘前数据
- **每个工作日下午3点**（北京时间）- 获取收盘后数据

## 🚀 手动触发

您也可以手动触发工作流：
1. 进入GitHub仓库的 Actions 页面
2. 选择 "同步股票数据到飞书" 工作流
3. 点击 "Run workflow"
4. 选择是否清空现有数据（默认为是）

## 📊 监控和日志

- 每次运行会生成详细的日志文件
- 日志会保存为工作流的artifacts，保留7天
- 如果同步失败，工作流会标记为失败状态

## 🔍 故障排查

### 常见问题

1. **认证失败**
   - 检查飞书Secrets是否正确配置
   - 确认飞书应用权限是否足够

2. **数据获取失败**
   - 检查akshare是否可以正常访问
   - 确认网络连接正常

3. **同步失败**
   - 查看feishu_sync.log日志
   - 检查飞书表格是否存在

### 调试步骤

1. 查看GitHub Actions的执行日志
2. 下载artifacts中的日志文件
3. 检查具体的错误信息

## 📝 本地测试

在提交到GitHub之前，建议先在本地测试：

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量（临时）
export FEISHU_APP_ID="cli_a8351c888cac9013"
export FEISHU_APP_SECRET="gIcB8ViEFF478MsW0cJQ2efsLUtNrzZa"
export FEISHU_BASE_URL="https://ydetzdeqyc.feishu.cn/base/U3iYbe8cGaBrLEso6jMctMVgnVb"
export FEISHU_TABLE_ID="tbl29O0osz3dn74L"

# 执行完整流程
python run_full_sync.py
```

## 🎯 下一步

1. 将代码推送到GitHub仓库
2. 配置上述Secrets
3. 工作流将自动开始按计划执行
4. 监控执行结果并根据需要调整

## ⚠️ 注意事项

- 请妥善保管飞书应用的密钥信息
- 定期检查飞书应用的权限有效性
- 监控GitHub Actions的使用配额
- 如需修改定时任务时间，编辑 `.github/workflows/sync-to-feishu.yml` 文件中的 cron 表达式