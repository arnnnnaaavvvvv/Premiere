# Premiere Development Launcher
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Starting Premiere Development Environment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Start FastAPI Backend in background job
Start-Process -NoNewWindow powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn api.main:app --reload --port 8000"
Write-Host "✓ FastAPI Backend launching on http://localhost:8000" -ForegroundColor Green

# Start Worker Daemon
Start-Process -NoNewWindow powershell -ArgumentList "-NoExit", "-Command", "python -m worker.main"
Write-Host "✓ Worker Daemon launched" -ForegroundColor Green

# Start Next.js Frontend
Write-Host "✓ Next.js Frontend launching on http://localhost:3000" -ForegroundColor Green
Set-Location web
npm run dev
