#!/usr/bin/env python3
"""
简化的数据同步脚本 - 使用现有表结构
"""

import requests
import json
from datetime import datetime

SUPABASE_URL = 'https://zzukfxwavknskqcepsjb.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw'

def sync_data():
    """同步数据到现有表"""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'apikey': SUPABASE_KEY
    }
    
    # 获取API数据
    api_response = requests.get('https://realtime-stock-api.pages.dev/api/quotes?symbols=sz000001,sh600519,sz300750')
    api_data = api_response.json()
    
    for stock in api_data.get('data', []):
        # 更新stocks表
        update_data = {
            'name': stock.get('stock_name'),
            'current_price': stock.get('current_price'),
            'last_updated': datetime.now().isoformat()
        }
        
        response = requests.patch(
            f'{SUPABASE_URL}/rest/v1/stocks?code=eq.{stock.get("stock_code")}',
            headers=headers,
            json=update_data
        )
        
        print(f"更新 {stock.get('stock_code')}: {response.status_code}")

if __name__ == '__main__':
    sync_data()
