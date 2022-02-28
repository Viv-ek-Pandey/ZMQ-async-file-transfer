:loop
echo %DATE% >> Time_stamp.txt
echo %TIME% >> Time_stamp.txt
timeout /t 5
echo " " >> Time_stamp.txt
goto loop