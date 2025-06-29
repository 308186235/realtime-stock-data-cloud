/**
 * 安全存储工具
 * 提供PIN码和敏感数据的加密存储服务
 */

// 简单的加盐加密函数 - 改为更可靠的实现
const encrypt = (data, salt = '') => {
  try {
    console.log('安全存储: 开始加密数据');
    
    // 确保数据是字符串
    if (typeof data !== 'string') {
      data = JSON.stringify(data);
    }

    // 使用一个简单但在移动环境中更可靠的加密方法
    const key = salt + 'trade_security_key_2023';
    
    // 简单的XOR加密
    let encryptedChars = [];
    for (let i = 0; i < data.length; i++) {
      const keyChar = key.charCodeAt(i % key.length);
      const dataChar = data.charCodeAt(i);
      encryptedChars.push(String.fromCharCode(dataChar ^ keyChar));
    }
    
    const encryptedString = encryptedChars.join('');
    
    // 使用URI编码替代Base64 - 更可靠
    const result = encodeURIComponent(encryptedString);
    console.log('安全存储: 加密完成');
    return result;
  } catch (e) {
    console.error('安全存储: 加密失败', e);
    return null;
  }
};

// 解密函数 - 匹配新的加密实现
const decrypt = (encryptedData, salt = '') => {
  try {
    // 使用URI解码
    const encryptedString = decodeURIComponent(encryptedData);
    
    const key = salt + 'trade_security_key_2023';
    
    // XOR解密
    let decryptedChars = [];
    for (let i = 0; i < encryptedString.length; i++) {
      const keyChar = key.charCodeAt(i % key.length);
      const encryptedChar = encryptedString.charCodeAt(i);
      decryptedChars.push(String.fromCharCode(encryptedChar ^ keyChar));
    }
    
    return decryptedChars.join('');
  } catch (e) {
    console.error('安全存储: 解密失败', e);
    return null;
  }
};

// 获取设备唯一标识作为加密盐值
const getDeviceId = () => {
  try {
    // 在实际应用中,应该使用设备的唯一标识
    // 这里简单使用设备信息的组合
    const systemInfo = uni.getSystemInfoSync();
    const deviceInfo = [
      systemInfo.brand,
      systemInfo.model,
      systemInfo.system,
      systemInfo.platform
    ].join('_');
    
    // 简单哈希处理
    let hash = 0;
    for (let i = 0; i < deviceInfo.length; i++) {
      const char = deviceInfo.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // 转为32位整数
    }
    
    return hash.toString(16);
  } catch (e) {
    console.error('获取设备ID失败', e);
    return 'default_salt';
  }
};

/**
 * 安全存储数据
 * @param {String} key 存储键名
 * @param {*} data 要存储的数据
 * @param {Boolean} useDeviceBinding 是否使用设备绑定(增加安全性,但数据将无法在设备间迁移)
 * @returns {Boolean} 是否成功存储
 */
const setSecureData = (key, data, useDeviceBinding = false) => {
  try {
    console.log(`安全存储: 开始存储数据 ${key}`, typeof data);
    
    // 获取加密盐
    const salt = useDeviceBinding ? getDeviceId() : '';
    if (useDeviceBinding) {
      console.log('安全存储: 使用设备绑定');
    }
    
    // 加密数据
    console.log('安全存储: 准备加密数据');
    const encryptedData = encrypt(data, salt);
    
    if (!encryptedData) {
      console.error('安全存储: 加密失败');
      return false;
    }
    
    // 存储加密数据
    console.log('安全存储: 写入存储', key);
    try {
      uni.setStorageSync(key, encryptedData);
      
      // 验证存储成功
      const verification = uni.getStorageSync(key);
      if (!verification) {
        console.error('安全存储: 存储后立即验证失败,数据不存在');
        return false;
      }
      
      // 如果使用了设备绑定,记录此信息
      if (useDeviceBinding) {
        try {
          console.log('安全存储: 记录设备绑定信息');
          const bindingInfo = uni.getStorageSync('secure_storage_binding') || '{}';
          let bindingMap;
          
          try {
            bindingMap = JSON.parse(bindingInfo);
          } catch (parseError) {
            console.error('安全存储: 绑定信息解析失败,重置');
            bindingMap = {};
          }
          
          bindingMap[key] = true;
          uni.setStorageSync('secure_storage_binding', JSON.stringify(bindingMap));
        } catch (bindingError) {
          console.error('安全存储: 记录绑定信息失败', bindingError);
          // 继续执行,因为主数据已经存储成功
        }
      }
      
      console.log('安全存储: 数据存储成功', key);
      return true;
    } catch (storageError) {
      console.error('安全存储: 存储写入失败', storageError);
      return false;
    }
  } catch (e) {
    console.error('安全存储失败', e);
    return false;
  }
};

