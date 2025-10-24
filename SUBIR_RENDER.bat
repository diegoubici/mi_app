@echo off
cd /d "C:\Users\Diego\mi_app"
echo ==============================
echo   Subiendo cambios a Render
echo ==============================
git status
git add .
set /p msg="Mensaje del commit (enter para 'AutoPush'): "
if "%msg%"=="" set msg=AutoPush
git commit -m "%msg%"
git push
echo.
echo 🚀 Cambios enviados a GitHub. Render actualizará tu app en unos minutos.
pause
