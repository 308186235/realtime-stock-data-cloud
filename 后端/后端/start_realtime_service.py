#!/usr/bin/env python3
"""
启动实时数据服务 - 端口8001
"""
import os
import sys
import subprocess

def main():
    """启动实时数据服务"""
    print("🚀 启动实时数据服务 (端口8001)...")
    
    # 设置环境变量
    env = os.environ.copy()
    env.update({
        'PORT': '8001',
        'JWT_SECRET_KEY': 'your-secret-key-here-for-development',
        'SUPABASE_URL': 'https://zzukfxwavknskqcepsjb.supabase.co',
        'SUPABASE_ANON_KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzU3MjU2NzQsImV4cCI6MjA1MTMwMTY3NH0.Ej4rJhGJZJQWQOJOGGSdBhfLJVm7VJQWQOJOGGSdBhf',
        'SUPABASE_SERVICE_ROLE_KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNTcyNTY3NCwiZXhwIjoyMDUxMzAxNjc0fQ.Ej4rJhGJZJQWQOJOGGSdBhfLJVm7VJQWQOJOGGSdBhf'
    })
    
    print("✅ 环境变量已设置")
    print(f"📂 工作目录: {os.getcwd()}")
    print(f"🌐 服务端口: {env['PORT']}")
    print()
    
    try:
        # 启动后端服务
        print("🔄 启动后端服务...")
        subprocess.run([
            sys.executable, 'backend/app.py'
        ], env=env, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 服务启动失败: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
        return 0
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