/**
 * 获取安全存储的数据
 * @param {String} key 存储键名
 * @param {*} defaultValue 默认值(如果获取失败)
 * @returns {*} 解密后的数据或默认值
 */
const getSecureData = (key, defaultValue = null) => {
  try {
    const encryptedData = uni.getStorageSync(key);
    if (!encryptedData) {
      return defaultValue;
    }
    
    // 检查是否为设备绑定数据
    const bindingInfo = uni.getStorageSync('secure_storage_binding') || '{}';
    const bindingMap = JSON.parse(bindingInfo);
    const useDeviceBinding = bindingMap[key] || false;
    
    // 根据是否设备绑定使用对应的盐值
    const salt = useDeviceBinding ? getDeviceId() : '';
    const decryptedData = decrypt(encryptedData, salt);
    
    if (decryptedData) {
      try {
        // 尝试解析为JSON
        return JSON.parse(decryptedData);
      } catch {
        // 如果不是JSON格式,直接返回解密后的字符串
        return decryptedData;
      }
    }
    
    return defaultValue;
  } catch (e) {
    console.error('获取安全存储数据失败', e);
    return defaultValue;
  }
};

/**
 * 移除安全存储的数据
 * @param {String} key 存储键名
 * @returns {Boolean} 是否成功移除
 */
const removeSecureData = (key) => {
  try {
    uni.removeStorageSync(key);
    
    // 同时移除绑定信息
    const bindingInfo = uni.getStorageSync('secure_storage_binding') || '{}';
    const bindingMap = JSON.parse(bindingInfo);
    if (bindingMap[key]) {
      delete bindingMap[key];
      uni.setStorageSync('secure_storage_binding', JSON.stringify(bindingMap));
    }
    
    return true;
  } catch (e) {
    console.error('移除安全存储数据失败', e);
    return false;
  }
};

/**
 * 安全存储 PIN 码
 * PIN 码始终使用设备绑定以提高安全性
 * @param {String} pinCode PIN码
 * @returns {Boolean} 是否成功存储
 */
const storePINCode = (pinCode) => {
  try {
    console.log('安全存储: 存储PIN码');
    
    // 检查输入
    if (!pinCode) {
      console.error('安全存储: PIN码为空');
      return false;
    }
    
    // 先尝试清除旧的键,确保不会有干扰
    removeSecureData('tradePINCode');
    
    // 使用通用的安全存储方法,启用设备绑定
    const success = setSecureData('appPINCode', pinCode, true);
    
    if (success) {
      console.log('安全存储: PIN码存储成功');
      return true;
    } else {
      console.error('安全存储: PIN码存储失败');
      
      // 尝试直接存储(不使用加密)进行调试
      try {
        // 临时直接存储以验证存储系统是否工作
        uni.setStorageSync('appPINCode_temp', pinCode);
        console.log('安全存储: 临时直接存储成功,问题可能在加密环节');
      } catch (e) {
        console.error('安全存储: 临时直接存储也失败,存储系统可能有问题', e);
      }
      
      return false;
    }
  } catch (e) {
    console.error('安全存储: PIN码存储异常', e);
    return false;
  }
};

/**
 * 验证 PIN 码
 * @param {String} inputPinCode 用户输入的PIN码
 * @returns {Boolean} 验证是否成功
 */
