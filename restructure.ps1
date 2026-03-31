$ErrorActionPreference = "Continue"

# 1. Create backend
if (-not (Test-Path "backend")) { New-Item -ItemType Directory -Force -Path "backend" }

# 2. Items to move
$itemsToMove = @(".pytest_cache", ".venv", "app", "data", "scripts", "tests", "venv", ".env", "env.example", "internai.db", "requirements.txt", "README.md", "*.py", "*.txt", "*.pdf", "*.json")

foreach ($item in $itemsToMove) {
    # Resolve all matching files (needed for wildcards)
    $resolved = Get-ChildItem -Path $item -ErrorAction SilentlyContinue 
    foreach ($file in $resolved) {
        # Only move if the item is not 'backend', 'Templates', 'frontend', 'start_backend.bat', 'restructure.ps1'
        if ($file.Name -notmatch "^(backend|Templates|frontend|start_backend\.bat|restructure\.ps1)$") {
            Move-Item -Path $file.FullName -Destination "backend\" -Force
        }
    }
}

# 3. Rewrite start_backend.bat
$batContent = '@echo off
cd /d "%~dp0backend"
echo ===================================================
echo   Starting InternAI FastAPI Backend Server
echo ===================================================
echo.
echo Activating virtual environment...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo WARNING: Cannot find venv or .venv folder. Relying on global Python.
)
echo.
echo Starting Uvicorn on http://localhost:8000...
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause'
Set-Content -Path "start_backend.bat" -Value $batContent

# 4. Rename Templates to frontend
try {
    Rename-Item -Path "Templates" -NewName "frontend" -ErrorAction Stop
    Write-Host "Successfully renamed Templates to frontend. Restructuring complete!"
} catch {
    Write-Host "WARNING: Failed to rename Templates folder! Your running 'npm run dev' terminal is locking the folder. You MUST stop it (Ctrl+C and close terminal) before the folder can be explicitly renamed."
}
