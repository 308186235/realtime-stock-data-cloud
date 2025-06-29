
// 前端连接测试代码 (JavaScript)
const API_BASE_URL = 'http://localhost:8002';

// 测试GET请求
async function testGetRequest() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        const data = await response.json();
        console.log('✅ GET请求成功:', data);
        return true;
    } catch (error) {
        console.error('❌ GET请求失败:', error);
        return false;
    }
}

// 测试POST请求
async function testPostRequest() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/test/echo`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: '前端测试消息',
                timestamp: new Date().toISOString()
            })
        });
        const data = await response.json();
        console.log('✅ POST请求成功:', data);
        return true;
    } catch (error) {
        console.error('❌ POST请求失败:', error);
        return false;
    }
}

// 运行所有测试
async function runAllTests() {
    console.log('🚀 开始前端连接测试...');
    
    const getResult = await testGetRequest();
    const postResult = await testPostRequest();
    
    if (getResult && postResult) {
        console.log('🎉 前后端连接测试全部通过！');
    } else {
        console.log('⚠️ 部分测试失败，请检查配置');
    }
}

// 执行测试
runAllTests();
