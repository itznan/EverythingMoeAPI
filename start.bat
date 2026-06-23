@echo off
echo ==================================================
echo   Starting EverythingMoe FastAPI Web Server...
echo ==================================================
echo   Server URL:         http://127.0.0.1:8000
echo   API Documentation:  http://127.0.0.1:8000/docs
echo ==================================================
uvicorn app.api.main:app --reload
pause
