@echo off
echo ====================================================================
echo  PAIMANA-AI: National Infrastructure Predictive Monitoring System
echo  Ministry of Statistics and Programme Implementation (MoSPI)
echo ====================================================================
echo.
echo [1/2] Verifying Python dependencies...
python -m pip install -q -r requirements.txt
echo.
echo [2/2] Launching PAIMANA-AI Platform on http://127.0.0.1:8000 ...
python -m uvicorn paimana_ai.server.main:app --host 127.0.0.1 --port 8000 --reload
pause
