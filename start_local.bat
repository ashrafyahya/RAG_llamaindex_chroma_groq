@echo off
echo Starting Agentic AI Assistant (Local Development Mode)
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Create necessary directories
if not exist "data" mkdir data
if not exist "chroma_db" mkdir chroma_db

REM Start the application
echo.
echo Starting Streamlit application...
echo Application will be available at: http://localhost:8503
echo.
python -m streamlit run ui/streamlit_app.py --server.port=8503

pause