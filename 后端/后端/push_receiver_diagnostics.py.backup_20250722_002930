#!/usr/bin/env python3
"""
推送接收器诊断工具 - 基于MCP调研结果
专门检查和修复接收推送的潜在问题
"""

import os
import sys
import json
import socket
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import subprocess

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DiagnosticResult:
    """诊断结果"""
    category: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    issue: str
    solution: str
    status: str  # PASS, FAIL, WARNING

class PushReceiverDiagnostics:
    """推送接收器诊断器"""
    
    def __init__(self):
        self.results: List[DiagnosticResult] = []
        self.config_file = "backend/services/realtime_stock_receiver.py"
        
    def run_full_diagnosis(self) -> Dict[str, Any]:
        """运行完整诊断"""
        logger.info("🔍 开始推送接收器全面诊断...")
        
        # 清空之前的结果
        self.results.clear()
        
        # 执行各项检查
        self._check_server_configuration()
        self._check_network_settings()
        self._check_heartbeat_mechanism()
        self._check_data_validation()
        self._check_error_handling()
        self._check_connection_monitoring()
        self._check_performance_settings()
        self._check_dependencies()
        
        # 生成报告
        return self._generate_report()
    
    def _check_server_configuration(self):
        """检查服务器配置"""
        logger.info("检查服务器配置...")
        
        try:
            # 检查配置文件是否存在
            if not os.path.exists(self.config_file):
                self._add_result(
                    "服务器配置", "CRITICAL",
                    "配置文件不存在",
                    "创建配置文件并填入正确的服务器信息",
                    "FAIL"
                )
                return
            
            # 读取配置文件
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查关键配置项
            issues = []
            if 'host: str = ""' in content or 'host = ""' in content:
                issues.append("服务器地址为空")
            
            if 'port: int = 0' in content or 'port = 0' in content:
                issues.append("服务器端口为0")
            
            if 'token: str = ""' in content or 'token = ""' in content:
                issues.append("认证token为空")
            
            if issues:
                self._add_result(
                    "服务器配置", "CRITICAL",
                    f"关键配置缺失: {', '.join(issues)}",
                    "在配置文件中填入正确的服务器地址、端口和token",
                    "FAIL"
                )
            else:
                self._add_result(
                    "服务器配置", "LOW",
                    "配置文件存在",
                    "验证配置值是否正确",
                    "PASS"
                )
                
        except Exception as e:
            self._add_result(
                "服务器配置", "HIGH",
                f"配置检查失败: {str(e)}",
                "检查文件权限和路径",
                "FAIL"
            )
    
    def _check_network_settings(self):
        """检查网络设置"""
        logger.info("检查网络设置...")
        
        try:
            # 检查网络连接
            test_hosts = [
                ("8.8.8.8", 53),  # Google DNS
                ("114.114.114.114", 53),  # 114 DNS
            ]
            
            network_ok = False
            for host, port in test_hosts:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    result = sock.connect_ex((host, port))
                    sock.close()
                    if result == 0:
                        network_ok = True
                        break
                except Exception:
                    continue
            
            if network_ok:
                self._add_result(
                    "网络设置", "LOW",
                    "基础网络连接正常",
                    "继续检查其他网络配置",
                    "PASS"
                )
            else:
                self._add_result(
                    "网络设置", "HIGH",
                    "网络连接异常",
                    "检查网络连接和防火墙设置",
                    "FAIL"
                )
            
            # 检查Socket优化设置
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                optimizations = [
                    "SO_KEEPALIVE",
                    "TCP_NODELAY", 
                    "SO_RCVBUF"
                ]
                
                missing_opts = [opt for opt in optimizations if opt not in content]
                if missing_opts:
                    self._add_result(
                        "网络设置", "MEDIUM",
                        f"缺少Socket优化: {', '.join(missing_opts)}",
                        "添加Socket性能优化选项",
                        "WARNING"
                    )
                else:
                    self._add_result(
                        "网络设置", "LOW",
                        "Socket优化配置完整",
                        "配置正确",
                        "PASS"
                    )
                    
        except Exception as e:
            self._add_result(
                "网络设置", "MEDIUM",
                f"网络检查失败: {str(e)}",
                "手动检查网络配置",
                "FAIL"
            )
    
    def _check_heartbeat_mechanism(self):
        """检查心跳机制"""
        logger.info("检查心跳机制...")
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查心跳相关代码
                heartbeat_features = [
                    "heartbeat_interval",
                    "heartbeat_timeout",
                    "_send_heartbeat",
                    "_heartbeat_loop"
                ]
                
                missing_features = [f for f in heartbeat_features if f not in content]
                
                if missing_features:
                    self._add_result(
                        "心跳机制", "CRITICAL",
                        f"缺少心跳功能: {', '.join(missing_features)}",
                        "实现完整的心跳保活机制",
                        "FAIL"
                    )
                else:
                    self._add_result(
                        "心跳机制", "LOW",
                        "心跳机制已实现",
                        "验证心跳参数设置",
                        "PASS"
                    )
            else:
                self._add_result(
                    "心跳机制", "CRITICAL",
                    "无法检查心跳机制",
                    "确保配置文件存在",
                    "FAIL"
                )
                
        except Exception as e:
            self._add_result(
                "心跳机制", "HIGH",
                f"心跳检查失败: {str(e)}",
                "手动检查心跳实现",
                "FAIL"
            )
    
    def _check_data_validation(self):
        """检查数据验证"""
        logger.info("检查数据验证...")
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                validation_features = [
                    "enable_checksum",
                    "max_message_size",
                    "_recv_exact",
                    "struct.unpack"
                ]
                
                missing_features = [f for f in validation_features if f not in content]
                
                if missing_features:
                    self._add_result(
                        "数据验证", "HIGH",
                        f"缺少数据验证功能: {', '.join(missing_features)}",
                        "实现数据完整性验证机制",
                        "FAIL"
                    )
                else:
                    self._add_result(
                        "数据验证", "LOW",
                        "数据验证机制已实现",
                        "验证校验和算法",
                        "PASS"
                    )
            
        except Exception as e:
            self._add_result(
                "数据验证", "MEDIUM",
                f"数据验证检查失败: {str(e)}",
                "手动检查数据验证实现",
                "FAIL"
            )
    
    def _check_error_handling(self):
        """检查错误处理"""
        logger.info("检查错误处理...")
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查异常处理
                error_handling_count = content.count("except Exception")
                try_count = content.count("try:")
                
                if error_handling_count < try_count * 0.8:  # 至少80%的try有对应的异常处理
                    self._add_result(
                        "错误处理", "MEDIUM",
                        "异常处理覆盖不足",
                        "增加更完善的异常处理机制",
                        "WARNING"
                    )
                else:
                    self._add_result(
                        "错误处理", "LOW",
                        "异常处理覆盖充分",
                        "继续优化错误分类",
                        "PASS"
                    )
                
                # 检查重连机制
                if "retry" in content and "reconnect" in content:
                    self._add_result(
                        "错误处理", "LOW",
                        "重连机制已实现",
                        "验证重连策略",
                        "PASS"
                    )
                else:
                    self._add_result(
                        "错误处理", "HIGH",
                        "缺少重连机制",
                        "实现自动重连功能",
                        "FAIL"
                    )
            
        except Exception as e:
            self._add_result(
                "错误处理", "MEDIUM",
                f"错误处理检查失败: {str(e)}",
                "手动检查错误处理实现",
                "FAIL"
            )
    
    def _check_connection_monitoring(self):
        """检查连接监控"""
        logger.info("检查连接监控...")
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                monitoring_features = [
                    "stats",
                    "metrics",
                    "connection_status",
                    "last_receive_time"
                ]
                
                present_features = [f for f in monitoring_features if f in content]
                
                if len(present_features) >= 3:
                    self._add_result(
                        "连接监控", "LOW",
                        "连接监控功能完善",
                        "继续优化监控指标",
                        "PASS"
                    )
                else:
                    self._add_result(
                        "连接监控", "MEDIUM",
                        "连接监控功能不足",
                        "增加连接状态和性能监控",
                        "WARNING"
                    )
            
        except Exception as e:
            self._add_result(
                "连接监控", "LOW",
                f"监控检查失败: {str(e)}",
                "手动检查监控实现",
                "WARNING"
            )
    
    def _check_performance_settings(self):
        """检查性能设置"""
        logger.info("检查性能设置...")
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查缓冲区设置
                if "buffer_size" in content:
                    self._add_result(
                        "性能设置", "LOW",
                        "缓冲区配置存在",
                        "验证缓冲区大小是否合适",
                        "PASS"
                    )
                else:
                    self._add_result(
                        "性能设置", "MEDIUM",
                        "缺少缓冲区配置",
                        "添加缓冲区大小配置",
                        "WARNING"
                    )
                
                # 检查队列设置
                if "queue" in content and "maxsize" in content:
                    self._add_result(
                        "性能设置", "LOW",
                        "队列配置存在",
                        "验证队列大小设置",
                        "PASS"
                    )
                else:
                    self._add_result(
                        "性能设置", "MEDIUM",
                        "队列配置可能不足",
                        "优化队列大小和处理策略",
                        "WARNING"
                    )
            
        except Exception as e:
            self._add_result(
                "性能设置", "LOW",
                f"性能检查失败: {str(e)}",
                "手动检查性能配置",
                "WARNING"
            )
    
    def _check_dependencies(self):
        """检查依赖项"""
        logger.info("检查依赖项...")
        
        required_modules = [
            "socket",
            "threading", 
            "queue",
            "json",
            "time"
        ]
        
        optional_modules = [
            "redis",
            "asyncio",
            "psutil"
        ]
        
        # 检查必需模块
        missing_required = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_required.append(module)
        
        if missing_required:
            self._add_result(
                "依赖项", "CRITICAL",
                f"缺少必需模块: {', '.join(missing_required)}",
                "安装缺少的Python模块",
                "FAIL"
            )
        else:
            self._add_result(
                "依赖项", "LOW",
                "必需模块完整",
                "检查可选模块",
                "PASS"
            )
        
        # 检查可选模块
        missing_optional = []
        for module in optional_modules:
            try:
                __import__(module)
            except ImportError:
                missing_optional.append(module)
        
        if missing_optional:
            self._add_result(
                "依赖项", "LOW",
                f"可选模块缺失: {', '.join(missing_optional)}",
                "根据需要安装可选模块以获得更好性能",
                "WARNING"
            )
    
    def _add_result(self, category: str, severity: str, issue: str, solution: str, status: str):
        """添加诊断结果"""
        result = DiagnosticResult(category, severity, issue, solution, status)
        self.results.append(result)
    
    def _generate_report(self) -> Dict[str, Any]:
        """生成诊断报告"""
        # 统计结果
        total = len(self.results)
        critical = len([r for r in self.results if r.severity == "CRITICAL"])
        high = len([r for r in self.results if r.severity == "HIGH"])
        medium = len([r for r in self.results if r.severity == "MEDIUM"])
        low = len([r for r in self.results if r.severity == "LOW"])
        
        passed = len([r for r in self.results if r.status == "PASS"])
        failed = len([r for r in self.results if r.status == "FAIL"])
        warnings = len([r for r in self.results if r.status == "WARNING"])
        
        # 计算健康分数
        health_score = max(0, 100 - (critical * 25 + high * 15 + medium * 10 + low * 5))
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_checks": total,
                "health_score": health_score,
                "severity_breakdown": {
                    "critical": critical,
                    "high": high,
                    "medium": medium,
                    "low": low
                },
                "status_breakdown": {
                    "passed": passed,
                    "failed": failed,
                    "warnings": warnings
                }
            },
            "results": [
                {
                    "category": r.category,
                    "severity": r.severity,
                    "issue": r.issue,
                    "solution": r.solution,
                    "status": r.status
                }
                for r in self.results
            ],
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """生成修复建议"""
        recommendations = []
        
        # 基于诊断结果生成建议
        critical_issues = [r for r in self.results if r.severity == "CRITICAL"]
        if critical_issues:
            recommendations.append("🔴 立即修复所有严重问题，系统无法正常工作")
        
        high_issues = [r for r in self.results if r.severity == "HIGH"]
        if high_issues:
            recommendations.append("🟠 优先修复高优先级问题，影响系统稳定性")
        
        medium_issues = [r for r in self.results if r.severity == "MEDIUM"]
        if medium_issues:
            recommendations.append("🟡 修复中等优先级问题，提升系统性能")
        
        # 具体建议
        server_config_issues = [r for r in self.results if r.category == "服务器配置" and r.status == "FAIL"]
        if server_config_issues:
            recommendations.append("📝 首先配置正确的服务器地址、端口和认证信息")
        
        heartbeat_issues = [r for r in self.results if r.category == "心跳机制" and r.status == "FAIL"]
        if heartbeat_issues:
            recommendations.append("💓 实现心跳机制以保持连接稳定")
        
        network_issues = [r for r in self.results if r.category == "网络设置" and r.status == "FAIL"]
        if network_issues:
            recommendations.append("🌐 检查网络连接和防火墙设置")
        
        return recommendations

