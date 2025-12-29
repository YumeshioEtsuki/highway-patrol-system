#!/usr/bin/env bash
# 开发工具菜单 (Linux/macOS)

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

show_menu() {
    echo ""
    echo "============================================================"
    echo "� 公路巡查系统 - 快速启动菜单"
    echo "============================================================"
    echo ""
    echo "【核心功能】"
    echo "   1. 🚀 快速启动（开发模式）"
    echo "   2. 🚀 完整启动（Redis + Celery + FastAPI）"
    echo "   3. 📊 数据库检查"
    echo ""
    echo "【开发工具】"
    echo "   4. 🔧 配置管理工具（Web/CLI）"
    echo ""
    echo "   0. 退出"
    echo ""
    echo "============================================================"
    echo ""
}

show_tool_menu() {
    echo ""
    echo "============================================================"
    echo "🔧 配置管理工具"
    echo "============================================================"
    echo "   1. 🌐 Web 界面（推荐）"
    echo "   2. 📟 命令行界面"
    echo "   0. 返回主菜单"
    echo "============================================================"
    echo ""
}

main() {
    while true; do
        show_menu
        read -p "请选择 (0-4): " choice
        
        case $choice in
            1)
                python start_server.py --env dev
                ;;
            2)
                bash bin/startup_full.sh 2>/dev/null || python start_server.py
                ;;
            3)
                python check_db.py
                ;;
            4)
                while true; do
                    show_tool_menu
                    read -p "请选择: " tool_choice
                    case $tool_choice in
                        1)
                            bash bin/env-manager-web.sh
                            ;;
                        2)
                            source .venv/bin/activate 2>/dev/null || python -m venv .venv
                            source .venv/bin/activate
                            python tooling/scripts/manage_env.py
                            ;;
                        0)
                            break
                            ;;
                        *)
                            echo "❌ 无效选择"
                            ;;
                    esac
                done
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
