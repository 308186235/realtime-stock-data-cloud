/**
 * Supabase前端配置
 */
import { createClient } from '@supabase/supabase-js'

// Supabase配置
const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || 'https://zzukfxwavknskqcepsjb.supabase.co'
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw'

// 创建Supabase客户端
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  },
  realtime: {
    params: {
      eventsPerSecond: 10
    }
  }
})

// 数据库操作工具类
export class SupabaseService {
  constructor() {
    this.client = supabase
  }

  // 用户认证相关
  async signUp(email, password, userData = {}) {
    try {
      const { data, error } = await this.client.auth.signUp({
        email,
        password,
        options: {
          data: userData
        }
      })
      
      if (error) throw error
      return data
    } catch (error) {
      console.error('注册失败:', error.message)
      throw error
    }
  }

  async signIn(email, password) {
    try {
      const { data, error } = await this.client.auth.signInWithPassword({
        email,
        password
      })
      
      if (error) throw error
      return data
    } catch (error) {
      console.error('登录失败:', error.message)
      throw error
    }
  }

  async signOut() {
    try {
      const { error } = await this.client.auth.signOut()
      if (error) throw error
    } catch (error) {
      console.error('登出失败:', error.message)
      throw error
    }
  }

  async getCurrentUser() {
    try {
      const { data: { user } } = await this.client.auth.getUser()
      return user
    } catch (error) {
      console.error('获取用户信息失败:', error.message)
      return null
    }
  }

  // 数据库操作
  async createRecord(table, data) {
    try {
      const { data: result, error } = await this.client
        .from(table)
        .insert(data)
        .select()
        .single()
      
      if (error) throw error
      return result
    } catch (error) {
      console.error(`创建${table}记录失败:`, error.message)
      throw error
    }
  }

  async getRecords(table, filters = {}, options = {}) {
    try {
      let query = this.client.from(table).select('*')
      
      // 应用过滤条件
      Object.entries(filters).forEach(([key, value]) => {
        query = query.eq(key, value)
      })
      
      // 应用排序和限制
      if (options.orderBy) {
        query = query.order(options.orderBy, { ascending: options.ascending !== false })
      }
      
      if (options.limit) {
        query = query.limit(options.limit)
      }
      
      const { data, error } = await query
      
      if (error) throw error
      return data
    } catch (error) {
      console.error(`查询${table}记录失败:`, error.message)
      throw error
    }
  }

  async updateRecord(table, id, data) {
    try {
      const { data: result, error } = await this.client
        .from(table)
        .update(data)
        .eq('id', id)
        .select()
        .single()
      
      if (error) throw error
      return result
    } catch (error) {
      console.error(`更新${table}记录失败:`, error.message)
      throw error
    }
  }

  async deleteRecord(table, id) {
    try {
      const { error } = await this.client
        .from(table)
        .delete()
        .eq('id', id)
      
      if (error) throw error
      return true
    } catch (error) {
      console.error(`删除${table}记录失败:`, error.message)
      throw error
    }
  }

  // 实时订阅
  subscribeToTable(table, callback, filters = {}) {
    let subscription = this.client
      .channel(`${table}_changes`)
      .on('postgres_changes', 
        { 
          event: '*', 
          schema: 'public', 
          table: table,
          ...filters
        }, 
        callback
      )
      .subscribe()
    
    return subscription
  }

  // 取消订阅
  unsubscribe(subscription) {
    if (subscription) {
      this.client.removeChannel(subscription)
    }
  }
}

// 创建服务实例
export const supabaseService = new SupabaseService()

// 导出默认客户端
export default supabase
