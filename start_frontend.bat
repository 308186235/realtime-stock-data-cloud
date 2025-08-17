@echo off
echo Starting stock trading system frontend
echo ==============================

REM Change to frontend directory
cd frontend\stock5

REM Start frontend service
echo Starting Uni-app development server...
echo Frontend will run on http://localhost:9000
echo Press Ctrl+C to stop server
echo.

npx uni serve 