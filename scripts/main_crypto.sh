#!/bin/bash

# AI-Trader 数字货币交易模式启动脚本
# 适用于币安交易所的加密货币交易

echo "🪙 启动 AI-Trader 数字货币交易模式..."
echo "💱 交易所: 币安 (Binance)"
echo "⚠️  注意: 默认使用测试网络，请在配置文件中启用真实交易"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3，请先安装 Python3"
    exit 1
fi

# 检查依赖包
echo "📦 检查依赖包..."
python3 -c "import binance" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  检测到缺少币安API依赖包，正在安装..."
    pip install python-binance websockets aiohttp pandas numpy cryptography
fi

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 检查配置文件
echo "🔧 检查配置文件..."
if [ ! -f "configs/local_quickstart.json" ]; then
    echo "❌ 错误: 配置文件 configs/local_quickstart.json 不存在"
    exit 1
fi

# 检查API密钥配置
echo "🔑 检查API密钥配置..."
python3 -c "
import json
with open('configs/local_quickstart.json', 'r') as f:
    config = json.load(f)
api_key = config.get('common_settings', {}).get('api_keys', {}).get('binance', '')
if api_key == 'YOUR_BINANCE_API_KEY':
    print('⚠️  警告: 请配置您的币安API密钥')
    print('📋 请在 configs/local_quickstart.json 中设置:')
    print('   - binance: 您的币安API密钥')
    print('   - binance_secret: 您的币安API密钥')
    print('🌐 如需使用测试网络，请在配置文件中启用 testnet_enabled')
else:
    print('✅ API密钥已配置')
"

# 创建数据目录
echo "📁 创建数据目录..."
mkdir -p data/agent_data_crypto

# 启动主程序
echo "🚀 启动数字货币交易程序..."
echo "📊 交易模式: 加密货币 (Crypto)"
echo "⏰ 开始时间: $(date)"
echo "=================================="

python3 main.py \
    --mode crypto \
    --config configs/local_quickstart.json \
    --log-dir data/agent_data_crypto \
    --prompt-path prompts/agent_prompt_binance.py

echo "=================================="
echo "🏁 程序执行完成"
echo "📈 交易日志保存在: data/agent_data_crypto/"