#!/usr/bin/env python3
"""
修复端口冲突问题
统一端口管理
"""

import os
import re
import shutil
from datetime import datetime
from typing import Dict

class PortConflictFixer:
    """端口冲突修复器"""
    
    def __init__(self):
        self.backup_dir = f"port_fix_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        # 标准端口分配
        self.standard_ports = {
            "agent_backend": 9999,
            "trading_api": 8888,
            "main_api": 8000,
            "frontend_dev": 3000,
            "redis": 6379,
            "chagubang": 6380,
            "websocket": 8001,
            "monitoring": 8002,
            "backup_api": 8003
        }
        
    def fix_all_port_conflicts(self):
        """修复所有端口冲突"""
        print("🔧 修复端口冲突问题")
        print("=" * 50)
        
        # 创建备份目录
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 1. 创建端口配置管理器
        self._create_port_manager()
        
        # 2. 扫描并修复端口冲突
        self._scan_and_fix_ports()
        
        # 3. 更新环境变量模板
        self._update_env_template()
        
        print(f"\n✅ 端口冲突修复完成!")
        print(f"📁 备份文件保存在: {self.backup_dir}")
        
    def _create_port_manager(self):
        """创建端口配置管理器"""
        print("\n🔧 创建端口配置管理器...")
        
        port_manager = f'''import os
from typing import Dict, Optional

class PortManager:
    """统一端口管理器"""
    
    # 标准端口分配
    STANDARD_PORTS = {self.standard_ports}
    
    def __init__(self):
        self.ports = self._load_ports()
    
    def _load_ports(self) -> Dict[str, int]:
        """从环境变量加载端口配置"""
        ports = {{}}
        for service, default_port in self.STANDARD_PORTS.items():
            env_key = f"{{service.upper()}}_PORT"
            ports[service] = int(os.getenv(env_key, default_port))
        return ports
    
    def get_port(self, service: str) -> int:
        """获取服务端口"""
        if service not in self.ports:
            raise ValueError(f"Unknown service: {{service}}")
        return self.ports[service]
    
    def get_all_ports(self) -> Dict[str, int]:
        """获取所有端口配置"""
        return self.ports.copy()
    
    def check_conflicts(self) -> Dict[int, list]:
        """检查端口冲突"""
        port_usage = {{}}
        for service, port in self.ports.items():
            if port not in port_usage:
                port_usage[port] = []
            port_usage[port].append(service)
        
        # 返回有冲突的端口
        conflicts = {{port: services for port, services in port_usage.items() if len(services) > 1}}
        return conflicts
    
    def validate_ports(self) -> bool:
        """验证端口配置"""
        conflicts = self.check_conflicts()
        if conflicts:
            print("❌ 发现端口冲突:")
            for port, services in conflicts.items():
                print(f"  端口 {{port}}: {{', '.join(services)}}")
            return False
        
        print("✅ 端口配置验证通过")
        return True
    
    def get_service_url(self, service: str, host: str = "localhost", protocol: str = "http") -> str:
        """获取服务URL"""
        port = self.get_port(service)
        return f"{{protocol}}://{{host}}:{{port}}"

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
'''
        
        with open("port_manager.py", 'w', encoding='utf-8') as f:
            f.write(port_manager)
        
        print("✅ 已创建端口配置管理器: port_manager.py")
    
    def _scan_and_fix_ports(self):
        """扫描并修复端口冲突"""
        print("\n🔧 扫描并修复端口冲突...")
        
        # 需要修复的文件模式
        files_to_fix = [
            ("local_agent_backend.py", {"9999": "port_manager.get_port('agent_backend')"}),
            ("local_trading_server.py", {"8888": "port_manager.get_port('trading_api')"}),
            ("backend/app.py", {"8000": "port_manager.get_port('main_api')"}),
            ("cloud_app.py", {"8000": "port_manager.get_port('main_api')"})
        ]
        
        for file_path, port_replacements in files_to_fix:
            if os.path.exists(file_path):
                self._fix_file_ports(file_path, port_replacements)
    
    def _fix_file_ports(self, file_path: str, port_replacements: Dict[str, str]):
        """修复单个文件的端口配置"""
        try:
            # 备份原文件
            backup_name = file_path.replace("/", "_").replace("\\\\", "_") + ".backup"
            shutil.copy2(file_path, os.path.join(self.backup_dir, backup_name))
            
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 添加端口管理器导入
            if "from port_manager import" not in content and "port_manager.get_port" in str(port_replacements.values()):
                # 在文件开头添加导入
                lines = content.split('\\n')
                import_line = "from port_manager import port_manager"
                
                # 找到合适的位置插入导入
                insert_pos = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        insert_pos = i + 1
                    elif line.strip() and not line.strip().startswith('#'):
                        break
                
                lines.insert(insert_pos, import_line)
                content = '\\n'.join(lines)
            
            # 替换端口配置
            updated_content = content
            for old_port, new_port_expr in port_replacements.items():
                # 替换直接的端口号
                patterns = [
                    f'port={old_port}',
                    f'port = {old_port}',
                    f'"port": {old_port}',
                    f"'port': {old_port}",
                    f'host="0.0.0.0", port={old_port}',
                    f"host='0.0.0.0', port={old_port}"
                ]
                
                for pattern in patterns:
                    if pattern in updated_content:
                        new_pattern = pattern.replace(old_port, new_port_expr)
                        updated_content = updated_content.replace(pattern, new_pattern)
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"✅ 已修复端口配置: {file_path}")
            
        except Exception as e:
            print(f"❌ 修复文件失败 {file_path}: {e}")
    
    def _update_env_template(self):
        """更新环境变量模板"""
        print("\n🔧 更新环境变量模板...")
        
        # 读取现有模板
        env_template_path = ".env.example"
        if os.path.exists(env_template_path):
            with open(env_template_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = ""
        
        # 添加端口配置部分
        port_config = f"""
# ==================== 服务端口配置 ====================
# 主要服务端口
AGENT_BACKEND_PORT={self.standard_ports['agent_backend']}
TRADING_API_PORT={self.standard_ports['trading_api']}
MAIN_API_PORT={self.standard_ports['main_api']}

# 前端开发端口
FRONTEND_DEV_PORT={self.standard_ports['frontend_dev']}

# 外部服务端口
REDIS_PORT={self.standard_ports['redis']}
CHAGUBANG_PORT={self.standard_ports['chagubang']}

# 其他服务端口
WEBSOCKET_PORT={self.standard_ports['websocket']}
MONITORING_PORT={self.standard_ports['monitoring']}
BACKUP_API_PORT={self.standard_ports['backup_api']}
"""
        
        # 如果端口配置不存在,则添加
        if "AGENT_BACKEND_PORT" not in content:
            content += port_config
        
        # 写回文件
        with open(env_template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 已更新环境变量模板: {env_template_path}")

if __name__ == "__main__":
    fixer = PortConflictFixer()
    fixer.fix_all_port_conflicts()
