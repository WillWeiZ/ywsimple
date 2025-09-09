#!/bin/bash

echo "🚀 准备GitHub Actions部署"
echo "==============================="

# 检查必需文件
echo "📋 检查必需文件..."

required_files=(
    "complete_sync.py"
    "feishu_config.py" 
    "fromyouwei.xlsx"
    "requirements.txt"
    ".github/workflows/sync-to-feishu.yml"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        missing_files+=("$file")
    else
        echo "✅ $file"
    fi
done

if [[ ${#missing_files[@]} -gt 0 ]]; then
    echo ""
    echo "❌ 缺少以下文件:"
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
    echo ""
    echo "请确保所有必需文件存在后重新运行此脚本。"
    exit 1
fi

echo ""
echo "✅ 所有必需文件检查完成"

# 检查git状态
echo ""
echo "📦 检查Git状态..."

if [[ ! -d ".git" ]]; then
    echo "❌ 当前目录不是Git仓库"
    echo "请先运行: git init"
    exit 1
fi

# 检查是否有远程仓库
if ! git remote get-url origin >/dev/null 2>&1; then
    echo "⚠️  未检测到远程Git仓库"
    echo "请确保已添加GitHub远程仓库:"
    echo "git remote add origin https://github.com/用户名/仓库名.git"
fi

echo ""
echo "📝 需要在GitHub配置的Secrets:"
echo "==============================="
echo "在GitHub仓库 Settings > Secrets and variables > Actions 中添加："
echo ""
echo "1. FEISHU_APP_ID = cli_a8351c888cac9013"
echo "2. FEISHU_APP_SECRET = gIcB8ViEFF478MsW0cJQ2efsLUtNrzZa"
echo "3. FEISHU_BASE_URL = https://ydetzdeqyc.feishu.cn/base/U3iYbe8cGaBrLEso6jMctMVgnVb"
echo "4. FEISHU_TABLE_ID = tbl29O0osz3dn74L"
echo "5. FEISHU_USER_TOKEN = u-duMNU3i9FcGrxiU3yP9lc_gl06sw058hhgG010a80evD"
echo ""

echo "🕐 自动执行时间安排:"
echo "==================="
echo "• 每个工作日 中午12:00 (北京时间)"
echo "• 每个工作日 下午17:00 (北京时间)"
echo ""

echo "📋 下一步操作:"
echo "============="
echo "1. 提交并推送代码到GitHub:"
echo "   git add ."
echo "   git commit -m \"Deploy GitHub Actions workflow\""
echo "   git push origin main"
echo ""
echo "2. 在GitHub配置上述5个Secrets"
echo ""
echo "3. 手动测试GitHub Actions:"
echo "   - 进入GitHub仓库的Actions标签"
echo "   - 选择"同步股票数据到飞书"工作流"
echo "   - 点击"Run workflow"进行测试"
echo ""

echo "🎯 部署准备完成!"
echo "详细说明请查看: GITHUB_DEPLOYMENT.md"