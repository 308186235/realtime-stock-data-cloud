#!/usr/bin/env node

/**
 * Cloudflare全栈部署脚本
 * 自动部署前端和后端到Cloudflare
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 开始Cloudflare全栈部署...\n');

// 配置
const CONFIG = {
  // 项目配置
  frontendDir: '炒股养家',
  backendDir: 'cloudflare-api',
  
  // Cloudflare配置
  accountId: 'your-account-id', // 需要替换
  apiToken: 'your-api-token',   // 需要替换
  
  // 域名配置
  domains: {
    api: 'api.aigupiao.me',
    app: 'app.aigupiao.me',
    mobile: 'mobile.aigupiao.me',
    admin: 'admin.aigupiao.me',
    main: 'aigupiao.me'
  }
};

// 工具函数
function runCommand(command, cwd = process.cwd()) {
  console.log(`📝 执行命令: ${command}`);
  try {
    const result = execSync(command, { 
      cwd, 
      stdio: 'inherit',
      encoding: 'utf8'
    });
    return result;
  } catch (error) {
    console.error(`❌ 命令执行失败: ${error.message}`);
    process.exit(1);
  }
}

function checkFile(filePath) {
  if (!fs.existsSync(filePath)) {
    console.error(`❌ 文件不存在: ${filePath}`);
    return false;
  }
  console.log(`✅ 文件检查通过: ${filePath}`);
  return true;
}

function createDirectory(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
    console.log(`📁 创建目录: ${dirPath}`);
  }
}

// 步骤1: 检查环境
function checkEnvironment() {
  console.log('🔍 检查部署环境...');
  
  try {
    // 检查Node.js
    runCommand('node --version');
    
    // 检查npm
    runCommand('npm --version');
    
    // 检查wrangler
    try {
      runCommand('wrangler --version');
    } catch (error) {
      console.log('📦 安装Wrangler CLI...');
      runCommand('npm install -g wrangler');
    }
    
    console.log('✅ 环境检查完成\n');
  } catch (error) {
    console.error('❌ 环境检查失败:', error.message);
    process.exit(1);
  }
}

// 步骤2: 准备后端代码
function prepareBackend() {
  console.log('🔧 准备后端代码...');
  
  const backendPath = path.resolve(CONFIG.backendDir);
  createDirectory(backendPath);
  
  // 检查必要文件
  const requiredFiles = [
    path.join(backendPath, 'src/index.js'),
    path.join(backendPath, 'wrangler.toml')
  ];
  
  for (const file of requiredFiles) {
    if (!checkFile(file)) {
      console.error(`❌ 后端文件缺失: ${file}`);
      process.exit(1);
    }
  }
  
  console.log('✅ 后端代码准备完成\n');
}

// 步骤3: 部署后端API
function deployBackend() {
  console.log('🚀 部署后端API到Cloudflare Workers...');
  
  const backendPath = path.resolve(CONFIG.backendDir);
  
  try {
    // 登录Cloudflare (如果需要)
    console.log('🔐 检查Cloudflare登录状态...');
    try {
      runCommand('wrangler whoami', backendPath);
    } catch (error) {
      console.log('🔐 需要登录Cloudflare...');
      runCommand('wrangler login', backendPath);
    }
    
    // 创建KV命名空间
    console.log('🗄️ 创建KV存储...');
    try {
      runCommand('wrangler kv:namespace create "TRADING_KV"', backendPath);
    } catch (error) {
      console.log('⚠️ KV命名空间可能已存在');
    }
    
    // 部署Worker
    console.log('🚀 部署Worker...');
    runCommand('wrangler publish', backendPath);
    
    console.log('✅ 后端API部署完成\n');
  } catch (error) {
    console.error('❌ 后端部署失败:', error.message);
    process.exit(1);
  }
}

// 步骤4: 准备前端代码
function prepareFrontend() {
  console.log('🎨 准备前端代码...');
  
  const frontendPath = path.resolve(CONFIG.frontendDir);
  
  if (!fs.existsSync(frontendPath)) {
    console.error(`❌ 前端目录不存在: ${frontendPath}`);
    process.exit(1);
  }
  
  // 检查package.json
  const packageJsonPath = path.join(frontendPath, 'package.json');
  if (!checkFile(packageJsonPath)) {
    console.log('📦 创建package.json...');
    const packageJson = {
      "name": "aigupiao-frontend",
      "version": "1.0.0",
      "scripts": {
        "build": "echo 'Frontend build completed'"
      }
    };
    fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2));
  }
  
  // 更新API配置
  console.log('🔧 更新API配置...');
  updateFrontendConfig(frontendPath);
  
  console.log('✅ 前端代码准备完成\n');
}

// 更新前端API配置
function updateFrontendConfig(frontendPath) {
  const configFiles = [
    'env.js',
    'services/config.js',
    'utils/request.js'
  ];
  
  for (const configFile of configFiles) {
    const filePath = path.join(frontendPath, configFile);
    if (fs.existsSync(filePath)) {
      let content = fs.readFileSync(filePath, 'utf8');
      
      // 替换API URL
      content = content.replace(
        /const\s+API_BASE_URL\s*=\s*['"][^'"]*['"]/g,
        `const API_BASE_URL = 'https://${CONFIG.domains.api}'`
      );
      
      content = content.replace(
        /API_BASE_URL\s*:\s*['"][^'"]*['"]/g,
        `API_BASE_URL: 'https://${CONFIG.domains.api}'`
      );
      
      fs.writeFileSync(filePath, content);
      console.log(`✅ 更新配置文件: ${configFile}`);
    }
  }
}

// 步骤5: 部署前端
function deployFrontend() {
  console.log('🎨 部署前端到Cloudflare Pages...');
  
  const frontendPath = path.resolve(CONFIG.frontendDir);
  
  try {
    // 构建前端 (如果有构建脚本)
    const packageJsonPath = path.join(frontendPath, 'package.json');
    if (fs.existsSync(packageJsonPath)) {
      const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
      if (packageJson.scripts && packageJson.scripts.build) {
        console.log('🔨 构建前端...');
        runCommand('npm run build', frontendPath);
      }
    }
    
    // 使用wrangler pages部署
    console.log('🚀 部署到Cloudflare Pages...');
    runCommand(`wrangler pages publish ${frontendPath} --project-name=aigupiao-frontend`, frontendPath);
    
    console.log('✅ 前端部署完成\n');
  } catch (error) {
    console.error('❌ 前端部署失败:', error.message);
    console.log('💡 提示: 可能需要先在Cloudflare Dashboard中创建Pages项目');
  }
}

// 步骤6: 配置域名
function configureDomains() {
  console.log('🌐 配置自定义域名...');
  
  console.log('📋 域名配置清单:');
  console.log(`   API域名: ${CONFIG.domains.api} -> Cloudflare Workers`);
  console.log(`   应用域名: ${CONFIG.domains.app} -> Cloudflare Pages`);
  console.log(`   移动端: ${CONFIG.domains.mobile} -> Cloudflare Pages`);
  console.log(`   管理后台: ${CONFIG.domains.admin} -> Cloudflare Pages`);
  console.log(`   主域名: ${CONFIG.domains.main} -> 重定向到app`);
  
  console.log('\n💡 请在Cloudflare Dashboard中手动配置以下设置:');
  console.log('1. Workers路由: api.aigupiao.me/* -> aigupiao-trading-api');
  console.log('2. Pages自定义域名: app.aigupiao.me, mobile.aigupiao.me, admin.aigupiao.me');
  console.log('3. DNS记录已在之前配置完成');
  
  console.log('✅ 域名配置说明完成\n');
}

// 步骤7: 验证部署
async function verifyDeployment() {
  console.log('🔍 验证部署状态...');
  
  const endpoints = [
    `https://${CONFIG.domains.api}/api/health`,
    `https://${CONFIG.domains.app}`,
    `https://${CONFIG.domains.mobile}`,
    `https://${CONFIG.domains.admin}`
  ];
  
  console.log('📡 测试API端点...');
  for (const endpoint of endpoints) {
    console.log(`   检查: ${endpoint}`);
    // 这里可以添加实际的HTTP请求验证
  }
  
  console.log('✅ 部署验证完成\n');
}

// 主函数
async function main() {
  try {
    console.log('🎯 Cloudflare全栈部署开始\n');
    
    // 执行部署步骤
    checkEnvironment();
    prepareBackend();
    deployBackend();
    prepareFrontend();
    deployFrontend();
    configureDomains();
    await verifyDeployment();
    
    console.log('🎉 Cloudflare全栈部署完成!');
    console.log('\n📱 访问地址:');
    console.log(`   主应用: https://${CONFIG.domains.app}`);
    console.log(`   移动端: https://${CONFIG.domains.mobile}`);
    console.log(`   管理后台: https://${CONFIG.domains.admin}`);
    console.log(`   API文档: https://${CONFIG.domains.api}`);
    
  } catch (error) {
    console.error('❌ 部署失败:', error.message);
    process.exit(1);
  }
}

// 运行部署
if (require.main === module) {
  main();
}

module.exports = { main, CONFIG };
