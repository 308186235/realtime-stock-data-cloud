#!/usr/bin/env python3
"""
恢复云端Agent配置
将前端配置恢复为云端Worker,并添加备用方案
"""

import os
import shutil
from datetime import datetime

class CloudAgentConfigRestorer:
    """云端Agent配置恢复器"""
    
    def __init__(self):
        self.backup_dir = f"cloud_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.cloud_worker_url = "https://trading-api.308186235.workers.dev"
        self.cloud_ws_url = "wss://trading-api.308186235.workers.dev/ws"
        self.local_backup_url = "http://localhost:9999"
        self.local_backup_ws = "ws://localhost:9999/ws"
        
    def restore_cloud_config(self):
        """恢复云端配置"""
        print("☁️ 恢复云端Agent配置")
        print("=" * 50)
        print(f"🎯 云端Worker: {self.cloud_worker_url}")
        print(f"🎯 备用本地: {self.local_backup_url}")
        print("=" * 50)
        
        # 创建备份目录
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 1. 恢复主要配置文件
        self._restore_main_configs()
        
        # 2. 创建智能切换配置
        self._create_smart_switching_config()
        
        # 3. 更新统一Agent服务
        self._update_unified_agent_service()
        
        print(f"\n✅ 云端Agent配置恢复完成!")
        print(f"📁 备份文件保存在: {self.backup_dir}")
        print("\n🌐 配置说明:")
        print(f"   主要: 云端Worker ({self.cloud_worker_url})")
        print(f"   备用: 本地Agent ({self.local_backup_url})")
        print("   系统会自动检测并切换到可用的服务")
        
    def _restore_main_configs(self):
        """恢复主要配置文件"""
        print("\n🔧 恢复主要配置文件...")
        
        config_files = [
            "炒股养家/env.js",
            "frontend/gupiao1/env.js", 
            "frontend/stock5/env.js"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                self._restore_env_file(config_file)
                print(f"✅ 已恢复: {config_file}")
            else:
                print(f"⚠️ 文件不存在: {config_file}")
    
    def _restore_env_file(self, file_path):
        """恢复单个env.js文件"""
        # 备份当前文件
        backup_name = file_path.replace("/", "_").replace("\\", "_") + ".backup"
        shutil.copy2(file_path, os.path.join(self.backup_dir, backup_name))
        
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 恢复为云端配置,但保留备用方案
        replacements = [
            # 主要API地址恢复为云端
            (f"'{self.local_backup_url}'", f"'{self.cloud_worker_url}'"),
            (f'"{self.local_backup_url}"', f'"{self.cloud_worker_url}"'),
            (f"'{self.local_backup_ws}'", f"'{self.cloud_ws_url}'"),
            (f'"{self.local_backup_ws}"', f'"{self.cloud_ws_url}"'),
            
            # 确保使用云端地址
            ("'http://localhost:9999'", f"'{self.cloud_worker_url}'"),
            ('"http://localhost:9999"', f'"{self.cloud_worker_url}"'),
            ("'ws://localhost:9999/ws'", f"'{self.cloud_ws_url}'"),
            ('"ws://localhost:9999/ws"', f'"{self.cloud_ws_url}"'),
        ]
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        # 添加备用配置注释
        if "// 备用配置" not in content:
            backup_config = f"""
    // 备用配置 - 如果云端不可用,可手动切换
    // 本地Agent后端: {self.local_backup_url}
    // 本地WebSocket: {self.local_backup_ws}
    """
            content = content.replace("};", backup_config + "\n};")
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _create_smart_switching_config(self):
        """创建智能切换配置"""
        print("\n🔧 创建智能切换配置...")
        
        smart_config = f'''/**
 * 智能API切换配置
 * 自动检测云端和本地服务可用性
 */

class SmartAPIConfig {{
  constructor() {{
    this.cloudUrl = '{self.cloud_worker_url}';
    this.localUrl = '{self.local_backup_url}';
    this.cloudWs = '{self.cloud_ws_url}';
    this.localWs = '{self.local_backup_ws}';
    this.currentUrl = this.cloudUrl;
    this.currentWs = this.cloudWs;
    this.isCloudAvailable = true;
    this.lastCheck = 0;
    this.checkInterval = 30000; // 30秒检查一次
  }}
  
  /**
   * 检测服务可用性
   */
  async checkServiceAvailability() {{
    const now = Date.now();
    if (now - this.lastCheck < this.checkInterval) {{
      return this.isCloudAvailable;
    }}
    
    try {{
      console.log('🔍 检测云端服务可用性...');
      const response = await fetch(`${{this.cloudUrl}}/health`, {{
        method: 'GET',
        timeout: 5000
      }});
      
      if (response.ok) {{
        console.log('✅ 云端服务可用');
        this.isCloudAvailable = true;
        this.currentUrl = this.cloudUrl;
        this.currentWs = this.cloudWs;
      }} else {{
        throw new Error(`云端服务响应异常: ${{response.status}}`);
      }}
    }} catch (error) {{
      console.log('❌ 云端服务不可用,切换到本地服务');
      console.log('错误:', error.message);
      this.isCloudAvailable = false;
      this.currentUrl = this.localUrl;
      this.currentWs = this.localWs;
    }}
    
    this.lastCheck = now;
    return this.isCloudAvailable;
  }}
  
  /**
   * 获取当前API地址
   */
  async getApiUrl() {{
    await this.checkServiceAvailability();
    return this.currentUrl;
  }}
  
  /**
   * 获取当前WebSocket地址
   */
  async getWsUrl() {{
    await this.checkServiceAvailability();
    return this.currentWs;
  }}
  
  /**
   * 强制使用云端服务
   */
  forceCloud() {{
    console.log('🌐 强制使用云端服务');
    this.currentUrl = this.cloudUrl;
    this.currentWs = this.cloudWs;
    this.isCloudAvailable = true;
  }}
  
  /**
   * 强制使用本地服务
   */
  forceLocal() {{
    console.log('🏠 强制使用本地服务');
    this.currentUrl = this.localUrl;
    this.currentWs = this.localWs;
    this.isCloudAvailable = false;
  }}
  
  /**
   * 获取当前状态
   */
  getStatus() {{
    return {{
      cloudUrl: this.cloudUrl,
      localUrl: this.localUrl,
      currentUrl: this.currentUrl,
      isCloudAvailable: this.isCloudAvailable,
      lastCheck: new Date(this.lastCheck).toISOString()
    }};
  }}
}}

// 全局实例
const smartAPI = new SmartAPIConfig();

// 导出配置
export {{ smartAPI }};
export default smartAPI;
'''
        
        with open("炒股养家/services/smartAPIConfig.js", 'w', encoding='utf-8') as f:
            f.write(smart_config)
        
        print("✅ 已创建智能切换配置: smartAPIConfig.js")
    
    def _update_unified_agent_service(self):
        """更新统一Agent服务"""
        print("\n🔧 更新统一Agent服务...")
        
        service_file = "炒股养家/services/unifiedAgentService.js"
        if os.path.exists(service_file):
            # 备份原文件
            backup_name = "unifiedAgentService.js.backup"
            shutil.copy2(service_file, os.path.join(self.backup_dir, backup_name))
            
            # 读取文件
            with open(service_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 恢复云端配置
            replacements = [
                # 恢复云端API地址
                ("this.cloudApiUrl = 'http://localhost:9999';", 
                 f"this.cloudApiUrl = '{self.cloud_worker_url}';"),
                ('this.cloudApiUrl = "http://localhost:9999";', 
                 f'this.cloudApiUrl = "{self.cloud_worker_url}";'),
                
                # 恢复WebSocket地址
                ("this.websocketUrl = 'ws://localhost:9999/ws';", 
                 f"this.websocketUrl = '{self.cloud_ws_url}';"),
                ('this.websocketUrl = "ws://localhost:9999/ws";', 
                 f'this.websocketUrl = "{self.cloud_ws_url}";'),
                
                # 本地API保持8888端口
                ("this.localApiUrl = 'http://localhost:9999';", 
                 "this.localApiUrl = 'http://localhost:8888';"),
                ('this.localApiUrl = "http://localhost:9999";', 
                 'this.localApiUrl = "http://localhost:8888";'),
            ]
            
            for old, new in replacements:
                content = content.replace(old, new)
            
            # 写回文件
            with open(service_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ 已更新: {service_file}")
        else:
            print(f"⚠️ 文件不存在: {service_file}")

if __name__ == "__main__":
    restorer = CloudAgentConfigRestorer()
    restorer.restore_cloud_config()
