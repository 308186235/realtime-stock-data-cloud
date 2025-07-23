@echo off
chcp 65001 >nul
title 实时数据服务 - 端口8001

echo 🚀 启动实时数据服务 (端口8001)...

REM 设置环境变量
set PORT=8001
set JWT_SECRET_KEY=your-secret-key-here
set SUPABASE_URL=https://zzukfxwavknskqcepsjb.supabase.co
set SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzU3MjU2NzQsImV4cCI6MjA1MTMwMTY3NH0.Ej4rJhGJZJQWQOJOGGSdBhfLJVm7VJQWQOJOGGSdBhf
set SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNTcyNTY3NCwiZXhwIjoyMDUxMzAxNjc0fQ.Ej4rJhGJZJQWQOJOGGSdBhfLJVm7VJQWQOJOGGSdBhf

echo ✅ 环境变量已设置
echo 📂 工作目录: %cd%
echo 🌐 服务端口: %PORT%
echo.

REM 启动服务
python backend/app.py

pause