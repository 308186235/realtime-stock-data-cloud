import glob
import os
from datetime import datetime, timedelta

def test_cleanup():
    """测试清理功能"""
    print("🧹 测试清理过期导出文件...")
    
    # 获取当前时间
    now = datetime.now()
    one_day_ago = now - timedelta(days=1)
    
    print(f"当前时间: {now}")
    print(f"1天前时间: {one_day_ago}")
    
    # 查找所有导出文件
    patterns = [
        "持仓数据_*.csv",
        "成交数据_*.csv", 
        "委托数据_*.csv",
        "测试过期文件_*.csv"
    ]
    
    deleted_count = 0
    for pattern in patterns:
        files = glob.glob(pattern)
        print(f"\n模式 '{pattern}' 找到 {len(files)} 个文件:")
        
        for file_path in files:
            try:
                # 获取文件修改时间
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                age_hours = (now - file_time).total_seconds() / 3600
                
                print(f"  📄 {file_path}")
                print(f"     文件时间: {file_time}")
                print(f"     文件年龄: {age_hours:.1f} 小时")
                
                # 如果文件超过1天，删除它
                if file_time < one_day_ago:
                    print(f"     🗑️ 应该删除 (超过24小时)")
                    # os.remove(file_path)  # 先注释掉，只测试
                    deleted_count += 1
                else:
                    print(f"     ✅ 保留 (不到24小时)")
                    
            except Exception as e:
                print(f"     ❌ 处理文件失败: {e}")
    
    print(f"\n总结: 找到 {deleted_count} 个过期文件")

if __name__ == "__main__":
    test_cleanup()
