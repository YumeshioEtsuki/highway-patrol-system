#!/usr/bin/env bash
# 开发工具菜单 (Linux/macOS)

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

show_menu() {
    echo ""
    echo "============================================================"
    echo "🔧 开发工具菜单"
    echo "============================================================"
    echo ""
    echo "选择要启动的工具："
    echo ""
    echo "   1. 🌐 Web 环境变量管理工具 (推荐)"
    echo "   2. 📟 CLI 环境变量管理工具"
    echo "   3. 🚀 项目启动（快速开发）"
    echo "   4. 🚀 项目启动（完整）"
    echo "   5. 📊 数据库检查"
    echo ""
    echo "   0. 退出"
    echo ""
    echo "============================================================"
    echo ""
}

main() {
    while true; do
        show_menu
        read -p "请选择 (0-5): " choice
        
        case $choice in
            1)
                bash bin/env-manager-web.sh
                ;;
            2)
                source .venv/bin/activate 2>/dev/null || python -m venv .venv
                source .venv/bin/activate
                python tooling/scripts/manage_env.py
                ;;
            3)
                python start_server.py --env dev
                ;;
            4)
                bash bin/startup_full.sh 2>/dev/null || python start_server.py
                ;;
            5)
                python check_db.py
                ;;
            0)
                echo "退出"
                exit 0
                ;;
            *)
                echo "❌ 无效选择"
                ;;
        esac
    done
}

main
