/**
 * 真机运行问题诊断脚本
 */

const fs = require('fs');
const path = require('path');

console.log('📱 诊断真机运行问题...\n');

// 检查manifest.json配置
console.log('📋 检查manifest.json配置:');
try {
    const manifest = JSON.parse(fs.readFileSync('炒股养家/manifest.json', 'utf8'));
    
    console.log(`✅ manifest.json解析成功`);
    console.log(`📱 应用名称: ${manifest.name}`);
    console.log(`🆔 AppID: ${manifest.appid}`);
    console.log(`🔢 版本: ${manifest.versionName} (${manifest.versionCode})`);
    console.log(`🎯 Vue版本: ${manifest.vueVersion}`);
    
    // 检查app-plus配置
    if (manifest['app-plus']) {
        console.log(`✅ app-plus配置存在`);
        console.log(`   编译器版本: ${manifest['app-plus'].compilerVersion}`);
        console.log(`   使用组件: ${manifest['app-plus'].usingComponents}`);
        
        // 检查Android配置
        if (manifest['app-plus'].distribute && manifest['app-plus'].distribute.android) {
            const android = manifest['app-plus'].distribute.android;
            console.log(`✅ Android配置存在`);
            console.log(`   权限数量: ${android.permissions ? android.permissions.length : 0}`);
            
            // 检查关键权限
            const permissions = android.permissions || [];
            const hasInternet = permissions.some(p => p.includes('INTERNET'));
            const hasNetworkState = permissions.some(p => p.includes('ACCESS_NETWORK_STATE'));
            
            console.log(`   INTERNET权限: ${hasInternet ? '✅' : '❌'}`);
            console.log(`   网络状态权限: ${hasNetworkState ? '✅' : '❌'}`);
            
            // 检查图标配置
            if (android.icons) {
                console.log(`✅ Android图标配置存在`);
                const iconSizes = Object.keys(android.icons);
                console.log(`   图标尺寸: ${iconSizes.join(', ')}`);
                
                // 检查图标文件是否存在
                iconSizes.forEach(size => {
                    const iconPath = `炒股养家/${android.icons[size]}`;
                    const exists = fs.existsSync(iconPath);
                    console.log(`   ${size}: ${exists ? '✅' : '❌'} ${iconPath}`);
                });
            } else {
                console.log(`❌ Android图标配置缺失`);
            }
        } else {
            console.log(`❌ Android配置缺失`);
        }
        
        // 检查iOS配置
        if (manifest['app-plus'].distribute && manifest['app-plus'].distribute.ios) {
            console.log(`✅ iOS配置存在`);
        } else {
            console.log(`❌ iOS配置缺失`);
        }
        
    } else {
        console.log(`❌ app-plus配置缺失`);
    }
    
} catch (error) {
    console.log(`❌ manifest.json检查失败: ${error.message}`);
}

// 检查必要的静态资源
console.log('\n📁 检查静态资源:');
const staticFiles = [
    'static/app-logo.png',
    'static/logo.png'
];

staticFiles.forEach(file => {
    const fullPath = `炒股养家/${file}`;
    const exists = fs.existsSync(fullPath);
    console.log(`${exists ? '✅' : '❌'} ${file}`);
    
    if (exists) {
        try {
            const stats = fs.statSync(fullPath);
            console.log(`   文件大小: ${(stats.size / 1024).toFixed(2)} KB`);
        } catch (error) {
            console.log(`   ⚠️  无法读取文件信息: ${error.message}`);
        }
    }
});

// 检查编译输出目录
console.log('\n📦 检查编译输出:');
const unpackagePath = '炒股养家/unpackage';
if (fs.existsSync(unpackagePath)) {
    console.log(`✅ unpackage目录存在`);
    
    const distPath = path.join(unpackagePath, 'dist');
    if (fs.existsSync(distPath)) {
        console.log(`✅ dist目录存在`);
        
        // 检查不同平台的编译输出
        const platforms = ['dev', 'build'];
        platforms.forEach(platform => {
            const platformPath = path.join(distPath, platform);
            if (fs.existsSync(platformPath)) {
                console.log(`✅ ${platform}目录存在`);
                
                const appPlusPath = path.join(platformPath, 'app-plus');
                if (fs.existsSync(appPlusPath)) {
                    console.log(`✅ app-plus编译输出存在`);
                } else {
                    console.log(`❌ app-plus编译输出缺失`);
                }
            } else {
                console.log(`❌ ${platform}目录不存在`);
            }
        });
    } else {
        console.log(`❌ dist目录不存在`);
    }
} else {
    console.log(`❌ unpackage目录不存在`);
}

// 检查HBuilderX相关配置
console.log('\n🛠️ 检查HBuilderX配置:');
const hxConfigFiles = [
    '.hbuilderx/launch.json',
    'unpackage/.hbuilderx'
];

hxConfigFiles.forEach(file => {
    const fullPath = `炒股养家/${file}`;
    const exists = fs.existsSync(fullPath);
    console.log(`${exists ? '✅' : '❌'} ${file}`);
});

// 常见真机运行问题检查
console.log('\n🔍 常见问题检查:');

// 1. 检查AppID是否为默认值
const manifest = JSON.parse(fs.readFileSync('炒股养家/manifest.json', 'utf8'));
if (manifest.appid === '__UNI__55E0502') {
    console.log(`⚠️  使用默认AppID，建议申请正式AppID`);
} else {
    console.log(`✅ 使用自定义AppID`);
}

// 2. 检查版本号格式
const versionCode = parseInt(manifest.versionCode);
if (isNaN(versionCode) || versionCode < 1) {
    console.log(`❌ 版本号格式错误: ${manifest.versionCode}`);
} else {
    console.log(`✅ 版本号格式正确: ${manifest.versionCode}`);
}

// 3. 检查应用名称
if (!manifest.name || manifest.name.trim() === '') {
    console.log(`❌ 应用名称为空`);
} else {
    console.log(`✅ 应用名称: ${manifest.name}`);
}

console.log('\n🎯 真机运行建议:');
console.log('1. 确保手机已开启开发者模式和USB调试');
console.log('2. 检查手机与电脑的连接状态');
console.log('3. 确认HBuilderX已识别到手机设备');
console.log('4. 尝试重新编译项目');
console.log('5. 检查手机是否信任该应用');
console.log('6. 如果是iOS设备，需要配置证书和描述文件');

console.log('\n✨ 诊断完成！');
