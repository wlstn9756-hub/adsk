# PowerShell Script for Running Naver Review System

Write-Host "========================================"
Write-Host " Naver Review Management System"
Write-Host "========================================"
Write-Host ""

Set-Location naver_review_system

Write-Host "[1/4] Creating virtual environment..."
if (-not (Test-Path venv)) {
    python -m venv venv
    Write-Host "Virtual environment created"
} else {
    Write-Host "Virtual environment already exists"
}

Write-Host ""
Write-Host "[2/4] Activating virtual environment..."
& venv\Scripts\Activate.ps1

Write-Host ""
Write-Host "[3/4] Installing required packages..."
pip install -r requirements_extended.txt

Write-Host ""
Write-Host "[4/4] Starting server..."
Write-Host ""
Write-Host "========================================"
Write-Host " Server is running!"
Write-Host " Open browser: http://localhost:8000"
Write-Host " Press Ctrl+C to stop"
Write-Host "========================================"
Write-Host ""

python main_integrated.py