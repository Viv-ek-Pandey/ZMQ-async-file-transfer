@REM This script is called before the logon after the Sysprep Specialize operation.
@REM This script should be placed under the path %WINDIR%\Setup\Scripts

wmic useraccount where name="Administrator" call rename name="otheradmin"