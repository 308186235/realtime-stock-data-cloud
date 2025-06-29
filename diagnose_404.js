/**
 * 移动应用404问题诊断脚本
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 开始诊断移动应用404问题...\n');

// 检查关键文件是否存在
const criticalFiles = [
    '炒股养家/pages.json',
    '炒股养家/manifest.json',
    '炒股养家/App.vue',
    '炒股养家/main.js',
    '炒股养家/pages/index/index.vue',
    '炒股养家/pages/ai-analysis/index.vue',
    '炒股养家/pages/ai-training/index.vue',
    '炒股养家/components/BackendConnectionStatus.vue'
];

console.log('📁 检查关键文件存在性:');
criticalFiles.forEach(file => {
    const exists = fs.existsSync(file);
    console.log(`${exists ? '✅' : '❌'} ${file}`);
});

// 检查pages.json配置
console.log('\n📋 检查pages.json配置:');
try {
    const pagesJson = JSON.parse(fs.readFileSync('炒股养家/pages.json', 'utf8'));
    
    console.log(`✅ pages.json解析成功`);
    console.log(`📄 总页面数: ${pagesJson.pages.length}`);
    
    // 检查首页配置
    const indexPage = pagesJson.pages[0];
    console.log(`🏠 首页路径: ${indexPage.path}`);
    
    // 检查关键页面是否注册
    const keyPages = ['pages/index/index', 'pages/ai-analysis/index', 'pages/ai-training/index'];
    keyPages.forEach(pagePath => {
        const found = pagesJson.pages.find(p => p.path === pagePath);
        console.log(`${found ? '✅' : '❌'} ${pagePath}`);
    });
    
    // 检查tabBar配置
    if (pagesJson.tabBar) {
        console.log(`📱 tabBar配置: ${pagesJson.tabBar.list.length}个标签`);
        pagesJson.tabBar.list.forEach(tab => {
            console.log(`   - ${tab.pagePath}: ${tab.text}`);
        });
    }
    
} catch (error) {
    console.log(`❌ pages.json解析失败: ${error.message}`);
}

// 检查manifest.json配置
console.log('\n📱 检查manifest.json配置:');
try {
    const manifest = JSON.parse(fs.readFileSync('炒股养家/manifest.json', 'utf8'));
    
    console.log(`✅ manifest.json解析成功`);
    console.log(`📱 应用名称: ${manifest.name}`);
    console.log(`🔢 版本: ${manifest.versionName}`);
    console.log(`🎯 Vue版本: ${manifest.vueVersion}`);
    
    // 检查权限配置
    if (manifest['app-plus'] && manifest['app-plus'].distribute && manifest['app-plus'].distribute.android) {
        const permissions = manifest['app-plus'].distribute.android.permissions;
        const hasInternet = permissions.some(p => p.includes('INTERNET'));
        console.log(`🌐 INTERNET权限: ${hasInternet ? '✅' : '❌'}`);
    }
    
} catch (error) {
    console.log(`❌ manifest.json解析失败: ${error.message}`);
}

// 检查页面文件语法
console.log('\n🔍 检查页面文件语法:');
const pageFiles = [
    '炒股养家/pages/index/index.vue',
    '炒股养家/pages/ai-analysis/index.vue',
    '炒股养家/pages/ai-training/index.vue'
];

pageFiles.forEach(file => {
    try {
        const content = fs.readFileSync(file, 'utf8');
        
        // 基本语法检查
        const hasTemplate = content.includes('<template>');
        const hasScript = content.includes('<script>');
        const hasStyle = content.includes('<style>');
        
        console.log(`📄 ${file}:`);
        console.log(`   Template: ${hasTemplate ? '✅' : '❌'}`);
        console.log(`   Script: ${hasScript ? '✅' : '❌'}`);
        console.log(`   Style: ${hasStyle ? '✅' : '❌'}`);
        
        // 检查是否有明显的语法错误
        const lines = content.split('\n');
        let hasError = false;
        
        lines.forEach((line, index) => {
            // 检查常见的语法错误
            if (line.includes('{{') && !line.includes('}}')) {
                console.log(`   ⚠️  第${index + 1}行: 可能的模板语法错误`);
                hasError = true;
            }
            if (line.includes('v-for') && !line.includes(':key')) {
                console.log(`   ⚠️  第${index + 1}行: v-for缺少key属性`);
            }
        });
        
        if (!hasError) {
            console.log(`   ✅ 未发现明显语法错误`);
        }
        
    } catch (error) {
        console.log(`❌ ${file}: ${error.message}`);
    }
});

// 检查组件导入
console.log('\n🧩 检查组件导入:');
try {
    const indexContent = fs.readFileSync('炒股养家/pages/index/index.vue', 'utf8');
    const componentImports = indexContent.match(/import\s+\w+\s+from\s+['"][^'"]+['"]/g) || [];
    
    console.log(`📦 首页组件导入数量: ${componentImports.length}`);
    componentImports.forEach(imp => {
        console.log(`   - ${imp}`);
        
        // 检查组件文件是否存在
        const match = imp.match(/from\s+['"]([^'"]+)['"]/);
        if (match) {
            let componentPath = match[1];
            if (componentPath.startsWith('@/')) {
                componentPath = componentPath.replace('@/', '炒股养家/');
            }
            if (!componentPath.endsWith('.vue')) {
                componentPath += '.vue';
            }
            
            const exists = fs.existsSync(componentPath);
            console.log(`     ${exists ? '✅' : '❌'} ${componentPath}`);
        }
    });
    
} catch (error) {
    console.log(`❌ 组件导入检查失败: ${error.message}`);
}

// 检查环境配置
console.log('\n⚙️ 检查环境配置:');
try {
    const envContent = fs.readFileSync('炒股养家/env.js', 'utf8');
    
    if (envContent.includes('api.aigupiao.me')) {
        console.log('✅ API地址配置正确');
    } else {
        console.log('❌ API地址配置可能有问题');
    }
    
    if (envContent.includes('wss://api.aigupiao.me/ws')) {
        console.log('✅ WebSocket地址配置正确');
    } else {
        console.log('❌ WebSocket地址配置可能有问题');
    }
    
} catch (error) {
    console.log(`❌ 环境配置检查失败: ${error.message}`);
}

console.log('\n🎯 诊断建议:');
console.log('1. 确保所有关键文件存在且语法正确');
console.log('2. 检查pages.json中的页面路径配置');
console.log('3. 验证组件导入路径正确');
console.log('4. 确认manifest.json配置完整');
console.log('5. 重新编译项目清除缓存');

console.log('\n✨ 诊断完成！');
