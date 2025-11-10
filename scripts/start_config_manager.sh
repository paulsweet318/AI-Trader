#!/bin/bash

# AI-Trader 配置管理服务启动脚本
# 启动配置管理API服务和Web界面

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 启动AI-Trader配置管理服务..."
echo "📁 项目根目录: $PROJECT_ROOT"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: Python3未安装"
    exit 1
fi

# 检查Python版本
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "🐍 Python版本: $PYTHON_VERSION"

# 检查依赖
if ! python3 -c "import flask" &> /dev/null; then
    echo "📦 安装Flask依赖..."
    pip install flask flask-cors
fi

# 检查配置文件
CONFIG_DIR="$PROJECT_ROOT/configs"
if [ ! -d "$CONFIG_DIR" ]; then
    echo "📁 创建配置目录..."
    mkdir -p "$CONFIG_DIR"
fi

# 检查配置文件是否存在
if [ ! -f "$CONFIG_DIR/config_manager.py" ]; then
    echo "❌ 错误: 配置管理器文件不存在: $CONFIG_DIR/config_manager.py"
    exit 1
fi

if [ ! -f "$CONFIG_DIR/config_api.py" ]; then
    echo "❌ 错误: 配置API文件不存在: $CONFIG_DIR/config_api.py"
    exit 1
fi

# 切换到项目根目录
cd "$PROJECT_ROOT"

# 设置环境变量
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
export FLASK_APP="configs/config_api.py"
export FLASK_ENV="development"

# 启动配置管理服务
echo "🌐 启动配置管理API服务..."
echo "📊 Web界面地址: http://localhost:5000"
echo "🔧 API文档地址: http://localhost:5000/api/*"
echo ""
echo "ℹ️  提示:"
echo "   - 使用 Ctrl+C 停止服务"
echo "   - 配置文件保存在: $CONFIG_DIR"
echo "   - 日志输出在控制台显示"
echo ""

# 运行配置管理API服务
python3 configs/config_api.py