@echo off
REM Falcon BMS Tacview Converter - Quick Launch Scripts

echo ===============================================
echo    Falcon BMS Tacview Converter Toolset
echo ===============================================
echo.
echo Available commands:
echo.
echo 1. List available theaters:
echo    run_toolset.bat theaters
echo.
echo 2. Convert coordinates:
echo    run_toolset.bat convert X Y --theater THEATER
echo.
echo 3. Show map corners:
echo    run_toolset.bat corners --theater THEATER  
echo.
echo 4. Generate Tacview XML:
echo    run_toolset.bat tacview THEATER
echo.
echo Examples:
echo    run_toolset.bat convert 1500000 2000000 --theater korea --elevation
echo    run_toolset.bat corners --theater korea
echo    run_toolset.bat tacview korea
echo.

if "%1"=="theaters" (
    python src\falcon_toolset.py theaters
    goto end
)

if "%1"=="convert" (
    python src\falcon_toolset.py %*
    goto end
)

if "%1"=="corners" (
    python src\falcon_toolset.py %*
    goto end
)

if "%1"=="tacview" (
    python src\eval_airbases_to_tacview_final.py %2 %3 %4 %5
    goto end
)

echo Invalid command. Use: theaters, convert, corners, or tacview

:end
pause
