# AI-Trader 多市场配置管理系统

## 🎯 功能概述

AI-Trader 现在支持三种市场模式，并提供完整的配置管理功能：

- **🇺🇸 美股模式**: 纳斯达克100成分股交易
- **🇨🇳 A股模式**: 上证50成分股交易  
- **🪙 数字货币模式**: 币安交易所加密货币交易
- **⚙️ 配置管理**: Web界面管理所有配置

## 🚀 快速开始

### 1. 使用多模式启动脚本（推荐）

```bash
# 启动交互式多模式选择界面
bash scripts/start_multi_mode.sh
```

这个脚本提供：
- 可视化模式选择菜单
- 一键切换和启动
- 配置验证和状态检查
- API密钥配置检查

### 2. 使用配置切换工具

```bash
# 列出所有可用模式
python3 scripts/config_switcher.py --list

# 切换到美股模式
python3 scripts/config_switcher.py --switch us

# 切换到A股模式
python3 scripts/config_switcher.py --switch cn

# 切换到数字货币模式
python3 scripts/config_switcher.py --switch crypto

# 验证配置
python3 scripts/config_switcher.py --validate us

# 查看配置摘要
python3 scripts/config_switcher.py --summary us

# 检查API密钥
python3 scripts/config_switcher.py --check-keys crypto
```

### 3. 使用Web配置管理界面

```bash
# 启动配置管理Web服务
bash scripts/start_config_manager.sh

# 然后在浏览器访问: http://localhost:5000
```

Web界面功能：
- 📊 可视化配置管理
- ✏️ 在线编辑配置
- 🔍 配置验证
- ▶️ 一键激活市场
- 🔑 API密钥状态
- 📱 响应式设计

## 📁 文件结构

```
configs/
├── config_manager.py          # 配置管理器核心
├── config_api.py              # Web API服务
├── local_quickstart.json      # 主配置文件
├── us_market_config.json      # 美股配置
├── cn_market_config.json      # A股配置
├── crypto_market_config.json  # 数字货币配置
└── multi_mode_config.json     # 多模式配置

scripts/
├── start_multi_mode.sh        # 多模式启动脚本
├── start_config_manager.sh    # 配置管理启动脚本
├── config_switcher.py         # 配置切换工具
├── main_us_stock_step2.sh     # 美股启动脚本
├── main_a_stock_step2.sh      # A股启动脚本
└── main_crypto.sh             # 数字货币启动脚本
```

## ⚙️ 配置说明

### 市场配置

每个市场都有独立的配置文件：

#### 美股配置 (us_market_config.json)
- **代理类型**: BaseAgent
- **数据源**: Alpha Vantage
- **支持模型**: Claude-3.7-Sonnet, DeepSeek, Qwen, Gemini, GPT-5
- **交易规则**: 美股交易规则
- **股票池**: 纳斯达克100成分股

#### A股配置 (cn_market_config.json)
- **代理类型**: BaseAgentAStock
- **数据源**: Tushare
- **特殊规则**: 
  - 一手交易（100股整数倍）
  - T+1结算
  - 涨跌停限制
- **股票池**: 上证50成分股

#### 数字货币配置 (crypto_market_config.json)
- **代理类型**: BaseAgentCrypto
- **数据源**: 币安交易所
- **特殊规则**:
  - 24/7交易
  - 不同币种精度要求
  - 实时结算
- **支持交易对**: BTCUSDT, ETHUSDT等

### 通用配置

在 `local_quickstart.json` 中配置：

```json
{
  "mode": "multi",
  "multi_mode_enabled": true,
  "config_manager": {
    "enabled": true,
    "web_interface": "http://localhost:5000",
    "auto_switch": true,
    "validate_configs": true
  },
  "common_settings": {
    "api_keys": {
      "alphavantage": "YOUR_ALPHAVANTAGE_API_KEY",
      "tushare": "YOUR_TUSHARE_API_KEY", 
      "binance": "YOUR_BINANCE_API_KEY",
      "binance_secret": "YOUR_BINANCE_API_SECRET",
      "openai": "YOUR_OPENAI_API_KEY"
    }
  }
}
```

## 🔑 API密钥配置

### 必需密钥

