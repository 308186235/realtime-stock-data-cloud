#!/usr/bin/env python3
"""
统一修复前端配置问题
"""

import os
import shutil
import re
import json
from datetime import datetime
from pathlib import Path

class FrontendConfigUnifier:
    """前端配置统一器"""
    
    def __init__(self):
        self.backup_dir = f"frontend_config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.fixed_files = []
        
        # 统一的配置标准
        self.unified_config = {
            'API_BASE_URL': 'https://api.aigupiao.me',
            'WS_BASE_URL': 'wss://api.aigupiao.me/ws',
            'DOMAIN': 'aigupiao.me',
            'USE_MOCK_DATA': False,
            'DEBUG_MODE': False
        }
        
        # 前端项目目录
        self.frontend_projects = [
            'frontend/gupiao1',
            'frontend/stock5',
            '炒股养家',
            '炒股养家_complete/gupiao1'
        ]
        
    def unify_all_frontend_configs(self):
        """统一所有前端配置"""
        print("🎯 统一前端配置")
        print("=" * 50)
        
        # 创建备份目录
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 1. 统一环境配置文件
        self._unify_env_configs()
        
        # 2. 统一API请求配置
        self._unify_request_configs()
        
        # 3. 统一服务配置
        self._unify_service_configs()
        
        # 4. 清理模拟数据配置
        self._cleanup_mock_configs()
        
        # 5. 生成统一配置文件
        self._generate_unified_config_files()
        
        # 6. 验证配置一致性
        self._verify_config_consistency()
        
        print(f"\n✅ 前端配置统一完成!")
        print(f"📁 备份文件保存在: {self.backup_dir}")
        print(f"🎯 统一了 {len(self.fixed_files)} 个文件")
        
    def _unify_env_configs(self):
        """统一环境配置文件"""
        print("\n🌍 统一环境配置文件...")
        
        for project in self.frontend_projects:
            env_files = [
                os.path.join(project, 'env.js'),
                os.path.join(project, 'config.js'),
                os.path.join(project, 'utils/config.js')
            ]
            
            for env_file in env_files:
                if os.path.exists(env_file):
                    self._fix_env_file(env_file)
    
    def _unify_request_configs(self):
        """统一API请求配置"""
        print("\n🌐 统一API请求配置...")
        
        for project in self.frontend_projects:
            request_files = [
                os.path.join(project, 'utils/request.js'),
                os.path.join(project, 'auto-trader/request.js'),
                os.path.join(project, 'services/request.js')
            ]
            
            for request_file in request_files:
                if os.path.exists(request_file):
                    self._fix_request_file(request_file)
    
    def _unify_service_configs(self):
        """统一服务配置"""
        print("\n⚙️ 统一服务配置...")
        
        service_patterns = [
            'services/*.js',
            'components/services/*.js'
        ]
        
        for project in self.frontend_projects:
            for pattern in service_patterns:
                service_dir = os.path.join(project, pattern.split('/')[0])
                if os.path.exists(service_dir):
                    for file in os.listdir(service_dir):
                        if file.endswith('.js'):
                            service_file = os.path.join(service_dir, file)
                            self._fix_service_file(service_file)
    
    def _cleanup_mock_configs(self):
        """清理模拟数据配置"""
        print("\n🧹 清理模拟数据配置...")
        
        for project in self.frontend_projects:
            # 删除mock目录
            mock_dir = os.path.join(project, 'mock')
            if os.path.exists(mock_dir):
                shutil.move(mock_dir, os.path.join(self.backup_dir, f"{project.replace('/', '_')}_mock"))
                print(f"✅ 移除mock目录: {mock_dir}")
            
            # 清理mock相关文件
            mock_files = [
                os.path.join(project, 'mock.js'),
                os.path.join(project, 'mockData.js'),
                os.path.join(project, 'testData.js')
            ]
            
            for mock_file in mock_files:
                if os.path.exists(mock_file):
                    shutil.move(mock_file, os.path.join(self.backup_dir, os.path.basename(mock_file)))
                    print(f"✅ 移除mock文件: {mock_file}")
    
    def _generate_unified_config_files(self):
        """生成统一配置文件"""
        print("\n📝 生成统一配置文件...")
        
        # 生成统一的环境配置模板
        unified_env_template = f'''// 统一环境配置 - 自动生成
// 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

const ENV_CONFIG = {{
  // API配置
  API_BASE_URL: '{self.unified_config['API_BASE_URL']}',
  WS_BASE_URL: '{self.unified_config['WS_BASE_URL']}',
  
  // 域名配置
  DOMAIN: '{self.unified_config['DOMAIN']}',
  
  // 功能开关
  USE_MOCK_DATA: {str(self.unified_config['USE_MOCK_DATA']).lower()},
  DEBUG_MODE: {str(self.unified_config['DEBUG_MODE']).lower()},
  
  // 环境检测
  isDevelopment: false,
  isProduction: true,
  
  // API端点
  ENDPOINTS: {{
    STOCK_QUOTE: '/api/stock/quote',
    TRADING_SUMMARY: '/api/t-trading/summary',
    AGENT_ANALYSIS: '/api/agent/analysis',
    REALTIME_DATA: '/api/realtime/data'
  }}
}};

// 导出配置
if (typeof module !== 'undefined' && module.exports) {{
  module.exports = ENV_CONFIG;
}} else if (typeof window !== 'undefined') {{
  window.ENV_CONFIG = ENV_CONFIG;
}}
'''
        
        # 为每个项目生成统一配置
        for project in self.frontend_projects:
            if os.path.exists(project):
                config_file = os.path.join(project, 'unified-config.js')
                with open(config_file, 'w', encoding='utf-8') as f:
                    f.write(unified_env_template)
                
                self.fixed_files.append(config_file)
                print(f"✅ 生成统一配置: {config_file}")
    
    def _verify_config_consistency(self):
        """验证配置一致性"""
        print("\n🔍 验证配置一致性...")
        
        inconsistencies = []
        
        for project in self.frontend_projects:
            if not os.path.exists(project):
                continue
                
            # 检查关键配置文件
            key_files = [
                os.path.join(project, 'env.js'),
                os.path.join(project, 'utils/request.js'),
                os.path.join(project, 'unified-config.js')
            ]
            
            for file_path in key_files:
                if os.path.exists(file_path):
                    issues = self._check_file_consistency(file_path)
                    if issues:
                        inconsistencies.extend(issues)
        
        if inconsistencies:
            print("⚠️ 发现配置不一致:")
            for issue in inconsistencies:
                print(f"  - {issue}")
        else:
            print("✅ 所有配置已统一")
    
    def _backup_file(self, file_path: str):
        """备份文件"""
        if not os.path.exists(file_path):
            return
            
        backup_name = file_path.replace("/", "_").replace("\\", "_") + ".backup"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            shutil.copy2(file_path, backup_path)
        except Exception as e:
            print(f"⚠️ 备份失败 {file_path}: {e}")
    
    def _fix_env_file(self, env_file: str):
        """修复环境配置文件"""
        try:
            self._backup_file(env_file)
            
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 统一API地址配置
            api_replacements = [
                (r'localhost:8000', self.unified_config['DOMAIN']),
                (r'localhost:8001', self.unified_config['DOMAIN']),
                (r'127\.0\.0\.1:\d+', self.unified_config['DOMAIN']),
                (r'http://[^/\s"\']+', self.unified_config['API_BASE_URL']),
                (r'ws://[^/\s"\']+', self.unified_config['WS_BASE_URL'])
            ]
            
            for pattern, replacement in api_replacements:
                content = re.sub(pattern, replacement, content)
            
            # 禁用模拟数据
            content = re.sub(r'USE_MOCK_DATA\s*[:=]\s*true', 'USE_MOCK_DATA: false', content)
            content = re.sub(r'DEBUG_MODE\s*[:=]\s*true', 'DEBUG_MODE: false', content)
            
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.fixed_files.append(env_file)
            print(f"✅ 统一环境配置: {env_file}")
            
        except Exception as e:
            print(f"⚠️ 修复环境配置失败 {env_file}: {e}")
    
    def _fix_request_file(self, request_file: str):
        """修复请求配置文件"""
        try:
            self._backup_file(request_file)
            
            with open(request_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 统一基础URL
            base_url_replacements = [
                (r"baseURL\s*:\s*['\"][^'\"]*['\"]", f"baseURL: '{self.unified_config['API_BASE_URL']}'"),
                (r"BASE_URL\s*=\s*['\"][^'\"]*['\"]", f"BASE_URL = '{self.unified_config['API_BASE_URL']}'"),
                (r"apiUrl\s*:\s*['\"][^'\"]*['\"]", f"apiUrl: '{self.unified_config['API_BASE_URL']}'")
            ]
            
            for pattern, replacement in base_url_replacements:
                content = re.sub(pattern, replacement, content)
            
            # 完全禁用模拟数据
            mock_replacements = [
                (r'USE_MOCK_DATA\s*=\s*true', 'USE_MOCK_DATA = false'),
                (r'if\s*\(\s*USE_MOCK_DATA\s*\)', 'if (false /* MOCK_DATA_DISABLED */)'),
                (r'mockResponse\s*\(', '// DISABLED: mockResponse('),
                (r'return\s+mockData', '// DISABLED: return mockData')
            ]
            
            for pattern, replacement in mock_replacements:
                content = re.sub(pattern, replacement, content)
            
            # 添加配置验证
            if 'function request(' in content and 'config validation' not in content:
                validation_code = '''
  // 配置验证
  if (!options.url) {
    return Promise.reject(new Error('❌ API地址不能为空'));
  }
  
  if (!options.url.startsWith('https://api.aigupiao.me')) {
    console.warn('⚠️ 使用非标准API地址:', options.url);
  }
'''
                content = content.replace('function request(', validation_code + '\\nfunction request(')
            
            with open(request_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.fixed_files.append(request_file)
            print(f"✅ 统一请求配置: {request_file}")
            
        except Exception as e:
            print(f"⚠️ 修复请求配置失败 {request_file}: {e}")
    
    def _fix_service_file(self, service_file: str):
        """修复服务配置文件"""
        try:
            self._backup_file(service_file)
            
            with open(service_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 统一API调用
            api_call_replacements = [
                (r"'http://localhost:\d+'", f"'{self.unified_config['API_BASE_URL']}'"),
                (r'"http://localhost:\d+"', f'"{self.unified_config['API_BASE_URL']}"'),
                (r'`http://localhost:\d+`', f"`{self.unified_config['API_BASE_URL']}`")
            ]
            
            for pattern, replacement in api_call_replacements:
                content = re.sub(pattern, replacement, content)
            
            # 禁用开发模式和模拟数据
            content = re.sub(r'isDevelopment\s*=\s*true', 'isDevelopment = false', content)
            content = re.sub(r'useMockData\s*=\s*true', 'useMockData = false', content)
            
            with open(service_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.fixed_files.append(service_file)
            print(f"✅ 统一服务配置: {service_file}")
            
        except Exception as e:
            print(f"⚠️ 修复服务配置失败 {service_file}: {e}")
    
    def _check_file_consistency(self, file_path: str) -> list:
        """检查文件配置一致性"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查API地址一致性
            if 'localhost' in content:
                issues.append(f"{file_path}: 仍包含localhost地址")
            
            if 'USE_MOCK_DATA = true' in content or 'USE_MOCK_DATA: true' in content:
                issues.append(f"{file_path}: 模拟数据未完全禁用")
            
            if 'mockResponse(' in content and '// DISABLED:' not in content:
                issues.append(f"{file_path}: 包含活跃的模拟数据函数")
                
        except Exception as e:
            issues.append(f"{file_path}: 读取文件失败 - {e}")
        
        return issues

if __name__ == "__main__":
    unifier = FrontendConfigUnifier()
    unifier.unify_all_frontend_configs()
