"""
AI-Trader 配置管理API服务
提供RESTful API用于管理多市场配置
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs.config_manager import ConfigManager

app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 全局配置管理器
config_manager = ConfigManager()

# 配置管理API路由

@app.route('/')
def index():
    """配置管理主页"""
    return render_template_string(CONFIG_HTML_TEMPLATE)

@app.route('/api/config/status')
def get_status():
    """获取配置系统状态"""
    try:
        available_configs = config_manager.get_available_configs()
        active_config = config_manager.get_active_config()
        
        return jsonify({
            "success": True,
            "data": {
                "available_markets": list(available_configs.keys()),
                "active_market": active_config.get("active_market") if active_config else None,
                "total_configs": len(available_configs),
                "config_dir": str(config_manager.config_dir)
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/config/markets')
def get_markets():
    """获取所有市场配置"""
    try:
        configs = config_manager.get_available_configs()
        markets = []
        
        for market, config in configs.items():
            validation = config_manager.validate_config(market, config)
            markets.append({
                "market": market,
                "name": config.get("name", market.upper()),
                "description": config.get("description", ""),
                "enabled": config.get("enabled", True),
                "agent_type": config.get("agent_type", ""),
                "data_source": config.get("data_source", ""),
                "validation": validation,
                "last_modified": os.path.getmtime(config_manager.config_templates[market])
            })
        
        return jsonify({
            "success": True,
            "data": {
                "markets": markets,
                "total": len(markets)
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/config/market/<market>')
def get_market_config(market):
    """获取指定市场的配置"""
    try:
        configs = config_manager.get_available_configs()
        if market not in configs:
            return jsonify({
                "success": False,
                "error": f"市场 {market} 的配置不存在"
            }), 404
        
        config = configs[market]
        validation = config_manager.validate_config(market, config)
        
        return jsonify({
            "success": True,
            "data": {
                "market": market,
                "config": config,
                "validation": validation
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/config/market/<market>', methods=['PUT'])
def update_market_config(market):
    """更新指定市场的配置"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "请求体不能为空"
            }), 400
        
        # 更新配置
        updated_config = config_manager.update_config(market, data)
        
        # 验证更新后的配置
        validation = config_manager.validate_config(market, updated_config)
        
        return jsonify({
            "success": True,
            "data": {
                "market": market,
                "config": updated_config,
                "validation": validation,
                "message": "配置更新成功"
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/config/activate/<market>', methods=['POST'])
def activate_market(market):
    """激活指定市场"""
    try:
        configs = config_manager.get_available_configs()
        if market not in configs:
            return jsonify({
                "success": False,
                "error": f"市场 {market} 的配置不存在"
            }), 404
        
        config = configs[market]
        validation = config_manager.validate_config(market, config)
        
        if not validation["valid"]:
            return jsonify({
                "success": False,
                "error": "配置验证失败",
                "validation": validation
            }), 400
        
        # 激活配置
        active_config = config_manager.set_active_config(market, config)
        
        return jsonify({
            "success": True,
            "data": {
                "market": market,
                "active_config": active_config,
                "message": f"市场 {market} 已激活"
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/config/active')
def get_active_config():
    """获取当前激活的配置"""
    try:
        active_config = config_manager.get_active_config()
        if not active_config:
            return jsonify({
                "success": False,
                "error": "没有激活的配置"
            }), 404
        
        return jsonify({
            "success": True,
            "data": active_config
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/config/common-settings')
def get_common_settings():
    """获取通用设置"""
    try:
        settings = config_manager.get_common_settings()
        return jsonify({
            "success": True,
            "data": settings
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/config/common-settings', methods=['PUT'])
def update_common_settings():
    """更新通用设置"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "请求体不能为空"
            }), 400
        
        settings = config_manager.update_common_settings(data)
        
        return jsonify({
            "success": True,
            "data": settings,
            "message": "通用设置更新成功"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/config/multi-mode')
def get_multi_mode_config():
    """获取多模式配置"""
    try:
        config_file = config_manager.multi_mode_config
        if not config_file.exists():
            # 创建默认的多模式配置
            config_manager.create_multi_mode_config()
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return jsonify({
            "success": True,
            "data": config
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/config/multi-mode', methods=['PUT'])
def update_multi_mode_config():
    """更新多模式配置"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "请求体不能为空"
            }), 400
        
        # 更新多模式配置
        with open(config_manager.multi_mode_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 深度更新配置
        def deep_update(base, update):
            for key, value in update.items():
                if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                    deep_update(base[key], value)
                else:
                    base[key] = value
        
        deep_update(config, data)
        
        # 保存更新
        with open(config_manager.multi_mode_config, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            "success": True,
            "data": config,
            "message": "多模式配置更新成功"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/config/validate/<market>')
def validate_config(market):
    """验证指定市场的配置"""
    try:
        configs = config_manager.get_available_configs()
        if market not in configs:
            return jsonify({
                "success": False,
                "error": f"市场 {market} 的配置不存在"
            }), 404
        
        config = configs[market]
        validation = config_manager.validate_config(market, config)
        
        return jsonify({
            "success": True,
            "data": {
                "market": market,
                "validation": validation
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/config/export/<market>')
def export_config(market):
    """导出配置"""
    try:
        output_file = f"exported_{market}_config.json"
        config_manager.export_config(market, output_file)
        
        return jsonify({
            "success": True,
            "data": {
                "market": market,
                "export_file": output_file,
                "message": "配置导出成功"
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/config/import/<market>", methods=['POST'])
def import_config(market):
    """导入配置"""
    try:
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "没有上传文件"
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "没有选择文件"
            }), 400
        
        # 保存上传的文件
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        file_path = upload_dir / file.filename
        file.save(file_path)
        
        # 导入配置
        config_manager.import_config(market, str(file_path))
        
        # 清理上传文件
        file_path.unlink()
        
        return jsonify({
            "success": True,
            "data": {
                "market": market,
                "message": "配置导入成功"
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# 前端HTML模板
CONFIG_HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-Trader 配置管理</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .config-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .config-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .config-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        }
        
        .config-card.active {
            border: 3px solid #4CAF50;
            box-shadow: 0 0 20px rgba(76, 175, 80, 0.3);
        }
        
        .config-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }
        
        .market-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .market-title {
            font-size: 1.3rem;
            font-weight: bold;
            color: #333;
        }
        
        .market-status {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .status-enabled {
            background: #e8f5e8;
            color: #4CAF50;
        }
        
        .status-disabled {
            background: #ffebee;
            color: #f44336;
        }
        
        .market-description {
            color: #666;
            margin-bottom: 15px;
            line-height: 1.4;
        }
        
        .market-info {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .info-item {
            background: #f8f9fa;
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 0.9rem;
            color: #555;
        }
        
        .info-label {
            font-weight: bold;
            color: #333;
        }
        
        .validation-status {
            margin-bottom: 15px;
        }
        
        .validation-valid {
            color: #4CAF50;
            font-weight: bold;
        }
        
        .validation-invalid {
            color: #f44336;
            font-weight: bold;
        }
        
        .validation-warnings {
            color: #ff9800;
            font-size: 0.9rem;
            margin-top: 5px;
        }
        
        .card-actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 10px 16px;
            border: none;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-success {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
        }
        
        .btn-success:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
        }
        
        .btn-warning {
            background: linear-gradient(135deg, #ff9800, #f57c00);
            color: white;
        }
        
        .btn-warning:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 152, 0, 0.4);
        }
        
        .btn-info {
            background: linear-gradient(135deg, #17a2b8, #138496);
            color: white;
        }
        
        .btn-info:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(23, 162, 184, 0.4);
        }
        
        .common-settings {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        .settings-section {
            margin-bottom: 25px;
        }
        
        .settings-title {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 5px;
        }
        
        .api-key-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        
        .api-key-name {
            font-weight: bold;
            color: #333;
        }
        
        .api-key-status {
            font-size: 0.9rem;
        }
        
        .status-configured {
            color: #4CAF50;
        }
        
        .status-not-configured {
            color: #f44336;
        }
        
        .loading {
            text-align: center;
            padding: 50px;
            color: #666;
        }
        
        .error-message {
            background: #ffebee;
            color: #f44336;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #f44336;
        }
        
        .success-message {
            background: #e8f5e8;
            color: #4CAF50;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #4CAF50;
        }
        
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
        }
        
        .modal-content {
            background: white;
            margin: 5% auto;
            padding: 30px;
            border-radius: 15px;
            width: 90%;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }
        
        .close {
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            color: #999;
        }
        
        .close:hover {
            color: #333;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }
        
        .form-control {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1rem;
        }
        
        .form-control:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 5px rgba(102, 126, 234, 0.3);
        }
        
        .json-editor {
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            background: #f8f9fa;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .config-grid {
                grid-template-columns: 1fr;
            }
            
            .card-actions {
                flex-direction: column;
            }
            
            .btn {
                width: 100%;
                justify-content: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI-Trader 配置管理</h1>
            <p>多市场交易系统配置管理面板</p>
        </div>
        
        <div id="message-container"></div>
        
        <div class="common-settings">
            <div class="settings-section">
                <h3 class="settings-title">🔑 API密钥配置</h3>
                <div id="api-keys-container">
                    <div class="loading">加载中...</div>
                </div>
            </div>
            
            <div class="settings-section">
                <h3 class="settings-title">⚙️ 通用设置</h3>
                <div id="common-settings-container">
                    <div class="loading">加载中...</div>
                </div>
            </div>
        </div>
        
        <div id="config-container">
            <div class="loading">加载市场配置中...</div>
        </div>
    </div>
    
    <!-- 配置编辑模态框 -->
    <div id="config-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 id="modal-title">编辑配置</h3>
                <span class="close">&times;</span>
            </div>
            <div id="modal-body">
                <div class="form-group">
                    <label class="form-label">配置内容 (JSON格式)</label>
                    <textarea id="config-editor" class="form-control json-editor" rows="20"></textarea>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-primary" onclick="saveConfig()">保存配置</button>
                <button type="button" class="btn btn-warning" onclick="closeModal()">取消</button>
            </div>
        </div>
    </div>
    
    <script>
        let currentMarket = null;
        let marketsData = {};
        
        // 初始化
        document.addEventListener('DOMContentLoaded', function() {
            loadMarkets();
            loadCommonSettings();
            
            // 模态框事件
            const modal = document.getElementById('config-modal');
            const closeBtn = document.querySelector('.close');
            
            closeBtn.onclick = function() {
                closeModal();
            }
            
            window.onclick = function(event) {
                if (event.target == modal) {
                    closeModal();
                }
            }
        });
        
        // 显示消息
        function showMessage(message, type = 'success') {
            const container = document.getElementById('message-container');
            const messageDiv = document.createElement('div');
            messageDiv.className = type === 'success' ? 'success-message' : 'error-message';
            messageDiv.textContent = message;
            container.appendChild(messageDiv);
            
            setTimeout(() => {
                messageDiv.remove();
            }, 5000);
        }
        
        // 加载市场配置
        async function loadMarkets() {
            try {
                const response = await fetch('/api/config/markets');
                const result = await response.json();
                
                if (result.success) {
                    marketsData = result.data.markets;
                    renderMarkets(marketsData);
                } else {
                    showMessage('加载市场配置失败: ' + result.error, 'error');
                }
            } catch (error) {
                showMessage('加载市场配置失败: ' + error.message, 'error');
            }
        }
        
        // 渲染市场配置
        function renderMarkets(markets) {
            const container = document.getElementById('config-container');
            
            if (markets.length === 0) {
                container.innerHTML = '<div class="error-message">没有可用的市场配置</div>';
                return;
            }
            
            const activeMarket = markets.find(m => m.enabled) || markets[0];
            
            container.innerHTML = '<div class="config-grid">' + 
                markets.map(market => {
                    const isActive = market.market === activeMarket.market;
                    const validation = market.validation;
                    
                    return `
                        <div class="config-card ${isActive ? 'active' : ''}" id="card-${market.market}">
                            <div class="market-header">
                                <div class="market-title">${market.name}</div>
                                <div class="market-status ${market.enabled ? 'status-enabled' : 'status-disabled'}">
                                    ${market.enabled ? '已启用' : '已禁用'}
                                </div>
                            </div>
                            <div class="market-description">${market.description}</div>
                            <div class="market-info">
                                <div class="info-item">
                                    <span class="info-label">代理类型:</span> ${market.agent_type}
                                </div>
                                <div class="info-item">
                                    <span class="info-label">数据源:</span> ${market.data_source}
                                </div>
                            </div>
                            <div class="validation-status">
                                <div class="${validation.valid ? 'validation-valid' : 'validation-invalid'}">
                                    ${validation.valid ? '✅ 配置有效' : '❌ 配置无效'}
                                </div>
                                ${validation.warnings.length > 0 ? 
                                    `<div class="validation-warnings">⚠️ ${validation.warnings.join(', ')}</div>` : 
                                    ''}
                            </div>
                            <div class="card-actions">
                                <button class="btn btn-primary" onclick="editConfig('${market.market}')">
                                    ✏️ 编辑配置
                                </button>
                                <button class="btn btn-info" onclick="validateConfig('${market.market}')">
                                    🔍 验证配置
                                </button>
                                ${!isActive ? 
                                    `<button class="btn btn-success" onclick="activateMarket('${market.market}')">
                                        ▶️ 激活市场
                                    </button>` : 
                                    `<button class="btn btn-warning" disabled>
                                        ✅ 已激活
                                    </button>`}
                            </div>
                        </div>
                    `;
                }).join('') + 
            '</div>';
        }
        
        // 加载通用设置
        async function loadCommonSettings() {
            try {
                const response = await fetch('/api/config/common-settings');
                const result = await response.json();
                
                if (result.success) {
                    renderCommonSettings(result.data);
                } else {
                    showMessage('加载通用设置失败: ' + result.error, 'error');
                }
            } catch (error) {
                showMessage('加载通用设置失败: ' + error.message, 'error');
            }
        }
        
        // 渲染通用设置
        function renderCommonSettings(settings) {
            const apiKeysContainer = document.getElementById('api-keys-container');
            const settingsContainer = document.getElementById('common-settings-container');
            
            // API密钥
            const apiKeys = settings.api_keys || {};
            apiKeysContainer.innerHTML = Object.entries(apiKeys).map(([key, value]) => {
                const isConfigured = value && !value.startsWith('YOUR_');
                return `
                    <div class="api-key-item">
                        <div class="api-key-name">${key.toUpperCase()}</div>
                        <div class="api-key-status ${isConfigured ? 'status-configured' : 'status-not-configured'}">
                            ${isConfigured ? '✅ 已配置' : '❌ 未配置'}
                        </div>
                    </div>
                `;
            }).join('');
            
            // 其他设置
            settingsContainer.innerHTML = `
                <div style="display: flex; flex-wrap: wrap; gap: 15px;">
                    <div class="info-item">
                        <span class="info-label">并行模式:</span> ${settings.parallel_mode ? '启用' : '禁用'}
                    </div>
                    <div class="info-item">
                        <span class="info-label">保存结果:</span> ${settings.save_results ? '是' : '否'}
                    </div>
                    <div class="info-item">
                        <span class="info-label">输出格式:</span> ${settings.output_format}
                    </div>
                    <div class="info-item">
                        <span class="info-label">日志级别:</span> ${settings.log_level}
                    </div>
                </div>
            `;
        }
        
        // 编辑配置
        async function editConfig(market) {
            try {
                const response = await fetch(`/api/config/market/${market}`);
                const result = await response.json();
                
                if (result.success) {
                    currentMarket = market;
                    document.getElementById('modal-title').textContent = `编辑 ${result.data.config.name} 配置`;
                    document.getElementById('config-editor').value = JSON.stringify(result.data.config, null, 2);
                    document.getElementById('config-modal').style.display = 'block';
                } else {
                    showMessage('加载配置失败: ' + result.error, 'error');
                }
            } catch (error) {
                showMessage('加载配置失败: ' + error.message, 'error');
            }
        }
        
        // 保存配置
        async function saveConfig() {
            if (!currentMarket) return;
            
            try {
                const configText = document.getElementById('config-editor').value;
                const config = JSON.parse(configText);
                
                const response = await fetch(`/api/config/market/${currentMarket}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(config)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showMessage('配置保存成功');
                    closeModal();
                    loadMarkets();
                } else {
                    showMessage('保存配置失败: ' + result.error, 'error');
                }
            } catch (error) {
                showMessage('保存配置失败: ' + error.message, 'error');
            }
        }
        
        // 验证配置
        async function validateConfig(market) {
            try {
                const response = await fetch(`/api/config/validate/${market}`);
                const result = await response.json();
                
                if (result.success) {
                    const validation = result.data.validation;
                    if (validation.valid) {
                        showMessage('✅ 配置验证通过');
                    } else {
                        showMessage('❌ 配置验证失败: ' + validation.errors.join(', '), 'error');
                    }
                } else {
                    showMessage('验证配置失败: ' + result.error, 'error');
                }
            } catch (error) {
                showMessage('验证配置失败: ' + error.message, 'error');
            }
        }
        
        // 激活市场
        async function activateMarket(market) {
            try {
                const response = await fetch(`/api/config/activate/${market}`, {
                    method: 'POST'
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showMessage(`✅ 市场 ${market} 已激活`);
                    loadMarkets();
                } else {
                    showMessage('激活市场失败: ' + result.error, 'error');
                }
            } catch (error) {
                showMessage('激活市场失败: ' + error.message, 'error');
            }
        }
        
        // 关闭模态框
        function closeModal() {
            document.getElementById('config-modal').style.display = 'none';
            currentMarket = null;
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🚀 启动AI-Trader配置管理API服务...")
    print("📊 配置管理界面: http://localhost:5000")
    print("🔧 API文档: http://localhost:5000/api/*")
    
    # 确保配置目录存在
    os.makedirs("configs", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    
    # 初始化配置
    if not config_manager.multi_mode_config.exists():
        print("📝 初始化默认配置...")
        config_manager.create_default_configs()
        config_manager.create_multi_mode_config()
        print("✅ 默认配置创建完成")
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=5000, debug=True)