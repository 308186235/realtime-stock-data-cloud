<template>
  <view :class="['container', isDarkMode ? 'dark-theme' : 'light-theme']">
    <view class="header">
      <view class="back-button" @click="goBack">
        <view class="back-arrow"></view>
        <text class="back-text">返回</text>
      </view>
      <text class="title">安全设置</text>
    </view>
    
    <view class="settings-section">
      <view class="section-title">
        <text class="title-text">应用解锁方式</text>
      </view>
      
      <view class="setting-group">
        <view class="setting-item">
          <text class="setting-label">密码解锁</text>
          <view class="setting-value">
            <switch :checked="usePINCode" @change="togglePasswordLock" color="#4c8dff" />
          </view>
        </view>
        
        <view class="setting-item" @click="toggleFingerprint" :class="{ disabled: !isFingerprintAvailable }">
          <text class="setting-label">指纹解锁</text>
          <view class="setting-value">
            <switch :checked="useFingerprint" @change="toggleFingerprint" color="#4c8dff" 
                   :disabled="!isFingerprintAvailable" />
          </view>
        </view>
        
        <view class="setting-item" @click="toggleFacialRecognition" :class="{ disabled: !isFacialAvailable }">
          <text class="setting-label">面容解锁</text>
          <view class="setting-value">
            <switch :checked="useFacialRecognition" @change="toggleFacialRecognition" color="#4c8dff"
                   :disabled="!isFacialAvailable" />
          </view>
        </view>
      </view>
    </view>
    
    <view class="settings-section" v-if="usePINCode">
      <view class="section-title">
        <text class="title-text">密码设置</text>
      </view>
      
      <view class="setting-group">
        <view class="setting-item" @click="changePassword">
          <text class="setting-label">修改密码</text>
          <view class="setting-value">
            <text class="value-text">{{pinStatusText}}</text>
            <view class="arrow-right"></view>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 密码修改弹窗 -->
    <view v-if="showPinDialog" class="custom-popup">
      <view class="custom-popup-mask" @click="closePINCodePopup"></view>
      <view class="custom-popup-content">
        <view class="custom-popup-title">
          <template v-if="isChangingPINCode">
            <template v-if="verifyingOldPIN">
              验证当前密码
            </template>
            <template v-else>
              设置新密码
            </template>
          </template>
          <template v-else>
            设置应用解锁密码
          </template>
        </view>
        <view class="pin-code-form">
          <template v-if="isChangingPINCode">
            <template v-if="verifyingOldPIN">
              <!-- 验证旧密码 -->
              <input 
                class="pin-input"
                type="password" 
                placeholder="请输入当前密码" 
                maxlength="6"
                v-model="pinCode"
              />
            </template>
            <template v-else>
              <!-- 设置新密码 -->
              <input 
                v-if="!confirmingPINCode" 
                class="pin-input"
                type="password" 
                placeholder="请输入新的6位数字密码" 
                maxlength="6"
                v-model="pinCode"
              />
              <input 
                v-else 
                class="pin-input"
                type="password" 
                placeholder="请再次输入新密码确认" 
                maxlength="6"
                v-model="pinCodeConfirm"
              />
            </template>
          </template>
          <template v-else>
            <!-- 首次设置密码 -->
            <input 
              v-if="!confirmingPINCode" 
              class="pin-input"
              type="password" 
              placeholder="请输入6位数字密码" 
              maxlength="6"
              v-model="pinCode"
            />
            <input 
              v-else 
              class="pin-input"
              type="password" 
              placeholder="请再次输入密码确认" 
              maxlength="6"
              v-model="pinCodeConfirm"
            />
          </template>
        </view>
        <view class="custom-popup-buttons">
          <button class="cancel-button" @click="closePINCodePopup">取消</button>
          <button class="confirm-button" @click="confirmPINCode">确定</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import authService from '../../services/auth-service.js';
import biometricAuth from '../../utils/biometric-auth.js';
import secureStorage from '../../utils/secure-storage.js';

