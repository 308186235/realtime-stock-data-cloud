#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理API
支持北交所开关、交易时间等配置管理
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import json
import os
from datetime import datetime

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter()

# 配置文件路径
CONFIG_FILE = "config/trading_config.json"

# 默认配置
DEFAULT_CONFIG = {
    "enable_beijing_exchange": False,
    "trading_start_time": "09:10",
    "trading_end_time": "15:00",
    "analysis_interval": 40,
    "reconnect_interval": 30,
    "max_reconnect_attempts": 10,
    "updated_at": datetime.now().isoformat()
}

class ConfigUpdateRequest(BaseModel):
    """配置更新请求模型"""
    enable_beijing_exchange: Optional[bool] = None
    trading_start_time: Optional[str] = None
    trading_end_time: Optional[str] = None
    analysis_interval: Optional[int] = None
    reconnect_interval: Optional[int] = None
    max_reconnect_attempts: Optional[int] = None

class ConfigResponse(BaseModel):
    """配置响应模型"""
    success: bool
    message: str
    config: Dict[str, Any]

def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    try:
        # 确保配置目录存在
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 合并默认配置，确保所有字段都存在
                merged_config = DEFAULT_CONFIG.copy()
                merged_config.update(config)
                return merged_config
        else:
            # 如果配置文件不存在，创建默认配置
            save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
    except Exception as e:
        logger.error(f"加载配置失败: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any]) -> bool:
    """保存配置文件"""
    try:
        # 确保配置目录存在
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        
        # 更新时间戳
        config["updated_at"] = datetime.now().isoformat()
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"配置已保存: {CONFIG_FILE}")
        return True
    except Exception as e:
        logger.error(f"保存配置失败: {e}")
        return False

@router.get("/config", response_model=Dict[str, Any])
async def get_config():
    """获取当前配置"""
    try:
        config = load_config()
        return {
            "success": True,
            "message": "配置获取成功",
            "config": config
        }
    except Exception as e:
        logger.error(f"获取配置失败: {e}")
        raise HTTPException(status_code=500, detail="获取配置失败")

@router.post("/config", response_model=ConfigResponse)
async def update_config(request: ConfigUpdateRequest):
    """更新配置"""
    try:
        # 加载当前配置
        current_config = load_config()
        
        # 更新配置
        update_data = request.dict(exclude_unset=True)
        
        for key, value in update_data.items():
            if key in current_config:
                old_value = current_config[key]
                current_config[key] = value
                logger.info(f"配置更新: {key} = {old_value} -> {value}")
        
        # 保存配置
        if save_config(current_config):
            return ConfigResponse(
                success=True,
                message="配置更新成功",
                config=current_config
            )
        else:
            raise HTTPException(status_code=500, detail="配置保存失败")
            
    except Exception as e:
        logger.error(f"更新配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")

@router.post("/config/beijing-exchange", response_model=ConfigResponse)
async def toggle_beijing_exchange(enabled: bool):
    """切换北交所交易权限"""
    try:
        current_config = load_config()
        old_value = current_config.get("enable_beijing_exchange", False)
        current_config["enable_beijing_exchange"] = enabled
        
        if save_config(current_config):
            status = "开启" if enabled else "关闭"
            logger.info(f"北交所权限已{status}: {old_value} -> {enabled}")
            
            return ConfigResponse(
                success=True,
                message=f"北交所交易权限已{status}",
                config=current_config
            )
        else:
            raise HTTPException(status_code=500, detail="配置保存失败")
            
    except Exception as e:
        logger.error(f"切换北交所权限失败: {e}")
        raise HTTPException(status_code=500, detail=f"切换北交所权限失败: {str(e)}")

@router.get("/config/beijing-exchange")
async def get_beijing_exchange_status():
    """获取北交所交易权限状态"""
    try:
        config = load_config()
        enabled = config.get("enable_beijing_exchange", False)
        
        return {
            "success": True,
            "enabled": enabled,
            "message": f"北交所权限: {'已开启' if enabled else '未开启'}"
        }
    except Exception as e:
        logger.error(f"获取北交所权限状态失败: {e}")
        raise HTTPException(status_code=500, detail="获取北交所权限状态失败")

@router.get("/config/trading-time")
async def get_trading_time():
    """获取交易时间配置"""
    try:
        config = load_config()
        
        return {
            "success": True,
            "trading_start_time": config.get("trading_start_time", "09:10"),
            "trading_end_time": config.get("trading_end_time", "15:00"),
            "message": "交易时间获取成功"
        }
    except Exception as e:
        logger.error(f"获取交易时间失败: {e}")
        raise HTTPException(status_code=500, detail="获取交易时间失败")

@router.post("/config/trading-time")
async def update_trading_time(start_time: str, end_time: str):
    """更新交易时间配置"""
    try:
        current_config = load_config()
        current_config["trading_start_time"] = start_time
        current_config["trading_end_time"] = end_time
        
        if save_config(current_config):
            logger.info(f"交易时间已更新: {start_time} - {end_time}")
            
            return {
                "success": True,
                "message": "交易时间更新成功",
                "trading_start_time": start_time,
                "trading_end_time": end_time
            }
        else:
            raise HTTPException(status_code=500, detail="配置保存失败")
            
    except Exception as e:
        logger.error(f"更新交易时间失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新交易时间失败: {str(e)}")

@router.get("/config/status")
async def get_system_status():
    """获取系统状态"""
    try:
        config = load_config()
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        is_trading_day = now.weekday() < 5  # 周一到周五
        
        start_time = config.get("trading_start_time", "09:10")
        end_time = config.get("trading_end_time", "15:00")
        is_trading_time = is_trading_day and start_time <= current_time <= end_time
        
        return {
            "success": True,
            "current_time": now.strftime('%Y-%m-%d %H:%M:%S'),
            "is_trading_day": is_trading_day,
            "is_trading_time": is_trading_time,
            "trading_window": f"{start_time} - {end_time}",
            "beijing_exchange_enabled": config.get("enable_beijing_exchange", False),
            "analysis_interval": config.get("analysis_interval", 40),
            "config_updated_at": config.get("updated_at", "未知")
        }
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        raise HTTPException(status_code=500, detail="获取系统状态失败")

@router.post("/config/reset")
async def reset_config():
    """重置配置为默认值"""
    try:
        if save_config(DEFAULT_CONFIG.copy()):
            logger.info("配置已重置为默认值")
            
            return {
                "success": True,
                "message": "配置已重置为默认值",
                "config": DEFAULT_CONFIG
            }
        else:
            raise HTTPException(status_code=500, detail="配置重置失败")
            
    except Exception as e:
        logger.error(f"重置配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"重置配置失败: {str(e)}")