def main():
    """主函数"""
    print("🔍 推送接收器诊断工具")
    print("=" * 50)
    
    diagnostics = PushReceiverDiagnostics()
    report = diagnostics.run_full_diagnosis()
    
    # 打印报告
    print(f"\n📊 诊断报告 - {report['timestamp']}")
    print("=" * 50)
    
    summary = report['summary']
    print(f"健康分数: {summary['health_score']}/100")
    print(f"总检查项: {summary['total_checks']}")
    print(f"通过: {summary['status_breakdown']['passed']}")
    print(f"失败: {summary['status_breakdown']['failed']}")
    print(f"警告: {summary['status_breakdown']['warnings']}")
    
    print(f"\n严重程度分布:")
    print(f"  严重: {summary['severity_breakdown']['critical']}")
    print(f"  高: {summary['severity_breakdown']['high']}")
    print(f"  中: {summary['severity_breakdown']['medium']}")
    print(f"  低: {summary['severity_breakdown']['low']}")
    
    print(f"\n🔍 详细结果:")
    print("-" * 50)
    for result in report['results']:
        status_icon = {"PASS": "✅", "FAIL": "❌", "WARNING": "⚠️"}[result['status']]
        severity_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}[result['severity']]
        
        print(f"{status_icon} {severity_icon} [{result['category']}] {result['issue']}")
        print(f"   💡 解决方案: {result['solution']}")
        print()
    
    print(f"🎯 修复建议:")
    print("-" * 50)
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"{i}. {rec}")
    
    # 保存报告
    report_file = f"push_receiver_diagnosis_{int(time.time())}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 详细报告已保存到: {report_file}")

if __name__ == "__main__":
    main()
