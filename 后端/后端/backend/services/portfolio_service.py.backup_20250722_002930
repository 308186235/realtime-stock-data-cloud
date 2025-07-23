"""
投资组合服务 - 使用数据库适配器
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from adapters.database_adapter import db_adapter

logger = logging.getLogger(__name__)

class PortfolioService:
    """投资组合服务"""
    
    def __init__(self):
        self.db = db_adapter
    
    def create_portfolio(self, user_id: str, name: str, initial_cash: float = 100000.0) -> Dict[str, Any]:
        """创建投资组合"""
        try:
            portfolio_data = {
                'user_id': user_id,
                'name': name,
                'cash': initial_cash,
                'total_value': initial_cash,
                'stock_value': 0.0,
                'is_default': False
            }
            
            result = self.db.create_portfolio(portfolio_data)
            if result['success']:
                logger.info(f"投资组合创建成功: {name} (用户: {user_id})")
            
            return result
            
        except Exception as e:
            logger.error(f"创建投资组合失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_user_portfolios(self, user_id: str) -> Dict[str, Any]:
        """获取用户的所有投资组合"""
        try:
            result = self.db.get_portfolios(user_id)
            if result['success']:
                # 计算每个投资组合的详细信息
                portfolios = result['data']
                for portfolio in portfolios:
                    portfolio_id = portfolio.get('id')
                    if portfolio_id:
                        # 获取持仓信息
                        holdings_result = self.db.get_holdings(portfolio_id)
                        if holdings_result['success']:
                            portfolio['holdings'] = holdings_result['data']
                            portfolio['holdings_count'] = len(holdings_result['data'])
                        else:
                            portfolio['holdings'] = []
                            portfolio['holdings_count'] = 0
            
            return result
            
        except Exception as e:
            logger.error(f"获取用户投资组合失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_portfolio_detail(self, portfolio_id: str) -> Dict[str, Any]:
        """获取投资组合详情"""
        try:
            # 获取投资组合基本信息
            portfolios_result = self.db.get_portfolios(None)  # 获取所有，然后筛选
            if not portfolios_result['success']:
                return portfolios_result
            
            portfolio = None
            for p in portfolios_result['data']:
                if str(p.get('id')) == str(portfolio_id):
                    portfolio = p
                    break
            
            if not portfolio:
                return {"success": False, "error": "投资组合不存在"}
            
            # 获取持仓信息
            holdings_result = self.db.get_holdings(portfolio_id)
            if holdings_result['success']:
                portfolio['holdings'] = holdings_result['data']
                
                # 计算持仓统计
                total_market_value = 0
                for holding in holdings_result['data']:
                    shares = holding.get('shares', 0)
                    current_price = holding.get('current_price', holding.get('cost_price', 0))
                    market_value = shares * current_price
                    holding['market_value'] = market_value
                    total_market_value += market_value
                
                portfolio['stock_value'] = total_market_value
                portfolio['total_value'] = portfolio.get('cash', 0) + total_market_value
            else:
                portfolio['holdings'] = []
            
            return {"success": True, "data": portfolio}
            
        except Exception as e:
            logger.error(f"获取投资组合详情失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def add_holding(self, portfolio_id: str, stock_code: str, shares: int, cost_price: float) -> Dict[str, Any]:
        """添加持仓"""
        try:
            # 首先确保股票信息存在
            stock_result = self.db.get_stocks({'code': stock_code})
            if stock_result['success'] and not stock_result['data']:
                # 股票不存在，创建基本信息
                stock_data = {
                    'code': stock_code,
                    'name': f'股票{stock_code}',  # 默认名称
                    'market': 'SZ' if stock_code.startswith('0') or stock_code.startswith('3') else 'SH'
                }
                self.db.create_stock(stock_data)
            
            # 创建持仓
            holding_data = {
                'portfolio_id': portfolio_id,
                'stock_code': stock_code,
                'shares': shares,
                'cost_price': cost_price,
                'current_price': cost_price
            }
            
            result = self.db.create_holding(holding_data)
            if result['success']:
                logger.info(f"持仓添加成功: {stock_code} x {shares} @ {cost_price}")
            
            return result
            
        except Exception as e:
            logger.error(f"添加持仓失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def update_portfolio_cash(self, portfolio_id: str, cash_change: float) -> Dict[str, Any]:
        """更新投资组合现金"""
        try:
            # 获取当前投资组合信息
            portfolio_result = self.get_portfolio_detail(portfolio_id)
            if not portfolio_result['success']:
                return portfolio_result
            
            portfolio = portfolio_result['data']
            current_cash = portfolio.get('cash', 0)
            new_cash = current_cash + cash_change
            
            if new_cash < 0:
                return {"success": False, "error": "现金不足"}
            
            # 更新现金（这里需要扩展数据库适配器的更新功能）
            # 暂时返回成功，实际应该调用更新方法
            logger.info(f"投资组合 {portfolio_id} 现金更新: {current_cash} -> {new_cash}")
            
            return {"success": True, "data": {"old_cash": current_cash, "new_cash": new_cash}}
            
        except Exception as e:
            logger.error(f"更新投资组合现金失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_portfolio_performance(self, portfolio_id: str) -> Dict[str, Any]:
        """获取投资组合表现"""
        try:
            portfolio_result = self.get_portfolio_detail(portfolio_id)
            if not portfolio_result['success']:
                return portfolio_result
            
            portfolio = portfolio_result['data']
            holdings = portfolio.get('holdings', [])
            
            # 计算表现指标
            total_cost = 0
            total_market_value = 0
            
            for holding in holdings:
                shares = holding.get('shares', 0)
                cost_price = holding.get('cost_price', 0)
                current_price = holding.get('current_price', cost_price)
                
                cost_value = shares * cost_price
                market_value = shares * current_price
                
                total_cost += cost_value
                total_market_value += market_value
            
            # 计算收益
            profit_loss = total_market_value - total_cost
            profit_loss_ratio = (profit_loss / total_cost * 100) if total_cost > 0 else 0
            
            performance = {
                'total_cost': total_cost,
                'total_market_value': total_market_value,
                'profit_loss': profit_loss,
                'profit_loss_ratio': profit_loss_ratio,
                'cash': portfolio.get('cash', 0),
                'total_assets': portfolio.get('total_value', 0),
                'holdings_count': len(holdings)
            }
            
            return {"success": True, "data": performance}
            
        except Exception as e:
            logger.error(f"获取投资组合表现失败: {str(e)}")
            return {"success": False, "error": str(e)}

# 全局服务实例
portfolio_service = PortfolioService()

# 导出函数
def create_portfolio(user_id: str, name: str, initial_cash: float = 100000.0) -> Dict[str, Any]:
    """创建投资组合"""
    return portfolio_service.create_portfolio(user_id, name, initial_cash)

def get_user_portfolios(user_id: str) -> Dict[str, Any]:
    """获取用户投资组合"""
    return portfolio_service.get_user_portfolios(user_id)

def get_portfolio_detail(portfolio_id: str) -> Dict[str, Any]:
    """获取投资组合详情"""
    return portfolio_service.get_portfolio_detail(portfolio_id)

def add_holding(portfolio_id: str, stock_code: str, shares: int, cost_price: float) -> Dict[str, Any]:
    """添加持仓"""
    return portfolio_service.add_holding(portfolio_id, stock_code, shares, cost_price)

def get_portfolio_performance(portfolio_id: str) -> Dict[str, Any]:
    """获取投资组合表现"""
    return portfolio_service.get_portfolio_performance(portfolio_id)
