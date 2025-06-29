#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uni-app版本兼容性修复工具
"""

import os
import json
import shutil
from pathlib import Path

class UniAppCompatibilityFixer:
    """uni-app兼容性修复器"""
    
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.fixes_applied = []
        
    def log_fix(self, fix_description):
        """记录修复操作"""
        self.fixes_applied.append(fix_description)
        print(f"✅ {fix_description}")
    
    def fix_package_json(self):
        """修复package.json版本兼容问题"""
        print("🔧 修复package.json版本兼容问题...")
        
        package_json_path = self.project_path / "package.json"
        
        if not package_json_path.exists():
            print("❌ 未找到package.json文件")
            return False
        
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            # 修复uni-app版本
            if '@dcloudio/uni-app' in package_data.get('dependencies', {}):
                old_version = package_data['dependencies']['@dcloudio/uni-app']
                package_data['dependencies']['@dcloudio/uni-app'] = '^3.0.0-3080620230817001'
                self.log_fix(f"更新@dcloudio/uni-app版本: {old_version} -> ^3.0.0-3080620230817001")
            
            # 修复uni-ui版本
            if '@dcloudio/uni-ui' in package_data.get('dependencies', {}):
                old_version = package_data['dependencies']['@dcloudio/uni-ui']
                package_data['dependencies']['@dcloudio/uni-ui'] = '^1.5.7'
                self.log_fix(f"更新@dcloudio/uni-ui版本: {old_version} -> ^1.5.7")
            
            # 修复Vue版本兼容
            if 'vue' in package_data.get('dependencies', {}):
                old_version = package_data['dependencies']['vue']
                package_data['dependencies']['vue'] = '^3.3.4'
                self.log_fix(f"更新Vue版本: {old_version} -> ^3.3.4")
            
            # 修复开发依赖
            dev_deps = package_data.get('devDependencies', {})
            
            # 更新uni-cli相关
            if '@dcloudio/uni-cli-shared' in dev_deps:
                dev_deps['@dcloudio/uni-cli-shared'] = '^3.0.0-3080620230817001'
                self.log_fix("更新@dcloudio/uni-cli-shared版本")
            
            if '@dcloudio/vue-cli-plugin-uni' in dev_deps:
                dev_deps['@dcloudio/vue-cli-plugin-uni'] = '^3.0.0-3080620230817001'
                self.log_fix("更新@dcloudio/vue-cli-plugin-uni版本")
            
            # 修复脚本命令
            scripts = package_data.get('scripts', {})
            if 'dev' in scripts and 'npx uni serve' in scripts['dev']:
                scripts['dev'] = 'npx uni'
                self.log_fix("修复dev脚本命令")
            
            # 保存修复后的package.json
            with open(package_json_path, 'w', encoding='utf-8') as f:
                json.dump(package_data, f, indent=2, ensure_ascii=False)
            
            self.log_fix("package.json修复完成")
            return True
            
        except Exception as e:
            print(f"❌ 修复package.json失败: {e}")
            return False
    
    def fix_manifest_json(self):
        """修复manifest.json配置"""
        print("🔧 修复manifest.json配置...")
        
        manifest_path = self.project_path / "manifest.json"
        
        if not manifest_path.exists():
            print("⚠️ 未找到manifest.json，创建默认配置")
            self.create_default_manifest()
            return True
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
            
            # 确保有基本配置
            if 'vueVersion' not in manifest_data:
                manifest_data['vueVersion'] = '3'
                self.log_fix("设置Vue版本为3")
            
            # 确保有H5配置
            if 'h5' not in manifest_data:
                manifest_data['h5'] = {
                    "devServer": {
                        "port": 9000,
                        "disableHostCheck": True,
                        "proxy": {
                            "/api": {
                                "target": "http://localhost:8002",
                                "changeOrigin": True,
                                "secure": False
                            }
                        }
                    },
                    "router": {
                        "mode": "hash"
                    }
                }
                self.log_fix("添加H5开发服务器配置")
            else:
                # 更新现有H5配置
                if 'devServer' not in manifest_data['h5']:
                    manifest_data['h5']['devServer'] = {}
                
                manifest_data['h5']['devServer'].update({
                    "port": 9000,
                    "disableHostCheck": True,
                    "proxy": {
                        "/api": {
                            "target": "http://localhost:8002",
                            "changeOrigin": True,
                            "secure": False
                        }
                    }
                })
                self.log_fix("更新H5开发服务器配置")
            
            # 保存修复后的manifest.json
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest_data, f, indent=2, ensure_ascii=False)
            
            self.log_fix("manifest.json修复完成")
            return True
            
        except Exception as e:
            print(f"❌ 修复manifest.json失败: {e}")
            return False
    
    def create_default_manifest(self):
        """创建默认的manifest.json"""
        manifest_data = {
            "name": "股票交易系统",
            "appid": "__UNI__STOCK_TRADER",
            "description": "AI驱动的股票交易系统",
            "versionName": "1.0.0",
            "versionCode": "100",
            "vueVersion": "3",
            "h5": {
                "devServer": {
                    "port": 9000,
                    "disableHostCheck": True,
                    "proxy": {
                        "/api": {
                            "target": "http://localhost:8002",
                            "changeOrigin": True,
                            "secure": False
                        }
                    }
                },
                "router": {
                    "mode": "hash"
                }
            },
            "mp-weixin": {
                "appid": "",
                "setting": {
                    "urlCheck": False
                },
                "usingComponents": True
            }
        }
        
        manifest_path = self.project_path / "manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)
        
        self.log_fix("创建默认manifest.json")
    
    def fix_pages_json(self):
        """修复pages.json配置"""
        print("🔧 检查pages.json配置...")
        
        pages_json_path = self.project_path / "pages.json"
        
        if not pages_json_path.exists():
            print("⚠️ 未找到pages.json，创建默认配置")
            self.create_default_pages_json()
            return True
        
        try:
            with open(pages_json_path, 'r', encoding='utf-8') as f:
                pages_data = json.load(f)
            
            # 确保有基本页面配置
            if 'pages' not in pages_data or not pages_data['pages']:
                pages_data['pages'] = [
                    {
                        "path": "pages/index/index",
                        "style": {
                            "navigationBarTitleText": "股票交易系统"
                        }
                    }
                ]
                self.log_fix("添加默认页面配置")
            
            # 确保有全局样式配置
            if 'globalStyle' not in pages_data:
                pages_data['globalStyle'] = {
                    "navigationBarTextStyle": "black",
                    "navigationBarTitleText": "股票交易系统",
                    "navigationBarBackgroundColor": "#F8F8F8",
                    "backgroundColor": "#F8F8F8"
                }
                self.log_fix("添加全局样式配置")
            
            # 保存修复后的pages.json
            with open(pages_json_path, 'w', encoding='utf-8') as f:
                json.dump(pages_data, f, indent=2, ensure_ascii=False)
            
            self.log_fix("pages.json检查完成")
            return True
            
        except Exception as e:
            print(f"❌ 修复pages.json失败: {e}")
            return False
    
    def create_default_pages_json(self):
        """创建默认的pages.json"""
        pages_data = {
            "pages": [
                {
                    "path": "pages/index/index",
                    "style": {
                        "navigationBarTitleText": "股票交易系统"
                    }
                }
            ],
            "globalStyle": {
                "navigationBarTextStyle": "black",
                "navigationBarTitleText": "股票交易系统",
                "navigationBarBackgroundColor": "#F8F8F8",
                "backgroundColor": "#F8F8F8"
            }
        }
        
        pages_json_path = self.project_path / "pages.json"
        with open(pages_json_path, 'w', encoding='utf-8') as f:
            json.dump(pages_data, f, indent=2, ensure_ascii=False)
        
        self.log_fix("创建默认pages.json")
    
    def clean_node_modules(self):
        """清理node_modules"""
        print("🧹 清理node_modules...")
        
        node_modules_path = self.project_path / "node_modules"
        if node_modules_path.exists():
            try:
                shutil.rmtree(node_modules_path)
                self.log_fix("清理node_modules完成")
                return True
            except Exception as e:
                print(f"⚠️ 清理node_modules失败: {e}")
                return False
        else:
            print("ℹ️ node_modules不存在，跳过清理")
            return True
    
    def generate_fix_report(self):
        """生成修复报告"""
        print("\n" + "="*60)
        print("📋 uni-app兼容性修复报告")
        print("="*60)
        
        print(f"\n📁 项目路径: {self.project_path}")
        print(f"🔧 修复操作数量: {len(self.fixes_applied)}")
        
        print("\n✅ 已执行的修复:")
        for i, fix in enumerate(self.fixes_applied, 1):
            print(f"  {i}. {fix}")
        
        print("\n📋 下一步操作:")
        print("  1. 运行 npm install 重新安装依赖")
        print("  2. 运行 npm run dev 启动开发服务器")
        print("  3. 访问 http://localhost:9000 查看前端")
        
        # 保存报告到文件
        report_path = self.project_path / "uniapp_fix_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("uni-app兼容性修复报告\n")
            f.write("="*40 + "\n\n")
            f.write(f"项目路径: {self.project_path}\n")
            f.write(f"修复时间: {__import__('datetime').datetime.now().isoformat()}\n\n")
            f.write("已执行的修复:\n")
            for i, fix in enumerate(self.fixes_applied, 1):
                f.write(f"  {i}. {fix}\n")
        
        print(f"\n📄 详细报告已保存到: {report_path}")
    
    def run_all_fixes(self):
        """运行所有修复"""
        print("🚀 开始uni-app兼容性修复...")
        print("="*60)
        
        # 1. 清理node_modules
        self.clean_node_modules()
        
        # 2. 修复package.json
        self.fix_package_json()
        
        # 3. 修复manifest.json
        self.fix_manifest_json()
        
        # 4. 修复pages.json
        self.fix_pages_json()
        
        # 5. 生成报告
        self.generate_fix_report()
        
        print("\n🎉 uni-app兼容性修复完成！")

def main():
    """主函数"""
    # 修复frontend/stock5项目
    stock5_path = "frontend/stock5"
    
    if os.path.exists(stock5_path):
        print(f"🔧 修复项目: {stock5_path}")
        fixer = UniAppCompatibilityFixer(stock5_path)
        fixer.run_all_fixes()
    else:
        print(f"❌ 项目路径不存在: {stock5_path}")

if __name__ == "__main__":
    main()
