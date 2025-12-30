#!/usr/bin/env bash
# 环境变量管理工具 - Web 版启动脚本（Linux/macOS）

set -e

echo "============================================================"
echo "🌐 环境变量管理工具 - Web 版"
echo "============================================================"
echo ""
echo "📱 启动地址: http://127.0.0.1:5051"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "============================================================"
echo ""

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "❌ 虚拟环境不存在！"
    echo "请先运行: python -m venv .venv"
    exit 1
fi

# 激活虚拟环境
source .venv/bin/activate

# 检查依赖
if ! python -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "⏳ 安装依赖中..."
    pip install fastapi uvicorn -q
fi

# 启动Web服务
echo "⏳ 启动服务..."
python tooling/scripts/web/env_manager_app.py
