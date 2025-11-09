#!/bin/bash

# 启动单独的 Binance MCP 服务

set -e

# 获取项目根目录（scripts/ 的父目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT/agent_tools"

echo "🔧 正在启动 Binance MCP 服务..."
export BINANCE_HTTP_PORT=${BINANCE_HTTP_PORT:-8005}
python tool_binance.py

echo "✅ Binance MCP 服务已启动在端口 ${BINANCE_HTTP_PORT}"