const verifyPINCode = (inputPinCode) => {
  try {
    console.log('安全存储: 验证PIN码');
    
    // 先检查新的appPINCode
    const encryptedData = uni.getStorageSync('appPINCode');
    if (encryptedData) {
      const storedPinCode = decrypt(encryptedData, getDeviceId());
      console.log('安全存储: 找到PIN码,开始验证');
      const result = storedPinCode === inputPinCode;
      console.log('安全存储: 验证结果:', result);
      return result;
    }
    
    // 如果没有找到,则检查旧的tradePINCode
    const oldEncryptedData = uni.getStorageSync('tradePINCode');
    if (oldEncryptedData) {
      console.log('安全存储: 找到旧的PIN码,开始验证');
      const oldPinCode = decrypt(oldEncryptedData, getDeviceId());
      const result = oldPinCode === inputPinCode;
      
      // 如果旧密码验证成功,自动迁移到新键
      if (result) {
        console.log('安全存储: 旧密码验证成功,自动迁移');
        storePINCode(inputPinCode);
      }
      
      return result;
    }
    
    // 如果两种加密PIN码都没找到,检查直接存储的PIN码
    const directPinCode = uni.getStorageSync('direct_pin_code');
    if (directPinCode) {
      console.log('安全存储: 找到直接存储的PIN码,开始验证');
      const result = directPinCode === inputPinCode;
      console.log('安全存储: 直接PIN码验证结果:', result);
      
      // 如果验证成功,尝试迁移到安全存储
      if (result) {
        console.log('安全存储: 尝试迁移直接存储的PIN码到安全存储');
        storePINCode(inputPinCode);
      }
      
      return result;
    }
    
    console.log('安全存储: 未找到任何PIN码');
    return false;
  } catch (e) {
    console.error('安全存储: PIN码验证异常', e);
    return false;
  }
};

/**
 * 检查是否已设置 PIN 码
 * @returns {Boolean} 是否已设置PIN码
 */
const hasPINCode = () => {
  try {
    console.log('安全存储: 检查是否设置了PIN码');
    
    // 检查新的appPINCode
    try {
      const encryptedData = uni.getStorageSync('appPINCode');
      if (encryptedData) {
        console.log('安全存储: 找到PIN码');
        return true;
      }
    } catch (e) {
      console.error('安全存储: 检查appPINCode失败', e);
    }
    
    // 检查旧的tradePINCode
    try {
      const oldEncryptedData = uni.getStorageSync('tradePINCode');
      if (oldEncryptedData) {
        console.log('安全存储: 找到旧的PIN码');
        return true;
      }
    } catch (e) {
      console.error('安全存储: 检查tradePINCode失败', e);
    }
    
    // 检查直接存储的PIN码
    try {
      const directPinCode = uni.getStorageSync('direct_pin_code');
      if (directPinCode) {
        console.log('安全存储: 找到直接存储的PIN码');
        return true;
      }
    } catch (e) {
      console.error('安全存储: 检查direct_pin_code失败', e);
    }
    
    console.log('安全存储: 未找到任何PIN码');
    return false;
  } catch (e) {
    console.error('安全存储: 检查PIN码异常', e);
    return false;
  }
};

/**
 * 迁移旧的PIN码到新格式
 * 这个函数会检查是否存在旧的PIN码,如果存在则迁移到新格式并清除旧数据
 * @returns {Boolean} 是否迁移成功或不需要迁移
 */
const migrateLegacyPINCode = () => {
  try {
    console.log('安全存储: 开始迁移旧PIN码');
    
    // 检查是否已有新格式的PIN码
    const newEncryptedData = uni.getStorageSync('appPINCode');
    if (newEncryptedData) {
      console.log('安全存储: 已有新PIN码,无需迁移');
      
      // 可以安全删除旧的PIN码
      uni.removeStorageSync('tradePINCode');
      return true;
    }
    
    // 检查是否有旧格式的PIN码
    const oldEncryptedData = uni.getStorageSync('tradePINCode');
    if (!oldEncryptedData) {
      console.log('安全存储: 没有旧PIN码,无需迁移');
      return true;
    }
    
    // 解密旧PIN码
    const oldPinCode = decrypt(oldEncryptedData, getDeviceId());
    if (!oldPinCode) {
      console.log('安全存储: 旧PIN码解密失败,删除损坏数据');
      uni.removeStorageSync('tradePINCode');
      return false;
    }
    
    console.log('安全存储: 旧PIN码解密成功,准备迁移');
    
    // 使用新格式存储PIN码
    const success = storePINCode(oldPinCode);
    if (success) {
      console.log('安全存储: 迁移成功,删除旧PIN码');
      uni.removeStorageSync('tradePINCode');
      return true;
    } else {
      console.error('安全存储: 迁移失败');
      return false;
    }
  } catch (e) {
    console.error('安全存储: 迁移PIN码异常', e);
    return false;
  }
};

// 导出函数
export default {
  setSecureData,
  getSecureData,
  removeSecureData,
  storePINCode,
  verifyPINCode,
  hasPINCode,
  migrateLegacyPINCode
}; 
