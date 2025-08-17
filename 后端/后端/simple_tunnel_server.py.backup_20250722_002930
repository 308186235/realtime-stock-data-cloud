#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的测试服务器，用于Cloudflare隧道测试
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import json
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    """主页"""
    return jsonify({
        "status": "success",
        "message": "AI股票交易系统 - Cloudflare隧道测试成功！",
        "timestamp": datetime.now().isoformat(),
        "domain": "aigupiao.me",
        "version": "1.0.0"
    })

@app.route('/api/health')
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "service": "AI股票交易系统",
        "timestamp": datetime.now().isoformat(),
        "tunnel_status": "active"
    })

@app.route('/api/test')
def test_endpoint():
    """测试端点"""
    return jsonify({
        "message": "测试成功！",
        "data": {
            "server": "Flask",
            "tunnel": "Cloudflare",
            "domain": "aigupiao.me",
            "timestamp": datetime.now().isoformat()
        }
    })

@app.route('/api/mobile/test')
def mobile_test():
    """手机端测试"""
    user_agent = request.headers.get('User-Agent', '')
    is_mobile = any(device in user_agent.lower() for device in ['mobile', 'android', 'iphone', 'ipad'])
    
    return jsonify({
        "message": "手机端连接测试成功！",
        "device_type": "mobile" if is_mobile else "desktop",
        "user_agent": user_agent,
        "timestamp": datetime.now().isoformat(),
        "status": "connected"
    })

@app.route('/api/stock/test')
def stock_test():
    """股票数据测试"""
    return jsonify({
        "message": "股票数据接口测试",
        "sample_data": {
            "symbol": "000001.SZ",
            "name": "平安银行",
            "price": 12.34,
            "change": 0.12,
            "change_percent": 0.98
        },
        "timestamp": datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not Found",
        "message": "请求的资源不存在",
        "status_code": 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal Server Error",
        "message": "服务器内部错误",
        "status_code": 500
    }), 500

if __name__ == '__main__':
    logger.info("启动AI股票交易系统测试服务器...")
    logger.info("服务器将在端口8080上运行")
    logger.info("Cloudflare隧道配置: aigupiao.me -> localhost:8080")
    
    app.run(
        host='0.0.0.0',
        port=8081,
        debug=False,
        threaded=True
    )
