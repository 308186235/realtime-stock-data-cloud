ÿþfrom fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

@app.get('/api/v1/agent-trading/system/status')
async def get_status():
    return {'success': True, 'data': {'isRunning': True, 'availableCash': 10183.94, 'holdingsCount': 0}}

@app.post('/api/v1/agent-trading/start')
async def start_agent():
    return {'success': True, 'message': 'Agent/T¨RbR'}

@app.post('/api/v1/agent-trading/stop') 
async def stop_agent():
    return {'success': True, 'message': 'Agentò]\Pbk'}

if __name__ == '__main__':
    import uvicorn
    print('=ØÞ APIMB\/T¨R: http://localhost:8000')
    uvicorn.run(app, host='0.0.0.0', port=8000)

