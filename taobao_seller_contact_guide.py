#!/usr/bin/env python3
"""
淘宝卖家联系指南
帮助用户从淘宝卖家获取股票数据推送服务的连接信息
"""

import os
import json
import time
import webbrowser
from typing import Dict, Any

class TaobaoSellerContactGuide:
    """淘宝卖家联系指南"""
    
    def __init__(self):
        self.api_key = "QT_wat5QfcJ6N9pDZM5"
        self.taobao_link = "https://m.tb.cn/h.hUlnKE6Pk6brYcw"
        self.seller_code = "HU591"
        
    def run_guide(self):
        """运行联系指南"""
        print("🛒 淘宝卖家联系指南")
        print("=" * 50)
        print(f"商品链接: {self.taobao_link}")
        print(f"卖家代码: {self.seller_code}")
        print(f"您的API Key: {self.api_key}")
        print()
        
        self._show_contact_methods()
        self._generate_inquiry_templates()
        self._create_config_checklist()
        self._show_next_steps()
    
    def _show_contact_methods(self):
        """显示联系方式"""
        print("📞 联系卖家的方法:")
        print("-" * 30)
        print("1. 🛒 通过淘宝订单页面")
        print("   - 打开手机淘宝APP")
        print("   - 进入'我的淘宝' -> '我的订单'")
        print("   - 找到股票数据服务订单")
        print("   - 点击'联系卖家'")
        print()
        
        print("2. 💬 通过旺旺客服")
        print("   - 在商品页面点击'联系客服'")
        print("   - 或搜索卖家旺旺号")
        print()
        
        print("3. 📱 通过卖家提供的微信/QQ群")
        print("   - 查看订单详情中的联系方式")
        print("   - 或询问是否有技术支持群")
        print()
    
    def _generate_inquiry_templates(self):
        """生成询问模板"""
        print("📝 询问模板 (复制发送给卖家):")
        print("-" * 40)
        
        # 模板1: 简洁版
        template1 = f"""您好！我购买了您家的股票数据推送服务。

我的API Key: {self.api_key}

请提供以下连接信息：
1. 推送服务器地址 (IP或域名)
2. 连接端口号
3. 认证Token

谢谢！"""
        
        # 模板2: 详细版
        template2 = f"""您好！

我购买了股票数据推送服务，现在需要配置连接参数。

订单信息：
- API Key: {self.api_key}
- 商品链接: {self.taobao_link}

需要的技术参数：
1. 服务器地址 (如: 192.168.1.100 或 api.example.com)
2. 端口号 (如: 8080, 9999等)
3. 认证Token (用于身份验证)

请问您能提供这些连接配置信息吗？

另外：
- 服务器运行时间是什么时候？
- 是否有技术文档或使用说明？
- 如果连接有问题，如何联系技术支持？

谢谢您的帮助！"""
        
        # 模板3: 技术版
        template3 = f"""技术咨询：股票数据推送服务配置

API Key: {self.api_key}

需要TCP连接参数：
- Host: ?
- Port: ?
- Auth Token: ?

数据格式：
- 是否为JSON格式？
- 推送频率是多少？
- 支持哪些股票代码？

连接协议：
- 是否需要心跳包？
- 认证方式是什么？
- 断线重连机制？

请提供详细的技术文档，谢谢！"""
        
        # 保存模板到文件
        templates = {
            "简洁版": template1,
            "详细版": template2,
            "技术版": template3
        }
        
        print("📋 已生成3个询问模板:")
        for name, template in templates.items():
            print(f"\n🔸 {name}:")
            print("-" * 20)
            print(template)
            print()
        
        # 保存到文件
        with open("taobao_inquiry_templates.txt", 'w', encoding='utf-8') as f:
            f.write("淘宝卖家询问模板\n")
            f.write("=" * 30 + "\n\n")
            for name, template in templates.items():
                f.write(f"{name}:\n")
                f.write("-" * 20 + "\n")
                f.write(template + "\n\n")
        
        print("💾 模板已保存到: taobao_inquiry_templates.txt")
    
    def _create_config_checklist(self):
        """创建配置检查清单"""
        print("\n✅ 配置信息检查清单:")
        print("-" * 30)
        
        checklist = [
            "□ 服务器地址 (IP地址或域名)",
            "□ 端口号 (1-65535之间的数字)",
            "□ 认证Token (字母数字组合)",
            "□ 服务运行时间 (如: 9:00-15:00)",
            "□ 数据格式说明 (JSON/二进制等)",
            "□ 推送频率 (如: 每3秒)",
            "□ 支持的股票范围 (A股/港股等)",
            "□ 技术支持联系方式",
            "□ 使用文档或说明",
            "□ 测试账号或试用期"
        ]
        
        for item in checklist:
            print(f"  {item}")
        
        # 保存检查清单
        with open("config_checklist.txt", 'w', encoding='utf-8') as f:
            f.write("股票数据服务配置检查清单\n")
            f.write("=" * 30 + "\n\n")
            f.write(f"API Key: {self.api_key}\n")
            f.write(f"卖家: {self.seller_code}\n\n")
            f.write("需要获取的信息:\n")
            for item in checklist:
                f.write(f"{item}\n")
        
        print(f"\n💾 检查清单已保存到: config_checklist.txt")
    
    def _show_next_steps(self):
        """显示后续步骤"""
        print("\n🚀 后续步骤:")
        print("-" * 20)
        print("1. 📱 使用上述模板联系卖家")
        print("2. ⏰ 等待卖家回复连接信息")
        print("3. ✅ 对照检查清单确认信息完整")
        print("4. 🔧 运行配置工具设置连接")
        print("5. 🧪 测试连接是否正常")
        print()
        
        print("🔧 获取信息后运行:")
        print("   python taobao_stock_api_helper.py")
        print()
        
        print("💡 如果卖家回复不及时:")
        print("   - 可以催促一下")
        print("   - 询问是否有技术支持QQ群")
        print("   - 要求提供使用文档")
        print("   - 如果长时间无回复可考虑退款")
    
    def create_seller_info_form(self):
        """创建卖家信息收集表单"""
        form_html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>股票数据服务配置信息收集</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #f0f8ff; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .form-group {{ margin-bottom: 15px; }}
        label {{ display: block; font-weight: bold; margin-bottom: 5px; }}
        input, textarea {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
        .btn {{ background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }}
        .template {{ background: #f9f9f9; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .checklist {{ background: #fff3cd; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🛒 股票数据服务配置信息</h1>
        <p><strong>API Key:</strong> {self.api_key}</p>
        <p><strong>卖家:</strong> {self.seller_code}</p>
        <p><strong>商品链接:</strong> <a href="{self.taobao_link}" target="_blank">点击查看</a></p>
    </div>
    
    <h2>📝 从卖家获取的信息</h2>
    <form id="configForm">
        <div class="form-group">
            <label for="host">服务器地址 (IP或域名):</label>
            <input type="text" id="host" name="host" placeholder="如: 192.168.1.100 或 api.example.com">
        </div>
        
        <div class="form-group">
            <label for="port">端口号:</label>
            <input type="number" id="port" name="port" placeholder="如: 8080, 9999">
        </div>
        
        <div class="form-group">
            <label for="token">认证Token:</label>
            <input type="text" id="token" name="token" placeholder="卖家提供的认证密钥">
        </div>
        
        <div class="form-group">
            <label for="schedule">服务时间:</label>
            <input type="text" id="schedule" name="schedule" placeholder="如: 9:00-15:00 工作日">
        </div>
        
        <div class="form-group">
            <label for="format">数据格式:</label>
            <input type="text" id="format" name="format" placeholder="如: JSON, 二进制">
        </div>
        
        <div class="form-group">
            <label for="frequency">推送频率:</label>
            <input type="text" id="frequency" name="frequency" placeholder="如: 每3秒">
        </div>
        
        <div class="form-group">
            <label for="support">技术支持联系方式:</label>
            <textarea id="support" name="support" rows="3" placeholder="QQ群、微信、电话等"></textarea>
        </div>
        
        <button type="button" class="btn" onclick="saveConfig()">💾 保存配置</button>
        <button type="button" class="btn" onclick="generateConfigFile()">🔧 生成配置文件</button>
    </form>
    
    <div class="template">
        <h3>📋 询问模板 (复制发送给卖家)</h3>
        <textarea readonly rows="8" style="width: 100%;">您好！我购买了您家的股票数据推送服务。

我的API Key: {self.api_key}

请提供以下连接信息：
1. 推送服务器地址 (IP或域名)
2. 连接端口号  
3. 认证Token

另外请告知：
- 服务运行时间
- 数据推送格式
- 技术支持联系方式

谢谢！</textarea>
    </div>
    
    <div class="checklist">
        <h3>✅ 信息完整性检查</h3>
        <ul>
            <li>□ 服务器地址已获取</li>
            <li>□ 端口号已确认</li>
            <li>□ 认证Token已提供</li>
            <li>□ 服务时间已明确</li>
            <li>□ 数据格式已说明</li>
            <li>□ 技术支持方式已知</li>
        </ul>
    </div>
    
    <script>
        function saveConfig() {{
            const config = {{
                api_key: '{self.api_key}',
                host: document.getElementById('host').value,
                port: document.getElementById('port').value,
                token: document.getElementById('token').value,
                schedule: document.getElementById('schedule').value,
                format: document.getElementById('format').value,
                frequency: document.getElementById('frequency').value,
                support: document.getElementById('support').value,
                timestamp: new Date().toISOString()
            }};
            
            localStorage.setItem('stockApiConfig', JSON.stringify(config));
            alert('✅ 配置已保存到浏览器本地存储');
        }}
        
        function generateConfigFile() {{
            const config = JSON.parse(localStorage.getItem('stockApiConfig') || '{{}}');
            if (!config.host || !config.port || !config.token) {{
                alert('❌ 请先填写完整的服务器地址、端口和Token');
                return;
            }}
            
            const configText = `# 股票数据服务配置
API_KEY = "{self.api_key}"
HOST = "${{config.host}}"
PORT = ${{config.port}}
TOKEN = "${{config.token}}"
SCHEDULE = "${{config.schedule}}"
FORMAT = "${{config.format}}"
FREQUENCY = "${{config.frequency}}"
SUPPORT = "${{config.support}}"`;
            
            const blob = new Blob([configText], {{ type: 'text/plain' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'stock_api_config.txt';
            a.click();
            URL.revokeObjectURL(url);
        }}
        
        // 加载已保存的配置
        window.onload = function() {{
            const saved = localStorage.getItem('stockApiConfig');
            if (saved) {{
                const config = JSON.parse(saved);
                Object.keys(config).forEach(key => {{
                    const element = document.getElementById(key);
                    if (element) element.value = config[key];
                }});
            }}
        }};
    </script>
</body>
</html>"""
        
        with open("seller_info_form.html", 'w', encoding='utf-8') as f:
            f.write(form_html)
        
        print("📄 信息收集表单已创建: seller_info_form.html")
        print("💡 可以在浏览器中打开此文件来填写卖家提供的信息")

def main():
    """主函数"""
    guide = TaobaoSellerContactGuide()
    
    print("🎯 选择操作:")
    print("1. 查看联系卖家指南")
    print("2. 创建信息收集表单")
    print("3. 打开淘宝商品页面")
    print("4. 退出")
    
    choice = input("\n请选择 (1-4): ").strip()
    
    if choice == "1":
        guide.run_guide()
    elif choice == "2":
        guide.create_seller_info_form()
        # 尝试在浏览器中打开表单
        try:
            webbrowser.open("seller_info_form.html")
            print("✅ 表单已在浏览器中打开")
        except:
            print("⚠️ 请手动打开 seller_info_form.html 文件")
    elif choice == "3":
        try:
            webbrowser.open(guide.taobao_link)
            print("✅ 淘宝商品页面已打开")
        except:
            print(f"⚠️ 请手动打开链接: {guide.taobao_link}")
    elif choice == "4":
        print("👋 再见！")
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()
