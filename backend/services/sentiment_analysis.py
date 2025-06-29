"""
市场情绪分析服务
基于FinanceGPT思路的市场情绪和新闻影响分析
注意:此模块只提供分析结果,不执行交易
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import re
import json

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """市场情绪分析器"""
    
    def __init__(self):
        # 情绪关键词词典
        self.positive_keywords = [
            '上涨', '利好', '突破', '强势', '看好', '推荐', '买入',
            '增长', '盈利', '业绩', '创新高', '反弹', '机会'
        ]
        
        self.negative_keywords = [
            '下跌', '利空', '跌破', '弱势', '看空', '卖出', '抛售',
            '亏损', '风险', '创新低', '回调', '危机', '警告'
        ]
        
        self.neutral_keywords = [
            '震荡', '整理', '观望', '持有', '平稳', '调整'
        ]
    
    def analyze_text_sentiment(self, text: str) -> Dict:
        """分析文本情绪"""
        if not text:
            return {'sentiment': 'neutral', 'score': 0.0, 'confidence': 0.0}
        
        text = text.lower()
        
        positive_count = sum(1 for keyword in self.positive_keywords if keyword in text)
        negative_count = sum(1 for keyword in self.negative_keywords if keyword in text)
        neutral_count = sum(1 for keyword in self.neutral_keywords if keyword in text)
        
        total_count = positive_count + negative_count + neutral_count
        
        if total_count == 0:
            return {'sentiment': 'neutral', 'score': 0.0, 'confidence': 0.0}
        
        positive_ratio = positive_count / total_count
        negative_ratio = negative_count / total_count
        
        if positive_ratio > negative_ratio:
            sentiment = 'positive'
            score = positive_ratio - negative_ratio
        elif negative_ratio > positive_ratio:
            sentiment = 'negative'
            score = negative_ratio - positive_ratio
        else:
            sentiment = 'neutral'
            score = 0.0
        
        confidence = min(total_count / 10.0, 1.0)  # 基于关键词数量的置信度
        
        return {
            'sentiment': sentiment,
            'score': score,
            'confidence': confidence,
            'keyword_counts': {
                'positive': positive_count,
                'negative': negative_count,
                'neutral': neutral_count
            }
        }
    
    def analyze_news_impact(self, news_list: List[Dict]) -> Dict:
        """分析新闻对市场的影响"""
        if not news_list:
            return {
                'overall_sentiment': 'neutral',
                'impact_score': 0.0,
                'news_count': 0,
                'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0}
            }
        
        sentiment_scores = []
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for news in news_list:
            title = news.get('title', '')
            content = news.get('content', '')
            full_text = f"{title} {content}"
            
            sentiment_result = self.analyze_text_sentiment(full_text)
            sentiment_scores.append(sentiment_result['score'])
            sentiment_counts[sentiment_result['sentiment']] += 1
        
        # 计算整体情绪
        avg_score = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        if avg_score > 0.1:
            overall_sentiment = 'positive'
        elif avg_score < -0.1:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        return {
            'overall_sentiment': overall_sentiment,
            'impact_score': abs(avg_score),
            'news_count': len(news_list),
            'sentiment_distribution': sentiment_counts,
            'average_score': avg_score
        }

class MarketHotspotDetector:
    """市场热点识别器"""
    
    def __init__(self):
        # 热点关键词
        self.hotspot_keywords = {
            'AI': ['人工智能', 'AI', '机器学习', '深度学习', 'ChatGPT'],
            '新能源': ['新能源', '电动车', '锂电池', '光伏', '风电'],
            '医药': ['医药', '生物医药', '疫苗', '创新药', '医疗'],
            '芯片': ['芯片', '半导体', '集成电路', '晶圆', '存储'],
            '5G': ['5G', '通信', '基站', '物联网', 'IoT'],
            '消费': ['消费', '零售', '品牌', '电商', '直播带货']
        }
    
    def detect_hotspots(self, text_data: List[str]) -> Dict:
        """检测市场热点"""
        hotspot_scores = {sector: 0 for sector in self.hotspot_keywords}
        
        for text in text_data:
            if not text:
                continue
                
            text = text.lower()
            
            for sector, keywords in self.hotspot_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in text:
                        hotspot_scores[sector] += 1
        
        # 排序热点
        sorted_hotspots = sorted(hotspot_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'hotspots': sorted_hotspots,
            'top_hotspot': sorted_hotspots[0][0] if sorted_hotspots[0][1] > 0 else None,
            'hotspot_scores': hotspot_scores
        }

class MarketSentimentService:
    """市场情绪分析服务"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.hotspot_detector = MarketHotspotDetector()
        self.sentiment_history = []  # 存储历史情绪数据
    
    def analyze_market_sentiment(self, stock_code: str, news_data: List[Dict] = None, 
                               social_data: List[str] = None) -> Dict:
        """综合分析市场情绪"""
        try:
            analysis_result = {
                'stock_code': stock_code,
                'timestamp': datetime.now().isoformat(),
                'news_sentiment': {},
                'social_sentiment': {},
                'hotspots': {},
                'overall_assessment': {}
            }
            
            # 新闻情绪分析
            if news_data:
                analysis_result['news_sentiment'] = self.sentiment_analyzer.analyze_news_impact(news_data)
            
            # 社交媒体情绪分析
            if social_data:
                social_texts = [text for text in social_data if text]
                if social_texts:
                    social_sentiment_scores = []
                    for text in social_texts:
                        sentiment = self.sentiment_analyzer.analyze_text_sentiment(text)
                        social_sentiment_scores.append(sentiment['score'])
                    
                    avg_social_score = sum(social_sentiment_scores) / len(social_sentiment_scores)
                    analysis_result['social_sentiment'] = {
                        'average_score': avg_social_score,
                        'sentiment': 'positive' if avg_social_score > 0.1 else 'negative' if avg_social_score < -0.1 else 'neutral',
                        'sample_count': len(social_texts)
                    }
            
            # 热点检测
            all_texts = []
            if news_data:
                all_texts.extend([f"{news.get('title', '')} {news.get('content', '')}" for news in news_data])
            if social_data:
                all_texts.extend(social_data)
            
            if all_texts:
                analysis_result['hotspots'] = self.hotspot_detector.detect_hotspots(all_texts)
            
            # 综合评估
            analysis_result['overall_assessment'] = self._generate_overall_assessment(analysis_result)
            
            # 保存历史数据
            self.sentiment_history.append({
                'timestamp': datetime.now(),
                'stock_code': stock_code,
                'sentiment_score': analysis_result['overall_assessment'].get('sentiment_score', 0)
            })
            
            # 只保留最近100条记录
            if len(self.sentiment_history) > 100:
                self.sentiment_history = self.sentiment_history[-100:]
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"市场情绪分析失败 {stock_code}: {e}")
            return {'error': str(e)}
    
    def _generate_overall_assessment(self, analysis_result: Dict) -> Dict:
        """生成综合评估"""
        news_score = analysis_result.get('news_sentiment', {}).get('average_score', 0)
        social_score = analysis_result.get('social_sentiment', {}).get('average_score', 0)
        
        # 加权平均(新闻权重0.6,社交媒体权重0.4)
        overall_score = news_score * 0.6 + social_score * 0.4
        
        if overall_score > 0.2:
            sentiment_level = 'very_positive'
            market_impact = 'bullish'
        elif overall_score > 0.05:
            sentiment_level = 'positive'
            market_impact = 'slightly_bullish'
        elif overall_score < -0.2:
            sentiment_level = 'very_negative'
            market_impact = 'bearish'
        elif overall_score < -0.05:
            sentiment_level = 'negative'
            market_impact = 'slightly_bearish'
        else:
            sentiment_level = 'neutral'
            market_impact = 'neutral'
        
        return {
            'sentiment_score': overall_score,
            'sentiment_level': sentiment_level,
            'market_impact': market_impact,
            'confidence': min(abs(overall_score) * 2, 1.0),
            'recommendation': self._get_sentiment_recommendation(sentiment_level)
        }
    
    def _get_sentiment_recommendation(self, sentiment_level: str) -> str:
        """基于情绪水平给出建议"""
        recommendations = {
            'very_positive': '市场情绪非常乐观,可考虑适当增加仓位',
            'positive': '市场情绪偏乐观,可保持现有仓位或小幅增加',
            'neutral': '市场情绪中性,建议观望或维持现状',
            'negative': '市场情绪偏悲观,建议谨慎操作或减少仓位',
            'very_negative': '市场情绪非常悲观,建议降低仓位或观望'
        }
        return recommendations.get(sentiment_level, '建议谨慎操作')
    
    def get_sentiment_trend(self, stock_code: str, days: int = 7) -> Dict:
        """获取情绪趋势"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_data = [
            record for record in self.sentiment_history 
            if record['stock_code'] == stock_code and record['timestamp'] >= cutoff_date
        ]
        
        if not recent_data:
            return {'trend': 'no_data', 'data_points': 0}
        
        scores = [record['sentiment_score'] for record in recent_data]
        
        if len(scores) < 2:
            return {'trend': 'insufficient_data', 'data_points': len(scores)}
        
        # 简单趋势计算
        first_half = scores[:len(scores)//2]
        second_half = scores[len(scores)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        if second_avg > first_avg + 0.1:
            trend = 'improving'
        elif second_avg < first_avg - 0.1:
            trend = 'deteriorating'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'data_points': len(scores),
            'current_score': scores[-1],
            'average_score': sum(scores) / len(scores),
            'score_range': [min(scores), max(scores)]
        }

# 全局实例
market_sentiment_service = MarketSentimentService()

def get_market_sentiment(stock_code: str, news_data: List[Dict] = None, 
                        social_data: List[str] = None) -> Dict:
    """获取市场情绪分析 - 供其他模块调用"""
    return market_sentiment_service.analyze_market_sentiment(stock_code, news_data, social_data)

def get_sentiment_trend(stock_code: str, days: int = 7) -> Dict:
    """获取情绪趋势 - 供其他模块调用"""
    return market_sentiment_service.get_sentiment_trend(stock_code, days)
