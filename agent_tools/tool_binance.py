"""
币安数字货币交易MCP工具
Binance Cryptocurrency Trading MCP Tool

提供币安交易所的市场数据、账户管理和交易操作功能
Provides market data, account management, and trading operations for Binance exchange
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union
from decimal import Decimal

from dotenv import load_dotenv
from fastmcp import FastMCP
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from binance.enums import *

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# 从环境变量获取API密钥
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')
BINANCE_TESTNET = os.getenv('BINANCE_TESTNET', 'true').lower() == 'true'

# 币安API客户端初始化
if BINANCE_TESTNET:
    # 使用测试网络
    client = Client(
        api_key=BINANCE_API_KEY,
        api_secret=BINANCE_API_SECRET,
        testnet=True
    )
else:
    # 使用主网络
    client = Client(
        api_key=BINANCE_API_KEY,
        api_secret=BINANCE_API_SECRET,
        testnet=False
    )

# 初始化 MCP 服务
mcp = FastMCP("Binance")

@mcp.tool()
def get_binance_price(symbol: str) -> Dict[str, Union[str, float]]:
    """
    获取指定交易对的当前价格
    Get current price for specified trading pair
    
    Args:
        symbol: 交易对，如 "BTCUSDT", "ETHUSDT"
        
    Returns:
        包含价格信息的字典
    """
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        return {
            "symbol": symbol,
            "price": float(ticker["price"]),
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    except BinanceAPIException as e:
        logger.error(f"获取价格失败: {e}")
        return {
            "symbol": symbol,
            "error": str(e),
            "status": "error"
        }

@mcp.tool()
def get_binance_orderbook(symbol: str, limit: int = 100) -> Dict[str, any]:
    """
    获取订单簿数据
    Get order book depth data
    
    Args:
        symbol: 交易对
        limit: 深度限制，默认100
        
    Returns:
        订单簿数据
    """
    try:
        order_book = client.get_order_book(symbol=symbol, limit=limit)
        return {
            "symbol": symbol,
            "bids": [[float(price), float(qty)] for price, qty in order_book["bids"][:10]],  # 前10个买单
            "asks": [[float(price), float(qty)] for price, qty in order_book["asks"][:10]],  # 前10个卖单
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    except BinanceAPIException as e:
        logger.error(f"获取订单簿失败: {e}")
        return {
            "symbol": symbol,
            "error": str(e),
            "status": "error"
        }

@mcp.tool()
def get_binance_klines(symbol: str, interval: str = "1h", limit: int = 24) -> List[Dict[str, any]]:
    """
    获取K线数据
    Get K-line/candlestick data
    
    Args:
        symbol: 交易对
        interval: 时间间隔，如 "1m", "5m", "1h", "1d"
        limit: 数据条数限制，默认24
        
    Returns:
        K线数据列表
    """
    try:
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        formatted_klines = []
        
        for kline in klines:
            formatted_klines.append({
                "open_time": datetime.fromtimestamp(kline[0] / 1000).isoformat(),
                "open": float(kline[1]),
                "high": float(kline[2]),
                "low": float(kline[3]),
                "close": float(kline[4]),
                "volume": float(kline[5]),
                "close_time": datetime.fromtimestamp(kline[6] / 1000).isoformat(),
                "quote_asset_volume": float(kline[7]),
                "number_of_trades": int(kline[8])
            })
        
        return formatted_klines
    except BinanceAPIException as e:
        logger.error(f"获取K线数据失败: {e}")
        return [{
            "symbol": symbol,
            "error": str(e),
            "status": "error"
        }]

@mcp.tool()
def get_binance_24hr_ticker(symbol: str) -> Dict[str, any]:
    """
    获取24小时价格统计信息
    Get 24-hour price change statistics
    
    Args:
        symbol: 交易对
        
    Returns:
        24小时统计信息
    """
    try:
        ticker = client.get_ticker(symbol=symbol)
        return {
            "symbol": symbol,
            "price_change": float(ticker["priceChange"]),
            "price_change_percent": float(ticker["priceChangePercent"]),
            "weighted_avg_price": float(ticker["weightedAvgPrice"]),
            "last_price": float(ticker["lastPrice"]),
            "last_qty": float(ticker["lastQty"]),
            "bid_price": float(ticker["bidPrice"]),
            "bid_qty": float(ticker["bidQty"]),
            "ask_price": float(ticker["askPrice"]),
            "ask_qty": float(ticker["askQty"]),
            "open_price": float(ticker["openPrice"]),
            "high_price": float(ticker["highPrice"]),
            "low_price": float(ticker["lowPrice"]),
            "volume": float(ticker["volume"]),
            "quote_volume": float(ticker["quoteVolume"]),
            "open_time": datetime.fromtimestamp(ticker["openTime"] / 1000).isoformat(),
            "close_time": datetime.fromtimestamp(ticker["closeTime"] / 1000).isoformat(),
            "count": int(ticker["count"]),
            "status": "success"
        }
    except BinanceAPIException as e:
        logger.error(f"获取24小时统计失败: {e}")
        return {
            "symbol": symbol,
            "error": str(e),
            "status": "error"
        }

@mcp.tool()
def get_binance_account_info() -> Dict[str, any]:
    """
    获取账户信息
    Get account information and balances
    
    Returns:
        账户信息
    """
    try:
        account = client.get_account()
        
        # 过滤非零余额
        balances = []
        for balance in account["balances"]:
            free = float(balance["free"])
            locked = float(balance["locked"])
            if free > 0 or locked > 0:
                balances.append({
                    "asset": balance["asset"],
                    "free": free,
                    "locked": locked,
                    "total": free + locked
                })
        
        return {
            "account_type": account.get("accountType", "SPOT"),
            "can_trade": account.get("canTrade", False),
            "can_withdraw": account.get("canWithdraw", False),
            "can_deposit": account.get("canDeposit", False),
            "balances": balances,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    except BinanceAPIException as e:
        logger.error(f"获取账户信息失败: {e}")
        return {
            "error": str(e),
            "status": "error"
        }

@mcp.tool()
def place_binance_order(
    symbol: str,
    side: str,
    type_: str,
    quantity: float,
    price: Optional[float] = None,
    time_in_force: str = "GTC"
) -> Dict[str, any]:
    """
    下单交易
    Place a new order
    
    Args:
        symbol: 交易对
        side: 交易方向，"BUY" 或 "SELL"
        type_: 订单类型，"MARKET", "LIMIT"
        quantity: 数量
        price: 价格（限价单需要）
        time_in_force: 有效时间，默认GTC（Good Till Cancel）
        
    Returns:
        订单信息
    """
    try:
        # 安全检查 - 如果是主网络，添加额外警告
        if not BINANCE_TESTNET:
            logger.warning("⚠️  警告：您正在使用主网络进行交易，涉及真实资金！")
            return {
                "warning": "主网络交易涉及真实资金，请谨慎操作",
                "status": "cancelled"
            }
        
        order_params = {
            "symbol": symbol,
            "side": side,
            "type": type_,
            "quantity": quantity,
            "timeInForce": time_in_force
        }
        
        if type_ == "LIMIT" and price is not None:
            order_params["price"] = price
        
        order = client.create_order(**order_params)
        
        return {
            "symbol": symbol,
            "order_id": order["orderId"],
            "client_order_id": order["clientOrderId"],
            "transact_time": datetime.fromtimestamp(order["transactTime"] / 1000).isoformat(),
            "price": float(order.get("price", 0)),
            "orig_qty": float(order["origQty"]),
            "executed_qty": float(order["executedQty"]),
            "status": order["status"],
            "side": order["side"],
            "type": order["type"],
            "message": "订单创建成功" if BINANCE_TESTNET else "⚠️ 真实交易订单已创建"
        }
    except BinanceAPIException as e:
        logger.error(f"下单失败: {e}")
        return {
            "symbol": symbol,
            "error": str(e),
            "status": "error"
        }
    except BinanceOrderException as e:
        logger.error(f"订单异常: {e}")
        return {
            "symbol": symbol,
            "error": str(e),
            "status": "error"
        }

@mcp.tool()
def get_binance_open_orders(symbol: Optional[str] = None) -> List[Dict[str, any]]:
    """
    获取当前挂单
    Get current open orders
    
    Args:
        symbol: 交易对，可选，不传则返回所有挂单
        
    Returns:
        挂单列表
    """
    try:
        if symbol:
            orders = client.get_open_orders(symbol=symbol)
        else:
            orders = client.get_open_orders()
        
        formatted_orders = []
        for order in orders:
            formatted_orders.append({
                "symbol": order["symbol"],
                "order_id": order["orderId"],
                "client_order_id": order["clientOrderId"],
                "price": float(order["price"]),
                "orig_qty": float(order["origQty"]),
                "executed_qty": float(order["executedQty"]),
                "status": order["status"],
                "side": order["side"],
                "type": order["type"],
                "time_in_force": order["timeInForce"],
                "create_time": datetime.fromtimestamp(order["time"] / 1000).isoformat()
            })
        
        return formatted_orders
    except BinanceAPIException as e:
        logger.error(f"获取挂单失败: {e}")
        return [{
            "symbol": symbol or "ALL",
            "error": str(e),
            "status": "error"
        }]

@mcp.tool()
def cancel_binance_order(symbol: str, order_id: int) -> Dict[str, any]:
    """
    取消订单
    Cancel specific order
    
    Args:
        symbol: 交易对
        order_id: 订单ID
        
    Returns:
        取消结果
    """
    try:
        result = client.cancel_order(symbol=symbol, orderId=order_id)
        return {
            "symbol": symbol,
            "order_id": result["orderId"],
            "client_order_id": result["clientOrderId"],
            "status": result["status"],
            "message": "订单取消成功",
            "timestamp": datetime.now().isoformat()
        }
    except BinanceAPIException as e:
        logger.error(f"取消订单失败: {e}")
        return {
            "symbol": symbol,
            "order_id": order_id,
            "error": str(e),
            "status": "error"
        }

@mcp.tool()
def get_top_cryptocurrencies(limit: int = 10) -> List[Dict[str, any]]:
    """
    获取热门加密货币列表
    Get top cryptocurrencies by 24h volume
    
    Args:
        limit: 返回数量限制
        
    Returns:
        热门加密货币列表
    """
    try:
        tickers = client.get_ticker()
        
        # 按24小时成交量排序
        sorted_tickers = sorted(tickers, key=lambda x: float(x["quoteVolume"]), reverse=True)
        
        top_cryptos = []
        for ticker in sorted_tickers[:limit]:
            if "USDT" in ticker["symbol"]:  # 只返回USDT交易对
                top_cryptos.append({
                    "symbol": ticker["symbol"],
                    "price": float(ticker["lastPrice"]),
                    "price_change_24h": float(ticker["priceChange"]),
                    "price_change_percent_24h": float(ticker["priceChangePercent"]),
                    "volume_24h": float(ticker["volume"]),
                    "quote_volume_24h": float(ticker["quoteVolume"]),
                    "high_24h": float(ticker["highPrice"]),
                    "low_24h": float(ticker["lowPrice"])
                })
        
        return top_cryptos
    except BinanceAPIException as e:
        logger.error(f"获取热门加密货币失败: {e}")
        return [{
            "error": str(e),
            "status": "error"
        }]

## 以上通过装饰器已完成工具注册，无需手动返回工具列表

if __name__ == "__main__":
    port = int(os.getenv("BINANCE_HTTP_PORT", "8005"))
    mcp.run(transport="streamable-http", port=port)