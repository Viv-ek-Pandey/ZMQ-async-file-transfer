@REM This script is called during the last phase of the Sysprep Specialize operation.

@REM Define a log file for debugging.
set LOG_FILE=C:\sysprep_specialize_log.txt

@REM Log helper function.
:log
    echo [%date% %time%] %* >> %LOG_FILE%
    exit /b 0

@REM Re-enable RDP connections.
reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f
if %ERRORLEVEL% equ 0 (
    call :log "Successfully enabled RDP connections."
) else (
    call :log "Failed to enable RDP connections."
)