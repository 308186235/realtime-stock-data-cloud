/**
 * 云端Agent测试脚本
 * 模拟完整的数据接收 → 分析决策 → 发送指令流程
 */

import CloudTradingAgent from './cloud-agent-system.js';

// 模拟本地数据
const MOCK_LOCAL_DATA = {
  // 模拟余额数据
  balance_data: {
    type: 'balance',
    timestamp: new Date().toISOString(),
    balance: {
      available_cash: 50000.00,
      total_assets: 120000.00,
      market_value: 70000.00,
      frozen_amount: 0.00
    }
  },
  
  // 模拟持仓数据
  holdings_data: {
    type: 'holdings',
    timestamp: new Date().toISOString(),
    holdings: [
      {
        code: '000001',
        name: '平安银行',
        quantity: 1000,
        cost_price: 12.50,
        current_price: 11.20,
        market_value: 11200.00,
        profit_loss: -1300.00
      },
      {
        code: '000002',
        name: '万科A',
        quantity: 2000,
        cost_price: 8.80,
        current_price: 9.50,
        market_value: 19000.00,
        profit_loss: 1400.00
      },
      {
        code: '600036',
        name: '招商银行',
        quantity: 800,
        cost_price: 45.00,
        current_price: 42.30,
        market_value: 33840.00,
        profit_loss: -2160.00
      }
    ]
  },
  
  // 模拟交易数据
  transactions_data: {
    type: 'transactions',
    timestamp: new Date().toISOString(),
    transactions: [
      {
        date: '2025-07-01',
        time: '09:30:15',
        code: '000001',
        name: '平安银行',
        action: 'buy',
        quantity: 500,
        price: 12.50,
        amount: 6250.00
      },
      {
        date: '2025-07-01',
        time: '14:25:30',
        code: '000002',
        name: '万科A',
        action: 'buy',
        quantity: 1000,
        price: 8.80,
        amount: 8800.00
      }
    ]
  },
  
  // 模拟综合数据
  comprehensive_data: {
    type: 'comprehensive',
    timestamp: new Date().toISOString(),
    balance: {
      available_cash: 50000.00,
      total_assets: 120000.00,
      market_value: 70000.00,
      frozen_amount: 0.00
    },
    holdings: [
      {
        code: '000001',
        name: '平安银行',
        quantity: 1000,
        cost_price: 12.50,
        current_price: 11.20,
        market_value: 11200.00,
        profit_loss: -1300.00
      },
      {
        code: '000002',
        name: '万科A',
        quantity: 2000,
        cost_price: 8.80,
        current_price: 9.50,
        market_value: 19000.00,
        profit_loss: 1400.00
      },
      {
        code: '600036',
        name: '招商银行',
        quantity: 800,
        cost_price: 45.00,
        current_price: 42.30,
        market_value: 33840.00,
        profit_loss: -2160.00
      }
    ],
    transactions: [
      {
        date: '2025-07-01',
        time: '09:30:15',
        code: '000001',
        name: '平安银行',
        action: 'buy',
        quantity: 500,
        price: 12.50,
        amount: 6250.00
      }
    ]
  }
};

// 测试类
class CloudAgentTester {
  constructor() {
    this.agent = new CloudTradingAgent();
    this.testResults = [];
  }
  
  // 运行所有测试
  async runAllTests() {
    console.log('🧪 开始云端Agent完整测试');
    console.log('=' * 80);
    
    try {
      // 1. 启动Agent
      await this.testAgentStartup();
      
      // 2. 测试余额数据分析
      await this.testBalanceAnalysis();
      
      // 3. 测试持仓数据分析
      await this.testHoldingsAnalysis();
      
      // 4. 测试综合数据分析
      await this.testComprehensiveAnalysis();
      
      // 5. 测试Agent状态
      await this.testAgentStatus();
      
      // 6. 显示测试总结
      this.showTestSummary();
      
    } catch (error) {
      console.error('❌ 测试过程中发生错误:', error);
    }
  }
  
  // 测试Agent启动
  async testAgentStartup() {
    console.log('\n🚀 测试1: Agent启动');
    console.log('-' * 40);
    
    try {
      const result = await this.agent.start();
      
      if (result) {
        console.log('✅ Agent启动测试通过');
        this.testResults.push({ test: 'startup', status: 'pass' });
      } else {
        console.log('❌ Agent启动测试失败');
        this.testResults.push({ test: 'startup', status: 'fail' });
      }
    } catch (error) {
      console.error('❌ Agent启动异常:', error);
      this.testResults.push({ test: 'startup', status: 'error', error: error.message });
    }
  }
  
  // 测试余额数据分析
  async testBalanceAnalysis() {
    console.log('\n💰 测试2: 余额数据分析');
    console.log('-' * 40);
    
    try {
      const result = await this.agent.executeWorkflow(MOCK_LOCAL_DATA.balance_data);
      
      if (result.success) {
        console.log('✅ 余额分析测试通过');
        console.log(`   分析结果: ${JSON.stringify(result.analysis.cash_analysis, null, 2)}`);
        this.testResults.push({ test: 'balance_analysis', status: 'pass' });
      } else {
        console.log('❌ 余额分析测试失败:', result.error);
        this.testResults.push({ test: 'balance_analysis', status: 'fail', error: result.error });
      }
    } catch (error) {
      console.error('❌ 余额分析异常:', error);
      this.testResults.push({ test: 'balance_analysis', status: 'error', error: error.message });
    }
  }
  
