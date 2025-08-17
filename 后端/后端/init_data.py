import requests
import json

# Supabase配置
SUPABASE_URL = 'https://process.env.SUPABASE_URL'
SUPABASE_KEY = 'process.env.SUPABASE_ANON_KEY

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'apikey': SUPABASE_KEY
}

# 基础股票数据
stocks_data = [
    {
        'stock_code': 'sz000001',
        'stock_name': '平安银行',
        'market': 'SZSE',
        'sector': '金融',
        'industry': '银行',
        'is_active': True
    },
    {
        'stock_code': 'sh600519',
        'stock_name': '贵州茅台',
        'market': 'SSE',
        'sector': '食品饮料',
        'industry': '白酒',
        'is_active': True
    },
    {
        'stock_code': 'sz300750',
        'stock_name': '宁德时代',
        'market': 'SZSE',
        'sector': '新能源',
        'industry': '电池',
        'is_active': True
    }
]

print("初始化stocks表数据...")
response = requests.post(f'{SUPABASE_URL}/rest/v1/stocks', headers=headers, json=stocks_data)
print(f"状态码: {response.status_code}")
print(f"响应: {response.text}")

print("\n测试API...")
api_response = requests.get('https://realtime-stock-api.pages.dev/api/quotes?symbols=sz000001')
print(f"API状态: {api_response.status_code}")
if api_response.status_code == 200:
    data = api_response.json()
    print(f"数据质量: {data.get('data_quality', {})}")
