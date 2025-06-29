<template>
  <view :class="['container', isDarkMode ? 'dark-theme' : 'light-theme']">
    <view class="header">
      <text class="title">系统设置</text>
    </view>
    
    <view class="settings-section">
      <view class="section-title">
        <text class="title-text">安全设置</text>
      </view>
      
      <view class="setting-group">
        <view class="setting-item" @click="navigateTo('/pages/settings/security')">
          <view class="tap-capture" @click.stop="navigateTo('/pages/settings/security')"></view>
          <text class="setting-label">安全设置</text>
          <view class="setting-value security-value">
            <text class="value-text">密码/生物识别</text>
            <view class="arrow-right"></view>
          </view>
        </view>
        
        <view class="setting-item" @click="navigateTo('/pages/settings/device-transfer-guide')">
          <view class="tap-capture" @click.stop="navigateTo('/pages/settings/device-transfer-guide')"></view>
          <text class="setting-label">换手机/设备</text>
          <view class="setting-value">
            <text class="value-text">数据迁移</text>
            <view class="arrow-right"></view>
          </view>
        </view>
      </view>
    </view>
    
    <view class="settings-section">
      <view class="section-title">
        <text class="title-text">交易设置</text>
      </view>
      
      <view class="setting-group">
        <view class="setting-item" @click="navigateTo('/pages/trade-settings/index')">
          <text class="setting-label">交易参数</text>
          <view class="setting-value">
            <view class="arrow-right"></view>
          </view>
        </view>
        
        <view class="setting-item">
          <text class="setting-label">风险控制</text>
          <view class="setting-value">
            <switch :checked="riskControl" @change="toggleRiskControl" color="#4c8dff" />
          </view>
        </view>
        
        <view class="setting-item">
          <text class="setting-label">提醒设置</text>
          <view class="setting-value">
            <view class="arrow-right"></view>
          </view>
        </view>
      </view>
    </view>
    
    <view class="settings-section">
      <view class="section-title">
        <text class="title-text">系统设置</text>
      </view>
      
      <view class="setting-group">
        <view class="setting-item dark-mode-item" @click="manualToggleDarkMode">
          <text class="setting-label">暗黑模式</text>
          <view class="setting-value" @click.stop>
            <switch :checked="isDarkMode" @change="toggleDarkMode" color="#4c8dff" />
          </view>
        </view>
        
        <view class="setting-item" @click="showLanguageOptions">
          <text class="setting-label">语言设置</text>
          <view class="setting-value language-value">
            <text class="value-text">简体中文</text>
            <view class="arrow-right"></view>
          </view>
        </view>
        
        <view class="setting-item" @click="navigateTo('/pages/settings/notification')">
          <text class="setting-label">通知设置</text>
          <view class="setting-value">
            <view class="arrow-right"></view>
          </view>
        </view>

        <view class="setting-item" @click="navigateTo('/pages/settings/network')">
          <text class="setting-label">网络设置</text>
          <view class="setting-value">
            <text class="value-text">后端连接配置</text>
            <view class="arrow-right"></view>
          </view>
        </view>
        
        <view class="setting-item" @click="checkForUpdate">
          <text class="setting-label">版本信息</text>
          <view class="setting-value">
            <text class="value-text">V1.0.0</text>
            <view class="arrow-right"></view>
          </view>
        </view>
      </view>
    </view>
    
    <view class="settings-section">
      <view class="setting-group">
        <view class="setting-item" @click="navigateTo('/pages/settings/feedback')">
          <text class="setting-label">意见反馈</text>
          <view class="setting-value">
            <view class="arrow-right"></view>
          </view>
        </view>
        
        <view class="setting-item" @click="navigateTo('/pages/settings/about')">
          <text class="setting-label">关于我们</text>
          <view class="setting-value">
            <view class="arrow-right"></view>
          </view>
        </view>

        <view class="setting-item" @click="goToNetworkTest">
          <text class="setting-label">网络连接测试</text>
          <view class="setting-value">
            <view class="arrow-right"></view>
          </view>
        </view>

        <view class="setting-item" @click="goToConnectionTest">
          <text class="setting-label">后端连接测试</text>
          <view class="setting-value">
            <text class="value-text">连接状态检测</text>
            <view class="arrow-right"></view>
          </view>
        </view>

        <view class="setting-item" @click="goToConnectionTest">
          <text class="setting-label">后端连接测试</text>
          <view class="setting-value">
            <text class="value-text">连接状态检测</text>
            <view class="arrow-right"></view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      isDarkMode: false,
      riskControl: true,
      language: '简体中文',
      lastBackupTime: null
    }
  },
  onLoad() {
    // 获取当前主题设置
    const app = getApp();
    this.isDarkMode = app.globalData.isDarkMode;
    
    // 获取最后备份时间
    try {
      this.lastBackupTime = uni.getStorageSync('lastBackupTime') || null;
    } catch (e) {
      console.error('获取备份时间失败', e);
    }
    
    // 监听设备迁移选项事件
    uni.$on('showDeviceTransferOptions', this.showDeviceTransferOptions);
  },
  onUnload() {
    // 移除事件监听
    uni.$off('showDeviceTransferOptions', this.showDeviceTransferOptions);
  },
  methods: {
    navigateTo(url) {
      // Show loading indicator
      uni.showLoading({
        title: '跳转中...',
        mask: true
      });
      
      // Navigate to the target page
      uni.navigateTo({
        url: url,
        success: () => {
          console.log('导航成功:', url);
        },
        fail: (err) => {
          console.error('导航失败:', url, err);
          // If navigation fails, try again with redirectTo
          uni.redirectTo({
            url: url,
            fail: (redirectErr) => {
              // Show error message if both methods fail
              uni.showToast({
                title: '页面跳转失败',
                icon: 'none'
              });
              console.error('重定向失败:', url, redirectErr);
            }
          });
        },
        complete: () => {
          // Hide loading indicator
          uni.hideLoading();
        }
      });
    },
    toggleDarkMode(e) {
      this.isDarkMode = e.detail.value;
      
      // 更新全局主题设置
      const app = getApp();
      app.toggleTheme(this.isDarkMode);
      
      // 兼容旧版本使用 theme 字符串的情况
      if (app.globalData) {
        app.globalData.theme = this.isDarkMode ? 'dark' : 'light';
      }
      
      uni.showToast({
        title: this.isDarkMode ? '已切换到暗黑模式' : '已切换到浅色模式',
        icon: 'none'
      });
    },
    toggleRiskControl(e) {
      this.riskControl = e.detail.value;
      uni.showToast({
        title: this.riskControl ? '已开启风险控制' : '已关闭风险控制',
        icon: 'none'
      });
    },
    showLanguageOptions() {
      uni.showActionSheet({
        itemList: ['简体中文', 'English', '繁體中文'],
        success: (res) => {
          const languages = ['简体中文', 'English', '繁體中文'];
          this.language = languages[res.tapIndex];
          uni.showToast({
            title: '语言设置已更新',
            icon: 'none'
          });
        }
      });
    },
    checkForUpdate() {
      uni.showLoading({
        title: '检查更新中'
      });
      
      setTimeout(() => {
        uni.hideLoading();
        uni.showModal({
          title: '版本信息',
          content: '当前已是最新版本 V1.0.0',
          showCancel: false
        });
      }, 1000);
    },
    showDeviceTransferOptions() {
      uni.showActionSheet({
        itemList: ['生成迁移码', '云端备份', '从云端恢复', '扫码迁移'],
        success: (res) => {
          switch(res.tapIndex) {
            case 0: // 生成迁移码
              this.generateTransferCode();
              break;
            case 1: // 云端备份
              this.backupToCloud();
              break;
            case 2: // 从云端恢复
              this.restoreFromCloud();
              break;
            case 3: // 扫码迁移
              this.scanTransferCode();
              break;
          }
        }
      });
    },
    
    // 生成迁移码
    generateTransferCode() {
      uni.showLoading({
        title: '准备数据'
      });
      
      // 收集需要迁移的数据项
      const dataItems = this.collectBackupData();
      
      // 模拟数据打包过程
      setTimeout(() => {
        uni.hideLoading();
        
        // 显示数据打包进度
        this.showPackagingProgress(dataItems, () => {
          // 生成迁移码和二维码
          const transferCode = this.generateUniqueTransferCode();
          const transferData = {
            code: transferCode,
            timestamp: new Date().getTime(),
            expiry: new Date().getTime() + (24 * 60 * 60 * 1000), // 24小时后过期
            deviceInfo: this.getDeviceInfo()
          };
          
          // 在实际应用中,这里应该将transferCode与打包的数据关联并上传到服务器
          uni.setStorageSync('lastTransferCode', JSON.stringify(transferData));
          
          // 显示迁移码弹窗
          uni.showModal({
            title: '迁移码已生成',
            content: `您的迁移码为: ${transferCode}\n此码有效期为24小时,请勿分享给他人\n\n在新设备上输入此码即可完成迁移,所有数据和设置将与本设备保持完全一致。`,
            confirmText: '复制',
            cancelText: '显示二维码',
            success: (res) => {
              if (res.confirm) {
                uni.setClipboardData({
                  data: transferCode,
                  success: () => {
                    uni.showToast({
                      title: '迁移码已复制',
                      icon: 'success'
                    });
                  }
                });
              } else {
                // 显示二维码
                this.showTransferQRCode(transferCode);
              }
            }
          });
        });
      }, 500);
    },
    
    // 显示数据打包进度
    showPackagingProgress(dataItems, completeCallback) {
      let currentIndex = 0;
      const totalItems = dataItems.length;
      
      const processNextItem = () => {
        if (currentIndex >= totalItems) {
          completeCallback();
          return;
        }
        
        const item = dataItems[currentIndex];
        uni.showLoading({
          title: `打包中(${currentIndex+1}/${totalItems}): ${item.name}`
        });
        
        // 模拟单个项目的打包时间
        setTimeout(() => {
          currentIndex++;
          if (currentIndex < totalItems) {
            processNextItem();
          } else {
            uni.hideLoading();
            completeCallback();
          }
        }, 200); // 每个项目打包时间
      };
      
      processNextItem();
    },
    
    // 生成唯一的迁移码
    generateUniqueTransferCode() {
      const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; // 去掉容易混淆的字符
      let code = 'TC-';
      
      // 生成4组4位字符
      for (let group = 0; group < 4; group++) {
        for (let i = 0; i < 4; i++) {
          code += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        if (group < 3) code += '-';
      }
      
      return code;
    },
    
    // 获取设备信息
    getDeviceInfo() {
      const info = {};
      // 在实际应用中,这里应该获取真实的设备信息
      try {
        const systemInfo = uni.getSystemInfoSync();
        info.platform = systemInfo.platform;
        info.brand = systemInfo.brand;
        info.model = systemInfo.model;
        info.system = systemInfo.system;
        info.deviceId = 'device_' + new Date().getTime();
      } catch (e) {
        console.error('获取设备信息失败', e);
      }
      return info;
    },
    
    // 显示转移二维码
    showTransferQRCode(code) {
      // 在实际应用中,这里应该生成包含迁移码的二维码
      // 此处仅模拟该功能
      uni.showLoading({
        title: '生成二维码'
      });
      
      setTimeout(() => {
        uni.hideLoading();
        uni.showModal({
          title: '扫描二维码',
          content: '请使用新设备扫描此二维码完成迁移\n\n二维码中包含: ' + code,
          showCancel: false
        });
      }, 1000);
    },
    
    // 云端备份
    backupToCloud() {
      uni.showLoading({
        title: '准备备份'
      });
      
      // 收集需要备份的数据项
      const backupData = this.collectBackupData();
      
      // 模拟备份过程 - 实际应用中应该调用API上传到云端
      setTimeout(() => {
        uni.hideLoading();
        
        // 显示备份进度
        this.showBackupProgress(backupData, () => {
          uni.showModal({
            title: '备份完成',
            content: '您的交易数据和设置已成功备份到云端\n最后备份时间:' + new Date().toLocaleString(),
            showCancel: false,
            success: () => {
              uni.setStorageSync('lastBackupTime', new Date().toISOString());
              // 在实际应用中,这里应该保存备份ID或其他标识
              uni.setStorageSync('backupDataComplete', JSON.stringify(true));
            }
          });
        });
      }, 500);
    },
    
    // 收集需要备份的数据
    collectBackupData() {
      return [
        { name: '交易记录', key: 'trade_history', size: '3.5MB' },
        { name: '自选股列表', key: 'stock_watchlist', size: '0.5MB' },
        { name: '交易策略设置', key: 'trading_strategies', size: '1.8MB' },
        { name: '图表偏好设置', key: 'chart_preferences', size: '0.7MB' },
        { name: 'AI模型参数', key: 'ai_model_params', size: '5.2MB' },
        { name: '风险控制设置', key: 'risk_control_settings', size: '0.3MB' },
        { name: '通知设置', key: 'notification_settings', size: '0.1MB' },
        { name: '界面偏好', key: 'ui_preferences', size: '0.4MB' },
        { name: '安全设置', key: 'security_settings', size: '0.3MB' }
      ];
    },
    
    // 显示备份进度
    showBackupProgress(dataItems, completeCallback) {
      let currentIndex = 0;
      const totalItems = dataItems.length;
      
      const processNextItem = () => {
        if (currentIndex >= totalItems) {
          completeCallback();
          return;
        }
        
        const item = dataItems[currentIndex];
        uni.showLoading({
          title: `备份中(${currentIndex+1}/${totalItems}): ${item.name}`
        });
        
        // 模拟单个项目的备份时间
        setTimeout(() => {
          currentIndex++;
          if (currentIndex < totalItems) {
            processNextItem();
          } else {
            uni.hideLoading();
            completeCallback();
          }
        }, 300); // 每个项目备份时间
      };
      
      processNextItem();
    },
    
    // 从云端恢复
    restoreFromCloud() {
      // 检查是否存在备份
      const lastBackupTime = uni.getStorageSync('lastBackupTime');
      const hasCompleteBackup = uni.getStorageSync('backupDataComplete');
      
      if (!lastBackupTime || !hasCompleteBackup) {
        uni.showModal({
          title: '未找到完整备份',
          content: '您尚未创建完整的云端备份,请先备份您的数据',
          showCancel: false
        });
        return;
      }
      
      uni.showModal({
        title: '从云端恢复',
        content: '确定要从云端恢复数据吗?这将覆盖您当前设备上的设置和数据。\n\n最后备份时间:' + new Date(lastBackupTime).toLocaleString() + '\n\n恢复后,您的新设备将和原设备保持完全一致,包括所有交易记录,设置和偏好。',
        success: (res) => {
          if (res.confirm) {
            // 获取要恢复的数据项
            const dataItems = this.collectBackupData();
            this.showRestoreProgress(dataItems, () => {
              uni.hideLoading();
              uni.showModal({
                title: '恢复完成',
                content: '您的数据已成功恢复到此设备\n\n此设备现在与原设备的数据和设置完全一致',
                showCancel: false,
                success: () => {
                  // 重启应用以应用新设置
                  setTimeout(() => {
                    uni.reLaunch({
                      url: '/pages/index/index'
                    });
                  }, 1500);
                }
              });
            });
          }
        }
      });
    },
    
    // 显示恢复进度
    showRestoreProgress(dataItems, completeCallback) {
      let currentIndex = 0;
      const totalItems = dataItems.length;
      
      const processNextItem = () => {
        if (currentIndex >= totalItems) {
          completeCallback();
          return;
        }
        
        const item = dataItems[currentIndex];
        uni.showLoading({
          title: `恢复中(${currentIndex+1}/${totalItems}): ${item.name}`
        });
        
        // 模拟单个项目的恢复时间
        setTimeout(() => {
          currentIndex++;
          if (currentIndex < totalItems) {
            processNextItem();
          } else {
            uni.hideLoading();
            completeCallback();
          }
        }, 300); // 每个项目恢复时间
      };
      
      processNextItem();
    },
    
    // 扫码迁移
    scanTransferCode() {
      uni.scanCode({
        scanType: ['qrCode'],
        success: (res) => {
          // 处理扫描结果
          const code = res.result;
          
          uni.showLoading({
            title: '验证迁移码'
          });
          
          // 模拟验证过程 - 实际应用中应该调用API进行验证
          setTimeout(() => {
            uni.hideLoading();
            
            if (code.startsWith('TC-') && this.validateTransferCode(code)) {
              // 显示要迁移的数据清单
              const dataItems = this.collectBackupData();
              
              uni.showModal({
                title: '确认迁移',
                content: `是否将原设备数据迁移到当前设备?\n\n迁移将包含以下数据:\n• 交易记录\n• 交易策略\n• 自选股列表\n• 图表设置\n• 个人偏好\n\n迁移后,此设备将与原设备保持完全一致。`,
                success: (res) => {
                  if (res.confirm) {
                    // 开始数据迁移过程
                    this.beginDataTransfer(dataItems, code);
                  }
                }
              });
            } else {
              // 无效的迁移码
              uni.showModal({
                title: '迁移失败',
                content: '无效的迁移码或已过期,请重新获取',
                showCancel: false
              });
            }
          }, 1000);
        },
        fail: () => {
          uni.showToast({
            title: '扫码取消或失败',
            icon: 'none'
          });
        }
      });
    },
    
    // 验证迁移码
    validateTransferCode(code) {
      // 在实际应用中,这里应该调用API验证迁移码的有效性
      // 此处仅模拟验证过程
      return code.length > 10 && code.split('-').length >= 4;
    },
    
    // 开始数据迁移过程
    beginDataTransfer(dataItems, code) {
      uni.showLoading({
        title: '准备迁移'
      });
      
      // 模拟与服务器建立连接并准备接收数据
      setTimeout(() => {
        uni.hideLoading();
        
        // 显示迁移进度
        this.showTransferProgress(dataItems, () => {
          // 迁移完成后,显示成功信息
          uni.showModal({
            title: '迁移成功',
            content: '设备迁移已完成,所有数据和设置已与原设备保持一致',
            showCancel: false,
            success: () => {
              // 重启应用以应用新设置
              setTimeout(() => {
                uni.reLaunch({
                  url: '/pages/index/index'
                });
              }, 1500);
            }
          });
        });
      }, 1000);
    },
    
    // 显示迁移进度
    showTransferProgress(dataItems, completeCallback) {
      let currentIndex = 0;
      const totalItems = dataItems.length;
      
      const processNextItem = () => {
        if (currentIndex >= totalItems) {
          completeCallback();
          return;
        }
        
        const item = dataItems[currentIndex];
        
        // 计算进度百分比
        const progress = Math.floor((currentIndex / totalItems) * 100);
        
        uni.showLoading({
          title: `迁移中(${progress}%): ${item.name}`
        });
        
        // 模拟单个项目的迁移时间 - 根据数据大小调整
        const transferTime = Math.max(300, parseInt(item.size) * 100);
        
        setTimeout(() => {
          currentIndex++;
          if (currentIndex < totalItems) {
            processNextItem();
          } else {
            uni.hideLoading();
            // 显示应用数据变更
            uni.showLoading({
              title: '应用数据变更'
            });
            setTimeout(() => {
              uni.hideLoading();
              completeCallback();
            }, 1000);
          }
        }, transferTime); 
      };
      
      processNextItem();
    },
    
    // 手动切换暗黑模式(当点击整个设置项时)
    manualToggleDarkMode() {
      this.isDarkMode = !this.isDarkMode;
      
      // 更新全局主题设置
      const app = getApp();
      app.toggleTheme(this.isDarkMode);
      
      // 兼容旧版本使用 theme 字符串的情况
      if (app.globalData) {
        app.globalData.theme = this.isDarkMode ? 'dark' : 'light';
      }
      
      uni.showToast({
        title: this.isDarkMode ? '已切换到暗黑模式' : '已切换到浅色模式',
        icon: 'none'
      });
    },

    // 跳转到网络测试页面
    goToNetworkTest() {
      uni.navigateTo({
        url: '/pages/network-test/index',
        fail: (err) => {
          console.error('跳转到网络测试页面失败:', err);
          uni.showToast({
            title: '页面跳转失败',
            icon: 'none'
          });
        }
      });
    },

    // 跳转到连接测试页面
    goToConnectionTest() {
      uni.navigateTo({
        url: '/pages/connection-test/index',
        fail: (err) => {
          console.error('跳转到连接测试页面失败:', err);
          uni.showToast({
            title: '页面跳转失败',
            icon: 'none'
          });
        }
      });
    },
  }
}
</script>

