@echo off

set /A index=0

:LOOP 
    for /L %%i in (1,1,20) do C:\Users\Administrator\Documents\rdfc DM_TEST_%index% 20000000
    set /A index+=1
    if %index% == 10 (
        del DM_TEST* -f
        set /A index=0
    )
    timeout /t 20
goto :LOOP