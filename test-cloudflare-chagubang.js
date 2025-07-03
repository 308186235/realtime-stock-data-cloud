/**
 * 茶股帮Cloudflare集成测试脚本
 * 测试部署到Cloudflare的茶股帮数据源API
 */

const API_BASE_URL = 'https://api.aigupiao.me';
const CHAGUBANG_BASE = `${API_BASE_URL}/api/chagubang`;

class CloudflareChaguBangTester {
  constructor() {
    this.testResults = {};
    this.totalTests = 0;
    this.passedTests = 0;
  }

  // 通用请求方法
  async request(endpoint, options = {}) {
    try {
      const response = await fetch(`${CHAGUBANG_BASE}${endpoint}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      });

      const data = await response.json();
      return { success: response.ok, data, status: response.status };
    } catch (error) {
      return { success: false, error: error.message, status: 0 };
    }
  }

  // 测试健康检查
  async testHealth() {
    console.log('🔍 测试1: 健康检查');
    console.log('-'.repeat(30));

    const result = await this.request('/health');
    
    if (result.success && result.data.status) {
      console.log('✅ 健康检查通过');
      console.log(`   状态: ${result.data.status}`);
      console.log(`   服务: ${JSON.stringify(result.data.services || {})}`);
      this.testResults.health = true;
    } else {
      console.log('❌ 健康检查失败');
      console.log(`   错误: ${result.error || result.data?.error}`);
      this.testResults.health = false;
    }

    this.totalTests++;
    if (this.testResults.health) this.passedTests++;
  }

  // 测试服务统计
  async testStats() {
    console.log('\n🔍 测试2: 服务统计');
    console.log('-'.repeat(30));

    const result = await this.request('/stats');
    
    if (result.success) {
      console.log('✅ 服务统计获取成功');
      console.log(`   总股票数: ${result.data.data?.total_stocks || 0}`);
      console.log(`   最后更新: ${result.data.data?.last_update || 'N/A'}`);
      this.testResults.stats = true;
    } else {
      console.log('❌ 服务统计获取失败');
      console.log(`   错误: ${result.error || result.data?.error}`);
      this.testResults.stats = false;
    }

    this.totalTests++;
    if (this.testResults.stats) this.passedTests++;
  }

  // 测试股票数据获取
  async testStockData() {
    console.log('\n🔍 测试3: 股票数据获取');
    console.log('-'.repeat(30));

    // 测试获取所有股票
    const allStocksResult = await this.request('/stocks?limit=5');
    
    if (allStocksResult.success) {
      console.log('✅ 获取股票列表成功');
      console.log(`   返回数量: ${allStocksResult.data.data?.length || 0}`);
      
      // 如果有股票数据，测试获取单只股票
      if (allStocksResult.data.data && allStocksResult.data.data.length > 0) {
        const firstStock = allStocksResult.data.data[0];
        const stockCode = firstStock.stock_code;
        
        console.log(`   测试股票: ${stockCode}`);
        
        const singleStockResult = await this.request(`/stocks/${stockCode}`);
        if (singleStockResult.success) {
          console.log(`   ✅ 获取单只股票成功: ${stockCode}`);
          console.log(`   价格: ${singleStockResult.data.data?.last_price || 'N/A'}`);
        } else {
          console.log(`   ❌ 获取单只股票失败: ${stockCode}`);
        }
      }
      
      this.testResults.stockData = true;
    } else {
      console.log('❌ 获取股票列表失败');
      console.log(`   错误: ${allStocksResult.error || allStocksResult.data?.error}`);
      this.testResults.stockData = false;
    }

    this.totalTests++;
    if (this.testResults.stockData) this.passedTests++;
  }

  // 测试市场概览
  async testMarketOverview() {
    console.log('\n🔍 测试4: 市场概览');
    console.log('-'.repeat(30));

    const result = await this.request('/market/overview');
    
    if (result.success) {
      console.log('✅ 市场概览获取成功');
      const overview = result.data.data || {};
      console.log(`   总股票数: ${overview.total_stocks || 0}`);
      console.log(`   平均涨跌: ${(overview.avg_change || 0).toFixed(2)}%`);
      console.log(`   上涨股票: ${overview.rising_stocks || 0}`);
      console.log(`   下跌股票: ${overview.falling_stocks || 0}`);
      this.testResults.marketOverview = true;
    } else {
      console.log('❌ 市场概览获取失败');
      console.log(`   错误: ${result.error || result.data?.error}`);
      this.testResults.marketOverview = false;
    }

    this.totalTests++;
    if (this.testResults.marketOverview) this.passedTests++;
  }

  // 测试热门股票
  async testHotStocks() {
    console.log('\n🔍 测试5: 热门股票');
    console.log('-'.repeat(30));

    const result = await this.request('/market/hot?limit=5');
    
    if (result.success) {
      console.log('✅ 热门股票获取成功');
      const hotStocks = result.data.data || [];
      console.log(`   返回数量: ${hotStocks.length}`);
      
      if (hotStocks.length > 0) {
        console.log('   前3只热门股票:');
        hotStocks.slice(0, 3).forEach((stock, index) => {
          console.log(`   ${index + 1}. ${stock.stock_code} ${stock.stock_name || ''} ${(stock.change_pct || 0).toFixed(2)}%`);
        });
      }
      
      this.testResults.hotStocks = true;
    } else {
      console.log('❌ 热门股票获取失败');
      console.log(`   错误: ${result.error || result.data?.error}`);
      this.testResults.hotStocks = false;
    }

    this.totalTests++;
    if (this.testResults.hotStocks) this.passedTests++;
  }

  // 测试搜索功能
  async testSearch() {
    console.log('\n🔍 测试6: 搜索功能');
    console.log('-'.repeat(30));

    const searchQueries = ['平安', '000001', '银行'];
    let searchSuccess = false;

    for (const query of searchQueries) {
      console.log(`   搜索: "${query}"`);
      const result = await this.request(`/search?q=${encodeURIComponent(query)}&limit=3`);
      
      if (result.success) {
        const results = result.data.data || [];
        console.log(`   ✅ 找到 ${results.length} 个结果`);
        
        if (results.length > 0) {
          results.forEach(stock => {
            console.log(`      ${stock.stock_code} ${stock.stock_name || ''}`);
          });
          searchSuccess = true;
        }
      } else {
        console.log(`   ❌ 搜索失败: ${result.error || result.data?.error}`);
      }
    }

    this.testResults.search = searchSuccess;
    this.totalTests++;
    if (this.testResults.search) this.passedTests++;
  }

  // 测试Token管理
  async testTokenManagement() {
    console.log('\n🔍 测试7: Token管理');
    console.log('-'.repeat(30));

    // 测试添加Token
    const testToken = 'test_token_' + Date.now();
    const addResult = await this.request('/token/add', {
      method: 'POST',
      body: JSON.stringify({
        token: testToken,
        description: '测试Token'
      })
    });

    if (addResult.success) {
      console.log('✅ Token添加成功');
      
      // 测试Token验证
      const testResult = await this.request('/token/test', {
        method: 'POST',
        body: JSON.stringify({
          token: testToken
        })
      });

      if (testResult.success) {
        console.log('✅ Token测试成功');
        console.log(`   Token有效性: ${testResult.data.data?.is_valid ? '有效' : '无效'}`);
        this.testResults.tokenManagement = true;
      } else {
        console.log('❌ Token测试失败');
        this.testResults.tokenManagement = false;
      }
    } else {
      console.log('❌ Token添加失败');
      console.log(`   错误: ${addResult.error || addResult.data?.error}`);
      this.testResults.tokenManagement = false;
    }

    this.totalTests++;
    if (this.testResults.tokenManagement) this.passedTests++;
  }

  // 运行所有测试
  async runAllTests() {
    console.log('🧪 茶股帮Cloudflare集成测试');
    console.log('='.repeat(50));
    console.log(`API地址: ${CHAGUBANG_BASE}`);
    console.log('='.repeat(50));

    try {
      await this.testHealth();
      await this.testStats();
      await this.testStockData();
      await this.testMarketOverview();
      await this.testHotStocks();
      await this.testSearch();
      await this.testTokenManagement();

      this.printSummary();
    } catch (error) {
      console.error('\n❌ 测试过程中发生异常:', error);
    }
  }

  // 打印测试总结
  printSummary() {
    console.log('\n' + '='.repeat(50));
    console.log('🎯 测试总结');
    console.log('='.repeat(50));

    for (const [testName, result] of Object.entries(this.testResults)) {
      const status = result ? '✅ 通过' : '❌ 失败';
      console.log(`${status} ${testName}`);
    }

    console.log(`\n📊 总体结果: ${this.passedTests}/${this.totalTests} 测试通过`);

    if (this.passedTests === this.totalTests) {
      console.log('\n🎉 所有测试通过！茶股帮Cloudflare集成工作正常');
      console.log('\n📋 下一步操作:');
      console.log('1. 添加真实的茶股帮Token');
      console.log('2. 配置定时任务同步数据');
      console.log('3. 更新前端应用使用新API');
      console.log('4. 监控系统运行状态');
    } else {
      console.log(`\n⚠️ ${this.totalTests - this.passedTests} 个测试失败`);
      console.log('\n🔧 可能的解决方案:');
      console.log('1. 检查Cloudflare Workers部署状态');
      console.log('2. 验证Supabase数据库连接');
      console.log('3. 确认KV命名空间配置');
      console.log('4. 检查域名DNS解析');
    }

    console.log('\n📞 技术支持:');
    console.log('- Cloudflare Workers文档: https://developers.cloudflare.com/workers/');
    console.log('- Supabase文档: https://supabase.com/docs');
    console.log('- API文档: https://api.aigupiao.me/api/chagubang/');
  }
}

// 运行测试
async function main() {
  const tester = new CloudflareChaguBangTester();
  await tester.runAllTests();
}

// 如果是Node.js环境
if (typeof require !== 'undefined' && require.main === module) {
  // 需要安装 node-fetch: npm install node-fetch
  const fetch = require('node-fetch');
  global.fetch = fetch;
  main().catch(console.error);
}

// 如果是浏览器环境
if (typeof window !== 'undefined') {
  window.testChaguBangCloudflare = main;
}

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { CloudflareChaguBangTester, main };
}
