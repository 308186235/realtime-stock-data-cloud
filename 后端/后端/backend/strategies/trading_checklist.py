import pandas as pd
import numpy as np
from datetime import datetime
import logging
from .base_strategy import BaseStrategy

class TradingChecklist:
    """
    交易清单检查器
    
    实现基于用户查询的系统化交易方法,将交易决策转化为具体可检查的清单项
    主要覆盖四个维度:风险控制,分析方法,操作策略,心态管理
    """
    
    def __init__(self):
        """初始化交易清单检查器"""
        self.logger = logging.getLogger(__name__)
        
        # 初始化检查项目
        self._init_checklist_items()
        
        # 交易记录
        self.trade_records = []
        
        # 交易统计
        self.trade_stats = {
            'total_trades': 0,
            'winning_trades': 0,
            'win_rate': 0.0,
            'avg_profit': 0.0,
            'max_drawdown': 0.0
        }
    
    def _init_checklist_items(self):
        """初始化检查项目"""
        self.pre_trade_checklist = {
            # 风险控制维度
            'fundamental_check': {
                'enabled': True,
                'items': [
                    {'id': 'profit_growth', 'name': '净利润增长率检查', 'criteria': '近1年>0且季度环比增速>10%'},
                    {'id': 'debt_ratio', 'name': '资产负债率检查', 'criteria': '制造业<60%,科技/消费<40%'},
                    {'id': 'goodwill_ratio', 'name': '商誉/市值比检查', 'criteria': '<10%'},
                    {'id': 'shareholder_check', 'name': '股东结构检查', 'criteria': '机构持仓>10%'},
                    {'id': 'regulatory_inquiry', 'name': '监管问询函检查', 'criteria': '近1年无交易所问询函'}
                ]
            },
            'technical_check': {
                'enabled': True,
                'items': [
                    {'id': 'ma_alignment', 'name': '均线系统检查', 'criteria': '5/10/20日均线多头排列且股价站稳20日均线'},
                    {'id': 'volume_check', 'name': '成交量检查', 'criteria': '上涨时温和放量(20%-50%),下跌时缩量(>30%)'},
                    {'id': 'macd_divergence', 'name': 'MACD背离检查', 'criteria': '寻找底背离信号'}
                ]
            },
            'position_check': {
                'enabled': True,
                'items': [
                    {'id': 'first_position', 'name': '首次建仓检查', 'criteria': '不超过总资金的20%'},
                    {'id': 'max_position', 'name': '极限仓位检查', 'criteria': '单只个股不超过50%仓位'},
                    {'id': 'add_position', 'name': '加仓条件检查', 'criteria': '买入后股价上涨5%且回踩5日均线不破'}
                ]
            },
            
            # 分析方法维度
            'entry_point_check': {
                'enabled': True,
                'items': [
                    {'id': 'support_level', 'name': '技术支撑位检查', 'criteria': '回踩前低/缺口/60日均线且缩量'},
                    {'id': 'pattern_check', 'name': '形态确认检查', 'criteria': '分时图出现W底或三重底形态'},
                    {'id': 'buying_time', 'name': '买入时间检查', 'criteria': '尾盘14:45后买入,避免早盘诱多'},
                    {'id': 'breakout_check', 'name': '突破确认检查', 'criteria': '放量突破前高且10:30前封涨停(牛市或热点板块)'}
                ]
            }
        }
        
        self.during_trade_checklist = {
            # 操作策略维度
            'execution_check': {
                'enabled': True,
                'items': [
                    {'id': 'stop_loss', 'name': '止损设置检查', 'criteria': '跌破买入价的7%或跌破关键支撑位(20日均线)'},
                    {'id': 'take_profit', 'name': '止盈设置检查', 'criteria': '达到目标涨幅(15%-20%)或出现顶背离信号'},
                    {'id': 'scaling_out', 'name': '分批卖出检查', 'criteria': '先卖50%,剩50%设移动止损(成本价上移5%)'}
                ]
            },
            'risk_behavior_check': {
                'enabled': True,
                'items': [
                    {'id': 'avoid_chasing', 'name': '追涨检查', 'criteria': '避免看到某股涨5%后追入'},
                    {'id': 'avoid_selling_dips', 'name': '杀跌检查', 'criteria': '避免跌3%后恐慌割肉'},
                    {'id': 'avoid_catching_knife', 'name': '抄底检查', 'criteria': '避免股价暴跌30%后无止跌信号就"捡便宜"'},
                    {'id': 'avoid_all_in', 'name': '满仓检查', 'criteria': '避免"某股必涨"押上所有资金'},
                    {'id': 'avoid_overtrading', 'name': '过度交易检查', 'criteria': '每周交易≤5次,避免频繁换股'}
                ]
            },
            'market_theme_check': {
                'enabled': True,
                'items': [
                    {'id': 'policy_check', 'name': '政策检查', 'criteria': '中央会议/行业规划出台后,3天内持续有个股涨停'},
                    {'id': 'money_flow_check', 'name': '资金流向检查', 'criteria': '连续5个交易日板块成交额占全市场15%以上'},
                    {'id': 'leading_stocks', 'name': '龙头股检查', 'criteria': '板块内有3只以上个股连板'},
                    {'id': 'previous_limit_up', 'name': '昨日涨停表现检查', 'criteria': '昨日涨停表现指数涨幅>2%且连涨3天'}
                ]
            },
            'time_graph_check': {
                'enabled': True,
                'items': [
                    {'id': 'early_dip', 'name': '早盘急跌买点检查', 'criteria': '9:45-10:00股价快速下跌5%以上但成交量未放大'},
                    {'id': 'late_surge', 'name': '尾盘抢筹信号检查', 'criteria': '14:50后股价直线拉抬且成交量持续放大'},
                    {'id': 'high_dive', 'name': '高位跳水止损检查', 'criteria': '13:30后从涨3%快速跌至-1%且跌破当天均价线'}
                ]
            },
            'position_adjustment_check': {
                'enabled': True,
                'items': [
                    {'id': 'macd_cross', 'name': '大盘MACD金叉检查', 'criteria': '大盘MACD金叉时仓位可提升至60%-80%'},
                    {'id': 'ma60_break', 'name': '大盘60日均线检查', 'criteria': '大盘跌破60日均线时仓位降至30%以下'},
                    {'id': 'bollinger_strategy', 'name': '布林带策略检查', 'criteria': '震荡市(布林带收口)时碰上轨卖30%,碰下轨买30%'}
                ]
            }
        }
        
        self.post_trade_checklist = {
            # 心态管理维度
            'daily_review_check': {
                'enabled': True,
                'items': [
                    {'id': 'buy_logic', 'name': '买入逻辑检查', 'criteria': '买入逻辑是否成立(如因"业绩预增"买入是否有公告支撑)'},
                    {'id': 'sell_logic', 'name': '卖出逻辑检查', 'criteria': '卖出后若股价继续涨,分析是指标背离没看懂还是情绪恐慌'},
                    {'id': 'position_logic', 'name': '仓位逻辑检查', 'criteria': '本次操作仓位是否符合金字塔法则'}
                ]
            },
            'weekly_analysis_check': {
                'enabled': True,
                'items': [
                    {'id': 'sector_rotation', 'name': '板块轮动分析', 'criteria': '整理本周领涨板块及驱动因素,预判下周持续性'},
                    {'id': 'pattern_collection', 'name': '个股K线库建设', 'criteria': '收集3-5只典型股,分析上涨/下跌时的指标共振信号'},
                    {'id': 'risk_cases', 'name': '风险案例记录', 'criteria': '记录本周踩的坑,标注避险措施'},
                    {'id': 'news_calendar', 'name': '消息日历建设', 'criteria': '标注下周重要事件,提前规划仓位应对'},
                    {'id': 'indicator_optimization', 'name': '指标优化', 'criteria': '对比常用的技术指标参数,调整灵敏度'}
                ]
            },
            'mental_management_check': {
                'enabled': True,
                'items': [
                    {'id': 'brave_buy_on_crash', 'name': '暴跌日敢买检查', 'criteria': '大盘暴跌2%以上时,筛选逆市红盘+缩量的个股'},
                    {'id': 'careful_chase', 'name': '暴涨日慎追检查', 'criteria': '板块集体涨停次日,避免追后排跟风股'},
                    {'id': 'reduce_on_profit', 'name': '盈利后减仓检查', 'criteria': '个股盈利超20%,卖出一半仓位,剩余设成本价止损'}
                ]
            },
            'tool_utilization_check': {
                'enabled': True,
                'items': [
                    {'id': 'tdx_usage', 'name': '通达信使用检查', 'criteria': '使用自定义选股设置筛选条件'},
                    {'id': 'eastmoney_usage', 'name': '东方财富使用检查', 'criteria': '查看资金流向板块选择超大单净流入占比高的个股'},
                    {'id': 'ifind_usage', 'name': '同花顺iFinD使用检查', 'criteria': '查个股机构持仓变化'}
                ]
            },
            'long_term_check': {
                'enabled': True,
                'items': [
                    {'id': 'avoid_stock_groups', 'name': '远离荐股群检查', 'criteria': '避免所谓专家推荐的股票'},
                    {'id': 'avoid_leverage', 'name': '远离杠杆检查', 'criteria': '避免使用配资等杠杆工具'},
                    {'id': 'avoid_excessive_trading', 'name': '远离过度交易检查', 'criteria': '避免频繁短线博弈'}
                ]
            }
        }
    
    def evaluate_pre_trade(self, stock_data, market_data=None):
        """
        评估交易前检查项
        
        Args:
            stock_data (dict): 股票数据,包含基本面信息
            market_data (pd.DataFrame, optional): 市场行情数据
            
        Returns:
            dict: 评估结果,包含各检查项结果
        """
        results = {}
        
        # 评估基本面检查
        if self.pre_trade_checklist['fundamental_check']['enabled']:
            fundamental_results = self._evaluate_fundamental(stock_data)
            results['fundamental_check'] = fundamental_results
        
        # 评估技术面检查
        if market_data is not None and self.pre_trade_checklist['technical_check']['enabled']:
            technical_results = self._evaluate_technical(market_data)
            results['technical_check'] = technical_results
        
        # 评估仓位检查
        if self.pre_trade_checklist['position_check']['enabled']:
            position_results = self._evaluate_position(stock_data.get('price', 0), 
                                                      stock_data.get('capital', 100000))
            results['position_check'] = position_results
        
        # 评估入场点检查
        if market_data is not None and self.pre_trade_checklist['entry_point_check']['enabled']:
            entry_results = self._evaluate_entry_point(market_data)
            results['entry_point_check'] = entry_results
        
        # 计算总体得分和建议
        self._calculate_pre_trade_score(results)
        
        return results
    
    def _evaluate_fundamental(self, stock_data):
        """评估基本面检查项"""
        results = {
            'passed': 0,
            'failed': 0,
            'items': []
        }
        
        checklist = self.pre_trade_checklist['fundamental_check']['items']
        
        for item in checklist:
            result = {
                'id': item['id'],
                'name': item['name'],
                'criteria': item['criteria'],
                'passed': False,
                'actual': 'N/A',
                'comment': ''
            }
            
            # 净利润增长率检查
            if item['id'] == 'profit_growth':
                if 'profit_growth' in stock_data:
                    profit_growth = stock_data['profit_growth']
                    result['actual'] = f"{profit_growth:.1%}"
                    
                    if profit_growth > 0 and stock_data.get('quarterly_growth', 0) > 0.1:
                        result['passed'] = True
                        result['comment'] = "净利润增长率符合要求"
                    else:
                        result['comment'] = "净利润增长率不达标或季度环比增速不足"
                else:
                    result['comment'] = "缺少净利润增长率数据"
            
            # 资产负债率检查
            elif item['id'] == 'debt_ratio':
                if 'debt_ratio' in stock_data:
                    debt_ratio = stock_data['debt_ratio']
                    result['actual'] = f"{debt_ratio:.1%}"
                    
                    industry = stock_data.get('industry', 'manufacturing')
                    threshold = 0.4 if industry in ['tech', 'consumer'] else 0.6
                    
                    if debt_ratio < threshold:
                        result['passed'] = True
                        result['comment'] = f"资产负债率({debt_ratio:.1%})低于行业标准({threshold:.1%})"
                    else:
                        result['comment'] = f"资产负债率({debt_ratio:.1%})高于行业标准({threshold:.1%})"
                else:
                    result['comment'] = "缺少资产负债率数据"
            
            # 商誉/市值比检查
            elif item['id'] == 'goodwill_ratio':
                if 'goodwill_ratio' in stock_data:
                    goodwill_ratio = stock_data['goodwill_ratio']
                    result['actual'] = f"{goodwill_ratio:.1%}"
                    
                    if goodwill_ratio < 0.1:
                        result['passed'] = True
                        result['comment'] = "商誉/市值比较低,减值风险小"
                    else:
                        result['comment'] = f"商誉/市值比({goodwill_ratio:.1%})较高,有减值风险"
                else:
                    result['comment'] = "缺少商誉数据"
            
            # 股东结构检查
            elif item['id'] == 'shareholder_check':
                if 'institutional_holdings' in stock_data:
                    inst_holdings = stock_data['institutional_holdings']
                    result['actual'] = f"{inst_holdings:.1%}"
                    
                    if inst_holdings > 0.1:
                        result['passed'] = True
                        result['comment'] = "机构持仓充足,股东结构健康"
                    else:
                        # 检查前十大股东是否有信托计划或个人投资者扎堆
                        if stock_data.get('has_trust_plans', False) or stock_data.get('individual_investors_concentrated', False):
                            result['comment'] = "机构持仓低且前十大股东中有信托计划或个人投资者扎堆,可能为庄股"
                        else:
                            result['comment'] = "机构持仓较低"
                else:
                    result['comment'] = "缺少股东结构数据"
            
            # 监管问询函检查
            elif item['id'] == 'regulatory_inquiry':
                if 'regulatory_inquiries' in stock_data:
                    inquiries = stock_data['regulatory_inquiries']
                    result['actual'] = str(inquiries)
                    
                    if inquiries == 0:
                        result['passed'] = True
                        result['comment'] = "近1年无监管问询函,财务风险小"
                    else:
                        result['comment'] = f"近1年收到{inquiries}次监管问询函,可能存在财务问题"
                else:
                    result['comment'] = "缺少监管问询数据"
            
            # 统计结果
            if result['passed']:
                results['passed'] += 1
            else:
                results['failed'] += 1
                
            results['items'].append(result)
        
        # 计算通过率
        total = results['passed'] + results['failed']
        results['pass_rate'] = results['passed'] / total if total > 0 else 0
        results['overall_passed'] = results['pass_rate'] >= 0.6  # 至少60%通过
        
        return results
    
    def _evaluate_technical(self, market_data):
        """评估技术面检查项"""
        # 实现类似上面的评估逻辑,针对技术面检查项
        # 为简洁起见,这里省略具体实现
        pass
    
    def _evaluate_position(self, price, capital):
        """评估仓位检查项"""
        # 实现类似上面的评估逻辑,针对仓位检查项
        # 为简洁起见,这里省略具体实现
        pass
    
    def _evaluate_entry_point(self, market_data):
        """评估入场点检查项"""
        # 实现类似上面的评估逻辑,针对入场点检查项
        # 为简洁起见,这里省略具体实现
        pass
    
    def _calculate_pre_trade_score(self, results):
        """计算交易前总体得分和建议"""
        # 计算各部分权重和总分
        # 为简洁起见,这里省略具体实现
        pass
    
    def evaluate_during_trade(self, current_data, position_data):
        """
        评估交易中检查项
        
        Args:
            current_data (dict): 当前市场数据
            position_data (dict): 持仓数据
            
        Returns:
            dict: 评估结果
        """
        # 实现交易中各项检查的评估逻辑
        # 为简洁起见,这里省略具体实现
        pass
    
    def evaluate_post_trade(self, trade_data, market_data):
        """
        评估交易后检查项
        
        Args:
            trade_data (dict): 交易数据
            market_data (dict): 市场数据
            
        Returns:
            dict: 评估结果
        """
        # 实现交易后各项检查的评估逻辑
        # 为简洁起见,这里省略具体实现
        pass
    
    def record_trade(self, trade_data):
        """
        记录交易
        
        Args:
            trade_data (dict): 交易数据
        """
        self.trade_records.append(trade_data)
        self.update_trade_stats()
    
    def update_trade_stats(self):
        """更新交易统计"""
        if not self.trade_records:
            return
            
        self.trade_stats['total_trades'] = len(self.trade_records)
        
        # 计算盈利交易数量和胜率
        winning_trades = [t for t in self.trade_records if t.get('profit', 0) > 0]
        self.trade_stats['winning_trades'] = len(winning_trades)
        self.trade_stats['win_rate'] = len(winning_trades) / len(self.trade_records)
        
        # 计算平均盈利
        profits = [t.get('profit', 0) for t in self.trade_records]
        self.trade_stats['avg_profit'] = sum(profits) / len(profits) if profits else 0
        
        # 计算最大回撤
        # 为简洁起见,这里省略具体实现
    
    def get_trade_stats(self):
        """
        获取交易统计
        
        Returns:
            dict: 交易统计
        """
        return self.trade_stats
    
    def get_improvement_suggestions(self):
        """
        获取改进建议
        
        Returns:
            list: 改进建议列表
        """
        suggestions = []
        
        # 基于交易统计和记录,生成针对性建议
        if self.trade_stats['win_rate'] < 0.4:
            suggestions.append("胜率低于40%,需要停止交易并反思交易系统")
        elif self.trade_stats['win_rate'] < 0.5:
            suggestions.append("胜率低于50%,需要优化交易系统,重点关注入场点和止损策略")
        
        # 更多建议逻辑
        # 为简洁起见,这里省略具体实现
        
        return suggestions
    
    def export_checklist_report(self, filepath=None):
        """
        导出检查清单报告
        
        Args:
            filepath (str, optional): 导出文件路径
            
        Returns:
            str: 报告内容或文件路径
        """
        # 生成报告
        # 为简洁起见,这里省略具体实现
        pass

