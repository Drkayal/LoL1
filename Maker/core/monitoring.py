"""
نظام المراقبة المتقدم
يوفر dashboard شامل وإحصائيات في الوقت الفعلي للبوتات
"""

import asyncio
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import psutil

# إعداد الـ logging
logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """مقاييس النظام"""
    timestamp: float
    cpu_usage: float
    memory_usage: float
    memory_total: float
    disk_usage: float
    disk_total: float
    network_sent: int
    network_recv: int
    active_processes: int

@dataclass
class BotMetrics:
    """مقاييس البوت"""
    username: str
    timestamp: float
    status: str
    cpu_usage: float
    memory_usage: float
    uptime: float
    error_count: int
    last_activity: float
    response_time: float

@dataclass
class Alert:
    """تنبيه النظام"""
    id: str
    timestamp: float
    level: str  # info, warning, error, critical
    title: str
    message: str
    bot_username: Optional[str] = None
    resolved: bool = False

class MonitoringDashboard:
    """لوحة المراقبة المتقدمة"""
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.system_metrics_history = deque(maxlen=max_history)
        self.bot_metrics_history = defaultdict(lambda: deque(maxlen=max_history))
        self.alerts = deque(maxlen=200)
        self.alert_counter = 0
        
        # إعدادات التنبيهات
        self.alert_thresholds = {
            'cpu_high': 80.0,
            'memory_high': 85.0,
            'disk_high': 90.0,
            'bot_memory_high': 500.0,  # MB
            'bot_cpu_high': 50.0,
            'response_time_high': 5.0,  # seconds
            'uptime_low': 300.0  # 5 minutes
        }
        
        # إحصائيات عامة
        self.stats = {
            'total_bots_created': 0,
            'total_uptime': 0,
            'total_errors': 0,
            'peak_memory_usage': 0,
            'peak_cpu_usage': 0,
            'start_time': time.time()
        }
        
        self.monitoring_active = False
        
    def collect_system_metrics(self) -> SystemMetrics:
        """جمع مقاييس النظام"""
        try:
            # معلومات المعالج
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # معلومات الذاكرة
            memory = psutil.virtual_memory()
            
            # معلومات القرص
            disk = psutil.disk_usage('/')
            
            # معلومات الشبكة
            network = psutil.net_io_counters()
            
            # عدد العمليات النشطة
            active_processes = len(psutil.pids())
            
            metrics = SystemMetrics(
                timestamp=time.time(),
                cpu_usage=cpu_percent,
                memory_usage=memory.percent,
                memory_total=memory.total / (1024**3),  # GB
                disk_usage=disk.percent,
                disk_total=disk.total / (1024**3),  # GB
                network_sent=network.bytes_sent,
                network_recv=network.bytes_recv,
                active_processes=active_processes
            )
            
            # تحديث الإحصائيات
            self.stats['peak_memory_usage'] = max(self.stats['peak_memory_usage'], memory.percent)
            self.stats['peak_cpu_usage'] = max(self.stats['peak_cpu_usage'], cpu_percent)
            
            return metrics
            
        except Exception as e:
            logger.error(f"خطأ في جمع مقاييس النظام: {e}")
            return None
    
    def collect_bot_metrics(self, bot_username: str, process_manager) -> Optional[BotMetrics]:
        """جمع مقاييس بوت معين"""
        try:
            bot_process = process_manager._get_bot_process_info(bot_username)
            if not bot_process:
                return None
            
            # حساب وقت التشغيل
            uptime = 0
            if bot_process.start_time:
                uptime = time.time() - bot_process.start_time
            
            # محاولة قياس زمن الاستجابة (مبسط)
            response_time = 0.0
            try:
                start_time = time.time()
                # هنا يمكن إضافة ping test للبوت
                response_time = time.time() - start_time
            except:
                response_time = 0.0
            
            metrics = BotMetrics(
                username=bot_username,
                timestamp=time.time(),
                status=bot_process.status.value,
                cpu_usage=bot_process.cpu_usage,
                memory_usage=bot_process.memory_usage,
                uptime=uptime,
                error_count=0,  # يمكن تحسينه لاحقاً
                last_activity=time.time(),
                response_time=response_time
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"خطأ في جمع مقاييس البوت {bot_username}: {e}")
            return None
    
    def add_alert(self, level: str, title: str, message: str, bot_username: Optional[str] = None):
        """إضافة تنبيه جديد"""
        self.alert_counter += 1
        alert = Alert(
            id=f"alert_{self.alert_counter}",
            timestamp=time.time(),
            level=level,
            title=title,
            message=message,
            bot_username=bot_username
        )
        
        self.alerts.appendleft(alert)
        logger.warning(f"تنبيه {level}: {title} - {message}")
        
        return alert
    
    def check_system_alerts(self, metrics: SystemMetrics):
        """فحص تنبيهات النظام"""
        # تنبيه استهلاك المعالج
        if metrics.cpu_usage > self.alert_thresholds['cpu_high']:
            self.add_alert(
                'warning',
                'استهلاك معالج مرتفع',
                f'استهلاك المعالج وصل إلى {metrics.cpu_usage:.1f}%'
            )
        
        # تنبيه استهلاك الذاكرة
        if metrics.memory_usage > self.alert_thresholds['memory_high']:
            self.add_alert(
                'warning',
                'استهلاك ذاكرة مرتفع',
                f'استهلاك الذاكرة وصل إلى {metrics.memory_usage:.1f}%'
            )
        
        # تنبيه استهلاك القرص
        if metrics.disk_usage > self.alert_thresholds['disk_high']:
            self.add_alert(
                'error',
                'مساحة القرص منخفضة',
                f'استهلاك القرص وصل إلى {metrics.disk_usage:.1f}%'
            )
    
    def check_bot_alerts(self, metrics: BotMetrics):
        """فحص تنبيهات البوت"""
        # تنبيه استهلاك ذاكرة البوت
        if metrics.memory_usage > self.alert_thresholds['bot_memory_high']:
            self.add_alert(
                'warning',
                'استهلاك ذاكرة البوت مرتفع',
                f'البوت @{metrics.username} يستهلك {metrics.memory_usage:.1f} MB',
                metrics.username
            )
        
        # تنبيه استهلاك معالج البوت
        if metrics.cpu_usage > self.alert_thresholds['bot_cpu_high']:
            self.add_alert(
                'warning',
                'استهلاك معالج البوت مرتفع',
                f'البوت @{metrics.username} يستهلك {metrics.cpu_usage:.1f}% من المعالج',
                metrics.username
            )
        
        # تنبيه زمن الاستجابة
        if metrics.response_time > self.alert_thresholds['response_time_high']:
            self.add_alert(
                'warning',
                'زمن استجابة بطيء',
                f'البوت @{metrics.username} يستجيب في {metrics.response_time:.2f} ثانية',
                metrics.username
            )
        
        # تنبيه إعادة التشغيل المتكررة
        if metrics.uptime < self.alert_thresholds['uptime_low']:
            self.add_alert(
                'info',
                'إعادة تشغيل حديثة',
                f'البوت @{metrics.username} تم إعادة تشغيله مؤخراً',
                metrics.username
            )
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """توليد بيانات لوحة المراقبة"""
        current_time = time.time()
        
        # الحصول على أحدث المقاييس
        latest_system = self.system_metrics_history[-1] if self.system_metrics_history else None
        
        # إحصائيات البوتات
        bot_stats = {}
        total_bot_memory = 0
        total_bot_cpu = 0
        running_bots = 0
        
        for bot_username, metrics_history in self.bot_metrics_history.items():
            if metrics_history:
                latest_bot = metrics_history[-1]
                bot_stats[bot_username] = asdict(latest_bot)
                
                if latest_bot.status == 'running':
                    running_bots += 1
                    total_bot_memory += latest_bot.memory_usage
                    total_bot_cpu += latest_bot.cpu_usage
        
        # التنبيهات الأخيرة
        recent_alerts = [asdict(alert) for alert in list(self.alerts)[:10]]
        
        # إحصائيات عامة
        uptime = current_time - self.stats['start_time']
        
        dashboard_data = {
            'timestamp': current_time,
            'system_metrics': asdict(latest_system) if latest_system else None,
            'bot_stats': bot_stats,
            'summary': {
                'total_bots': len(self.bot_metrics_history),
                'running_bots': running_bots,
                'total_bot_memory': total_bot_memory,
                'total_bot_cpu': total_bot_cpu,
                'system_uptime': uptime,
                'total_alerts': len(self.alerts),
                'unresolved_alerts': len([a for a in self.alerts if not a.resolved])
            },
            'recent_alerts': recent_alerts,
            'performance': {
                'peak_memory': self.stats['peak_memory_usage'],
                'peak_cpu': self.stats['peak_cpu_usage'],
                'avg_response_time': self._calculate_avg_response_time(),
                'success_rate': self._calculate_success_rate()
            }
        }
        
        return dashboard_data
    
    def _calculate_avg_response_time(self) -> float:
        """حساب متوسط زمن الاستجابة"""
        total_time = 0
        count = 0
        
        for metrics_history in self.bot_metrics_history.values():
            for metrics in metrics_history:
                total_time += metrics.response_time
                count += 1
        
        return total_time / count if count > 0 else 0.0
    
    def _calculate_success_rate(self) -> float:
        """حساب معدل النجاح"""
        # مبسط - يمكن تحسينه لاحقاً
        total_bots = len(self.bot_metrics_history)
        if total_bots == 0:
            return 100.0
        
        running_bots = 0
        for metrics_history in self.bot_metrics_history.values():
            if metrics_history and metrics_history[-1].status == 'running':
                running_bots += 1
        
        return (running_bots / total_bots) * 100
    
    def generate_report(self, hours: int = 24) -> Dict[str, Any]:
        """توليد تقرير مفصل"""
        end_time = time.time()
        start_time = end_time - (hours * 3600)
        
        # فلترة البيانات حسب الفترة الزمنية
        system_data = [m for m in self.system_metrics_history if m.timestamp >= start_time]
        
        bot_data = {}
        for bot_username, metrics_history in self.bot_metrics_history.items():
            bot_data[bot_username] = [m for m in metrics_history if m.timestamp >= start_time]
        
        alerts_data = [a for a in self.alerts if a.timestamp >= start_time]
        
        # تحليل البيانات
        report = {
            'period': {
                'start': start_time,
                'end': end_time,
                'duration_hours': hours
            },
            'system_analysis': self._analyze_system_data(system_data),
            'bot_analysis': self._analyze_bot_data(bot_data),
            'alerts_analysis': self._analyze_alerts(alerts_data),
            'recommendations': self._generate_recommendations(system_data, bot_data, alerts_data)
        }
        
        return report
    
    def _analyze_system_data(self, data: List[SystemMetrics]) -> Dict[str, Any]:
        """تحليل بيانات النظام"""
        if not data:
            return {}
        
        cpu_values = [m.cpu_usage for m in data]
        memory_values = [m.memory_usage for m in data]
        
        return {
            'cpu': {
                'avg': sum(cpu_values) / len(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values)
            },
            'memory': {
                'avg': sum(memory_values) / len(memory_values),
                'max': max(memory_values),
                'min': min(memory_values)
            },
            'samples': len(data)
        }
    
    def _analyze_bot_data(self, data: Dict[str, List[BotMetrics]]) -> Dict[str, Any]:
        """تحليل بيانات البوتات"""
        analysis = {}
        
        for bot_username, metrics_list in data.items():
            if not metrics_list:
                continue
            
            memory_values = [m.memory_usage for m in metrics_list]
            cpu_values = [m.cpu_usage for m in metrics_list]
            uptime_values = [m.uptime for m in metrics_list]
            
            analysis[bot_username] = {
                'memory': {
                    'avg': sum(memory_values) / len(memory_values),
                    'max': max(memory_values),
                    'min': min(memory_values)
                },
                'cpu': {
                    'avg': sum(cpu_values) / len(cpu_values),
                    'max': max(cpu_values),
                    'min': min(cpu_values)
                },
                'uptime': {
                    'current': uptime_values[-1] if uptime_values else 0,
                    'avg': sum(uptime_values) / len(uptime_values)
                },
                'samples': len(metrics_list)
            }
        
        return analysis
    
    def _analyze_alerts(self, alerts: List[Alert]) -> Dict[str, Any]:
        """تحليل التنبيهات"""
        if not alerts:
            return {'total': 0}
        
        by_level = defaultdict(int)
        by_bot = defaultdict(int)
        
        for alert in alerts:
            by_level[alert.level] += 1
            if alert.bot_username:
                by_bot[alert.bot_username] += 1
        
        return {
            'total': len(alerts),
            'by_level': dict(by_level),
            'by_bot': dict(by_bot),
            'resolved': len([a for a in alerts if a.resolved]),
            'unresolved': len([a for a in alerts if not a.resolved])
        }
    
    def _generate_recommendations(self, system_data, bot_data, alerts_data) -> List[str]:
        """توليد توصيات للتحسين"""
        recommendations = []
        
        # تحليل استهلاك النظام
        if system_data:
            avg_cpu = sum(m.cpu_usage for m in system_data) / len(system_data)
            avg_memory = sum(m.memory_usage for m in system_data) / len(system_data)
            
            if avg_cpu > 70:
                recommendations.append("🔧 يُنصح بترقية المعالج أو تقليل عدد البوتات المشغلة")
            
            if avg_memory > 80:
                recommendations.append("💾 يُنصح بزيادة الذاكرة أو تحسين استهلاك البوتات")
        
        # تحليل البوتات
        high_memory_bots = []
        for bot_username, metrics_list in bot_data.items():
            if metrics_list:
                avg_memory = sum(m.memory_usage for m in metrics_list) / len(metrics_list)
                if avg_memory > 300:  # MB
                    high_memory_bots.append(bot_username)
        
        if high_memory_bots:
            recommendations.append(f"⚠️ البوتات التالية تستهلك ذاكرة عالية: {', '.join(high_memory_bots)}")
        
        # تحليل التنبيهات
        if alerts_data:
            error_alerts = [a for a in alerts_data if a.level == 'error']
            if len(error_alerts) > 10:
                recommendations.append("🚨 عدد كبير من التنبيهات الحرجة، يُنصح بمراجعة النظام")
        
        if not recommendations:
            recommendations.append("✅ النظام يعمل بشكل جيد، لا توجد توصيات خاصة")
        
        return recommendations
    
    async def start_monitoring(self, process_manager, interval: int = 30):
        """بدء المراقبة المتقدمة"""
        self.monitoring_active = True
        logger.info("🔍 بدء نظام المراقبة المتقدم...")
        
        while self.monitoring_active:
            try:
                # جمع مقاييس النظام
                system_metrics = self.collect_system_metrics()
                if system_metrics:
                    self.system_metrics_history.append(system_metrics)
                    self.check_system_alerts(system_metrics)
                
                # جمع مقاييس البوتات
                all_bots = process_manager.scan_bot_processes()
                for bot_process in all_bots:
                    bot_metrics = self.collect_bot_metrics(bot_process.username, process_manager)
                    if bot_metrics:
                        self.bot_metrics_history[bot_process.username].append(bot_metrics)
                        self.check_bot_alerts(bot_metrics)
                
                # انتظار الفترة المحددة
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"خطأ في نظام المراقبة: {e}")
                await asyncio.sleep(interval)
    
    def stop_monitoring(self):
        """إيقاف المراقبة"""
        self.monitoring_active = False
        logger.info("🔴 تم إيقاف نظام المراقبة المتقدم")

# إنشاء مثيل نظام المراقبة
monitoring_dashboard = MonitoringDashboard()