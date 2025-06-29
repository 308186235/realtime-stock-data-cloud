<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <h1>策略回测系统</h1>
        <p>请登录以继续使用</p>
      </div>
      
      <div class="login-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input 
            type="text" 
            id="username" 
            v-model="username"
            placeholder="请输入用户名"
            @keyup.enter="login"
          >
        </div>
        
        <div class="form-group">
          <label for="password">密码</label>
          <input 
            type="password" 
            id="password" 
            v-model="password"
            placeholder="请输入密码"
            @keyup.enter="login"
          >
        </div>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <button @click="login" :disabled="isLoggingIn" class="login-btn">
          {{ isLoggingIn ? '登录中...' : '登录' }}
        </button>
      </div>
      
      <div class="login-footer">
        <p>默认账号: admin | 密码: admin123</p>
        <p>© {{ new Date().getFullYear() }} 股票交易策略回测系统</p>
      </div>
    </div>
  </div>
</template>

<script>
import { authService } from '../../services/auth-service.js';

export default {
  data() {
    return {
      username: '',
      password: '',
      error: null,
      isLoggingIn: false
    };
  },
  mounted() {
    // 检查用户是否已登录,如果已登录则跳转到主页
    if (authService.isAuthenticated()) {
      this.$router.push('/backtest');
    }
  },
  methods: {
    async login() {
      // 输入验证
      if (!this.username.trim()) {
        this.error = '请输入用户名';
        return;
      }
      
      if (!this.password) {
        this.error = '请输入密码';
        return;
      }
      
      // 执行登录
      this.isLoggingIn = true;
      this.error = null;
      
      try {
        await authService.login(this.username, this.password);
        
        // 登录成功,跳转到回测页面
        this.$router.push('/backtest');
      } catch (error) {
        console.error('登录失败:', error);
        this.error = error.message || '登录失败,请检查用户名和密码';
      } finally {
        this.isLoggingIn = false;
      }
    }
  }
};
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.login-container {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  padding: 30px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  margin: 0;
  color: #333;
  font-size: 24px;
}

.login-header p {
  color: #666;
  margin-top: 5px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 5px;
  color: #555;
  font-weight: 500;
}

input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

input:focus {
  border-color: #4caf50;
  outline: none;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.3s;
}

.login-btn:hover {
  background: #43a047;
}

.login-btn:disabled {
  background: #9e9e9e;
  cursor: not-allowed;
}

.error-message {
  background: #ffebee;
  color: #c62828;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  font-size: 14px;
}

.login-footer {
  margin-top: 30px;
  text-align: center;
  font-size: 12px;
  color: #777;
}

.login-footer p {
  margin: 5px 0;
}
</style> 
