import requests
import time

print('⏳ 检查部署状态...')
for i in range(6):
    try:
        response = requests.get('https://aigupiao.me', timeout=10)
        content_length = len(response.text)
        print(f'检查 {i+1}/6: 内容长度 {content_length} 字符')
        
        if content_length > 5000:
            print('✅ 新页面已部署!')
            print('🎯 内容包含完整的前端应用')
            break
        elif 'AI股票交易系统' in response.text and '智能化A股交易平台' in response.text:
            print('✅ 新页面已部署!')
            print('🎯 内容包含新的标题')
            break
        else:
            print('⏳ 还是旧页面,继续等待...')
            
    except Exception as e:
        print(f'检查 {i+1}/6: 连接失败 - {e}')
    
    if i < 5:
        time.sleep(10)

print('检查完成!现在访问 https://aigupiao.me 查看结果')
