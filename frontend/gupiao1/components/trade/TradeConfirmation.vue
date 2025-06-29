<template>
  <view class="trade-confirmation">
    <!-- 交易确认弹窗 -->
    <uni-popup ref="confirmPopup" type="dialog">
      <uni-popup-dialog
        :title="tradeAction === 'buy' ? '买入确认' : '卖出确认'"
        :content="generateConfirmContent()"
        :before-close="true"
        @confirm="handleConfirm"
        @close="handleCancel"
        :confirmText="tradeAction === 'buy' ? '买入' : '卖出'"
        :cancelText="'取消'"
        :confirmColor="tradeAction === 'buy' ? '#ff5252' : '#4caf50'"
      >
      </uni-popup-dialog>
    </uni-popup>
    
    <!-- PIN码验证弹窗 -->
    <uni-popup ref="pinPopup" type="dialog">
      <uni-popup-dialog
        title="输入交易密码"
        :before-close="true"
        @confirm="confirmPin"
        @close="cancelPin"
        confirmText="确认"
        cancelText="取消"
      >
        <view class="pin-code-form">
          <input 
            class="pin-input"
            type="password" 
            placeholder="请输入6位数字密码" 
            maxlength="6"
            v-model="pinCode"
            password
          />
        </view>
      </uni-popup-dialog>
    </uni-popup>
    
    <!-- 生物识别提示 -->
    <uni-popup ref="biometricPopup" type="message">
      <text class="biometric-popup-text">请通过生物识别确认交易</text>
    </uni-popup>
  </view>
</template>

<script>
import authService from '../../services/auth-service.js';
import uniPopup from '@dcloudio/uni-ui/lib/uni-popup/uni-popup.vue';
import uniPopupDialog from '@dcloudio/uni-ui/lib/uni-popup-dialog/uni-popup-dialog.vue';

export default {
  name: 'TradeConfirmation',
  components: {
    uniPopup,
    uniPopupDialog
  },
  props: {
    // 交易类型: 'buy' 或 'sell'
    tradeAction: {
      type: String,
      required: true
    },
    // 交易股票信息
    stockInfo: {
      type: Object,
      required: false,
      default: () => ({
        name: '未选择',
        code: '',
        price: 0
      })
    },
    // 交易相关数据
    tradeData: {
      type: Object,
      required: true,
      default: () => ({})
    }
  },
  data() {
    return {
      pinCode: '',
      isBiometricVerifying: false
    }
  },
  methods: {
    /**
     * 打开交易确认弹窗
     */
    open() {
      this.$refs.confirmPopup.open();
    },
    
    /**
     * 关闭交易确认弹窗
     */
    close() {
      this.$refs.confirmPopup.close();
    },
    
    /**
     * 生成确认弹窗内容
     */
    generateConfirmContent() {
      if (!this.stockInfo) {
        return '请先选择交易股票';
      }
      
      const { price, quantity } = this.tradeData;
      const totalAmount = (price * quantity).toFixed(2);
      
      // 构建确认内容
      return `${this.stockInfo.name || '未选择'} (${this.stockInfo.code || ''})\n` + 
             `价格: ¥${price || 0}\n` + 
             `数量: ${quantity || 0}股\n` + 
             `总金额: ¥${totalAmount}`;
    },
    
    /**
     * 处理确认按钮点击
     */
    handleConfirm() {
      // 获取安全设置
      const settings = authService.getSecuritySettings();
      
      // 如果启用了生物识别确认,先进行生物识别
      if (settings.useBiometricConfirmation && 
          (settings.useFingerprint || settings.useFacialRecognition)) {
        this.verifyBiometric();
      } 
      // 如果启用了交易密码验证,要求输入密码
      else if (settings.useTradePasswordVerification && settings.hasPINCode) {
        this.promptForPin();
      }
      // 如果没有启用任何安全验证,直接执行交易
      else {
        this.executeTradeAction();
      }
      
      return false; // 阻止弹窗自动关闭
    },
    
    /**
     * 处理取消按钮点击
     */
    handleCancel() {
      this.$emit('cancel');
    },
    
    /**
     * 执行交易操作
     */
    executeTradeAction() {
      this.close(); // 关闭确认弹窗
      this.$emit('confirm', {
        action: this.tradeAction,
        stockInfo: this.stockInfo,
        tradeData: this.tradeData
      });
    },
    
    /**
     * 验证生物识别
     */
    verifyBiometric() {
      if (this.isBiometricVerifying) return;
      
      this.isBiometricVerifying = true;
      this.$refs.biometricPopup.open();
      
      const operation = this.tradeAction === 'buy' ? '买入' : '卖出';
      
      authService.confirmTradeWithBiometric(operation)
        .then(result => {
          this.isBiometricVerifying = false;
          this.$refs.biometricPopup.close();
          
          if (result.status === 'success') {
            this.executeTradeAction();
          } else if (result.status === 'canceled') {
            // 用户取消生物识别,询问是否使用密码
            const settings = authService.getSecuritySettings();
            if (settings.useTradePasswordVerification && settings.hasPINCode) {
              this.promptForPin();
            }
          } else {
            // 生物识别失败
            uni.showToast({
              title: '生物识别失败',
              icon: 'none'
            });
          }
        })
        .catch(error => {
          this.isBiometricVerifying = false;
          this.$refs.biometricPopup.close();
          
          console.error('生物识别错误', error);
          
          // 尝试使用PIN码作为备选
          const settings = authService.getSecuritySettings();
          if (settings.useTradePasswordVerification && settings.hasPINCode) {
            this.promptForPin();
          } else {
            uni.showToast({
              title: '验证失败',
              icon: 'none'
            });
          }
        });
    },
    
    /**
     * 提示输入PIN码
     */
    promptForPin() {
      this.pinCode = '';
      this.$refs.pinPopup.open();
    },
    
    /**
     * 确认PIN码
     */
    confirmPin() {
      if (this.pinCode.length !== 6) {
        uni.showToast({
          title: '请输入6位数字密码',
          icon: 'none'
        });
        return false; // 阻止弹窗关闭
      }
      
      const result = authService.confirmTradeWithPINCode(this.pinCode);
      
      if (result.status === 'success') {
        this.executeTradeAction();
        return true; // 允许弹窗关闭
      } else {
        uni.showToast({
          title: '密码错误',
          icon: 'none'
        });
        this.pinCode = '';
        return false; // 阻止弹窗关闭
      }
    },
    
    /**
     * 取消PIN码输入
     */
    cancelPin() {
      this.pinCode = '';
      this.$emit('cancel');
    }
  }
}
</script>

<style>
.pin-code-form {
  padding: 20rpx 0;
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

.biometric-popup-text {
  font-size: 28rpx;
  color: #333;
  text-align: center;
  padding: 30rpx;
}
</style> 
