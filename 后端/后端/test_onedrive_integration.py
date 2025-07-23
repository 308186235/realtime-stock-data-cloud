#!/usr/bin/env python3
# test_onedrive_integration.py

import os
import json
import time
from datetime import datetime

def test_onedrive_integration():
    print("🧪 测试OneDrive集成...")
    
    mount_path = r"C:\mnt\onedrive\TradingData"
    
    # 检查挂载状态
    if not os.path.exists(mount_path):
        print(f"❌ 挂载点不存在: {mount_path}")
        return False
    
    # 测试写入
    test_data = {
        "test_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "test_type": "onedrive_integration",
        "status": "testing"
    }
    
    test_file = os.path.join(mount_path, "integration_test.json")
    
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 测试文件写入成功: {test_file}")
        
        # 等待同步
        time.sleep(2)
        
        # 测试读取
        with open(test_file, 'r', encoding='utf-8') as f:
            read_data = json.load(f)
        
        print(f"✅ 测试文件读取成功: {read_data['test_time']}")
        
        # 清理测试文件
        os.remove(test_file)
        print("✅ 测试文件已清理")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_onedrive_integration()
    if success:
        print("🎉 OneDrive集成测试成功!")
    else:
        print("💥 OneDrive集成测试失败!")
