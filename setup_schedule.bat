@echo off
schtasks /Create /SC DAILY /ST 18:00 /TN "Daily Sales Report" /TR "python \"%~dp0report.py\"" /F
echo.
echo Done. The report will run every day at 6pm.
pause