export default {
  data() {
    return {
      isDarkMode: false,
      
      // 安全设置选项
      usePINCode: false,
      useFingerprint: false,
      useFacialRecognition: false,
      
      // 设备生物识别能力
      isFingerprintAvailable: false,
      isFacialAvailable: false,
      isBiometricAvailable: false,
      
      // 密码设置
      hasPINCode: false,
      pinCode: '',
      pinCodeConfirm: '',
      confirmingPINCode: false,
      showPinDialog: false,
      
      // 修改密码模式
      isChangingPINCode: false,   // 是否为修改密码模式
      verifyingOldPIN: false,     // 是否正在验证旧密码
      oldPINVerified: false,      // 旧密码是否已验证
      
      // 回调函数
      pinDialogCancelCallback: null,  // 弹窗取消回调
      pinVerificationCallback: null,  // 密码验证成功回调
      
      // 错误计数
      pinAttempts: 0,
      maxPinAttempts: 5
    }
  },
  computed: {
    // 计算属性:密码状态文本
    pinStatusText() {
      return this.hasPINCode ? '已设置' : '未设置';
    }
  },
  onLoad() {
    console.log('安全设置页面加载');
    // 获取当前主题设置
    const app = getApp();
    this.isDarkMode = app.globalData.isDarkMode;
    
    // 主动迁移旧密码到新格式
    this.migrateOldPINCode();
    
    // 加载用户安全设置
    this.loadSecuritySettings();
    
    // 检查设备生物识别能力
    this.checkBiometricCapabilities();
  },
  methods: {
    // 迁移旧密码到新格式
    migrateOldPINCode() {
      try {
        // 调用迁移方法
        console.log('开始迁移旧密码');
        const result = secureStorage.migrateLegacyPINCode();
        console.log('密码迁移结果:', result);
      } catch (e) {
        console.error('密码迁移失败', e);
      }
    },
    
    goBack() {
      uni.navigateBack();
    },
    
    // 加载安全设置
    loadSecuritySettings() {
      try {
        // 从认证服务加载设置 - 只调用一次
        const settings = authService.getSecuritySettings();
        console.log('加载的安全设置:', settings);
        
        // 更新本地状态
        this.usePINCode = settings.usePINCode || false;
        this.useFingerprint = settings.useFingerprint || false;
        this.useFacialRecognition = settings.useFacialRecognition || false;
        this.hasPINCode = settings.hasPINCode || false;
        
        console.log('安全设置状态:', {
          usePINCode: this.usePINCode,
          hasPINCode: this.hasPINCode
        });
      } catch (e) {
        console.error('加载安全设置失败', e);
        // 初始化默认设置
        this.saveSecuritySettings();
      }
    },
    
    // 保存安全设置
    saveSecuritySettings() {
      try {
        // 检查PIN码状态
        const hasPinCode = secureStorage.hasPINCode();
        
        // 构建设置对象
        const settings = {
          usePINCode: hasPinCode ? this.usePINCode : false, // 如果没有PIN码,强制禁用
          useFingerprint: this.useFingerprint,
          useFacialRecognition: this.useFacialRecognition,
          hasPINCode: hasPinCode // 使用存储中的实际状态
        };
        
        console.log('保存安全设置', settings);
        
        // 先清除缓存
        authService.clearSettingsCache();
        
        // 使用认证服务保存设置
        const savedSettings = authService.saveSecuritySettings(settings);
        
        // 如果保存成功,更新本地状态
        if (savedSettings) {
          // 强制同步本地状态与存储状态
          this.hasPINCode = savedSettings.hasPINCode;
          this.usePINCode = savedSettings.usePINCode;
          
          console.log('设置已更新:', {
            usePINCode: this.usePINCode,
            hasPINCode: this.hasPINCode
          });
        }
      } catch (e) {
        console.error('保存安全设置失败', e);
        uni.showToast({
          title: '保存设置失败',
          icon: 'none',
          duration: 2000
        });
      }
    },
    
    // 检查生物识别功能
    async checkBiometricCapabilities() {
      try {
        // 使用生物认证工具检查设备能力
        const support = await biometricAuth.checkBiometricSupport();
        this.isFingerprintAvailable = support.fingerprintSupported;
        this.isFacialAvailable = support.facialSupported;
        this.isBiometricAvailable = support.fingerprintSupported || support.facialSupported;
        
        console.log('生物识别支持情况:', {
          指纹支持: this.isFingerprintAvailable,
          面容支持: this.isFacialAvailable,
          类型: support.type
        });
      } catch (e) {
        console.error('检查生物识别能力失败', e);
        this.isFingerprintAvailable = false;
        this.isFacialAvailable = false;
        this.isBiometricAvailable = false;
      }
    },
    
    // 切换密码解锁
    togglePasswordLock(e) {
      console.log('切换密码解锁:', e);
      
      // 获取新状态
      const newValue = e.detail.value;
      console.log('密码解锁状态切换为:', newValue);
      
      // 如果是从开启到关闭,需要先验证密码
      if (!newValue && this.usePINCode && this.hasPINCode) {
        // 设置验证密码模式
        this.isChangingPINCode = true;
        this.verifyingOldPIN = true;
        this.oldPINVerified = false;
        
        // 清空输入字段
        this.pinCode = '';
        this.pinCodeConfirm = '';
        this.confirmingPINCode = false;
        
        // 打开密码验证弹窗
        this.togglePinCodePopup();
        
        // 设置弹窗关闭回调 - 如果取消,不改变开关状态
        this.pinDialogCancelCallback = () => {
          console.log('用户取消关闭密码解锁,保持开关状态');
          this.usePINCode = true;
        };
        
        // 添加验证成功回调
        this.pinVerificationCallback = () => {
          console.log('密码验证成功,关闭密码解锁');
          this.usePINCode = false;
          this.saveSecuritySettings();
        };
        
        return;
      }
      
      // 更新状态
      this.usePINCode = newValue;
      
      // 如果开启密码但未设置,则打开设置弹窗
      if (this.usePINCode && !this.hasPINCode) {
        console.log('未设置密码,打开密码设置框');
        this.togglePinCodePopup();
      } else {
        // 直接保存设置
        this.saveSecuritySettings();
      }
    },
    
    // 切换指纹解锁
    toggleFingerprint(e) {
      if (!this.isFingerprintAvailable) {
        // 移除toast显示
        return;
      }
      
      if (typeof e === 'object') {
        this.useFingerprint = e.detail.value;
      } else {
        this.useFingerprint = !this.useFingerprint;
      }
      
      if (this.useFingerprint) {
        // 验证指纹
        this.verifyFingerprint(() => {
          // 如果切换指纹识别成功,确保至少有一种认证方式
          this.ensureAuthMethod();
          this.saveSecuritySettings();
        }, () => {
          this.useFingerprint = false;
          this.saveSecuritySettings();
        });
      } else {
        this.ensureAuthMethod();
        this.saveSecuritySettings();
      }
    },
    
    // 切换面容解锁
    toggleFacialRecognition(e) {
      if (!this.isFacialAvailable) {
        // 移除toast显示
        return;
      }
      
      if (typeof e === 'object') {
        this.useFacialRecognition = e.detail.value;
      } else {
        this.useFacialRecognition = !this.useFacialRecognition;
      }
      
      if (this.useFacialRecognition) {
        // 验证面容识别
        this.verifyFacialRecognition(() => {
          // 如果切换面容识别成功,确保至少有一种认证方式
          this.ensureAuthMethod();
          this.saveSecuritySettings();
        }, () => {
          this.useFacialRecognition = false;
          this.saveSecuritySettings();
        });
      } else {
        this.ensureAuthMethod();
        this.saveSecuritySettings();
      }
    },
    
    // 确保至少启用一种认证方式
    ensureAuthMethod() {
      // 如果没有启用任何生物认证,则确保至少有PIN码
      if (!this.useFingerprint && !this.useFacialRecognition) {
        this.usePINCode = true;
        
        // 如果PIN码未设置,弹出设置界面
        if (!this.hasPINCode) {
          this.$nextTick(() => {
            this.togglePinCodePopup();
          });
        }
      }
    },
    
    // 修改密码
    changePassword() {
      console.log('用户点击修改密码');
      
      // 检查是否已设置密码
      if (!this.hasPINCode) {
        // 如果未设置密码,直接进入设置流程
        console.log('未设置密码,进入设置流程');
        this.isChangingPINCode = false;
        this.verifyingOldPIN = false;
        this.oldPINVerified = false;
      } else {
        // 已有密码,需要先验证旧密码
        console.log('已有密码,进入验证流程');
        this.isChangingPINCode = true;
        this.verifyingOldPIN = true;
        this.oldPINVerified = false;
      }
      
      // 重置输入状态
      this.pinCode = '';
      this.pinCodeConfirm = '';
      this.confirmingPINCode = false;
      
      // 打开密码设置弹窗
      this.togglePinCodePopup();
    },
    
    // 打开/关闭PIN码弹窗
    togglePinCodePopup() {
      // 显示弹窗
      this.showPinDialog = true;
      
      // 根据状态设置标题文本
      if (this.isChangingPINCode) {
        if (this.verifyingOldPIN) {
          console.log('显示验证原密码弹窗');
        } else {
          console.log('显示设置新密码弹窗');
        }
      } else {
        console.log('显示密码设置弹窗');
      }
      
      // 如果用户取消了PIN码设置并且没有已有PIN码
      if (!this.hasPINCode) {
        // 添加取消时的回调,以便在用户取消设置时重置开关状态
        this.pinDialogCancelCallback = () => {
          console.log('用户取消PIN码设置,重置开关状态');
          this.usePINCode = false;
          this.saveSecuritySettings();
        };
      } else {
        // 清除取消回调
        this.pinDialogCancelCallback = null;
      }
    },
    
    closePINCodePopup() {
      console.log('关闭密码设置弹窗');
      this.showPinDialog = false;
      this.pinCode = '';
      this.pinCodeConfirm = '';
      this.confirmingPINCode = false;
      this.isChangingPINCode = false;
      this.verifyingOldPIN = false;
      this.oldPINVerified = false;
      
      // 执行取消回调(如果有)
      if (this.pinDialogCancelCallback) {
        this.pinDialogCancelCallback();
        this.pinDialogCancelCallback = null;
      }
      
      // 清除验证回调
      this.pinVerificationCallback = null;
    },
    
    // 确认密码设置
    confirmPINCode() {
      // 如果是修改密码模式且正在验证旧密码
      if (this.isChangingPINCode && this.verifyingOldPIN) {
        this.verifyOldPINCode();
        return;
      }
      
      console.log("确认密码,阶段:", this.confirmingPINCode ? "确认阶段" : "输入阶段");
      
      if (!this.confirmingPINCode) {
        // 第一次输入密码 - 验证格式
        console.log('验证密码格式:', this.pinCode);
        
        if (!this.pinCode || this.pinCode.trim() === '') {
          // 移除toast显示
          return;
        }
        
        if (this.pinCode.length !== 6 || !/^\d{6}$/.test(this.pinCode)) {
          // 移除toast显示
          return;
        }
        
        // 进入确认密码阶段
        this.confirmingPINCode = true;
        console.log('密码格式正确,进入确认阶段');
        return;
      } else {
        // 确认密码
        console.log('验证两次密码是否一致');
        
        if (!this.pinCodeConfirm || this.pinCodeConfirm.trim() === '') {
          // 移除toast显示
          return;
        }
        
        if (this.pinCode !== this.pinCodeConfirm) {
          // 移除toast显示
          this.pinCodeConfirm = '';
          return;
        }
        
        // 保存PIN码变量,防止在弹窗关闭后丢失
        const finalPinCode = this.pinCode;
        
        // 先关闭弹窗,避免重复操作
        this.closePINCodePopup();
        
        // 显示加载
        uni.showLoading({
          title: '正在保存...',
          mask: true
        });
        
        // 根据是否为修改密码模式选择不同的日志信息
        if (this.isChangingPINCode) {
          console.log('开始更新PIN码:', finalPinCode);
        } else {
          console.log('开始保存PIN码:', finalPinCode);
        }
        
        // 保存密码 - 添加备选存储方法
        try {
          // 存储成功标志
          let storageSuccess = false;
          
          // 方法1:使用安全服务
          const success = authService.setPINCode(finalPinCode);
          console.log('方法1-安全服务存储结果:', success);
          
          if (success) {
            storageSuccess = true;
          } else {
            // 方法2:直接使用安全存储
            console.log('尝试方法2-直接安全存储');
            const directSuccess = secureStorage.storePINCode(finalPinCode);
            console.log('方法2-直接存储结果:', directSuccess);
            
            if (directSuccess) {
              storageSuccess = true;
            } else {
              // 方法3:不加密直接存储
              console.log('尝试方法3-未加密直接存储');
              uni.setStorageSync('direct_pin_code', finalPinCode);
              // 检查是否已存储
              const storedValue = uni.getStorageSync('direct_pin_code');
              const method3Success = storedValue === finalPinCode;
              console.log('方法3-直接存储结果:', method3Success);
              storageSuccess = method3Success;
            }
          }
          
          uni.hideLoading();
          
          // 如果任何一种存储方法成功
          if (storageSuccess) {
            // 手动更新内存中的状态
            this.hasPINCode = true;
            this.usePINCode = true;
            
            // 强制清除缓存并更新安全设置
            try {
              // 清除缓存强制读取最新值
              authService.clearSettingsCache();
              
              // 保存设置到存储
              authService.saveSecuritySettings({
                usePINCode: true,
                useFingerprint: this.useFingerprint,
                useFacialRecognition: this.useFacialRecognition,
                hasPINCode: true
              });
              
              // 根据是否为修改密码显示不同的成功信息
              if (this.isChangingPINCode) {
                console.log('PIN码修改成功并更新UI状态');
              } else {
                console.log('PIN码设置成功并更新UI状态');
              }
            } catch (e) {
              console.error('更新设置失败', e);
            }
            
            // 重置修改密码状态
            this.isChangingPINCode = false;
            this.verifyingOldPIN = false;
            this.oldPINVerified = false;
          } else {
            // 所有方法都失败
            console.error('所有存储方法都失败');
            // 重置状态
            this.usePINCode = false;
            this.hasPINCode = false;
            this.saveSecuritySettings();
          }
        } catch (e) {
          uni.hideLoading();
          console.error('保存密码失败:', e);
          // 重置状态
          this.usePINCode = false;
          this.hasPINCode = false;
          this.saveSecuritySettings();
        }
      }
    },
    
    // 验证指纹
    verifyFingerprint(successCallback, failCallback) {
      biometricAuth.verifyFingerprint('请验证指纹以启用指纹解锁功能')
        .then(result => {
          if (result.status === biometricAuth.BIOMETRIC_STATUS.SUCCESS) {
            // 移除toast显示
            if (successCallback) successCallback();
          } else {
            // 用户取消或其他非失败状态
            // 移除toast显示
            if (failCallback) failCallback();
          }
        })
        .catch(err => {
          console.log('指纹验证失败', err);
          
          // 移除toast显示
          
          if (failCallback) failCallback();
        });
    },
    
    // 验证面容识别
    verifyFacialRecognition(successCallback, failCallback) {
      biometricAuth.verifyFacial('请面向屏幕以启用面容解锁功能')
        .then(result => {
          if (result.status === biometricAuth.BIOMETRIC_STATUS.SUCCESS) {
            // 移除toast显示
            if (successCallback) successCallback();
          } else {
            // 用户取消或其他非失败状态
            // 移除toast显示
            if (failCallback) failCallback();
          }
        })
        .catch(err => {
          console.log('面容验证失败', err);
          
          // 移除toast显示
          
          if (failCallback) failCallback();
        });
    },
    
    // 验证旧密码
    verifyOldPINCode() {
      console.log('验证旧密码:', this.pinCode);
      
      if (!this.pinCode || this.pinCode.trim() === '') {
        // 移除toast显示
        return;
      }
      
      // 验证密码
      const isValid = authService.verifyPINCode(this.pinCode);
      
      if (isValid) {
        console.log('原密码验证成功,进入设置新密码阶段');
        
        // 检查是否有密码验证回调函数
        if (this.pinVerificationCallback) {
          // 保存回调的引用,防止被清除
          const callback = this.pinVerificationCallback;
          
          // 先关闭弹窗
          this.closePINCodePopup();
          
          // 执行回调
          callback();
        } else {
          // 正常的修改密码流程:验证成功,进入设置新密码阶段
          this.verifyingOldPIN = false;
          this.oldPINVerified = true;
          this.pinCode = '';
          this.pinCodeConfirm = '';
          this.confirmingPINCode = false;
        }
      } else {
        console.log('原密码验证失败');
        // 移除toast显示
        this.pinCode = '';
      }
    }
  }
}
</script>

