/**
 * 生物识别认证工具
 * 提供指纹识别和面容识别功能
 */

// 生物识别类型
const BIOMETRIC_TYPES = {
  FINGERPRINT: 'fingerprint',
  FACIAL: 'facial',
  NONE: 'none'
};

// 生物识别状态
const BIOMETRIC_STATUS = {
  SUCCESS: 'success',
  FAILED: 'failed',
  CANCELED: 'canceled',
  NOT_SUPPORTED: 'not_supported',
  NOT_ENROLLED: 'not_enrolled',
  LOCKED_OUT: 'locked_out',     // 新增:设备因多次失败而锁定
  UNAVAILABLE: 'unavailable'    // 新增:设备暂时不可用
};

/**
 * 检查设备支持的生物识别类型
 * @returns {Promise} 返回支持的生物识别类型 {fingerprintSupported, facialSupported, type}
 */
const checkBiometricSupport = () => {
  return new Promise((resolve) => {
    let result = {
      fingerprintSupported: false,
      facialSupported: false,
      type: BIOMETRIC_TYPES.NONE
    };
    
    // 检查是否支持指纹识别
    try {
      // 检查是否在支持plus的环境中
      if (typeof plus === 'undefined') {
        console.log('当前环境不支持plus对象，跳过生物识别检查');
        resolve(result);
        return;
      }

      plus.fingerprint.isSupport((res) => {
        result.fingerprintSupported = true;
        result.type = BIOMETRIC_TYPES.FINGERPRINT;
        
        // 检查Face ID支持
        detectFacialSupport().then(facialSupported => {
          if (facialSupported) {
            result.facialSupported = true;
            // 如果同时支持指纹和面容识别,优先使用面容识别
            result.type = BIOMETRIC_TYPES.FACIAL;
          }
          resolve(result);
        }).catch(err => {
          console.error('检查面容识别失败', err);
          resolve(result);
        });
      }, (err) => {
        console.log('指纹识别不支持', err);
        
        // 检查是否支持面容识别
        detectFacialSupport().then(facialSupported => {
          if (facialSupported) {
            result.facialSupported = true;
            result.type = BIOMETRIC_TYPES.FACIAL;
          }
          resolve(result);
        }).catch(err => {
          console.error('检查面容识别失败', err);
          resolve(result);
        });
      });
    } catch (e) {
      console.error('检查生物识别功能失败', e);
      
      // 尝试检查面容识别
      detectFacialSupport().then(facialSupported => {
        if (facialSupported) {
          result.facialSupported = true;
          result.type = BIOMETRIC_TYPES.FACIAL;
        }
        resolve(result);
      }).catch(err => {
        console.error('检查面容识别失败', err);
        resolve(result);
      });
    }
  });
};

/**
 * 检测设备是否支持面容识别
 * 使用更准确的方法检测Face ID或其他面容识别功能
 * @returns {Promise<boolean>} 返回是否支持面容识别
 */
const detectFacialSupport = () => {
  return new Promise((resolve, reject) => {
    try {
      const systemInfo = uni.getSystemInfoSync();
      
      // 检查iOS设备
      if (systemInfo.platform === 'ios') {
        // 获取设备型号
        const model = systemInfo.model;
        const osVersion = parseInt(systemInfo.system.replace(/^iOS /, ''));
        
        // 支持FaceID的设备:iPhone X及更新型号,iOS 11+
        const isFaceIDCapable = (
          // iPhone X, XR, XS, XS Max
          /iPhone X/.test(model) || 
          // iPhone 11系列
          /iPhone 1[1-9]/.test(model) || 
          // iPhone 12系列及以上
          /iPhone 1[2-9]/.test(model) ||
          // 新型iPad Pro (有Face ID)
          (/iPad Pro/.test(model) && parseInt(model.split('inch')[0].trim()) >= 11)
        );
        
        // iOS 11及以上版本支持Face ID API
        if (isFaceIDCapable && osVersion >= 11) {
          // 在真实实现中,可以尝试调用相关API进行检测
          resolve(true);
        } else {
          resolve(false);
        }
      } 
      // 检查Android设备
      else if (systemInfo.platform === 'android') {
        // 安卓设备面容识别检测
        // 由于安卓设备多样性,很难通过型号确定
        // 在此处,我们可以尝试调用相关API进行检测
        // 此处为模拟实现,实际应用中应查询设备实际能力
        
        // 检查Android版本 - 大多数面部识别需要Android 9+
        const osVersion = parseInt(systemInfo.system.replace(/^Android /, ''));
        if (osVersion >= 9) {
          // 可以通过插件调用原生API检查面部识别能力
          // 由于我们没有实际插件,这里暂时返回false
          // 实际应用中应替换为真实的能力检查
          resolve(false);
        } else {
          resolve(false);
        }
      } else {
        resolve(false);
      }
    } catch (error) {
      console.error('面容识别检测出错', error);
      reject(error);
    }
  });
};

