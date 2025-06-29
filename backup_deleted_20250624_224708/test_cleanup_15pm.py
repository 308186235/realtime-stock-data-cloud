import glob
import os
from datetime import datetime, time, timedelta

def test_cleanup_15pm():
    """测试15点过期清理功能"""
    print("🧹 测试15点过期清理功能...")
    
    # 获取当前时间
    now = datetime.now()
    
    # 判断过期时间：今天15点
    today_3pm = datetime.combine(now.date(), time(15, 0))
    
    # 如果现在还没到15点，则以昨天15点为过期时间
    if now < today_3pm:
        yesterday_3pm = today_3pm - timedelta(days=1)
        cutoff_time = yesterday_3pm
        print(f"   当前时间: {now.strftime('%H:%M')}")
        print(f"   过期标准: 昨天15:00后的文件")
    else:
        cutoff_time = today_3pm
        print(f"   当前时间: {now.strftime('%H:%M')}")
        print(f"   过期标准: 今天15:00后的文件")
    
    print(f"   过期时间点: {cutoff_time}")
    
    # 查找所有导出文件
    patterns = [
        "持仓数据_*.csv",
        "成交数据_*.csv", 
        "委托数据_*.csv"
    ]
    
    deleted_count = 0
    for pattern in patterns:
        files = glob.glob(pattern)
        print(f"\n模式 '{pattern}' 找到 {len(files)} 个文件:")
        
        for file_path in files:
            try:
                # 获取文件修改时间
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                print(f"  📄 {file_path}")
                print(f"     文件时间: {file_time}")
                
                # 如果文件在15点后，删除它
                if file_time < cutoff_time:
                    print(f"     🗑️ 应该删除 (在过期时间前)")
                    deleted_count += 1
                else:
                    print(f"     ✅ 保留 (在过期时间后)")
                    
            except Exception as e:
                print(f"     ❌ 处理文件失败: {e}")
    
    print(f"\n总结: 找到 {deleted_count} 个过期文件")

if __name__ == "__main__":
    test_cleanup_15pm()