# Create a strategy class that wraps TradingChecklist functionality
class TradingChecklistStrategy(BaseStrategy):
    """
    交易清单策略
    
    基于交易清单检查器实现的策略,用于系统化地检查交易决策
    """
    
    def __init__(self, parameters=None):
        """
        初始化交易清单策略
        
        Args:
            parameters (dict): 策略参数
        """
        super().__init__(parameters or self.get_default_parameters())
        self.name = "交易清单策略"
        self.description = "基于系统化交易清单,对交易过程中的各项指标进行检查,提供交易建议"
        self.checklist = TradingChecklist()
    
    def get_default_parameters(self):
        """
        获取默认策略参数
        
        Returns:
            dict: 默认参数
        """
        return {
            'min_score_to_buy': 70,          # 最低买入得分
            'min_technical_score': 60,       # 最低技术面得分
            'min_fundamental_score': 50,     # 最低基本面得分
            'use_technical_checks': True,    # 使用技术面检查
            'use_fundamental_checks': True,  # 使用基本面检查
            'use_position_checks': True,     # 使用仓位检查
            'use_entry_checks': True,        # 使用入场点检查
        }
    
    def get_parameter_ranges(self):
        """
        获取参数范围,用于优化
        
        Returns:
            dict: 参数范围
        """
        return {
            'min_score_to_buy': {'min': 50, 'max': 90, 'step': 5},
            'min_technical_score': {'min': 40, 'max': 80, 'step': 5},
            'min_fundamental_score': {'min': 30, 'max': 70, 'step': 5},
        }
    
    def generate_signals(self, data):
        """
        生成交易信号
        
        Args:
            data (pd.DataFrame): 包含OHLCV的历史市场数据
            
        Returns:
            pd.Series: 交易信号序列 (1:买入, -1:卖出, 0:持有)
        """
        # 创建数据副本
        df = data.copy()
        
        # 初始化信号
        signals = pd.Series(0, index=df.index)
        
        # 模拟股票数据
        stock_data = {
            'price': df['close'].iloc[-1],
            'capital': 100000,
            'pe_ratio': 20,
            'profit_growth': 0.15,
            'debt_ratio': 0.4,
            'goodwill_ratio': 0.05,
            'institutional_holding': 0.15
        }
        
        # 对每个交易日评估
        for i in range(5, len(df)):
            # 获取当前数据窗口
            window = df.iloc[i-5:i+1]
            
            # 更新模拟股票数据
            stock_data['price'] = window['close'].iloc[-1]
            
            # 进行交易前评估
            pre_trade_results = self.checklist.evaluate_pre_trade(stock_data, window)
            
            # 计算总得分(简化版)
            total_score = 0
            items_count = 0
            
            for category, category_results in pre_trade_results.items():
                for item_result in category_results:
                    if item_result['result'] == 'pass':
                        total_score += 1
                    items_count += 1
            
            # 计算百分比得分
            score_percentage = (total_score / items_count * 100) if items_count > 0 else 0
            
            # 生成信号
            if score_percentage >= self.parameters['min_score_to_buy']:
                signals.iloc[i] = 1  # 买入信号
            elif score_percentage < self.parameters['min_score_to_buy'] * 0.7:
                signals.iloc[i] = -1  # 卖出信号
        
        return signals 
