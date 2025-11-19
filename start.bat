@echo off
REM Startup script for RAG System (Backend + Frontend)
REM This script starts both the FastAPI backend and React frontend

echo Starting RAG System...
echo.

REM Start backend
echo Starting FastAPI backend on port 8000...
cd backend
start "RAG Backend" cmd /k python main.py

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
echo Starting React frontend on port 3000...
cd ..\frontend
start "RAG Frontend" cmd /k npm start

echo.
echo Both services are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
pause
