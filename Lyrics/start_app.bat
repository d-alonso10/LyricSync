@echo off
echo Iniciando VocaSync...

:: Iniciar Backend (Python)
echo Iniciando servidor Python...
start "VocaSync Backend" cmd /k "cd backend && python server.py"

:: Esperar unos segundos para que el backend arranque
timeout /t 3 /nobreak

:: Iniciar Frontend (Electron + React)
echo Iniciando interfaz Electron...
start "VocaSync Frontend" cmd /k "npm run electron:dev"

echo ¡Aplicación iniciada! Disfruta del karaoke.
