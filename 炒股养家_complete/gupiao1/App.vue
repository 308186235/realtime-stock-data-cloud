<script>
    import authService from './services/auth-service.js';
    
    export default {
        globalData: {
            isDarkMode: false, // 默认为浅色模式
            theme: 'light', // 默认为浅色模式(字符串形式,兼容旧代码)
            isAuthenticated: false, // 用户认证状态
            biometricSupport: null // 生物识别支持状态
        },
        onLaunch: function() {
            console.log('App Launch')
            
            // 获取存储的主题设置,确保一致性
            try {
                const savedTheme = uni.getStorageSync('app_theme');
                if (savedTheme) {
                    if (typeof savedTheme === 'boolean') {
                        this.globalData.isDarkMode = savedTheme;
                        this.globalData.theme = savedTheme ? 'dark' : 'light';
                    } else if (typeof savedTheme === 'string') {
                        this.globalData.theme = savedTheme;
                        this.globalData.isDarkMode = savedTheme === 'dark';
                    }
                }
            } catch (e) {
                console.error('读取主题设置失败', e);
            }
            
            this.applyTheme()
            this.initSecurityServices()
        },
        onShow: function() {
            console.log('App Show')
            // 检查应用锁定状态
            this.checkAppLockStatus()
        },
        onHide: function() {
            console.log('App Hide')
            // 应用进入后台时考虑锁定
            this.handleAppBackground()
        },
        // #ifdef APP-ANDROID
        onLastPageBackPress: function() {
            console.log('App LastPageBackPress')
            // 应用退出前锁定
            this.lockAppBeforeExit()
        },
        // #endif
        onExit: function() {
            console.log('App Exit')
            // 应用退出时锁定
            this.lockAppBeforeExit()
        },
        methods: {
            applyTheme() {
                const isDark = this.globalData.isDarkMode
                // 更新 theme 字符串,确保与 isDarkMode 保持同步
                this.globalData.theme = isDark ? 'dark' : 'light'
                
                // 保存主题设置到本地存储
                try {
                    uni.setStorageSync('app_theme', isDark);
                } catch (e) {
                    console.error('保存主题设置失败', e);
                }
                
                // 设置底部Tab样式
                uni.setTabBarStyle({
                    color: '#999',
                    selectedColor: '#4c8dff',
                    backgroundColor: isDark ? '#222' : '#ffffff',
                    borderStyle: isDark ? 'black' : 'white'
                })
                // 更新系统状态栏
                uni.setNavigationBarColor({
                    frontColor: isDark ? '#ffffff' : '#000000',
                    backgroundColor: isDark ? '#141414' : '#f5f5f5'
                })
            },
            toggleTheme(isDark) {
                this.globalData.isDarkMode = isDark
                this.applyTheme()
                
                // 发布主题变化事件,所有页面都能监听到
                uni.$emit('theme-changed')
            },
            
            // 初始化安全服务
            async initSecurityServices() {
                try {
                    // 初始化安全服务
                    const securityInfo = await authService.initSecurityService();
                    this.globalData.biometricSupport = securityInfo.biometricSupport;
                    
                    // 检查是否需要锁定
                    this.checkAppLockStatus();
                } catch (error) {
                    console.error('初始化安全服务失败', error);
                }
            },
            
            // 检查应用锁定状态
            checkAppLockStatus() {
                if (authService.isAppLocked()) {
                    // 如果应用被锁定,跳转到锁定屏幕
                    const currentPage = getCurrentPages();
                    const currentRoute = currentPage[currentPage.length - 1]?.route || '';
                    
                    // 如果当前不在锁屏页面,则跳转到锁屏
                    if (currentRoute !== 'pages/lock-screen') {
                        uni.reLaunch({
                            url: '/pages/lock-screen'
                        });
                    }
                }
            },
            
            // 处理应用进入后台
            handleAppBackground() {
                // 获取安全设置
                const settings = authService.getSecuritySettings();
                
                // 如果启用了任何安全措施,应用进入后台时锁定
                if (settings.usePINCode || settings.useFingerprint || settings.useFacialRecognition) {
                    authService.lockApp();
                }
            },
            
            // 退出应用前锁定
            lockAppBeforeExit() {
                // 获取安全设置
                const settings = authService.getSecuritySettings();
                
                // 如果启用了任何安全措施,则在退出前强制锁定
                if (settings.usePINCode || settings.useFingerprint || settings.useFacialRecognition) {
                    console.log('应用退出,强制锁定');
                    authService.lockApp();
                    
                    // 存储锁定状态,确保下次打开时应用处于锁定状态
                    try {
                        uni.setStorageSync('forceAppLock', 'true');
                    } catch (e) {
                        console.error('存储强制锁定状态失败', e);
                    }
                }
            }
        }
    }
</script>

<style>
    /*每个页面公共css */
    /* 浅色主题样式 */
    page {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    }
    
    /* 浅色主题 */
    .light-theme {
        background-color: #f5f5f5 !important;
        color: #333333 !important;
    }
    
    .light-theme .container {
        padding: 15px;
        background-color: #f5f5f5 !important;
        color: #333333 !important;
    }
    
    .light-theme .section {
        margin-bottom: 20px;
        background-color: #ffffff !important;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    }
    
    .light-theme .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        border-bottom: 1px solid #eeeeee !important;
        padding-bottom: 10px;
    }
    
    .light-theme .section-title {
        font-size: 18px;
        font-weight: bold;
        color: #333333 !important;
    }
    
    .light-theme .refresh-button, .light-theme .setup-button {
        font-size: 14px;
        color: #4c8dff !important;
        padding: 5px 10px;
        background-color: #f0f0f0 !important;
        border-radius: 15px;
    }
    
    /* 深色主题 */
    .dark-theme {
        background-color: #141414 !important;
        color: #e0e0e0 !important;
    }
    
    .dark-theme .container {
        padding: 15px;
        background-color: #141414 !important;
        color: #e0e0e0 !important;
    }
    
    .dark-theme .section {
        margin-bottom: 20px;
        background-color: #1e1e1e !important;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
    }
    
    .dark-theme .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        border-bottom: 1px solid #333 !important;
        padding-bottom: 10px;
    }
    
    .dark-theme .section-title {
        font-size: 18px;
        font-weight: bold;
        color: #fff !important;
    }
    
    .dark-theme .refresh-button, .dark-theme .setup-button {
        font-size: 14px;
        color: #4c8dff !important;
        padding: 5px 10px;
        background-color: #2a2a2a !important;
        border-radius: 15px;
    }
    
    /* 涨跌颜色 - 所有主题通用 */
    .up {
        color: #ff4d4f !important;
    }
    
    .down {
        color: #52c41a !important;
    }
</style>
