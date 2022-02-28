:loop
mysql -u root -pDatamotive@123 datamotive -e "insert into time (curr_time) values (NOW())"
timeout /t 5
goto loop