<style>
.container {
  padding: 30rpx;
  min-height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  margin-bottom: 40rpx;
}

.back-button {
  display: flex;
  align-items: center;
  margin-right: 20rpx;
}

.back-arrow {
  width: 20rpx;
  height: 20rpx;
  border-top: 2px solid #333;
  border-left: 2px solid #333;
  transform: rotate(-45deg);
}

.dark-theme .back-arrow {
  border-color: #fff;
}

.back-text {
  font-size: 28rpx;
  margin-left: 10rpx;
  color: #333;
}

.dark-theme .back-text {
  color: #fff;
}

.title {
  font-size: 36rpx;
  font-weight: bold;
  flex: 1;
  text-align: center;
  margin-right: 50rpx;
}

.light-theme .title {
  color: #333;
}

.dark-theme .title {
  color: #fff;
}

.settings-section {
  margin-bottom: 40rpx;
}

.section-title {
  margin-bottom: 20rpx;
}

.title-text {
  font-size: 30rpx;
  font-weight: bold;
}

.light-theme .title-text {
  color: #333;
}

.dark-theme .title-text {
  color: #fff;
}

.setting-group {
  border-radius: 12rpx;
  overflow: hidden;
}

.light-theme .setting-group {
  background-color: #fff;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.dark-theme .setting-group {
  background-color: #222;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.2);
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
}