<style>
/* 主题样式已移至App.vue的全局CSS中,这里是组件特定样式 */

/* 浅色主题 */
.light-theme .header {
  margin-bottom: 30rpx;
}

.light-theme .title {
  font-size: 40rpx;
  font-weight: bold;
  color: #333333;
}

.light-theme .settings-section {
  margin-bottom: 40rpx;
}

.light-theme .section-title {
  margin-bottom: 20rpx;
}

.light-theme .title-text {
  font-size: 32rpx;
  font-weight: bold;
  color: #333333;
}

.light-theme .setting-group {
  background-color: #ffffff;
  border-radius: 12rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.light-theme .setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx 40rpx 30rpx 30rpx;
  border-bottom: 1px solid #eeeeee;
  position: relative;
  z-index: 1;
}

.light-theme .setting-item:last-child {
  border-bottom: none;
}

.light-theme .setting-item:active {
  opacity: 0.7;
  background-color: rgba(0, 0, 0, 0.05);
}

.light-theme .setting-item::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
}

.light-theme .setting-label {
  font-size: 28rpx;
  color: #333333;
}

.light-theme .setting-value {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  max-width: 60%;
  flex-shrink: 0;
}

.light-theme .value-text {
  font-size: 26rpx;
  color: #999999;
  margin-right: 20rpx;
  text-align: right;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200rpx;
}

