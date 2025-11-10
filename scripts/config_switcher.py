#!/usr/bin/env python3
"""
AI-Trader 配置切换工具
支持多市场配置的快速切换和验证
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import argparse
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs.config_manager import ConfigManager

class ConfigSwitcher:
    """配置切换器"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.project_root = Path(__file__).parent.parent
        self.configs_dir = self.project_root / "configs"
        
    def list_available_modes(self) -> Dict[str, Any]:
        """列出所有可用的模式"""
        try:
            configs = self.config_manager.get_available_configs()
            active_config = self.config_manager.get_active_config()
            
            modes = {}
            for market, config in configs.items():
                validation = self.config_manager.validate_config(market, config)
                modes[market] = {
                    "name": config.get("name", market.upper()),
                    "description": config.get("description", ""),
                    "enabled": config.get("enabled", True),
                    "agent_type": config.get("agent_type", ""),
                    "data_source": config.get("data_source", ""),
                    "validation": validation,
                    "is_active": active_config and active_config.get("active_market") == market
                }
            
            return modes
        except Exception as e:
            print(f"❌ 获取可用模式失败: {e}")
            return {}
    
    def validate_market_config(self, market: str) -> Dict[str, Any]:
        """验证指定市场的配置"""
        try:
            configs = self.config_manager.get_available_configs()
            if market not in configs:
                return {
                    "valid": False,
                    "errors": [f"市场 '{market}' 的配置不存在"],
                    "warnings": []
                }
            
            config = configs[market]
            return self.config_manager.validate_config(market, config)
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"验证配置时出错: {e}"],
                "warnings": []
            }
    
    def switch_to_market(self, market: str, validate: bool = True) -> bool:
        """切换到指定市场"""
        try:
            configs = self.config_manager.get_available_configs()
            if market not in configs:
                print(f"❌ 市场 '{market}' 的配置不存在")
                return False
            
            config = configs[market]
            
            # 验证配置
            if validate:
                validation = self.config_manager.validate_config(market, config)
                if not validation["valid"]:
                    print(f"❌ 配置验证失败:")
                    for error in validation["errors"]:
                        print(f"   - {error}")
                    if validation["warnings"]:
                        print("⚠️  警告:")
                        for warning in validation["warnings"]:
                            print(f"   - {warning}")
                    return False
            
            # 激活配置
            active_config = self.config_manager.set_active_config(market, config)
            
            # 更新local_quickstart.json
            self._update_local_quickstart(market)
            
            print(f"✅ 成功切换到市场: {market}")
            print(f"   代理类型: {config.get('agent_type', '未知')}")
            print(f"   数据源: {config.get('data_source', '未知')}")
            
            if validation.get("warnings"):
                print("⚠️  注意:")
                for warning in validation["warnings"]:
                    print(f"   - {warning}")
            
            return True
            
        except Exception as e:
            print(f"❌ 切换市场失败: {e}")
            return False
    
    def _update_local_quickstart(self, market: str):
        """更新local_quickstart.json文件"""
        try:
            quickstart_file = self.configs_dir / "local_quickstart.json"
            if quickstart_file.exists():
                with open(quickstart_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 更新模式
                config["mode"] = market
                config["last_switch_time"] = datetime.now().isoformat()
                
                with open(quickstart_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                print(f"📝 已更新 local_quickstart.json 模式为: {market}")
                
        except Exception as e:
            print(f"⚠️  更新 local_quickstart.json 失败: {e}")
    
    def show_config_summary(self, market: str):
        """显示配置摘要"""
        try:
            configs = self.config_manager.get_available_configs()
            if market not in configs:
                print(f"❌ 市场 '{market}' 的配置不存在")
                return
            
            config = configs[market]
            validation = self.config_manager.validate_config(market, config)
            
            print(f"\n📊 {config.get('name', market.upper())} 配置摘要:")
            print(f"   描述: {config.get('description', '无描述')}")
            print(f"   代理类型: {config.get('agent_type', '未知')}")
            print(f"   数据源: {config.get('data_source', '未知')}")
            print(f"   启用状态: {'✅ 已启用' if config.get('enabled', True) else '❌ 已禁用'}")
            
            # 显示模型信息
            models = config.get('models', [])
            enabled_models = [m for m in models if m.get('enabled', False)]
            print(f"   模型配置: {len(enabled_models)}/{len(models)} 个模型已启用")
            for model in enabled_models:
                print(f"     - {model.get('name', '未知模型')}: {model.get('basemodel', '未知')}")
            
            # 显示代理配置
            agent_config = config.get('agent_config', {})
            print(f"   代理配置:")
            print(f"     - 最大步骤: {agent_config.get('max_steps', '未设置')}")
            print(f"     - 重试次数: {agent_config.get('max_retries', '未设置')}")
            print(f"     - 初始资金: {agent_config.get('initial_cash', '未设置')}")
            
            # 显示验证状态
            if validation["valid"]:
                print(f"   ✅ 配置验证: 通过")
            else:
                print(f"   ❌ 配置验证: 失败")
                for error in validation["errors"]:
                    print(f"     - {error}")
            
            if validation["warnings"]:
                print(f"   ⚠️  警告:")
                for warning in validation["warnings"]:
                    print(f"     - {warning}")
            
        except Exception as e:
            print(f"❌ 显示配置摘要失败: {e}")
    
    def check_api_keys(self, market: str) -> Dict[str, Any]:
        """检查API密钥配置"""
        try:
            configs = self.config_manager.get_available_configs()
            if market not in configs:
                return {"error": f"市场 '{market}' 的配置不存在"}
            
            config = configs[market]
            common_settings = self.config_manager.get_common_settings()
            api_keys = common_settings.get('api_keys', {})
            
            # 根据市场类型检查所需的API密钥
            required_keys = []
            if market == 'us':
                required_keys = ['alphavantage', 'openai']
            elif market == 'cn':
                required_keys = ['tushare', 'openai']
            elif market == 'crypto':
                required_keys = ['binance', 'binance_secret', 'openai']
            
            key_status = {}
            all_configured = True
            
            for key in required_keys:
                value = api_keys.get(key, '')
                is_configured = value and not value.startswith('YOUR_')
                key_status[key] = {
                    "configured": is_configured,
                    "value": value if is_configured else "未配置"
                }
                if not is_configured:
                    all_configured = False
            
            return {
                "market": market,
                "all_configured": all_configured,
                "keys": key_status,
                "required_keys": required_keys
            }
            
        except Exception as e:
            return {"error": str(e)}

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI-Trader 配置切换工具")
    parser.add_argument("--list", "-l", action="store_true", help="列出所有可用模式")
    parser.add_argument("--switch", "-s", type=str, help="切换到指定模式 (us/cn/crypto)")
    parser.add_argument("--validate", "-v", type=str, help="验证指定模式的配置")
    parser.add_argument("--summary", "--info", type=str, help="显示指定模式的配置摘要")
    parser.add_argument("--check-keys", "-k", type=str, help="检查指定模式的API密钥配置")
    parser.add_argument("--no-validate", action="store_true", help="切换模式时不验证配置")
    
    args = parser.parse_args()
    
    switcher = ConfigSwitcher()
    
    if args.list:
        modes = switcher.list_available_modes()
        if modes:
            print("📋 可用模式列表:")
            for market, info in modes.items():
                active = "🟢" if info["is_active"] else "⚪"
                status = "✅ 已启用" if info["enabled"] else "❌ 已禁用"
                validation = "✅ 有效" if info["validation"]["valid"] else "❌ 无效"
                
                print(f"{active} {market.upper()}: {info['name']}")
                print(f"   状态: {status}")
                print(f"   验证: {validation}")
                print(f"   代理: {info['agent_type']}")
                print(f"   数据源: {info['data_source']}")
                print(f"   描述: {info['description']}")
                print()
        else:
            print("❌ 没有可用的模式")
    
    elif args.switch:
        market = args.switch.lower()
        validate = not args.no_validate
        success = switcher.switch_to_market(market, validate=validate)
        if success:
            print(f"\n🎉 成功切换到 {market.upper()} 模式")
            print("💡 提示: 使用 --check-keys 检查API密钥配置")
        else:
            print(f"\n❌ 切换到 {market.upper()} 模式失败")
            sys.exit(1)
    
    elif args.validate:
        market = args.validate.lower()
        validation = switcher.validate_market_config(market)
        
        print(f"🔍 {market.upper()} 配置验证结果:")
        if validation["valid"]:
            print("✅ 配置验证通过")
        else:
            print("❌ 配置验证失败")
            print("错误:")
            for error in validation["errors"]:
                print(f"   - {error}")
        
        if validation["warnings"]:
            print("⚠️  警告:")
            for warning in validation["warnings"]:
                print(f"   - {warning}")
    
    elif args.summary:
        market = args.summary.lower()
        switcher.show_config_summary(market)
    
    elif args.check_keys:
        market = args.check_keys.lower()
        result = switcher.check_api_keys(market)
        
        if "error" in result:
            print(f"❌ 检查API密钥失败: {result['error']}")
        else:
            print(f"🔑 {market.upper()} API密钥检查:")
            print(f"全部配置: {'✅ 是' if result['all_configured'] else '❌ 否'}")
            print()
            
            for key, status in result["keys"].items():
                configured = "✅ 已配置" if status["configured"] else "❌ 未配置"
                print(f"{key}: {configured}")
                if not status["configured"]:
                    print(f"   期望值: {status['value']}")
                print()
    
    else:
        # 默认显示帮助
        parser.print_help()
        print("\n💡 示例:")
        print("  python3 scripts/config_switcher.py --list")
        print("  python3 scripts/config_switcher.py --switch us")
        print("  python3 scripts/config_switcher.py --switch crypto --no-validate")
        print("  python3 scripts/config_switcher.py --validate cn")
        print("  python3 scripts/config_switcher.py --summary us")
        print("  python3 scripts/config_switcher.py --check-keys crypto")

if __name__ == "__main__":
    main()