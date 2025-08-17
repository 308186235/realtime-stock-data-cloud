import os
import sys
import uvicorn

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("启动股票交易系统后端服务器...")
    print("服务器将运行在 http://localhost:8000")
    print("API文档地址: http://localhost:8000/api/docs")
    print("按 Ctrl+C 停止服务器")
    
    # 启动服务器
    uvicorn.run(
        "backend.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    ) 
