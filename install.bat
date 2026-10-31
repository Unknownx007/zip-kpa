@echo off
setlocal EnableDelayedExpansion
REM ZIP-KPA installer — DEDSEC

set BK_VERSION=1.8.1
set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

echo ===============================================
echo   ZIP-KPA installer  --  DEDSEC
echo ===============================================

echo [*] Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

echo [*] Installing Python dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [!] pip install failed.
    pause
    exit /b 1
)
echo [OK] Python deps installed.

REM ---------- bkcrack (optional, for Mode 2) ----------
if exist "%PROJECT_DIR%bkcrack.exe" (
    echo [OK] bkcrack.exe already present. Skipping download.
    goto :done
)
where bkcrack >nul 2>&1
if not errorlevel 1 (
    echo [OK] bkcrack already in PATH. Skipping download.
    goto :done
)

echo.
echo [*] Downloading bkcrack v%BK_VERSION% (needed for Mode 2 -- KPA)...

REM Pick 64-bit or 32-bit asset
set "ASSET=bkcrack-%BK_VERSION%-win32.zip"
if /i "%PROCESSOR_ARCHITECTURE%"=="AMD64" set "ASSET=bkcrack-%BK_VERSION%-win64.zip"
if /i "%PROCESSOR_ARCHITECTURE%"=="ARM64" set "ASSET=bkcrack-%BK_VERSION%-win64.zip"

set "URL=https://github.com/kimci86/bkcrack/releases/download/v%BK_VERSION%/%ASSET%"
set "TMPDIR=%TEMP%\bkcrack_%RANDOM%"
mkdir "%TMPDIR%" 2>nul
pushd "%TMPDIR%"

echo     URL: %URL%

powershell -NoProfile -Command "try { Invoke-WebRequest -Uri '%URL%' -OutFile '%ASSET%' -UseBasicParsing; exit 0 } catch { Write-Host $_; exit 1 }"
if errorlevel 1 (
    echo [!] Download failed.
    popd
    rmdir /s /q "%TMPDIR%" 2>nul
    pause
    exit /b 1
)

powershell -NoProfile -Command "Expand-Archive -Path '%ASSET%' -DestinationPath '.' -Force"
if errorlevel 1 (
    echo [!] Extraction failed.
    popd
    rmdir /s /q "%TMPDIR%" 2>nul
    pause
    exit /b 1
)

for /r "%TMPDIR%" %%F in (bkcrack.exe) do (
    copy /y "%%F" "%PROJECT_DIR%bkcrack.exe" >nul
    goto :copied
)
:copied

popd
rmdir /s /q "%TMPDIR%" 2>nul

if exist "%PROJECT_DIR%bkcrack.exe" (
    echo [OK] bkcrack.exe installed.
) else (
    echo [!] Could not locate bkcrack.exe in the archive.
)

:done
echo.
echo [OK] Setup complete. Run:  python run.py
pause