.light-theme .setting-item {
  border-bottom: 1px solid #eee;
}

.dark-theme .setting-item {
  border-bottom: 1px solid #333;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-label {
  font-size: 28rpx;
}

.light-theme .setting-label {
  color: #333;
}

.dark-theme .setting-label {
  color: #fff;
}

.setting-value {
  display: flex;
  align-items: center;
}

.value-text {
  font-size: 26rpx;
  margin-right: 10rpx;
}

.light-theme .value-text {
  color: #999;
}

.dark-theme .value-text {
  color: #999;
}

.arrow-right {
  width: 16rpx;
  height: 16rpx;
  border-top: 2px solid #ccc;
  border-right: 2px solid #ccc;
  transform: rotate(45deg);
}

.dark-theme .arrow-right {
  border-color: #666;
}

.disabled {
  opacity: 0.5;
}

.pin-code-form {
  margin-top: 20rpx;
}

.pin-input {
  width: 100%;
  height: 80rpx;
  border: 1px solid #ddd;
  border-radius: 8rpx;
  padding: 0 20rpx;
  text-align: center;
  font-size: 32rpx;
  letter-spacing: 5rpx;
}

.dark-theme .pin-input {
  background-color: #333;
  border-color: #555;
  color: #fff;
}

.custom-popup {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.custom-popup-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
}

