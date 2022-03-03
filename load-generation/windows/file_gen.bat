@echo off

set /A index=0

:LOOP
    echo "This is just a sample line appended to create a big file ..">>SAMPLE_%index%.txt
    for /L %%i in (1,1,20) do type SAMPLE_%index%.txt>>SAMPLE_%index%.txt
    set /A index+=1
    if %index% == 5 (
        del *.txt -f
        set /A index=0
    )
    timeout /t 60
goto :LOOP