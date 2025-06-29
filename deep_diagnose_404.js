/**
 * 深度诊断uni-app 404问题
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 深度诊断uni-app 404问题...\n');

// 检查uni-app项目结构
console.log('📁 检查uni-app项目结构:');
const requiredDirs = [
    '炒股养家/pages',
    '炒股养家/components',
    '炒股养家/static',
    '炒股养家/services'
];

requiredDirs.forEach(dir => {
    const exists = fs.existsSync(dir);
    console.log(`${exists ? '✅' : '❌'} ${dir}`);
});

// 检查关键配置文件
console.log('\n📋 检查关键配置文件:');
const configFiles = [
    '炒股养家/pages.json',
    '炒股养家/manifest.json', 
    '炒股养家/main.js',
    '炒股养家/App.vue',
    '炒股养家/uni.scss'
];

configFiles.forEach(file => {
    const exists = fs.existsSync(file);
    console.log(`${exists ? '✅' : '❌'} ${file}`);
    
    if (exists) {
        try {
            const content = fs.readFileSync(file, 'utf8');
            const size = content.length;
            console.log(`   📏 文件大小: ${size} 字符`);
            
            // 检查BOM
            if (content.charCodeAt(0) === 0xFEFF) {
                console.log(`   ⚠️  检测到BOM字符`);
            }
        } catch (error) {
            console.log(`   ❌ 读取失败: ${error.message}`);
        }
    }
});

// 深度检查pages.json
console.log('\n📄 深度检查pages.json:');
try {
    const pagesContent = fs.readFileSync('炒股养家/pages.json', 'utf8');
    const pagesJson = JSON.parse(pagesContent);
    
    console.log(`✅ pages.json解析成功`);
    console.log(`📄 总页面数: ${pagesJson.pages.length}`);
    
    // 检查每个页面文件是否存在
    console.log('\n📋 检查页面文件存在性:');
    pagesJson.pages.forEach((page, index) => {
        const pagePath = `炒股养家/${page.path}.vue`;
        const exists = fs.existsSync(pagePath);
        console.log(`${exists ? '✅' : '❌'} [${index}] ${page.path} -> ${pagePath}`);
        
        if (!exists) {
            console.log(`   ⚠️  页面文件不存在: ${pagePath}`);
        }
    });
    
    // 检查首页配置
    const firstPage = pagesJson.pages[0];
    console.log(`\n🏠 首页配置: ${firstPage.path}`);
    
    // 检查tabBar配置
    if (pagesJson.tabBar) {
        console.log(`\n📱 tabBar配置:`);
        console.log(`   标签数量: ${pagesJson.tabBar.list.length}`);
        pagesJson.tabBar.list.forEach((tab, index) => {
            const tabPageExists = pagesJson.pages.find(p => p.path === tab.pagePath);
            console.log(`   [${index}] ${tab.pagePath} -> ${tab.text} ${tabPageExists ? '✅' : '❌'}`);
        });
    }
    
    // 检查globalStyle
    if (pagesJson.globalStyle) {
        console.log(`\n🎨 globalStyle配置:`);
        console.log(`   导航栏标题: ${pagesJson.globalStyle.navigationBarTitleText || '未设置'}`);
        console.log(`   导航栏背景: ${pagesJson.globalStyle.navigationBarBackgroundColor || '未设置'}`);
    }
    
} catch (error) {
    console.log(`❌ pages.json检查失败: ${error.message}`);
}

// 深度检查manifest.json
console.log('\n📱 深度检查manifest.json:');
try {
    const manifestContent = fs.readFileSync('炒股养家/manifest.json', 'utf8');
    const manifest = JSON.parse(manifestContent);
    
    console.log(`✅ manifest.json解析成功`);
    console.log(`📱 应用名称: ${manifest.name}`);
    console.log(`🔢 版本: ${manifest.versionName}`);
    console.log(`🎯 Vue版本: ${manifest.vueVersion}`);
    console.log(`🆔 AppID: ${manifest.appid}`);
    
    // 检查平台配置
    const platforms = ['app-plus', 'h5', 'mp-weixin', 'mp-alipay'];
    platforms.forEach(platform => {
        if (manifest[platform]) {
            console.log(`✅ ${platform}配置存在`);
        } else {
            console.log(`❌ ${platform}配置缺失`);
        }
    });
    
    // 检查easycom配置
    if (manifest.easycom) {
        console.log(`✅ easycom配置存在`);
        console.log(`   自动扫描: ${manifest.easycom.autoscan}`);
    } else {
        console.log(`❌ easycom配置缺失`);
    }
    
} catch (error) {
    console.log(`❌ manifest.json检查失败: ${error.message}`);
}

// 检查main.js
console.log('\n🚀 检查main.js:');
try {
    const mainContent = fs.readFileSync('炒股养家/main.js', 'utf8');
    
    console.log(`✅ main.js读取成功`);
    
    // 检查Vue版本配置
    if (mainContent.includes('createSSRApp')) {
        console.log(`✅ Vue3配置正确`);
    } else if (mainContent.includes('new Vue')) {
        console.log(`⚠️  Vue2配置`);
    } else {
        console.log(`❌ Vue配置异常`);
    }
    
    // 检查App导入
    if (mainContent.includes("import App from './App.vue'") || mainContent.includes("import App from './App'")) {
        console.log(`✅ App组件导入正确`);
    } else {
        console.log(`❌ App组件导入异常`);
    }
    
    // 检查createApp函数
    if (mainContent.includes('export function createApp')) {
        console.log(`✅ createApp函数存在`);
    } else {
        console.log(`❌ createApp函数缺失`);
    }
    
} catch (error) {
    console.log(`❌ main.js检查失败: ${error.message}`);
}

// 检查App.vue
console.log('\n📱 检查App.vue:');
try {
    const appContent = fs.readFileSync('炒股养家/App.vue', 'utf8');
    
    console.log(`✅ App.vue读取成功`);
    
    // 检查基本结构
    const hasScript = appContent.includes('<script>');
    const hasStyle = appContent.includes('<style>');
    
    console.log(`   Script标签: ${hasScript ? '✅' : '❌'}`);
    console.log(`   Style标签: ${hasStyle ? '✅' : '❌'}`);
    
    // 检查生命周期
    if (appContent.includes('onLaunch')) {
        console.log(`✅ onLaunch生命周期存在`);
    } else {
        console.log(`❌ onLaunch生命周期缺失`);
    }
    
    // 检查globalData
    if (appContent.includes('globalData')) {
        console.log(`✅ globalData配置存在`);
    } else {
        console.log(`❌ globalData配置缺失`);
    }
    
} catch (error) {
    console.log(`❌ App.vue检查失败: ${error.message}`);
}

// 检查首页文件
console.log('\n🏠 检查首页文件:');
try {
    const indexContent = fs.readFileSync('炒股养家/pages/index/index.vue', 'utf8');
    
    console.log(`✅ 首页文件读取成功`);
    
    // 检查Vue组件结构
    const hasTemplate = indexContent.includes('<template>');
    const hasScript = indexContent.includes('<script>');
    const hasStyle = indexContent.includes('<style>');
    
    console.log(`   Template: ${hasTemplate ? '✅' : '❌'}`);
    console.log(`   Script: ${hasScript ? '✅' : '❌'}`);
    console.log(`   Style: ${hasStyle ? '✅' : '❌'}`);
    
    // 检查export default
    if (indexContent.includes('export default')) {
        console.log(`✅ export default存在`);
    } else {
        console.log(`❌ export default缺失`);
    }
    
    // 检查data函数
    if (indexContent.includes('data()') || indexContent.includes('data:')) {
        console.log(`✅ data函数存在`);
    } else {
        console.log(`❌ data函数缺失`);
    }
    
} catch (error) {
    console.log(`❌ 首页文件检查失败: ${error.message}`);
}

console.log('\n🎯 深度诊断建议:');
console.log('1. 检查所有页面文件是否存在且路径正确');
console.log('2. 验证pages.json中的页面配置与实际文件匹配');
console.log('3. 确认manifest.json配置完整且无语法错误');
console.log('4. 检查main.js的Vue版本配置');
console.log('5. 验证App.vue的生命周期配置');
console.log('6. 清理项目缓存并重新编译');

console.log('\n✨ 深度诊断完成！');