/**
 * 验证指纹
 * @param {String} message 提示消息
 * @returns {Promise} 验证结果
 */
const verifyFingerprint = (message = '请验证指纹') => {
  return new Promise((resolve, reject) => {
    try {
      // 检查是否在支持plus的环境中
      if (typeof plus === 'undefined') {
        reject({
          status: BIOMETRIC_STATUS.UNAVAILABLE,
          message: '当前环境不支持指纹识别'
        });
        return;
      }

      plus.fingerprint.authenticate(() => {
        // 验证成功
        resolve({
          status: BIOMETRIC_STATUS.SUCCESS,
          type: BIOMETRIC_TYPES.FINGERPRINT
        });
      }, (err) => {
        if (err.code === -1) {
          // 用户取消
          resolve({
            status: BIOMETRIC_STATUS.CANCELED,
            type: BIOMETRIC_TYPES.FINGERPRINT,
            message: '验证已取消',
            error: err
          });
        } else if (err.code === 10) {
          // 调用太频繁等临时错误
          reject({
            status: BIOMETRIC_STATUS.UNAVAILABLE,
            type: BIOMETRIC_TYPES.FINGERPRINT,
            message: '指纹识别暂时不可用,请稍后再试',
            error: err
          });
        } else if (err.code === 11) {
          // 多次失败导致锁定
          reject({
            status: BIOMETRIC_STATUS.LOCKED_OUT,
            type: BIOMETRIC_TYPES.FINGERPRINT,
            message: '指纹验证失败次数过多,已被锁定',
            error: err
          });
        } else {
          // 其他错误
          reject({
            status: BIOMETRIC_STATUS.FAILED,
            type: BIOMETRIC_TYPES.FINGERPRINT,
            message: '指纹验证失败',
            error: err
          });
        }
      }, {
        message: message
      });
    } catch (e) {
      reject({
        status: BIOMETRIC_STATUS.FAILED,
        type: BIOMETRIC_TYPES.FINGERPRINT,
        message: '指纹验证功能错误',
        error: e
      });
    }
  });
};

/**
 * 验证面容
 * 注:此实现需要通过插件调用平台特定API
 * 目前模拟实现,实际应用需集成原生插件
 * 
 * @param {String} message 提示消息
 * @returns {Promise} 验证结果
 */