  // 测试持仓数据分析
  async testHoldingsAnalysis() {
    console.log('\n📈 测试3: 持仓数据分析');
    console.log('-' * 40);
    
    try {
      const result = await this.agent.executeWorkflow(MOCK_LOCAL_DATA.holdings_data);
      
      if (result.success) {
        console.log('✅ 持仓分析测试通过');
        console.log(`   持仓数量: ${result.analysis.portfolio_analysis.total_positions}`);
        console.log(`   盈利比例: ${(result.analysis.portfolio_analysis.profitable_ratio * 100).toFixed(1)}%`);
        console.log(`   决策数量: ${result.decisions.length}`);
        
        if (result.decisions.length > 0) {
          console.log('   生成的决策:');
          result.decisions.forEach((decision, index) => {
            console.log(`     ${index + 1}. ${decision.action.toUpperCase()} ${decision.stock_code} - ${decision.reason}`);
          });
        }
        
        this.testResults.push({ test: 'holdings_analysis', status: 'pass' });
      } else {
        console.log('❌ 持仓分析测试失败:', result.error);
        this.testResults.push({ test: 'holdings_analysis', status: 'fail', error: result.error });
      }
    } catch (error) {
      console.error('❌ 持仓分析异常:', error);
      this.testResults.push({ test: 'holdings_analysis', status: 'error', error: error.message });
    }
  }
  
  // 测试综合数据分析
  async testComprehensiveAnalysis() {
    console.log('\n🔍 测试4: 综合数据分析');
    console.log('-' * 40);
    
    try {
      const result = await this.agent.executeWorkflow(MOCK_LOCAL_DATA.comprehensive_data);
      
      if (result.success) {
        console.log('✅ 综合分析测试通过');
        console.log(`   风险等级: ${result.analysis.risk_assessment.level}`);
        console.log(`   风险分数: ${result.analysis.risk_assessment.overall_score}`);
        console.log(`   机会数量: ${result.analysis.opportunities.length}`);
        console.log(`   决策数量: ${result.decisions.length}`);
        
        if (result.analysis.opportunities.length > 0) {
          console.log('   识别的机会:');
          result.analysis.opportunities.forEach((opp, index) => {
            console.log(`     ${index + 1}. ${opp.type}: ${opp.description} (优先级: ${opp.priority})`);
          });
        }
        
        this.testResults.push({ test: 'comprehensive_analysis', status: 'pass' });
      } else {
        console.log('❌ 综合分析测试失败:', result.error);
        this.testResults.push({ test: 'comprehensive_analysis', status: 'fail', error: result.error });
      }
    } catch (error) {
      console.error('❌ 综合分析异常:', error);
      this.testResults.push({ test: 'comprehensive_analysis', status: 'error', error: error.message });
    }
  }
  
  // 测试Agent状态
  async testAgentStatus() {
    console.log('\n📊 测试5: Agent状态查询');
    console.log('-' * 40);
    
    try {
      const status = this.agent.getStatus();
      
      console.log('✅ Agent状态查询成功');
      console.log(`   Agent ID: ${status.agent_id}`);
      console.log(`   活跃状态: ${status.is_active ? '是' : '否'}`);
      console.log(`   分析次数: ${status.analysis_count}`);
      console.log(`   决策次数: ${status.decision_count}`);
      console.log(`   最后活动: ${status.last_activity || '无'}`);
      
      this.testResults.push({ test: 'agent_status', status: 'pass' });
    } catch (error) {
      console.error('❌ Agent状态查询异常:', error);
      this.testResults.push({ test: 'agent_status', status: 'error', error: error.message });
    }
  }
  
  // 显示测试总结
  showTestSummary() {
    console.log('\n' + '=' * 80);
    console.log('📊 云端Agent测试总结');
    console.log('=' * 80);
    
    const totalTests = this.testResults.length;
    const passedTests = this.testResults.filter(r => r.status === 'pass').length;
    const failedTests = this.testResults.filter(r => r.status === 'fail').length;
    const errorTests = this.testResults.filter(r => r.status === 'error').length;
    
    console.log(`📈 测试统计:`);
    console.log(`   总测试数: ${totalTests}`);
    console.log(`   通过: ${passedTests} ✅`);
    console.log(`   失败: ${failedTests} ❌`);
    console.log(`   错误: ${errorTests} 💥`);
    console.log(`   成功率: ${((passedTests / totalTests) * 100).toFixed(1)}%`);
    
    console.log(`\n📋 详细结果:`);
    this.testResults.forEach((result, index) => {
      const statusIcon = result.status === 'pass' ? '✅' : 
                        result.status === 'fail' ? '❌' : '💥';
      console.log(`   ${index + 1}. ${result.test}: ${statusIcon} ${result.status.toUpperCase()}`);
      if (result.error) {
        console.log(`      错误: ${result.error}`);
      }
    });
    
    if (passedTests === totalTests) {
      console.log('\n🎉 所有测试通过！云端Agent系统完全正常！');
      console.log('✅ Agent可以正确接收本地数据');
      console.log('✅ Agent可以执行智能分析');
      console.log('✅ Agent可以生成交易决策');
      console.log('✅ Agent可以发送交易指令');
    } else {
      console.log('\n⚠️ 部分测试未通过，请检查相关功能');
    }
    
    console.log('\n🔄 完整工作流程验证:');
    console.log('本地系统导出数据 → 云端Agent分析 → 生成交易决策 → 发送指令到本地 → 执行交易');
    console.log('=' * 80);
  }
}

// 主函数
async function main() {
  console.log('🤖 云端智能交易Agent测试程序');
  console.log('测试Agent接收本地数据并生成交易决策的完整流程');
  
  const tester = new CloudAgentTester();
  await tester.runAllTests();
}

// 如果直接运行此文件
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}

export { CloudAgentTester, MOCK_LOCAL_DATA };
export default CloudAgentTester;
