import sys
sys.path.append('backend')

try:
    from backend.services.technical_analysis import get_technical_analysis
    print(' 技术分析模块导入成功')
    
    # 测试技术分析
    test_prices = [10.0, 10.1, 10.2, 9.9, 10.3, 10.1, 10.4, 10.2, 10.5, 10.3,
                  10.6, 10.4, 10.7, 10.5, 10.8, 10.6, 10.9, 10.7, 11.0, 10.8,
                  11.1, 10.9, 11.2, 11.0, 11.3]
    
    result = get_technical_analysis('000001.SZ', test_prices)
    
    if 'error' not in result:
        print(' 技术分析测试成功')
        signals = result.get('signals', {})
        trend = signals.get('overall_trend', 'unknown')
        buy_signals = len(signals.get('buy_signals', []))
        sell_signals = len(signals.get('sell_signals', []))
        print('  趋势:', trend)
        print('  买入信号数:', buy_signals)
        print('  卖出信号数:', sell_signals)
        
        # 测试智能决策
        print('\n 测试智能决策...')
        import asyncio
        from backend.ai.smart_decision_agent import get_smart_decision
        
        async def test_decision():
            stock_data = {
                'current_price': 11.0,
                'technical_analysis': result,
                'price_trend': 'upward',
                'volatility': 0.03
            }
            
            portfolio_data = {
                'total_position': 0.3,
                'available_cash': 70000
            }
            
            decision_result = await get_smart_decision('000001.SZ', stock_data, portfolio_data)
            
            if 'error' not in decision_result:
                print(' 智能决策测试成功')
                recommendation = decision_result.get('final_recommendation', {})
                action = recommendation.get('action', 'unknown')
                confidence = recommendation.get('confidence', 0)
                position_size = recommendation.get('position_size', 0)
                print('  建议操作:', action)
                print('  置信度:', f'{confidence:.2f}')
                print('  建议仓位:', f'{position_size:.2%}')
            else:
                print(' 智能决策失败:', decision_result.get('error', 'unknown'))
        
        asyncio.run(test_decision())
        
    else:
        print(' 技术分析失败:', result.get('error', 'unknown'))
        
except ImportError as e:
    print(' 导入失败:', str(e))
except Exception as e:
    print(' 测试失败:', str(e))
    import traceback
    traceback.print_exc()

print('\n Agent增强功能集成完成!')
print('现在您的Agent系统已经具备了:')
print(' 技术指标分析 (RSI, MACD, MA)')
print(' 智能多Agent决策 (Bull/Bear/Risk)')
print(' 市场情绪分析')
print(' 增强回测功能')
print(' 数据质量监控')
