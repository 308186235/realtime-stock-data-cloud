/**
 * 移动应用连接测试脚本
 */

const fs = require('fs');
const { exec } = require('child_process');

console.log('📱 移动应用连接测试...\n');

// 测试API连接
async function testAPI() {
    console.log('🌐 测试API连接...');
    
    const endpoints = [
        'https://api.aigupiao.me/health',
        'https://api.aigupiao.me/api/test',
        'https://api.aigupiao.me/api/trading/brokers',
        'https://api.aigupiao.me/api/trading/account'
    ];
    
    for (const endpoint of endpoints) {
        try {
            const response = await fetch(endpoint);
            const data = await response.json();
            console.log(`✅ ${endpoint}: ${response.status}`);
        } catch (error) {
            console.log(`❌ ${endpoint}: ${error.message}`);
        }
    }
}

// 检查移动应用配置
function checkMobileConfig() {
    console.log('\n📋 检查移动应用配置...');
    
    // 检查env.js
    try {
        const envContent = fs.readFileSync('炒股养家/env.js', 'utf8');
        if (envContent.includes('api.aigupiao.me')) {
            console.log('✅ env.js API地址配置正确');
        } else {
            console.log('❌ env.js API地址配置错误');
        }
    } catch (error) {
        console.log('❌ env.js读取失败:', error.message);
    }
    
    // 检查config.js
    try {
        const configContent = fs.readFileSync('炒股养家/services/config.js', 'utf8');
        if (configContent.includes('api.aigupiao.me')) {
            console.log('✅ config.js API地址配置正确');
        } else {
            console.log('❌ config.js API地址配置错误');
        }
    } catch (error) {
        console.log('❌ config.js读取失败:', error.message);
    }
    
    // 检查manifest.json
    try {
        const manifest = JSON.parse(fs.readFileSync('炒股养家/manifest.json', 'utf8'));
        console.log('✅ manifest.json解析成功');
        console.log(`   AppID: ${manifest.appid}`);
        console.log(`   版本: ${manifest.versionName}`);
        
        // 检查网络权限
        const permissions = manifest['app-plus']?.distribute?.android?.permissions || [];
        const hasInternet = permissions.some(p => p.includes('INTERNET'));
        console.log(`   网络权限: ${hasInternet ? '✅' : '❌'}`);
        
    } catch (error) {
        console.log('❌ manifest.json解析失败:', error.message);
    }
}

// 检查编译状态
function checkCompileStatus() {
    console.log('\n🔧 检查编译状态...');
    
    const unpackagePath = '炒股养家/unpackage';
    if (fs.existsSync(unpackagePath)) {
        console.log('✅ unpackage目录存在');
        
        const distPath = `${unpackagePath}/dist`;
        if (fs.existsSync(distPath)) {
            console.log('✅ dist目录存在');
            
            const devPath = `${distPath}/dev`;
            if (fs.existsSync(devPath)) {
                console.log('✅ dev编译输出存在');
                
                const appPlusPath = `${devPath}/app-plus`;
                if (fs.existsSync(appPlusPath)) {
                    console.log('✅ app-plus编译输出存在');
                } else {
                    console.log('❌ app-plus编译输出缺失');
                }
            } else {
                console.log('❌ dev编译输出不存在');
            }
        } else {
            console.log('❌ dist目录不存在');
        }
    } else {
        console.log('❌ unpackage目录不存在');
    }
}

// 生成移动应用测试报告
function generateTestReport() {
    console.log('\n📊 生成测试报告...');
    
    const report = {
        timestamp: new Date().toISOString(),
        api_status: 'checking...',
        mobile_config: 'checking...',
        compile_status: 'checking...',
        recommendations: []
    };
    
    // 保存报告
    fs.writeFileSync('mobile_app_test_report.json', JSON.stringify(report, null, 2));
    console.log('✅ 测试报告已保存到 mobile_app_test_report.json');
}

// 提供解决方案
function provideSolutions() {
    console.log('\n💡 可能的解决方案:');
    console.log('1. 重新编译移动应用');
    console.log('   - 在HBuilderX中选择"运行" → "运行到浏览器"');
    console.log('   - 或者运行到手机模拟器');
    
    console.log('\n2. 检查网络连接');
    console.log('   - 确保设备能访问 https://api.aigupiao.me');
    console.log('   - 检查防火墙设置');
    
    console.log('\n3. 清理缓存');
    console.log('   - 删除 unpackage 目录');
    console.log('   - 重新编译项目');
    
    console.log('\n4. 检查移动应用日志');
    console.log('   - 在HBuilderX控制台查看错误信息');
    console.log('   - 检查网络请求是否成功');
    
    console.log('\n5. 使用浏览器测试');
    console.log('   - 先在浏览器中测试H5版本');
    console.log('   - 确认功能正常后再测试移动端');
}

// 主函数
async function main() {
    try {
        await testAPI();
        checkMobileConfig();
        checkCompileStatus();
        generateTestReport();
        provideSolutions();
        
        console.log('\n✨ 测试完成！');
        console.log('\n如果问题仍然存在，请提供：');
        console.log('1. HBuilderX控制台的错误日志');
        console.log('2. 移动应用的具体错误信息');
        console.log('3. 网络请求的失败详情');
        
    } catch (error) {
        console.error('❌ 测试过程中出现错误:', error.message);
    }
}

// 运行测试
main();
