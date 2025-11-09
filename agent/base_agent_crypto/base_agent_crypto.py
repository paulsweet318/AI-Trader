"""
币安数字货币交易智能体
基于AI-Trader框架的加密货币交易专用智能体
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal, ROUND_DOWN

from ..base_agent.base_agent import BaseAgent


class BaseAgentCrypto(BaseAgent):
    """
    币安数字货币交易智能体
    专门用于处理加密货币交易的智能体类
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.market = "crypto"
        self.exchange = "binance"
        self.testnet_enabled = kwargs.get('testnet_enabled', True)
        
        # 加密货币特定配置
        self.trading_pairs = [
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "DOTUSDT",
            "XRPUSDT", "LTCUSDT", "LINKUSDT", "BCHUSDT", "XLMUSDT"
        ]
        
        # 交易精度配置
        self.precision_config = {
            "BTCUSDT": {"quantity": 6, "price": 2},
            "ETHUSDT": {"quantity": 5, "price": 2},
            "BNBUSDT": {"quantity": 4, "price": 2},
            "ADAUSDT": {"quantity": 0, "price": 4},
            "DOTUSDT": {"quantity": 3, "price": 3},
            "XRPUSDT": {"quantity": 1, "price": 4},
            "LTCUSDT": {"quantity": 3, "price": 2},
            "LINKUSDT": {"quantity": 2, "price": 3},
            "BCHUSDT": {"quantity": 3, "price": 2},
            "XLMUSDT": {"quantity": 1, "price": 5}
        }
        
        # 风险管理配置
        self.risk_config = {
            "max_position_size": 10000.0,
            "max_daily_loss": 1000.0,
            "stop_loss_percentage": 5.0,
            "take_profit_percentage": 10.0,
            "max_open_orders": 10
        }
        
        self.logger = logging.getLogger(__name__)
    
    def format_crypto_position(self, symbol: str, quantity: float) -> str:
        """
        格式化加密货币持仓显示
        """
        if symbol in self.precision_config:
            precision = self.precision_config[symbol]["quantity"]
            quantity = Decimal(str(quantity)).quantize(
                Decimal('0.' + '0' * precision), 
                rounding=ROUND_DOWN
            )
        return f"{symbol}: {quantity}"
    
    def validate_crypto_symbol(self, symbol: str) -> bool:
        """
        验证加密货币交易对是否有效
        """
        return symbol.upper() in self.trading_pairs
    
    def get_crypto_precision(self, symbol: str) -> Dict[str, int]:
        """
        获取指定交易对的精度配置
        """
        symbol = symbol.upper()
        if symbol in self.precision_config:
            return self.precision_config[symbol]
        return {"quantity": 6, "price": 2}  # 默认精度
    
    def validate_order_quantity(self, symbol: str, quantity: float) -> tuple[bool, str]:
        """
        验证订单数量是否符合要求
        """
        symbol = symbol.upper()
        if not self.validate_crypto_symbol(symbol):
            return False, f"不支持的交易对: {symbol}"
        
        if quantity <= 0:
            return False, "订单数量必须大于0"
        
        # 检查最小交易量（简化版，实际应该查询交易所规则）
        min_quantities = {
            "BTCUSDT": 0.000001,
            "ETHUSDT": 0.00001,
            "BNBUSDT": 0.0001,
            "ADAUSDT": 1.0,
            "DOTUSDT": 0.001,
            "XRPUSDT": 0.1,
            "LTCUSDT": 0.001,
            "LINKUSDT": 0.01,
            "BCHUSDT": 0.001,
            "XLMUSDT": 0.1
        }
        
        min_qty = min_quantities.get(symbol, 0.000001)
        if quantity < min_qty:
            return False, f"{symbol} 最小交易量为 {min_qty}"
        
        return True, ""
    
    def calculate_position_size(self, symbol: str, available_cash: float, 
                               current_price: float, risk_percentage: float = 2.0) -> float:
        """
        计算基于风险管理的仓位大小
        """
        # 基于风险百分比计算仓位
        risk_amount = available_cash * (risk_percentage / 100)
        position_size = risk_amount / current_price
        
        # 应用精度限制
        precision = self.get_crypto_precision(symbol)["quantity"]
        position_size = float(Decimal(str(position_size)).quantize(
            Decimal('0.' + '0' * precision), 
            rounding=ROUND_DOWN
        ))
        
        return position_size
    
    def format_crypto_price(self, symbol: str, price: float) -> float:
        """
        格式化加密货币价格
        """
        precision = self.get_crypto_precision(symbol)["price"]
        return float(Decimal(str(price)).quantize(
            Decimal('0.' + '0' * precision), 
            rounding=ROUND_DOWN
        ))
    
    def get_crypto_market_info(self, symbol: str) -> Dict[str, Any]:
        """
        获取加密货币市场信息
        """
        symbol = symbol.upper()
        if not self.validate_crypto_symbol(symbol):
            return {}
        
        return {
            "symbol": symbol,
            "precision": self.get_crypto_precision(symbol),
            "min_quantity": self.get_min_quantity(symbol),
            "price_tick_size": self.get_price_tick_size(symbol),
            "is_active": True
        }
    
    def get_min_quantity(self, symbol: str) -> float:
        """
        获取最小交易量
        """
        min_quantities = {
            "BTCUSDT": 0.000001,
            "ETHUSDT": 0.00001,
            "BNBUSDT": 0.0001,
            "ADAUSDT": 1.0,
            "DOTUSDT": 0.001,
            "XRPUSDT": 0.1,
            "LTCUSDT": 0.001,
            "LINKUSDT": 0.01,
            "BCHUSDT": 0.001,
            "XLMUSDT": 0.1
        }
        return min_quantities.get(symbol.upper(), 0.000001)
    
    def get_price_tick_size(self, symbol: str) -> float:
        """
        获取价格最小变动单位
        """
        tick_sizes = {
            "BTCUSDT": 0.01,
            "ETHUSDT": 0.01,
            "BNBUSDT": 0.01,
            "ADAUSDT": 0.0001,
            "DOTUSDT": 0.001,
            "XRPUSDT": 0.0001,
            "LTCUSDT": 0.01,
            "LINKUSDT": 0.001,
            "BCHUSDT": 0.01,
            "XLMUSDT": 0.00001
        }
        return tick_sizes.get(symbol.upper(), 0.01)
    
    def format_agent_response(self, action: str, symbol: str, quantity: float, 
                            price: float, reason: str = "") -> str:
        """
        格式化智能体响应
        """
        formatted_quantity = self.format_crypto_position(symbol, quantity)
        formatted_price = self.format_crypto_price(symbol, price)
        
        response = f"【数字货币交易】\n"
        response += f"操作: {action}\n"
        response += f"交易对: {symbol}\n"
        response += f"数量: {formatted_quantity}\n"
        response += f"价格: ${formatted_price:.2f}\n"
        
        if reason:
            response += f"原因: {reason}\n"
        
        # 添加风险提示
        if action in ["买入", "卖出"]:
            response += "⚠️ 风险提示: 数字货币交易风险极高，请谨慎投资\n"
        
        return response
    
    def validate_crypto_trading_hours(self) -> bool:
        """
        验证加密货币交易时间（24小时交易）
        """
        # 加密货币7×24小时交易，始终返回True
        return True
    
    def get_crypto_trading_status(self) -> Dict[str, Any]:
        """
        获取加密货币交易状态
        """
        return {
            "market_open": True,
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "trading_pairs_count": len(self.trading_pairs),
            "testnet_enabled": self.testnet_enabled,
            "risk_management_enabled": True
        }
    
    def process_crypto_action(self, action: str, symbol: str, quantity: float, 
                            price: float, **kwargs) -> Dict[str, Any]:
        """
        处理加密货币交易动作
        """
        try:
            # 验证交易对
            if not self.validate_crypto_symbol(symbol):
                return {
                    "success": False,
                    "error": f"不支持的交易对: {symbol}",
                    "action": action,
                    "symbol": symbol
                }
            
            # 验证订单数量
            is_valid, error_msg = self.validate_order_quantity(symbol, quantity)
            if not is_valid:
                return {
                    "success": False,
                    "error": error_msg,
                    "action": action,
                    "symbol": symbol,
                    "quantity": quantity
                }
            
            # 格式化价格和数量
            formatted_quantity = self.format_crypto_position(symbol, quantity)
            formatted_price = self.format_crypto_price(symbol, price)
            
            # 生成交易ID（模拟）
            trade_id = f"crypto_{datetime.now().strftime('%Y%m%d%H%M%S')}_{symbol.lower()}"
            
            # 构建响应
            response = {
                "success": True,
                "trade_id": trade_id,
                "action": action,
                "symbol": symbol.upper(),
                "quantity": float(quantity),
                "price": float(formatted_price),
                "formatted_quantity": formatted_quantity,
                "timestamp": datetime.now().isoformat(),
                "testnet": self.testnet_enabled,
                "reason": kwargs.get("reason", "")
            }
            
            # 添加风险管理信息
            if action in ["买入", "卖出"]:
                response["risk_info"] = {
                    "stop_loss": formatted_price * (1 - self.risk_config["stop_loss_percentage"] / 100),
                    "take_profit": formatted_price * (1 + self.risk_config["take_profit_percentage"] / 100),
                    "position_size_usdt": float(quantity * formatted_price)
                }
            
            self.logger.info(f"加密货币交易执行成功: {response}")
            return response
            
        except Exception as e:
            self.logger.error(f"加密货币交易执行失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "action": action,
                "symbol": symbol,
                "quantity": quantity,
                "price": price
            }
    
    def get_crypto_summary(self) -> str:
        """
        获取加密货币交易摘要
        """
        status = self.get_crypto_trading_status()
        summary = f"【币安数字货币交易智能体】\n"
        summary += f"交易对数量: {status['trading_pairs_count']}\n"
        summary += f"测试网络: {'启用' if status['testnet_enabled'] else '禁用'}\n"
        summary += f"风险管理: {'启用' if status['risk_management_enabled'] else '禁用'}\n"
        summary += f"当前时间: {status['current_time']}\n"
        summary += f"市场状态: {'24小时交易' if status['market_open'] else '暂停交易'}\n"
        
        # 显示支持的交易对
        summary += f"\n支持的交易对: {', '.join(self.trading_pairs[:5])}...\n"
        
        return summary