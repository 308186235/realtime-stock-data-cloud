/**
 * 认证服务
 * 提供应用安全认证和登录服务
 */
import biometricAuth from '../utils/biometric-auth.js';
import secureStorage from '../utils/secure-storage.js';

// 锁定状态
const LOCK_STATUS = {
  LOCKED: 'locked',
  UNLOCKED: 'unlocked',
  PENDING: 'pending'
};

// 为应用锁定状态使用的安全存储键
const APP_LOCK_KEY = 'appLockStatus';
const AUTH_SESSION_KEY = 'authSession';
const SECURITY_SETTINGS_KEY = 'securitySettings';

// 设置缓存
let securitySettingsCache = null;
let cacheTime = 0;
const CACHE_EXPIRY = 5000; // 5秒缓存

/**
 * 获取安全设置
 * @returns {Object} 安全设置
 */
const getSecuritySettings = () => {
  try {
    const now = Date.now();
    
    // 如果缓存有效,直接返回缓存
    if (securitySettingsCache && (now - cacheTime < CACHE_EXPIRY)) {
      console.log('使用缓存的安全设置');
      return {...securitySettingsCache}; // 返回副本
    }
    
    console.log('从存储中读取安全设置');
    
    // 使用安全存储获取设置
    const settings = secureStorage.getSecureData(SECURITY_SETTINGS_KEY);
    
    // 确保settings是对象类型
    let validSettings = {};
    if (settings && typeof settings === 'object' && !Array.isArray(settings)) {
      validSettings = settings;
    } else if (settings) {
      console.error('安全设置格式无效,重置为默认值', typeof settings);
      // 如果不是对象,可能是已损坏的数据,清除它
      secureStorage.removeSecureData(SECURITY_SETTINGS_KEY);
    }
    
    // 确保返回的设置中包含hasPINCode状态
    validSettings.hasPINCode = secureStorage.hasPINCode();
    
    // 更新缓存
    securitySettingsCache = {...validSettings};
    cacheTime = now;
    
    return validSettings;
  } catch (e) {
    console.error('获取安全设置失败', e);
  }
  
  // 默认安全设置
  const defaultSettings = {
    usePINCode: false,
    useFingerprint: false,
    useFacialRecognition: false,
    hasPINCode: secureStorage.hasPINCode()
  };
  
  // 更新缓存
  securitySettingsCache = {...defaultSettings};
  cacheTime = Date.now();
  
  return defaultSettings;
};

/**
 * 清除设置缓存,确保下次读取最新数据
 */
const clearSettingsCache = () => {
  securitySettingsCache = null;
  cacheTime = 0;
};

/**
 * 保存安全设置
 * @param {Object} settings 安全设置对象
 */
const saveSecuritySettings = (settings) => {
  try {
    // 清除缓存确保使用最新状态
    clearSettingsCache();
    
    // 在保存前更新PIN码状态
    settings.hasPINCode = secureStorage.hasPINCode();
    
    // 确保usePINCode状态与hasPINCode一致
    if (!settings.hasPINCode) {
      // 如果没有PIN码,不能启用PIN码解锁
      settings.usePINCode = false;
    }
    
    console.log('保存安全设置前最终状态:', settings);
    
    // 使用安全存储保存设置
    secureStorage.setSecureData(SECURITY_SETTINGS_KEY, settings);
    
    // 更新缓存
    securitySettingsCache = {...settings};
    cacheTime = Date.now();
    
    // 触发应用设置更新事件
    uni.$emit('securitySettingsChanged', settings);
    
    return settings;
  } catch (e) {
    console.error('保存安全设置失败', e);
    return null;
  }
};

/**
 * 检查应用是否锁定
 * @returns {Boolean} 是否锁定
 */
const isAppLocked = () => {
  try {
    // 从安全存储获取锁定状态
    const lockStatus = secureStorage.getSecureData(APP_LOCK_KEY, LOCK_STATUS.UNLOCKED);
    return lockStatus === LOCK_STATUS.LOCKED;
  } catch (e) {
    console.error('获取锁定状态失败', e);
    return false;
  }
};

/**
 * 设置应用锁定状态
 * @param {Boolean} locked 是否锁定
 */
const setAppLocked = (locked) => {
  try {
    const status = locked ? LOCK_STATUS.LOCKED : LOCK_STATUS.UNLOCKED;
    secureStorage.setSecureData(APP_LOCK_KEY, status);
    
    // 如果解锁,记录会话时间
    if (!locked) {
      const sessionData = {
        unlockTime: new Date().getTime(),
        expiryTime: new Date().getTime() + (30 * 60 * 1000) // 30分钟过期
      };
      secureStorage.setSecureData(AUTH_SESSION_KEY, sessionData);
    }
  } catch (e) {
    console.error('设置锁定状态失败', e);
  }
};

/**
 * 验证PIN码
 * @param {String} pinCode 用户输入的PIN码
 * @returns {Boolean} 验证是否成功
 */