const verifyFacial = (message = '请面向屏幕进行验证') => {
  return new Promise((resolve, reject) => {
    try {
      const systemInfo = uni.getSystemInfoSync();
      const isIOS = systemInfo.platform === 'ios';
      
      // 显示验证提示
      uni.showLoading({
        title: message
      });

      // 这部分代码在实际应用中应替换为调用原生插件的代码
      if (isIOS) {
        // 在iOS上通过插件调用FaceID
        // 目前使用模拟实现,实际应替换为插件调用
        setTimeout(() => {
          uni.hideLoading();
          
          // 模拟FaceID成功
          resolve({
            status: BIOMETRIC_STATUS.SUCCESS,
            type: BIOMETRIC_TYPES.FACIAL
          });
          
          /* 实际调用示例:
          nativeFaceIDPlugin.authenticate({
            message: message,
            success: () => {
              resolve({
                status: BIOMETRIC_STATUS.SUCCESS,
                type: BIOMETRIC_TYPES.FACIAL
              });
            },
            fail: (error) => {
              // 处理不同的错误类型
              // 用户取消
              if (error.code === 'user_cancel') {
                resolve({
                  status: BIOMETRIC_STATUS.CANCELED,
                  type: BIOMETRIC_TYPES.FACIAL,
                  message: '验证已取消',
                  error: error
                });
              } 
              // 设备锁定
              else if (error.code === 'lockout') {
                reject({
                  status: BIOMETRIC_STATUS.LOCKED_OUT,
                  type: BIOMETRIC_TYPES.FACIAL,
                  message: '面容验证失败次数过多,已被锁定',
                  error: error
                });
              }
              // 其他错误
              else {
                reject({
                  status: BIOMETRIC_STATUS.FAILED,
                  type: BIOMETRIC_TYPES.FACIAL,
                  message: '面容验证失败',
                  error: error
                });
              }
            }
          });
          */
          
        }, 1500);
      } 
      // Android设备
      else {
        // 在Android上通过插件调用面部识别
        // 同样使用模拟实现,实际应替换为插件调用
        setTimeout(() => {
          uni.hideLoading();
          
          // 模拟面部识别成功
          resolve({
            status: BIOMETRIC_STATUS.SUCCESS,
            type: BIOMETRIC_TYPES.FACIAL
          });
          
          /* 实际调用示例:
          nativeBiometricPlugin.authenticateFace({
            title: '面容验证',
            description: message,
            success: () => {
              resolve({
                status: BIOMETRIC_STATUS.SUCCESS,
                type: BIOMETRIC_TYPES.FACIAL
              });
            },
            fail: (error) => {
              // 处理各种错误
              if (error.code === 'USER_CANCELED') {
                resolve({
                  status: BIOMETRIC_STATUS.CANCELED,
                  type: BIOMETRIC_TYPES.FACIAL,
                  message: '验证已取消',
                  error: error
                });
              } else {
                reject({
                  status: BIOMETRIC_STATUS.FAILED,
                  type: BIOMETRIC_TYPES.FACIAL,
                  message: '面容验证失败: ' + error.message,
                  error: error
                });
              }
            }
          });
          */
        }, 1500);
      }
    } catch (e) {
      uni.hideLoading();
      reject({
        status: BIOMETRIC_STATUS.FAILED,
        type: BIOMETRIC_TYPES.FACIAL,
        message: '面容验证功能错误',
        error: e
      });
    }
  });
};

/**
 * 根据设备支持情况验证生物识别
 * @param {String} preferredType 优先使用的生物识别类型
 * @param {String} message 提示消息
 * @returns {Promise} 验证结果
 */
const verifyBiometric = async (preferredType = null, message = '请进行生物识别验证') => {
  try {
    // 检查设备支持
    const support = await checkBiometricSupport();
    
    // 确定使用的生物识别类型
    let type = preferredType || support.type;
    
    // 如果指定的类型不可用,使用可用的类型
    if (type === BIOMETRIC_TYPES.FINGERPRINT && !support.fingerprintSupported) {
      type = support.facialSupported ? BIOMETRIC_TYPES.FACIAL : BIOMETRIC_TYPES.NONE;
    } else if (type === BIOMETRIC_TYPES.FACIAL && !support.facialSupported) {
      type = support.fingerprintSupported ? BIOMETRIC_TYPES.FINGERPRINT : BIOMETRIC_TYPES.NONE;
    }
    
    // 如果没有可用的生物识别方式
    if (type === BIOMETRIC_TYPES.NONE) {
      return Promise.reject({
        status: BIOMETRIC_STATUS.NOT_SUPPORTED,
        type: BIOMETRIC_TYPES.NONE,
        message: '设备不支持生物识别'
      });
    }
    
    // 根据类型调用相应的验证方法
    if (type === BIOMETRIC_TYPES.FINGERPRINT) {
      return verifyFingerprint(message);
    } else if (type === BIOMETRIC_TYPES.FACIAL) {
      return verifyFacial(message);
    }
  } catch (e) {
    return Promise.reject({
      status: BIOMETRIC_STATUS.FAILED,
      type: BIOMETRIC_TYPES.NONE,
      message: '生物识别出错',
      error: e
    });
  }
};

/**
 * 检查是否支持安全存储API
 * @returns {Boolean} 是否支持安全存储
 */
const isSecureStorageAvailable = () => {
  try {
    // 尝试检测安全存储API是否可用
    // 实际应用中,应根据平台特性进行检测
    return (typeof plus !== 'undefined' && 
            typeof plus.os !== 'undefined' && 
            typeof uni.getStorageInfoSync === 'function');
  } catch (e) {
    console.error('检查安全存储失败', e);
    return false;
  }
};

export default {
  BIOMETRIC_TYPES,
  BIOMETRIC_STATUS,
  checkBiometricSupport,
  verifyFingerprint,
  verifyFacial,
  verifyBiometric,
  isSecureStorageAvailable
}; 
