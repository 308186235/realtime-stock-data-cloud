import os
from typing import Dict, Optional

class PortManager:
    """统一端口管理器"""
    
    # 标准端口分配
    STANDARD_PORTS = {'agent_backend': 9999, 'trading_api': 8888, 'main_api': 8000, 'frontend_dev': 3000, 'redis': 6379, 'chagubang': 6380, 'websocket': 8001, 'monitoring': 8002, 'backup_api': 8003}
    
    def __init__(self):
        self.ports = self._load_ports()
    
    def _load_ports(self) -> Dict[str, int]:
        """从环境变量加载端口配置"""
        ports = {}
        for service, default_port in self.STANDARD_PORTS.items():
            env_key = f"{service.upper()}_PORT"
            ports[service] = int(os.getenv(env_key, default_port))
        return ports
    
    def get_port(self, service: str) -> int:
        """获取服务端口"""
        if service not in self.ports:
            raise ValueError(f"Unknown service: {service}")
        return self.ports[service]
    
    def get_all_ports(self) -> Dict[str, int]:
        """获取所有端口配置"""
        return self.ports.copy()
    
    def check_conflicts(self) -> Dict[int, list]:
        """检查端口冲突"""
        port_usage = {}
        for service, port in self.ports.items():
            if port not in port_usage:
                port_usage[port] = []
            port_usage[port].append(service)
        
        # 返回有冲突的端口
        conflicts = {port: services for port, services in port_usage.items() if len(services) > 1}
        return conflicts
    
    def validate_ports(self) -> bool:
        """验证端口配置"""
        conflicts = self.check_conflicts()
        if conflicts:
            print("❌ 发现端口冲突:")
            for port, services in conflicts.items():
                print(f"  端口 {port}: {', '.join(services)}")
            return False
        
        print("✅ 端口配置验证通过")
        return True
    
    def get_service_url(self, service: str, host: str = "localhost", protocol: str = "http") -> str:
        """获取服务URL"""
        port = self.get_port(service)
        return f"{protocol}://{host}:{port}"

# 全局端口管理器
port_manager = PortManager()

# 便捷函数
def get_port(service: str) -> int:
    """获取服务端口"""
    return port_manager.get_port(service)

def get_service_url(service: str, host: str = "localhost", protocol: str = "http") -> str:
    """获取服务URL"""
    return port_manager.get_service_url(service, host, protocol)

# 常用端口常量
AGENT_BACKEND_PORT = port_manager.get_port("agent_backend")
TRADING_API_PORT = port_manager.get_port("trading_api")
MAIN_API_PORT = port_manager.get_port("main_api")
REDIS_PORT = port_manager.get_port("redis")
CHAGUBANG_PORT = port_manager.get_port("chagubang")