| 市场 | 必需密钥 | 获取方式 |
|------|----------|----------|
| 美股 | Alpha Vantage | [alphavantage.co](https://www.alphavantage.co/support/#api-key) |
| A股 | Tushare | [tushare.pro](https://tushare.pro/) |
| 数字货币 | 币安API | [binance.com](https://www.binance.com/en/support/faq/360002502072) |
| 所有 | OpenAI | [platform.openai.com](https://platform.openai.com/) |

### 配置方法

1. **Web界面配置**: 访问 http://localhost:5000
2. **直接编辑**: 修改 `local_quickstart.json`
3. **环境变量**: 设置对应的环境变量

## 🤖 AI模型配置（多模型）

AI-Trader 支持为每个市场（美股/A股/加密货币）独立配置多个 AI 模型，包括启用/禁用、参数调节、优先级排序，以及模型选择策略：
- `priority`（按优先级）
- `round_robin`（轮询）
- `cost_optimized`（成本优化）
- `performance_optimized`（性能优化）

### 入口与市场标识说明
- Web 界面：配置管理页内的“模型概览 / 模型配置 / 市场模型”标签页
- API：模型相关端点前缀为 `/api/models/...`
- 市场标识：
  - 可用模型查询使用 `us`、`cn`、`crypto`
  - 市场配置使用 `us_market`、`cn_market`、`crypto_market`

### 查询可用模型（按市场过滤）
```bash
curl -s "http://localhost:5000/api/models/available?market=us" | jq
```

### 查看指定市场的模型配置与选择结果
```bash
curl -s "http://localhost:5000/api/models/market/us_market" | jq
```

### 更新市场的多模型配置
向指定市场提交启用的模型列表、选择策略与 API 密钥：
```bash
curl -s -X PUT "http://localhost:5000/api/models/market/us_market" \
  -H 'Content-Type: application/json' \
  -d '{
    "model_selection": {
      "strategy": "priority",
      "fallback_enabled": true,
      "max_retries": 3,
      "timeout_seconds": 30
    },
    "enabled_models": [
      {
        "model_id": "gpt-4-turbo",
        "name": "GPT-4 Turbo",
        "provider": "openai",
        "enabled": true,
        "priority": 1,
        "parameters": { "temperature": 0.6, "max_tokens": 2000 },
        "rate_limit": { "requests_per_minute": 300, "tokens_per_minute": 80000 }
      },
      {
        "model_id": "claude-3-sonnet-20240229",
        "name": "Claude 3 Sonnet",
        "provider": "anthropic",
        "enabled": true,
        "priority": 2,
        "parameters": { "temperature": 0.7, "max_tokens": 2000 },
        "rate_limit": { "requests_per_minute": 200, "tokens_per_minute": 80000 }
      }
    ],
    "api_keys": { "openai": "YOUR_OPENAI_API_KEY", "anthropic": "YOUR_ANTHROPIC_API_KEY" }
  }'
```

### 验证市场模型配置
返回每个启用模型的验证结果和总体有效性：
```bash
curl -s "http://localhost:5000/api/models/validate/us_market" | jq
```

### 估算模型使用成本
提供输入/输出令牌，返回美元计价的成本估算：
```bash
curl -s -X POST "http://localhost:5000/api/models/cost-estimate" \
  -H 'Content-Type: application/json' \
  -d '{
    "model_id": "gpt-4-turbo",
    "provider": "openai",
    "input_tokens": 2000,
    "output_tokens": 1500
  }' | jq
```

### 注意事项
- 先在“通用设置”或“API 密钥配置”中填好各供应商的密钥，否则模型验证将失败。
- 启用多个模型时，`priority` 越小优先级越高；`round_robin` 会在启用模型间轮换。
- `available` 接口的 `market` 参数使用短码（`us/cn/crypto`），市场配置相关接口使用市场键（`us_market/cn_market/crypto_market`）。

### 快速检查
```bash
# 1) 拉取可用模型（美股）
curl -s "http://localhost:5000/api/models/available?market=us" | jq '.data.total'

# 2) 查看当前市场的启用模型与选择结果
curl -s "http://localhost:5000/api/models/market/us_market" | jq '.data.selected_models | length'

# 3) 运行验证
curl -s "http://localhost:5000/api/models/validate/us_market" | jq '.data.overall_valid'
```

## 🛠️ 高级功能

### 配置验证

系统会自动验证：
- ✅ 配置文件格式
- ✅ 必需字段完整性
- ✅ API密钥有效性
- ✅ 交易规则合规性
- ✅ 数据源连接性

### 多模式并行

支持同时运行多个市场模式：
```bash
# 在不同的终端分别启动
bash scripts/main_us_stock_step2.sh  # 终端1 - 美股
bash scripts/main_a_stock_step2.sh    # 终端2 - A股
bash scripts/main_crypto.sh           # 终端3 - 数字货币
```

### 自定义配置

1. **复制现有配置**:
```bash
cp configs/us_market_config.json configs/my_us_config.json
```

2. **修改配置**: 使用Web界面或文本编辑器

3. **注册配置**: 在 `config_manager.py` 中添加新配置

## 🔧 故障排除

### 常见问题

1. **配置验证失败**
   - 检查API密钥是否正确
   - 确认网络连接正常
   - 验证JSON格式

2. **Web界面无法访问**
   - 确认端口5000未被占用
   - 检查防火墙设置
   - 查看控制台错误信息

3. **模式切换失败**
   - 使用 `--no-validate` 跳过验证
   - 检查配置文件权限
   - 查看详细错误信息

### 调试命令

```bash
# 检查配置状态
python3 scripts/config_switcher.py --list

# 验证特定配置
python3 scripts/config_switcher.py --validate us

# 检查API密钥
python3 scripts/config_switcher.py --check-keys crypto

# 查看详细配置
python3 scripts/config_switcher.py --summary us
```

## 📈 使用建议

1. **开发阶段**: 使用测试网络和模拟交易
2. **测试阶段**: 小额真实资金验证策略
3. **生产阶段**: 启用所有验证和风险管理

## 🤝 贡献指南

欢迎贡献新的市场模式或改进现有功能：

1. Fork 项目
2. 创建功能分支
3. 提交改进代码
4. 创建Pull Request

## 📞 支持

如有问题，请：
1. 查看本使用说明
2. 运行调试命令
3. 检查日志文件
4. 提交Issue

---

**🎉 享受AI-Trader带来的智能交易体验！**