.light-theme .arrow-right {
  width: 16rpx;
  height: 16rpx;
  min-width: 16rpx;
  border-top: 2px solid #cccccc;
  border-right: 2px solid #cccccc;
  transform: rotate(45deg);
  margin-left: 10rpx;
}

/* 深色主题 */
.dark-theme .header {
  margin-bottom: 30rpx;
}

.dark-theme .title {
  font-size: 40rpx;
  font-weight: bold;
  color: #ffffff;
}

.dark-theme .settings-section {
  margin-bottom: 40rpx;
}

.dark-theme .section-title {
  margin-bottom: 20rpx;
}

.dark-theme .title-text {
  font-size: 32rpx;
  font-weight: bold;
  color: #ffffff;
}

.dark-theme .setting-group {
  background-color: #222222;
  border-radius: 12rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.2);
}

.dark-theme .setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx 40rpx 30rpx 30rpx;
  border-bottom: 1px solid #333333;
  position: relative;
  z-index: 1;
}

.dark-theme .setting-item:last-child {
  border-bottom: none;
}

.dark-theme .setting-item:active {
  background-color: rgba(255, 255, 255, 0.1);
}

.dark-theme .setting-item::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
}

.dark-theme .setting-label {
  font-size: 28rpx;
  color: #ffffff;
}

.dark-theme .setting-value {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  max-width: 60%;
  flex-shrink: 0;
}

.dark-theme .value-text {
  font-size: 26rpx;
  color: #999999;
  margin-right: 20rpx;
  text-align: right;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200rpx;
}

.dark-theme .arrow-right {
  width: 16rpx;
  height: 16rpx;
  min-width: 16rpx;
  border-top: 2px solid #666666;
  border-right: 2px solid #666666;
  transform: rotate(45deg);
  margin-left: 10rpx;
}

/* 通用 */
.light-theme .language-value .value-text,
.dark-theme .language-value .value-text,
.light-theme .security-value .value-text,
.dark-theme .security-value .value-text {
  max-width: 180rpx;
  min-width: 120rpx;
}

/* Add tap capture element styles */
.tap-capture {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 2;
}

/* 确保暗黑模式设置项可点击 */
.dark-mode-item {
  cursor: pointer;
}
</style> 