.dark-theme .custom-popup-mask {
  background-color: rgba(0, 0, 0, 0.7);
}

.custom-popup-content {
  background-color: #fff;
  padding: 40rpx;
  border-radius: 12rpx;
  width: 80%;
  max-width: 600rpx;
  position: relative;
  z-index: 1000;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.1);
}

.dark-theme .custom-popup-content {
  background-color: #222;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.3);
}

.custom-popup-title {
  font-size: 36rpx;
  font-weight: bold;
  margin-bottom: 40rpx;
  text-align: center;
}

.dark-theme .custom-popup-title {
  color: #fff;
}

.pin-code-form {
  margin: 20rpx 0 40rpx;
}

.pin-input {
  width: 100%;
  height: 90rpx;
  border: 1px solid #ddd;
  border-radius: 8rpx;
  padding: 0 20rpx;
  text-align: center;
  font-size: 40rpx;
  letter-spacing: 8rpx;
  background-color: #f9f9f9;
}

.dark-theme .pin-input {
  background-color: #333;
  border-color: #555;
  color: #fff;
}

.custom-popup-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 40rpx;
}

.cancel-button,
.confirm-button {
  flex: 1;
  padding: 20rpx 0;
  border: none;
  border-radius: 8rpx;
  font-size: 32rpx;
  color: #fff;
  margin: 0 10rpx;
  height: 80rpx;
  line-height: 80rpx;
  text-align: center;
}

.cancel-button {
  background-color: #999;
}

.dark-theme .cancel-button {
  background-color: #555;
}

.confirm-button {
  background-color: #4c8dff;
}
</style> 
