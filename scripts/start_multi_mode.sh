#!/bin/bash

# AI-Trader 多模式启动脚本
# 支持快速切换美股、A股、数字货币模式，以及配置管理

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# 打印彩色输出
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 打印标题
print_header() {
    echo ""
    print_color $CYAN "╔══════════════════════════════════════════════════════════════╗"
    print_color $CYAN "║                    🤖 AI-Trader 多模式启动                  ║"
    print_color $CYAN "╚══════════════════════════════════════════════════════════════╝"
    echo ""
}

# 打印菜单
print_menu() {
    print_color $WHITE "📋 请选择启动模式:"
    echo ""
    print_color $GREEN "   1) 🇺🇸 美股模式 (US Stock Market)"
    print_color $GREEN "   2) 🇨🇳 A股模式 (A-Share Market)" 
    print_color $GREEN "   3) 🪙 数字货币模式 (Cryptocurrency)"
    print_color $BLUE "   4) ⚙️  配置管理 (Configuration Manager)"
    print_color $PURPLE "   5) 🔧 快速切换工具 (Quick Switch Tool)"
    print_color $YELLOW "   6) 📊 查看配置状态 (View Config Status)"
    print_color $RED "   0) ❌ 退出 (Exit)"
    echo ""
    print_color $CYAN "请输入选项 (0-6): "
}

# 检查Python环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_color $RED "❌ 错误: Python3未安装"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_color $GREEN "🐍 Python版本: $PYTHON_VERSION"
}

# 检查配置文件
check_configs() {
    local config_file="$PROJECT_ROOT/configs/local_quickstart.json"
    if [ ! -f "$config_file" ]; then
        print_color $RED "❌ 错误: 配置文件不存在: $config_file"
        exit 1
    fi
    
    print_color $GREEN "✅ 配置文件检查通过"
}

# 启动美股模式
start_us_mode() {
    print_color $BLUE "🇺🇸 启动美股模式..."
    
    # 使用配置切换工具切换到美股模式
    if python3 "$SCRIPT_DIR/config_switcher.py" --switch us; then
        print_color $GREEN "✅ 美股模式配置成功"
        
        # 启动美股交易脚本
        print_color $CYAN "🚀 启动美股交易服务..."
        if [ -f "$SCRIPT_DIR/main_us_stock_step2.sh" ]; then
            bash "$SCRIPT_DIR/main_us_stock_step2.sh"
        else
            print_color $YELLOW "⚠️  美股启动脚本不存在，使用通用启动方式"
            cd "$PROJECT_ROOT"
            python3 main.py --mode us --config configs/local_quickstart.json
        fi
    else
        print_color $RED "❌ 美股模式配置失败"
        exit 1
    fi
}

# 启动A股模式
start_cn_mode() {
    print_color $BLUE "🇨🇳 启动A股模式..."
    
    # 使用配置切换工具切换到A股模式
    if python3 "$SCRIPT_DIR/config_switcher.py" --switch cn; then
        print_color $GREEN "✅ A股模式配置成功"
        
        # 启动A股交易脚本
        print_color $CYAN "🚀 启动A股交易服务..."
        if [ -f "$SCRIPT_DIR/main_a_stock_step2.sh" ]; then
            bash "$SCRIPT_DIR/main_a_stock_step2.sh"
        else
            print_color $YELLOW "⚠️  A股启动脚本不存在，使用通用启动方式"
            cd "$PROJECT_ROOT"
            python3 main.py --mode cn --config configs/local_quickstart.json
        fi
    else
        print_color $RED "❌ A股模式配置失败"
        exit 1
    fi
}

