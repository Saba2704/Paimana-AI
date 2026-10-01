# PAIMANA-AI PowerShell Launch Script
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host " PAIMANA-AI: National Infrastructure Predictive Monitoring System" -ForegroundColor Yellow
Write-Host " Ministry of Statistics and Programme Implementation (MoSPI)" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[*] Launching PAIMANA-AI Dashboard on http://127.0.0.1:8000" -ForegroundColor Green
python -m uvicorn paimana_ai.server.main:app --host 127.0.0.1 --port 8000 --reload