const verifyPINCode = (pinCode) => {
  try {
    // 首先通过安全存储验证
    const secureResult = secureStorage.verifyPINCode(pinCode);
    if (secureResult) {
      return true;
    }
    
    // 如果安全存储验证失败,尝试直接存储
    try {
      const directPinCode = uni.getStorageSync('direct_pin_code');
      if (directPinCode && directPinCode === pinCode) {
        console.log('通过直接存储验证PIN码成功');
        return true;
      }
    } catch (e) {
      console.error('直接存储验证失败', e);
    }
    
    return false;
  } catch (e) {
    console.error('验证PIN码失败', e);
    return false;
  }
};

/**
 * 设置/更新PIN码
 * @param {String} pinCode 新的PIN码
 * @returns {Boolean} 设置是否成功
 */
const setPINCode = (pinCode) => {
  console.log('开始设置PIN码');
  
  // 验证输入
  if (!pinCode || typeof pinCode !== 'string' || pinCode.trim() === '') {
    console.error('PIN码无效');
    return false;
  }
  
  try {
    // 清除缓存
    clearSettingsCache();
    
    // 先清除旧的PIN码,确保不会有冲突
    secureStorage.removeSecureData('tradePINCode');
    
    // 调用全部参数的存储方法,指明这是PIN码
    console.log('尝试存储PIN码:', pinCode);
    const success = secureStorage.storePINCode(pinCode);
    console.log('PIN码存储结果:', success);
    
    if (success) {
      // 验证PIN码是否正确存储
      const hasPIN = secureStorage.hasPINCode();
      const verifyResult = secureStorage.verifyPINCode(pinCode);
      console.log('PIN码验证:', { hasPIN, verifyResult });
      
      if (hasPIN && verifyResult) {
        // 更新安全设置以反映PIN码已设置
        const settings = getSecuritySettings();
        settings.hasPINCode = true;
        settings.usePINCode = true; // 自动启用PIN码解锁
        saveSecuritySettings(settings);
        
        console.log('安全设置已更新,PIN码已启用');
        return true;
      } else {
        console.error('PIN码存储成功但验证失败');
        return false;
      }
    } else {
      // 尝试备选存储方法
      try {
        console.log('尝试备选方法存储PIN码');
        uni.setStorageSync('direct_pin_code', pinCode);
        const storedCode = uni.getStorageSync('direct_pin_code');
        
        if (storedCode === pinCode) {
          // 更新安全设置
          console.log('备选方法PIN码存储成功');
          const settings = getSecuritySettings();
          settings.hasPINCode = true;
          settings.usePINCode = true;
          saveSecuritySettings(settings);
          
          return true;
        }
      } catch (e) {
        console.error('备选PIN码存储失败', e);
      }
      
      console.error('所有PIN码存储方法都失败');
      return false;
    }
  } catch (e) {
    console.error('设置PIN码失败', e);
    return false;
  }
};

/**
 * 应用解锁 - 使用生物识别
 * @returns {Promise} 解锁结果
 */
const unlockWithBiometric = async () => {
  try {
    const settings = getSecuritySettings();
    let preferredType = null;
    
    // 确定使用的生物识别类型
    if (settings.useFingerprint) {
      preferredType = biometricAuth.BIOMETRIC_TYPES.FINGERPRINT;
    } else if (settings.useFacialRecognition) {
      preferredType = biometricAuth.BIOMETRIC_TYPES.FACIAL;
    }
    
    // 如果没有启用生物识别
    if (!settings.useFingerprint && !settings.useFacialRecognition) {
      return Promise.reject({
        status: 'failed',
        message: '未启用生物识别'
      });
    }
    
    // 执行生物识别验证
    const result = await biometricAuth.verifyBiometric(preferredType, '请验证身份以解锁应用');
    
    if (result.status === biometricAuth.BIOMETRIC_STATUS.SUCCESS) {
      // 解锁成功
      setAppLocked(false);
      return {
        status: 'success',
        message: '解锁成功',
        type: result.type
      };
    } else {
      // 其他状态(取消等)
      return result;
    }
  } catch (error) {
    console.error('生物识别解锁失败', error);
    
    // 根据错误类型提供更具体的信息
    if (error.status === biometricAuth.BIOMETRIC_STATUS.LOCKED_OUT) {
      return {
        status: 'locked_out',
        message: '生物识别已锁定,请使用PIN码解锁',
        error
      };
    } else if (error.status === biometricAuth.BIOMETRIC_STATUS.UNAVAILABLE) {
      return {
        status: 'unavailable',
        message: '生物识别暂时不可用,请稍后再试或使用PIN码',
        error
      };
    } else {
      return {
        status: 'failed',
        message: error.message || '生物识别失败',
        error
      };
    }
  }
};

/**
 * 应用解锁 - 使用PIN码
 * @param {String} pinCode 用户输入的PIN码
 * @returns {Object} 解锁结果
 */
const unlockWithPINCode = (pinCode) => {
  if (verifyPINCode(pinCode)) {
    setAppLocked(false);
    return {
      status: 'success',
      message: '解锁成功'
    };
  } else {
    return {
      status: 'failed',
      message: 'PIN码错误'
    };
  }
};

/**
 * 交易确认 - 使用生物识别
 * @param {String} operation 操作类型描述
 * @returns {Promise} 确认结果
 */