# 启动数字货币模式
start_crypto_mode() {
    print_color $BLUE "🪙 启动数字货币模式..."
    
    # 使用配置切换工具切换到数字货币模式
    if python3 "$SCRIPT_DIR/config_switcher.py" --switch crypto; then
        print_color $GREEN "✅ 数字货币模式配置成功"
        
        # 启动数字货币交易脚本
        print_color $CYAN "🚀 启动数字货币交易服务..."
        if [ -f "$SCRIPT_DIR/main_crypto.sh" ]; then
            bash "$SCRIPT_DIR/main_crypto.sh"
        else
            print_color $YELLOW "⚠️  数字货币启动脚本不存在，使用通用启动方式"
            cd "$PROJECT_ROOT"
            python3 main.py --mode crypto --config configs/local_quickstart.json
        fi
    else
        print_color $RED "❌ 数字货币模式配置失败"
        exit 1
    fi
}

# 启动配置管理器
start_config_manager() {
    print_color $BLUE "⚙️  启动配置管理器..."
    
    if [ -f "$SCRIPT_DIR/start_config_manager.sh" ]; then
        bash "$SCRIPT_DIR/start_config_manager.sh"
    else
        print_color $YELLOW "⚠️  配置管理启动脚本不存在，使用Python直接启动"
        cd "$PROJECT_ROOT"
        python3 configs/config_api.py
    fi
}

# 启动快速切换工具
start_switch_tool() {
    print_color $BLUE "🔧 启动快速切换工具..."
    
    while true; do
        echo ""
        print_color $WHITE "🔄 快速切换工具菜单:"
        echo ""
        print_color $GREEN "   1) 切换到美股模式"
        print_color $GREEN "   2) 切换到A股模式"
        print_color $GREEN "   3) 切换到数字货币模式"
        print_color $BLUE "   4) 验证当前配置"
        print_color $PURPLE "   5) 查看配置摘要"
        print_color $YELLOW "   6) 检查API密钥"
        print_color $RED "   0) 返回主菜单"
        echo ""
        print_color $CYAN "请输入选项 (0-6): "
        
        read -r sub_choice
        case $sub_choice in
            1)
                python3 "$SCRIPT_DIR/config_switcher.py" --switch us
                ;;
            2)
                python3 "$SCRIPT_DIR/config_switcher.py" --switch cn
                ;;
            3)
                python3 "$SCRIPT_DIR/config_switcher.py" --switch crypto
                ;;
            4)
                python3 "$SCRIPT_DIR/config_switcher.py" --validate $(python3 "$SCRIPT_DIR/config_switcher.py" --list | grep "🟢" | cut -d' ' -f2 | tr -d ':')
                ;;
            5)
                python3 "$SCRIPT_DIR/config_switcher.py" --summary $(python3 "$SCRIPT_DIR/config_switcher.py" --list | grep "🟢" | cut -d' ' -f2 | tr -d ':')
                ;;
            6)
                python3 "$SCRIPT_DIR/config_switcher.py" --check-keys $(python3 "$SCRIPT_DIR/config_switcher.py" --list | grep "🟢" | cut -d' ' -f2 | tr -d ':')
                ;;
            0)
                break
                ;;
            *)
                print_color $RED "❌ 无效选项，请重新输入"
                ;;
        esac
    done
}

# 查看配置状态
view_config_status() {
    print_color $BLUE "📊 查看配置状态..."
    python3 "$SCRIPT_DIR/config_switcher.py" --list
}

# 主函数
main() {
    # 检查环境和配置
    check_python
    check_configs
    
    # 显示标题
    print_header
    
    # 主循环
    while true; do
        print_menu
        read -r choice
        
        case $choice in
            1)
                start_us_mode
                ;;
            2)
                start_cn_mode
                ;;
            3)
                start_crypto_mode
                ;;
            4)
                start_config_manager
                ;;
            5)
                start_switch_tool
                ;;
            6)
                view_config_status
                ;;
            0)
                print_color $GREEN "👋 感谢使用 AI-Trader，再见！"
                exit 0
                ;;
            *)
                print_color $RED "❌ 无效选项，请重新输入"
                ;;
        esac
        
        echo ""
        print_color $CYAN "按回车键继续..."
        read -r
    done
}

# 如果直接运行脚本（不是被source），则执行主函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi