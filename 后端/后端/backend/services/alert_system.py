"""
告警系统
"""

import time
import json
import smtplib
import requests
from typing import Dict, List, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass
from enum import Enum

class AlertLevel(Enum):
    """告警级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertChannel(Enum):
    """告警渠道"""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    DINGTALK = "dingtalk"

@dataclass
class Alert:
    """告警信息"""
    id: str
    title: str
    message: str
    level: AlertLevel
    category: str
    timestamp: float
    resolved: bool = False
    resolve_time: Optional[float] = None

class AlertManager:
    """告警管理器"""

    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules = self._load_alert_rules()
        self.notification_config = self._load_notification_config()

    def _load_alert_rules(self) -> Dict[str, Any]:
        """加载告警规则"""
        return {
            "trading_error_rate": {
                "metric": "trading.orders.error_rate",
                "threshold": 0.1,
                "operator": ">",
                "level": AlertLevel.HIGH,
                "message": "交易错误率过高"
            },
            "system_cpu_high": {
                "metric": "system.cpu.usage",
                "threshold": 0.8,
                "operator": ">",
                "level": AlertLevel.MEDIUM,
                "message": "系统CPU使用率过高"
            },
            "api_response_slow": {
                "metric": "api.requests.response_time",
                "threshold": 5000,
                "operator": ">",
                "level": AlertLevel.MEDIUM,
                "message": "API响应时间过长"
            },
            "market_data_delay": {
                "metric": "market_data.latency",
                "threshold": 2000,
                "operator": ">",
                "level": AlertLevel.HIGH,
                "message": "市场数据延迟过高"
            }
        }

    def _load_notification_config(self) -> Dict[str, Any]:
        """加载通知配置"""
        return {
            "email": {
                "enabled": True,
                "smtp_server": "smtp.qq.com",
                "smtp_port": 587,
                "username": "your_email@qq.com",
                "password": "your_password",
                "recipients": ["admin@example.com"]
            },
            "dingtalk": {
                "enabled": True,
                "webhook_url": "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN",
                "secret": "YOUR_SECRET"
            },
            "webhook": {
                "enabled": True,
                "url": "https://your-webhook-url.com/alerts"
            }
        }

    def create_alert(self, title: str, message: str, level: AlertLevel,
                    category: str = "system") -> str:
        """创建告警"""
        alert_id = f"{category}_{int(time.time())}"

        alert = Alert(
            id=alert_id,
            title=title,
            message=message,
            level=level,
            category=category,
            timestamp=time.time()
        )

        self.alerts[alert_id] = alert

        # 发送通知
        self._send_notifications(alert)

        return alert_id

    def resolve_alert(self, alert_id: str):
        """解决告警"""
        if alert_id in self.alerts:
            self.alerts[alert_id].resolved = True
            self.alerts[alert_id].resolve_time = time.time()

    def _send_notifications(self, alert: Alert):
        """发送通知"""
        if alert.level == AlertLevel.CRITICAL:
            # 严重告警发送所有渠道
            self._send_email_notification(alert)
            self._send_dingtalk_notification(alert)
            self._send_webhook_notification(alert)
        elif alert.level == AlertLevel.HIGH:
            # 高级告警发送邮件和钉钉
            self._send_email_notification(alert)
            self._send_dingtalk_notification(alert)
        else:
            # 其他告警只发送钉钉
            self._send_dingtalk_notification(alert)

    def _send_email_notification(self, alert: Alert):
        """发送邮件通知"""
        if not self.notification_config["email"]["enabled"]:
            return

        try:
            config = self.notification_config["email"]

            msg = MIMEMultipart()
            msg['From'] = config["username"]
            msg['To'] = ", ".join(config["recipients"])
            msg['Subject'] = f"[{alert.level.value.upper()}] {alert.title}"

            body = f"""
告警详情:
- 标题: {alert.title}
- 级别: {alert.level.value}
- 分类: {alert.category}
- 时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(alert.timestamp))}
- 消息: {alert.message}
"""

            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
            server.starttls()
            server.login(config["username"], config["password"])
            server.send_message(msg)
            server.quit()

        except Exception as e:
            print(f"发送邮件通知失败: {e}")

    def _send_dingtalk_notification(self, alert: Alert):
        """发送钉钉通知"""
        if not self.notification_config["dingtalk"]["enabled"]:
            return

        try:
            config = self.notification_config["dingtalk"]

            message = {
                "msgtype": "markdown",
                "markdown": {
                    "title": f"系统告警 - {alert.level.value.upper()}",
                    "text": f"""
## 🚨 系统告警

**告警级别**: {alert.level.value.upper()}
**告警分类**: {alert.category}
**告警时间**: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(alert.timestamp))}

**告警内容**: {alert.message}

> 请及时处理相关问题
"""
                }
            }

            response = requests.post(
                config["webhook_url"],
                json=message,
                timeout=10
            )

            if response.status_code != 200:
                print(f"钉钉通知发送失败: {response.text}")

        except Exception as e:
            print(f"发送钉钉通知失败: {e}")

    def _send_webhook_notification(self, alert: Alert):
        """发送Webhook通知"""
        if not self.notification_config["webhook"]["enabled"]:
            return

        try:
            config = self.notification_config["webhook"]

            payload = {
                "alert_id": alert.id,
                "title": alert.title,
                "message": alert.message,
                "level": alert.level.value,
                "category": alert.category,
                "timestamp": alert.timestamp
            }

            response = requests.post(
                config["url"],
                json=payload,
                timeout=10
            )

            if response.status_code != 200:
                print(f"Webhook通知发送失败: {response.text}")

        except Exception as e:
            print(f"发送Webhook通知失败: {e}")

    def get_active_alerts(self) -> List[Alert]:
        """获取活跃告警"""
        return [alert for alert in self.alerts.values() if not alert.resolved]

    def get_alert_stats(self) -> Dict[str, Any]:
        """获取告警统计"""
        total_alerts = len(self.alerts)
        active_alerts = len(self.get_active_alerts())

        level_counts = {}
        for alert in self.alerts.values():
            level = alert.level.value
            level_counts[level] = level_counts.get(level, 0) + 1

        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "resolved_alerts": total_alerts - active_alerts,
            "level_distribution": level_counts
        }

# 全局告警管理器
alert_manager = AlertManager()

# 便捷函数
def send_critical_alert(title: str, message: str, category: str = "system"):
    """发送严重告警"""
    return alert_manager.create_alert(title, message, AlertLevel.CRITICAL, category)

def send_high_alert(title: str, message: str, category: str = "system"):
    """发送高级告警"""
    return alert_manager.create_alert(title, message, AlertLevel.HIGH, category)

def send_medium_alert(title: str, message: str, category: str = "system"):
    """发送中级告警"""
    return alert_manager.create_alert(title, message, AlertLevel.MEDIUM, category)