const confirmTradeWithBiometric = async (operation) => {
  try {
    const settings = getSecuritySettings();
    
    // 如果未启用交易生物识别
    if (!settings.useBiometricConfirmation) {
      return Promise.reject({
        status: 'not_enabled',
        message: '未启用交易生物识别'
      });
    }
    
    // 使用指纹或面容识别进行确认
    let preferredType = null;
    if (settings.useFingerprint) {
      preferredType = biometricAuth.BIOMETRIC_TYPES.FINGERPRINT;
    } else if (settings.useFacialRecognition) {
      preferredType = biometricAuth.BIOMETRIC_TYPES.FACIAL;
    }
    
    const message = `请验证身份以确认${operation}`;
    const result = await biometricAuth.verifyBiometric(preferredType, message);
    
    if (result.status === biometricAuth.BIOMETRIC_STATUS.SUCCESS) {
      return {
        status: 'success',
        message: '验证成功',
        type: result.type
      };
    } else {
      return result;
    }
  } catch (error) {
    console.error('交易确认失败', error);
    
    // 根据错误类型提供更具体的信息
    if (error.status === biometricAuth.BIOMETRIC_STATUS.LOCKED_OUT) {
      return {
        status: 'locked_out',
        message: '生物识别已锁定,请使用PIN码确认',
        error
      };
    } else if (error.status === biometricAuth.BIOMETRIC_STATUS.UNAVAILABLE) {
      return {
        status: 'unavailable',
        message: '生物识别暂时不可用,请使用PIN码确认',
        error
      };
    } else {
      return {
        status: 'failed',
        message: error.message || '验证失败',
        error
      };
    }
  }
};

/**
 * 交易确认 - 使用密码
 * @param {String} pinCode 交易密码
 * @returns {Object} 确认结果
 */
const confirmTradeWithPINCode = (pinCode) => {
  if (verifyPINCode(pinCode)) {
    return {
      status: 'success',
      message: '验证成功'
    };
  } else {
    return {
      status: 'failed',
      message: '交易密码错误'
    };
  }
};

/**
 * 锁定应用
 */
const lockApp = () => {
  setAppLocked(true);
};

/**
 * 检查认证会话是否过期
 * 如果会话过期,自动锁定应用
 * @returns {Boolean} 会话是否有效
 */
const checkAuthSession = () => {
  try {
    const sessionData = secureStorage.getSecureData(AUTH_SESSION_KEY);
    if (!sessionData || !sessionData.expiryTime) {
      // 无会话数据,视为过期
      lockApp();
      return false;
    }
    
    const now = new Date().getTime();
    if (now > sessionData.expiryTime) {
      // 会话已过期
      lockApp();
      return false;
    }
    
    // 会话有效,更新过期时间
    sessionData.expiryTime = now + (30 * 60 * 1000); // 再延长30分钟
    secureStorage.setSecureData(AUTH_SESSION_KEY, sessionData);
    return true;
  } catch (e) {
    console.error('检查认证会话失败', e);
    return false;
  }
};

/**
 * 初始化安全服务
 * 应在应用启动时调用
 */
const initSecurityService = async () => {
  console.log('初始化安全服务');
  
  // 迁移旧的PIN码到新格式
  const migrationResult = secureStorage.migrateLegacyPINCode();
  console.log('PIN码迁移结果:', migrationResult);
  
  // 检查是否存在强制锁定标志
  try {
    const forceLock = uni.getStorageSync('forceAppLock');
    if (forceLock === 'true') {
      console.log('检测到强制锁定标志,应用将被锁定');
      // 移除标志
      uni.removeStorageSync('forceAppLock');
      // 强制锁定应用
      setAppLocked(true);
    }
  } catch (e) {
    console.error('检查强制锁定标志失败', e);
  }
  
  // 检查生物识别支持
  const biometricSupport = await biometricAuth.checkBiometricSupport();
  
  // 获取安全设置
  const settings = getSecuritySettings();
  
  // 更新生物识别可用性
  if (!biometricSupport.fingerprintSupported) {
    settings.useFingerprint = false;
  }
  if (!biometricSupport.facialSupported) {
    settings.useFacialRecognition = false;
  }
  if (!biometricSupport.fingerprintSupported && !biometricSupport.facialSupported) {
    settings.useBiometricConfirmation = false;
  }
  
  // 保存更新后的设置
  saveSecuritySettings(settings);
  
  // 设置默认锁定状态
  if ((settings.usePINCode || settings.useFingerprint || settings.useFacialRecognition) &&
      !secureStorage.getSecureData(APP_LOCK_KEY)) {
    setAppLocked(true);
  }
  
  return {
    biometricSupport,
    settings
  };
};

export default {
  LOCK_STATUS,
  getSecuritySettings,
  saveSecuritySettings,
  clearSettingsCache,
  isAppLocked,
  setAppLocked,
  verifyPINCode,
  setPINCode,
  unlockWithBiometric,
  unlockWithPINCode,
  confirmTradeWithBiometric,
  confirmTradeWithPINCode,
  lockApp,
  checkAuthSession,
  initSecurityService
}; 
