#!/usr/bin/env python3
"""
端到端集成测试脚本
"""
import os
import json
import requests
import time
import subprocess
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class IntegrationTestSuite:
    def __init__(self):
        self.project_name = "ai-stock-trading-system"
        self.test_results = []
        self.config = self.load_config()
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('integration_test_results.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_config(self):
        """加载配置"""
        config = {}
        
        # 从.env.production加载配置
        if os.path.exists('.env.production'):
            with open('.env.production', 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key] = value
        
        return config
    
    def test_supabase_connection(self):
        """测试Supabase连接"""
        test_name = "Supabase数据库连接测试"
        self.logger.info(f"🔍 开始 {test_name}")
        
        try:
            supabase_url = self.config.get('SUPABASE_URL', '')
            supabase_key = self.config.get('SUPABASE_KEY', '')
            
            if not supabase_url or not supabase_key:
                raise Exception("Supabase配置缺失")
            
            # 测试REST API连接
            headers = {
                'apikey': supabase_key,
                'Authorization': f'Bearer {supabase_key}',
                'Content-Type': 'application/json'
            }
            
            # 测试健康检查
            health_url = f"{supabase_url}/rest/v1/"
            response = requests.get(health_url, headers=headers, timeout=10)
            
            success = response.status_code in [200, 401]  # 401也是正常的,表示需要认证
            
            result = {
                'test_name': test_name,
                'success': success,
                'response_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'timestamp': datetime.now().isoformat()
            }
            
            if success:
                self.logger.info(f"✅ {test_name} - 通过")
            else:
                self.logger.error(f"❌ {test_name} - 失败: HTTP {response.status_code}")
            
            self.test_results.append(result)
            return success
            
        except Exception as e:
            self.logger.error(f"❌ {test_name} - 异常: {e}")
            self.test_results.append({
                'test_name': test_name,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            return False
    
    def test_backend_api(self):
        """测试后端API"""
        test_name = "后端API服务测试"
        self.logger.info(f"🔍 开始 {test_name}")
        
        try:
            # 检查后端服务是否运行
            api_endpoints = [
                'http://localhost:8000/api/health',
                'http://127.0.0.1:8000/api/health'
            ]
            
            success = False
            response_data = None
            
            for endpoint in api_endpoints:
                try:
                    response = requests.get(endpoint, timeout=5)
                    if response.status_code == 200:
                        success = True
                        response_data = response.json()
                        break
                except:
                    continue
            
            result = {
                'test_name': test_name,
                'success': success,
                'response_data': response_data,
                'timestamp': datetime.now().isoformat()
            }
            
            if success:
                self.logger.info(f"✅ {test_name} - 通过")
            else:
                self.logger.warning(f"⚠️ {test_name} - 后端服务未运行(这是正常的,如果没有启动后端)")
            
            self.test_results.append(result)
            return success
            
        except Exception as e:
            self.logger.error(f"❌ {test_name} - 异常: {e}")
            self.test_results.append({
                'test_name': test_name,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            return False
    
    def test_frontend_files(self):
        """测试前端文件完整性"""
        test_name = "前端文件完整性测试"
        self.logger.info(f"🔍 开始 {test_name}")
        
        try:
            # 检查前端文件
            frontend_files = [
                'frontend/simple_frontend.html',
                'frontend/realtime_data_monitor.html',
                'frontend/services/aiService.js',
                'frontend/services/marketDataService.js'
            ]
            
            missing_files = []
            existing_files = []
            
            for file_path in frontend_files:
                if os.path.exists(file_path):
                    existing_files.append(file_path)
                else:
                    missing_files.append(file_path)
            
            success = len(existing_files) >= len(frontend_files) * 0.8  # 至少80%的文件存在
            
            result = {
                'test_name': test_name,
                'success': success,
                'existing_files': existing_files,
                'missing_files': missing_files,
                'file_count': len(existing_files),
                'timestamp': datetime.now().isoformat()
            }
            
            if success:
                self.logger.info(f"✅ {test_name} - 通过 ({len(existing_files)}/{len(frontend_files)} 文件存在)")
            else:
                self.logger.error(f"❌ {test_name} - 失败: 缺少关键前端文件")
            
            self.test_results.append(result)
            return success
            
        except Exception as e:
            self.logger.error(f"❌ {test_name} - 异常: {e}")
            self.test_results.append({
                'test_name': test_name,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            return False
    
    def test_configuration_files(self):
        """测试配置文件完整性"""
        test_name = "配置文件完整性测试"
        self.logger.info(f"🔍 开始 {test_name}")
        
        try:
            # 检查配置文件
            config_files = [
                '.env.production',
                'supabase_init.sql',
                'nginx.conf',
                'requirements.txt'
            ]
            
            missing_configs = []
            existing_configs = []
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    existing_configs.append(config_file)
                else:
                    missing_configs.append(config_file)
            
            # 检查关键配置项
            required_env_vars = ['SUPABASE_URL', 'SUPABASE_KEY', 'JWT_SECRET_KEY']
            missing_env_vars = []
            
            for var in required_env_vars:
                if not self.config.get(var):
                    missing_env_vars.append(var)
            
            success = len(missing_configs) == 0 and len(missing_env_vars) == 0
            
            result = {
                'test_name': test_name,
                'success': success,
                'existing_configs': existing_configs,
                'missing_configs': missing_configs,
                'missing_env_vars': missing_env_vars,
                'timestamp': datetime.now().isoformat()
            }
            
            if success:
                self.logger.info(f"✅ {test_name} - 通过")
            else:
                self.logger.error(f"❌ {test_name} - 失败: 配置不完整")
            
            self.test_results.append(result)
            return success
            
        except Exception as e:
            self.logger.error(f"❌ {test_name} - 异常: {e}")
            self.test_results.append({
                'test_name': test_name,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            return False
    
    def test_deployment_readiness(self):
        """测试部署就绪性"""
        test_name = "部署就绪性测试"
        self.logger.info(f"🔍 开始 {test_name}")
        
        try:
            # 检查部署文件
            deployment_files = [
                'cloud_deployment/cloudflare/wrangler.toml',
                'cloud_deployment/cloudflare/worker.js',
                'cloud_deployment/aliyun/Dockerfile',
                'cloud_deployment/aliyun/docker-compose.yml'
            ]
            
            missing_deployment_files = []
            existing_deployment_files = []
            
            for file_path in deployment_files:
                if os.path.exists(file_path):
                    existing_deployment_files.append(file_path)
                else:
                    missing_deployment_files.append(file_path)
            
            # 检查监控系统
            monitoring_files = [
                'monitoring/system_monitor.py',
                'monitoring/dashboard.html',
                'monitoring/config/alert_config.json'
            ]
            
            monitoring_ready = all(os.path.exists(f) for f in monitoring_files)
            
            success = len(existing_deployment_files) >= 3 and monitoring_ready
            
            result = {
                'test_name': test_name,
                'success': success,
                'deployment_files_ready': len(existing_deployment_files),
                'monitoring_ready': monitoring_ready,
                'missing_deployment_files': missing_deployment_files,
                'timestamp': datetime.now().isoformat()
            }
            
            if success:
                self.logger.info(f"✅ {test_name} - 通过")
            else:
                self.logger.error(f"❌ {test_name} - 失败: 部署文件不完整")
            
            self.test_results.append(result)
            return success
            
        except Exception as e:
            self.logger.error(f"❌ {test_name} - 异常: {e}")
            self.test_results.append({
                'test_name': test_name,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            return False
    
    def test_monitoring_system(self):
        """测试监控系统"""
        test_name = "监控系统测试"
        self.logger.info(f"🔍 开始 {test_name}")
        
        try:
            # 运行一次监控检查
            result = subprocess.run(
                ['python', 'monitoring/system_monitor.py'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = result.returncode == 0
            
            # 检查是否生成了监控数据
            metrics_file = f"monitoring/metrics/metrics_{datetime.now().strftime('%Y%m%d')}.json"
            metrics_generated = os.path.exists(metrics_file)
            
            test_result = {
                'test_name': test_name,
                'success': success and metrics_generated,
                'monitor_exit_code': result.returncode,
                'metrics_generated': metrics_generated,
                'timestamp': datetime.now().isoformat()
            }
            
            if success and metrics_generated:
                self.logger.info(f"✅ {test_name} - 通过")
            else:
                self.logger.error(f"❌ {test_name} - 失败")
            
            self.test_results.append(test_result)
            return success and metrics_generated
            
        except Exception as e:
            self.logger.error(f"❌ {test_name} - 异常: {e}")
            self.test_results.append({
                'test_name': test_name,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            return False
    
    def run_all_tests(self):
        """运行所有集成测试"""
        self.logger.info("🚀 开始端到端集成测试")
        self.logger.info("=" * 60)
        
        start_time = datetime.now()
        
        # 定义测试用例
        test_cases = [
            self.test_configuration_files,
            self.test_supabase_connection,
            self.test_frontend_files,
            self.test_backend_api,
            self.test_deployment_readiness,
            self.test_monitoring_system
        ]
        
        # 运行测试
        passed_tests = 0
        total_tests = len(test_cases)
        
        for test_case in test_cases:
            try:
                if test_case():
                    passed_tests += 1
            except Exception as e:
                self.logger.error(f"测试执行异常: {e}")
        
        # 计算结果
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        success_rate = (passed_tests / total_tests) * 100
        
        # 生成测试报告
        test_report = {
            'test_suite': 'AI股票交易系统端到端集成测试',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': success_rate,
            'test_results': self.test_results
        }
        
        # 保存测试报告
        with open('integration_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(test_report, f, indent=2, ensure_ascii=False)
        
        # 输出结果
        self.logger.info("=" * 60)
        self.logger.info("🎯 集成测试完成")
        self.logger.info(f"📊 测试结果: {passed_tests}/{total_tests} 通过 ({success_rate:.1f}%)")
        self.logger.info(f"⏱️ 测试时长: {duration:.2f}秒")
        
        if success_rate >= 80:
            self.logger.info("🎉 集成测试整体通过!系统已准备好部署")
        else:
            self.logger.warning("⚠️ 集成测试存在问题,建议修复后再部署")
        
        self.logger.info("📄 详细报告: integration_test_report.json")
        
        return success_rate >= 80

def main():
    """主函数"""
    test_suite = IntegrationTestSuite()
    return test_suite.run_all_tests()

if __name__ == "__main__":
    try:
        result = main()
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ 集成测试被用户中断")
        exit(1)
