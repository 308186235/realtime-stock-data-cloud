from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

@app.get('/api/v1/agent-trading/system/status')
async def get_status():
    return {'success': True, 'data': {'isRunning': True, 'availableCash': 10183.94, 'holdingsCount': 0, 'dailyProfit': 1250.80}}

@app.post('/api/v1/agent-trading/start')
async def start_agent():
    return {'success': True, 'message': 'Agent�����ɹ�'}

@app.post('/api/v1/agent-trading/stop') 
async def stop_agent():
    return {'success': True, 'message': 'Agent��ֹͣ'}

@app.get('/')
async def root():
    return {'message': 'Agent����API�����������', 'version': '1.0.0'}

if __name__ == '__main__':
    import uvicorn
    print('?? API���������: http://localhost:8000')
    uvicorn.run(app, host='0.0.0.0', port=8000)
