#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare Pages部署验证脚本
"""

import os
import json
from pathlib import Path

def verify_pages_deployment():
    """验证Cloudflare Pages部署配置"""
    print("🔍 验证Cloudflare Pages部署配置...")
    
    issues = []
    success = []
    
    # 检查必需文件
    required_files = {
        'index.html': '主页文件',
        '_redirects': '重定向配置'
    }
    
    for file_name, description in required_files.items():
        if os.path.exists(file_name):
            success.append(f"✅ {file_name} - {description}")
            
            # 检查文件内容
            if file_name == 'index.html':
                with open(file_name, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'AI股票交易系统' in content:
                    success.append(f"✅ {file_name} 内容正确")
                else:
                    issues.append(f"❌ {file_name} 内容可能有问题")
                    
        else:
            issues.append(f"❌ 缺少 {file_name} - {description}")
    
    # 检查不应该存在的文件
    problematic_files = [
        'wrangler.toml',  # 这是Workers配置,对Pages有害
        'package.json',   # 可能导致构建问题
        'webpack.config.js',
        'vite.config.js'
    ]
    
    for file_name in problematic_files:
        if os.path.exists(file_name):
            issues.append(f"⚠️  发现可能有问题的文件: {file_name}")
        else:
            success.append(f"✅ 没有问题文件: {file_name}")
    
    # 检查目录结构
    if os.path.isfile('index.html'):
        success.append("✅ index.html 在根目录")
    else:
        issues.append("❌ index.html 不在根目录")
    
    # 生成报告
    print("\n" + "="*50)
    print("📋 Cloudflare Pages 部署验证报告")
    print("="*50)
    
    if success:
        print("\n✅ 成功项目:")
        for item in success:
            print(f"  {item}")
    
    if issues:
        print("\n❌ 需要修复的问题:")
        for item in issues:
            print(f"  {item}")
    
    # 生成建议
    print("\n💡 部署建议:")
    print("1. 在Cloudflare Pages中设置:")
    print("   - Framework preset: None")
    print("   - Build command: (留空)")
    print("   - Build output directory: /")
    print("   - Root directory: (留空)")
    
    print("\n2. 确保域名配置:")
    print("   - 主域名: abf7ecd1.stock-trading.pages.dev")
    print("   - 自定义域名: app.aigupiao.me")
    
    print("\n3. 如果仍然显示空白:")
    print("   - 检查Cloudflare Pages构建日志")
    print("   - 尝试重新部署")
    print("   - 清除浏览器缓存")
    
    # 返回状态
    return len(issues) == 0

def create_deployment_summary():
    """创建部署摘要文件"""
    summary = {
        "deployment_type": "Cloudflare Pages",
        "entry_file": "index.html",
        "redirects_file": "_redirects",
        "build_command": None,
        "build_output": "/",
        "framework": "Static HTML",
        "domains": [
            "abf7ecd1.stock-trading.pages.dev",
            "app.aigupiao.me"
        ],
        "api_endpoints": [
            "https://api.aigupiao.me"
        ],
        "status": "Ready for deployment"
    }
    
    with open('deployment_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print("📄 部署摘要已保存到: deployment_summary.json")

def main():
    """主函数"""
    print("🚀 Cloudflare Pages 部署验证")
    print("="*40)
    
    # 验证配置
    is_ready = verify_pages_deployment()
    
    # 创建摘要
    create_deployment_summary()
    
    # 最终状态
    if is_ready:
        print("\n🎉 部署配置验证通过!")
        print("可以进行Cloudflare Pages部署")
    else:
        print("\n⚠️  发现配置问题,请先修复")
    
    return 0 if is_ready else 1

if __name__ == '__main__':
    exit(main())
