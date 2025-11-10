"""
AI-Trader 多市场配置管理器
支持美股、A股、数字货币三种模式的统一配置管理
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class MarketConfig:
    """市场配置基类"""
    name: str
    description: str
    agent_type: str
    market: str
    enabled: bool = True


@dataclass 
class USMarketConfig(MarketConfig):
    """美股市场配置"""
    def __init__(self):
        super().__init__(
            name="美股市场",
            description="纳斯达克100成分股交易",
            agent_type="BaseAgent",
            market="us"
        )


@dataclass
class CNMarketConfig(MarketConfig):
    """A股市场配置"""
    def __init__(self):
        super().__init__(
            name="A股市场", 
            description="上证50成分股交易",
            agent_type="BaseAgentAStock",
            market="cn"
        )


@dataclass
class CryptoMarketConfig(MarketConfig):
    """数字货币市场配置"""
    def __init__(self):
        super().__init__(
            name="数字货币市场",
            description="币安交易所加密货币交易", 
            agent_type="BaseAgentCrypto",
            market="crypto"
        )


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.active_config_file = self.config_dir / "active_config.json"
        self.config_templates = {
            "us": self.config_dir / "us_market_config.json",
            "cn": self.config_dir / "cn_market_config.json", 
            "crypto": self.config_dir / "crypto_market_config.json"
        }
        self.multi_mode_config = self.config_dir / "multi_mode_config.json"
        
    def create_default_configs(self):
        """创建默认配置文件"""
        # 美股配置
        us_config = {
            "name": "美股市场配置",
            "description": "纳斯达克100成分股交易配置",
            "market": "us",
            "agent_type": "BaseAgent",
            "date_range": {
                "init_date": "2025-10-01",
                "end_date": "2025-10-21"
            },
            "models": [
                {
                    "name": "claude-3.7-sonnet",
                    "basemodel": "anthropic/claude-3.7-sonnet",
                    "signature": "claude-3.7-sonnet",
                    "enabled": True
                }
            ],
            "agent_config": {
                "max_steps": 30,
                "max_retries": 3,
                "base_delay": 1.0,
                "initial_cash": 10000.0
            },
            "data_source": "alphavantage",
            "api_key_required": ["alphavantage", "openai"],
            "enabled": True
        }
        
        # A股配置
        cn_config = {
            "name": "A股市场配置",
            "description": "上证50成分股交易配置",
            "market": "cn", 
            "agent_type": "BaseAgentAStock",
            "date_range": {
                "init_date": "2025-10-01",
                "end_date": "2025-11-03"
            },
            "models": [
                {
                    "name": "claude-3.7-sonnet",
                    "basemodel": "anthropic/claude-3.7-sonnet",
                    "signature": "claude-3.7-sonnet",
                    "enabled": True
                }
            ],
            "agent_config": {
                "max_steps": 2,
                "max_retries": 3,
                "base_delay": 1.0,
                "initial_cash": 10000.0
            },
            "data_source": "tushare",
            "api_key_required": ["tushare", "openai"],
            "enabled": True
        }
        
        # 数字货币配置
        crypto_config = {
            "name": "数字货币市场配置",
            "description": "币安交易所加密货币交易配置",
            "market": "crypto",
            "agent_type": "BaseAgentCrypto", 
            "exchange": "binance",
            "date_range": {
                "init_date": "2025-10-01",
                "end_date": "2025-10-21"
            },
            "models": [
                {
                    "name": "claude-3.7-sonnet",
                    "basemodel": "anthropic/claude-3.7-sonnet",
                    "signature": "claude-3.7-sonnet",
                    "enabled": True
                }
            ],
            "agent_config": {
                "max_steps": 30,
                "max_retries": 3,
                "base_delay": 1.0,
                "initial_cash": 10000.0,
                "testnet_enabled": True
            },
            "data_source": "binance",
            "api_key_required": ["binance", "binance_secret", "openai"],
            "enabled": True
        }
        
        # 保存配置文件
        configs = {
            "us": us_config,
            "cn": cn_config,
            "crypto": crypto_config
        }
        
        for market, config in configs.items():
            config_file = self.config_templates[market]
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
        return configs
    
    def create_multi_mode_config(self, enabled_modes: List[str] = None):
        """创建多模式配置"""
        if enabled_modes is None:
            enabled_modes = ["us", "cn", "crypto"]
            
        multi_config = {
            "name": "AI-Trader 多市场配置",
            "description": "支持美股、A股、数字货币的多市场交易系统",
            "version": "1.0.0",
            "active_modes": enabled_modes,
            "mode_configs": {
                "us": {
                    "name": "美股市场",
                    "description": "纳斯达克100成分股交易",
                    "config_file": "us_market_config.json",
                    "enabled": "us" in enabled_modes
                },
                "cn": {
                    "name": "A股市场", 
                    "description": "上证50成分股交易",
                    "config_file": "cn_market_config.json",
                    "enabled": "cn" in enabled_modes
                },
                "crypto": {
                    "name": "数字货币市场",
                    "description": "币安交易所加密货币交易",
                    "config_file": "crypto_market_config.json", 
                    "enabled": "crypto" in enabled_modes
                }
            },
            "common_settings": {
                "api_keys": {
                    "alphavantage": "YOUR_ALPHAVANTAGE_API_KEY",
                    "tushare": "YOUR_TUSHARE_API_KEY",
                    "binance": "YOUR_BINANCE_API_KEY",
                    "binance_secret": "YOUR_BINANCE_API_SECRET",
                    "openai": "YOUR_OPENAI_API_KEY"
                },
                "parallel_mode": False,
                "save_results": True,
                "output_format": "json",
                "log_level": "INFO"
            },
            "ui_settings": {
                "theme": "dark",
                "refresh_interval": 30,
                "auto_save": True,
                "confirm_before_trade": True
            }
        }
        
        with open(self.multi_mode_config, 'w', encoding='utf-8') as f:
            json.dump(multi_config, f, indent=2, ensure_ascii=False)
            
        return multi_config
    
    def get_available_configs(self) -> Dict[str, Dict]:
        """获取所有可用配置"""
        configs = {}
        
        # 读取各个市场的配置文件
        for market, config_file in self.config_templates.items():
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        configs[market] = json.load(f)
                except Exception as e:
                    print(f"读取配置文件 {config_file} 失败: {e}")
                    
        return configs
    
    def get_active_config(self) -> Optional[Dict]:
        """获取当前激活的配置"""
        if self.active_config_file.exists():
            try:
                with open(self.active_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"读取激活配置失败: {e}")
        return None
    
    def set_active_config(self, market: str, config: Dict):
        """设置激活的配置"""
        active_config = {
            "active_market": market,
            "config": config,
            "timestamp": self._get_timestamp()
        }
        
        with open(self.active_config_file, 'w', encoding='utf-8') as f:
            json.dump(active_config, f, indent=2, ensure_ascii=False)
            
        return active_config
    
    def update_config(self, market: str, updates: Dict) -> Dict:
        """更新配置"""
        config_file = self.config_templates.get(market)
        if not config_file or not config_file.exists():
            raise ValueError(f"市场 {market} 的配置文件不存在")
            
        # 读取现有配置
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # 更新配置
        self._deep_update(config, updates)
        
        # 保存更新后的配置
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        return config
    
    def validate_config(self, market: str, config: Dict) -> Dict[str, Any]:
        """验证配置"""
        errors = []
        warnings = []
        
        # 基本验证
        required_fields = ["name", "market", "agent_type"]
        for field in required_fields:
            if field not in config:
                errors.append(f"缺少必填字段: {field}")
                
        # API密钥验证
        if "api_key_required" in config:
            common_settings = self.get_common_settings()
            api_keys = common_settings.get("api_keys", {})
            
            for key_name in config["api_key_required"]:
                if key_name not in api_keys or api_keys[key_name].startswith("YOUR_"):
                    warnings.append(f"API密钥未配置: {key_name}")
                    
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def get_common_settings(self) -> Dict:
        """获取通用设置"""
        if self.multi_mode_config.exists():
            try:
                with open(self.multi_mode_config, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get("common_settings", {})
            except:
                pass
                
        # 返回默认设置
        return {
            "api_keys": {
                "alphavantage": "YOUR_ALPHAVANTAGE_API_KEY",
                "tushare": "YOUR_TUSHARE_API_KEY", 
                "binance": "YOUR_BINANCE_API_KEY",
                "binance_secret": "YOUR_BINANCE_API_SECRET",
                "openai": "YOUR_OPENAI_API_KEY"
            }
        }
    
    def update_common_settings(self, settings: Dict) -> Dict:
        """更新通用设置"""
        if self.multi_mode_config.exists():
            with open(self.multi_mode_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = self.create_multi_mode_config()
            
        # 更新通用设置
        if "common_settings" not in config:
            config["common_settings"] = {}
            
        self._deep_update(config["common_settings"], settings)
        
        # 保存更新
        with open(self.multi_mode_config, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        return config["common_settings"]
    
    def export_config(self, market: str, output_file: str):
        """导出配置"""
        config_file = self.config_templates.get(market)
        if not config_file or not config_file.exists():
            raise ValueError(f"市场 {market} 的配置文件不存在")
            
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        return str(output_path)
    
    def import_config(self, market: str, input_file: str):
        """导入配置"""
        config_file = self.config_templates.get(market)
        if not config_file:
            raise ValueError(f"不支持的市场: {market}")
            
        input_path = Path(input_file)
        if not input_path.exists():
            raise ValueError(f"导入文件不存在: {input_file}")
            
        with open(input_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # 验证配置
        validation = self.validate_config(market, config)
        if not validation["valid"]:
            raise ValueError(f"配置验证失败: {validation['errors']}")
            
        # 保存配置
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        return config
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict):
        """深度更新字典"""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# 全局配置管理器实例
config_manager = ConfigManager()


if __name__ == "__main__":
    # 初始化配置
    print("初始化AI-Trader配置管理器...")
    
    # 创建默认配置
    configs = config_manager.create_default_configs()
    print(f"✅ 创建了 {len(configs)} 个市场配置文件")
    
    # 创建多模式配置
    multi_config = config_manager.create_multi_mode_config()
    print(f"✅ 创建了多模式配置文件")
    
    # 显示可用配置
    available_configs = config_manager.get_available_configs()
    print(f"✅ 可用配置: {list(available_configs.keys())}")
    
    print("配置管理器初始化完成！")