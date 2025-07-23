#!/usr/bin/env python3
"""
Agent数据分析演示
展示如何使用混合数据源进行智能分析
"""

import json
import requests
from datetime import datetime

class TradingAgent:
    """交易分析Agent"""
    
    def __init__(self, api_base="https://api.aigupiao.me"):
        self.api_base = api_base
        self.analysis_results = {}
    
    def get_complete_data(self, stock_codes=None):
        """获取完整数据集"""
        if stock_codes is None:
            stock_codes = ["000001", "600036", "000002"]
        
        try:
            url = f"{self.api_base}/api/agent/complete-data"
            params = {"stocks": ",".join(stock_codes)}
            
            print("🤖 Agent正在获取完整数据集...")
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("✅ 完整数据集获取成功")
                    return data["data"]
                else:
                    print("❌ API返回失败状态")
                    return None
            else:
                print(f"❌ API请求失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 数据获取异常: {e}")
            return None
    
    def analyze_market_data(self, complete_data):
        """分析市场数据"""
        print("\n📊 分析市场数据...")
        
        stock_data = complete_data.get("stock_data", {})
        stocks = stock_data.get("stocks", [])
        
        if not stocks:
            print("⚠️ 没有股票数据可分析")
            return {}
        
        analysis = {
            "stock_count": len(stocks),
            "stocks_analysis": [],
            "market_summary": {}
        }
        
        total_volume = 0
        price_changes = []
        
        for stock in stocks:
            stock_analysis = {
                "code": stock.get("code", "未知"),
                "name": stock.get("name", "未知"),
                "current_price": stock.get("current_price", 0),
                "volume": stock.get("volume", 0),
                "change_percent": stock.get("change_percent", 0)
            }
            
            analysis["stocks_analysis"].append(stock_analysis)
            total_volume += stock_analysis["volume"]
            price_changes.append(stock_analysis["change_percent"])
            
            print(f"   📈 {stock_analysis['code']} {stock_analysis['name']}")
            print(f"      价格: ¥{stock_analysis['current_price']:.2f}")
            print(f"      涨跌: {stock_analysis['change_percent']:+.2f}%")
        
        # 市场总结
        avg_change = sum(price_changes) / len(price_changes) if price_changes else 0
        rising_stocks = len([c for c in price_changes if c > 0])
        
        analysis["market_summary"] = {
            "total_volume": total_volume,
            "average_change": avg_change,
            "rising_stocks": rising_stocks,
            "falling_stocks": len(price_changes) - rising_stocks,
            "market_sentiment": "看涨" if avg_change > 0 else "看跌" if avg_change < 0 else "平稳"
        }
        
        print(f"\n📊 市场总结:")
        print(f"   平均涨跌: {avg_change:+.2f}%")
        print(f"   上涨股票: {rising_stocks}/{len(price_changes)}")
        print(f"   市场情绪: {analysis['market_summary']['market_sentiment']}")
        
        return analysis
    
    def analyze_portfolio(self, complete_data):
        """分析投资组合"""
        print("\n💼 分析投资组合...")
        
        trading_data = complete_data.get("trading_data", {})
        positions_data = trading_data.get("positions", {})
        balance_data = trading_data.get("balance", {})
        
        positions = positions_data.get("positions", [])
        balance = balance_data.get("balance", {})
        
        if not positions:
            print("⚠️ 没有持仓数据可分析")
            return {}
        
        analysis = {
            "positions_count": len(positions),
            "positions_analysis": [],
            "portfolio_summary": {},
            "risk_analysis": {}
        }
        
        total_market_value = 0
        total_cost = 0
        total_profit_loss = 0
        
        for position in positions:
            pos_analysis = {
                "code": position.get("stock_code", "未知"),
                "name": position.get("stock_name", "未知"),
                "quantity": position.get("quantity", 0),
                "current_price": position.get("current_price", 0),
                "market_value": position.get("market_value", 0),
                "cost_price": position.get("cost_price", 0),
                "profit_loss": position.get("profit_loss", 0),
                "profit_loss_ratio": position.get("profit_loss_ratio", 0)
            }
            
            analysis["positions_analysis"].append(pos_analysis)
            total_market_value += pos_analysis["market_value"]
            total_cost += pos_analysis["quantity"] * pos_analysis["cost_price"]
            total_profit_loss += pos_analysis["profit_loss"]
            
            print(f"   📊 {pos_analysis['code']} {pos_analysis['name']}")
            print(f"      持仓: {pos_analysis['quantity']} 股")
            print(f"      市值: ¥{pos_analysis['market_value']:,.2f}")
            print(f"      盈亏: ¥{pos_analysis['profit_loss']:+,.2f} ({pos_analysis['profit_loss_ratio']:+.2f}%)")
        
        # 组合总结
        total_profit_ratio = (total_profit_loss / total_cost * 100) if total_cost > 0 else 0
        available_cash = balance.get("available_cash", 0)
        total_assets = balance.get("total_assets", 0)
        
        analysis["portfolio_summary"] = {
            "total_market_value": total_market_value,
            "total_cost": total_cost,
            "total_profit_loss": total_profit_loss,
            "total_profit_ratio": total_profit_ratio,
            "available_cash": available_cash,
            "total_assets": total_assets,
            "position_ratio": (total_market_value / total_assets * 100) if total_assets > 0 else 0
        }
        
        print(f"\n💼 组合总结:")
        print(f"   总市值: ¥{total_market_value:,.2f}")
        print(f"   总盈亏: ¥{total_profit_loss:+,.2f} ({total_profit_ratio:+.2f}%)")
        print(f"   可用资金: ¥{available_cash:,.2f}")
        print(f"   仓位比例: {analysis['portfolio_summary']['position_ratio']:.1f}%")
        
        return analysis
    
    def generate_trading_suggestions(self, market_analysis, portfolio_analysis):
        """生成交易建议"""
        print("\n🎯 生成交易建议...")
        
        suggestions = {
            "timestamp": datetime.now().isoformat(),
            "market_view": "",
            "position_advice": [],
            "risk_warnings": [],
            "action_items": []
        }
        
        # 市场观点
        market_sentiment = market_analysis.get("market_summary", {}).get("market_sentiment", "平稳")
        avg_change = market_analysis.get("market_summary", {}).get("average_change", 0)
        
        if market_sentiment == "看涨":
            suggestions["market_view"] = f"市场整体向好,平均涨幅{avg_change:.2f}%,可考虑适当加仓"
        elif market_sentiment == "看跌":
            suggestions["market_view"] = f"市场整体偏弱,平均跌幅{abs(avg_change):.2f}%,建议谨慎操作"
        else:
            suggestions["market_view"] = "市场震荡整理,建议观望为主"
        
        # 持仓建议
        positions = portfolio_analysis.get("positions_analysis", [])
        for position in positions:
            profit_ratio = position.get("profit_loss_ratio", 0)
            
            if profit_ratio > 10:
                suggestions["position_advice"].append({
                    "stock": f"{position['code']} {position['name']}",
                    "advice": "考虑部分止盈",
                    "reason": f"盈利{profit_ratio:.1f}%,建议锁定部分利润"
                })
            elif profit_ratio < -10:
                suggestions["position_advice"].append({
                    "stock": f"{position['code']} {position['name']}",
                    "advice": "关注止损",
                    "reason": f"亏损{abs(profit_ratio):.1f}%,需要关注风险控制"
                })
        
        # 风险提醒
        position_ratio = portfolio_analysis.get("portfolio_summary", {}).get("position_ratio", 0)
        if position_ratio > 80:
            suggestions["risk_warnings"].append("仓位过重,建议适当减仓")
        elif position_ratio < 30:
            suggestions["risk_warnings"].append("仓位较轻,可考虑适当加仓")
        
        # 行动项目
        if market_sentiment == "看涨" and position_ratio < 70:
            suggestions["action_items"].append("市场向好且仓位不重,可考虑选股加仓")
        
        if any(pos.get("profit_loss_ratio", 0) > 15 for pos in positions):
            suggestions["action_items"].append("部分持仓盈利较多,建议分批止盈")
        
        # 显示建议
        print(f"📈 市场观点: {suggestions['market_view']}")
        
        if suggestions["position_advice"]:
            print("📊 持仓建议:")
            for advice in suggestions["position_advice"]:
                print(f"   • {advice['stock']}: {advice['advice']} - {advice['reason']}")
        
        if suggestions["risk_warnings"]:
            print("⚠️ 风险提醒:")
            for warning in suggestions["risk_warnings"]:
                print(f"   • {warning}")
        
        if suggestions["action_items"]:
            print("🎯 行动建议:")
            for action in suggestions["action_items"]:
                print(f"   • {action}")
        
        return suggestions
    
    def run_complete_analysis(self, stock_codes=None):
        """运行完整分析"""
        print("🤖 AI交易Agent开始分析")
        print("=" * 60)
        
        # 1. 获取完整数据
        complete_data = self.get_complete_data(stock_codes)
        if not complete_data:
            print("❌ 无法获取数据,分析终止")
            return None
        
        # 2. 分析市场数据
        market_analysis = self.analyze_market_data(complete_data)
        
        # 3. 分析投资组合
        portfolio_analysis = self.analyze_portfolio(complete_data)
        
        # 4. 生成交易建议
        suggestions = self.generate_trading_suggestions(market_analysis, portfolio_analysis)
        
        # 5. 保存分析结果
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "data_sources": complete_data.get("data_sources", {}),
            "market_analysis": market_analysis,
            "portfolio_analysis": portfolio_analysis,
            "trading_suggestions": suggestions
        }
        
        print("\n" + "=" * 60)
        print("🎉 AI交易Agent分析完成!")
        print("=" * 60)
        
        return self.analysis_results

def main():
    """主函数"""
    print("🤖 AI交易Agent演示")
    print("展示如何使用混合数据源进行智能分析")
    print()
    
    # 创建Agent实例
    agent = TradingAgent()
    
    # 运行完整分析
    results = agent.run_complete_analysis()
    
    if results:
        print("\n📋 分析结果已生成")
        print("Agent成功整合了:")
        print("✅ 股票实时数据 (数据库)")
        print("✅ 本地交易数据 (OneDrive)")
        print("✅ 智能分析和建议")
    else:
        print("\n💥 分析失败")
        print("请检查API连接和数据源状态")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
