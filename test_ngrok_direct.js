/**
 * 直接测试ngrok隧道性能
 */

const https = require('https');
const { performance } = require('perf_hooks');

async function testNgrokDirect() {
    console.log('🚀 直接测试ngrok隧道性能');
    console.log('='.repeat(50));
    
    const ngrokUrl = 'https://2346443b1406.ngrok-free.app';
    
    const tests = [
        { name: 'ngrok根路径', path: '/' },
        { name: 'ngrok健康检查', path: '/api/health' },
        { name: 'ngrok健康检查2', path: '/health' },
        { name: 'ngrok API文档', path: '/docs' }
    ];
    
    for (const test of tests) {
        try {
            console.log(`\n🧪 测试: ${test.name}`);
            const startTime = performance.now();
            
            const result = await makeRequest(ngrokUrl + test.path);
            const latency = Math.round(performance.now() - startTime);
            
            console.log(`⏱️ 延迟: ${latency}ms`);
            console.log(`📊 状态码: ${result.statusCode}`);
            
            if (result.statusCode === 200) {
                console.log(`✅ ${test.name}: 成功`);
                console.log(`📄 响应长度: ${result.data.length}字符`);
            } else if (result.statusCode === 404) {
                console.log(`⚠️ ${test.name}: 路径不存在`);
            } else {
                console.log(`⚠️ ${test.name}: 状态码 ${result.statusCode}`);
            }
            
        } catch (error) {
            console.log(`❌ ${test.name}: 失败 - ${error.message}`);
        }
        
        await sleep(1000);
    }
    
    // 测试本地服务对比
    console.log('\n🖥️ 对比本地服务:');
    try {
        const startTime = performance.now();
        const result = await makeLocalRequest('http://localhost:8000/api/health');
        const latency = Math.round(performance.now() - startTime);
        
        console.log(`✅ 本地服务: ${latency}ms (状态码: ${result.statusCode})`);
    } catch (error) {
        console.log(`❌ 本地服务: 失败 - ${error.message}`);
    }
    
    console.log('\n🎯 测试完成');
}

function makeRequest(url) {
    return new Promise((resolve, reject) => {
        const urlObj = new URL(url);
        const options = {
            hostname: urlObj.hostname,
            port: 443,
            path: urlObj.pathname,
            method: 'GET',
            headers: {
                'User-Agent': 'Ngrok-Test/1.0',
                'Accept': 'application/json, text/html, */*'
            }
        };

        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                resolve({
                    statusCode: res.statusCode,
                    headers: res.headers,
                    data: data
                });
            });
        });

        req.on('error', reject);
        req.setTimeout(15000, () => {
            req.destroy();
            reject(new Error('Request timeout'));
        });

        req.end();
    });
}

function makeLocalRequest(url) {
    return new Promise((resolve, reject) => {
        const http = require('http');
        const urlObj = new URL(url);
        const options = {
            hostname: urlObj.hostname,
            port: urlObj.port || 80,
            path: urlObj.pathname,
            method: 'GET'
        };

        const req = http.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                resolve({
                    statusCode: res.statusCode,
                    data: data
                });
            });
        });

        req.on('error', reject);
        req.setTimeout(10000, () => {
            req.destroy();
            reject(new Error('Request timeout'));
        });

        req.end();
    });
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// 运行测试
testNgrokDirect().catch(console.error);
