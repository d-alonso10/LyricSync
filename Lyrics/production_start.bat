@echo off
cd /d "%~dp0"

:: 1. Start Python Backend (Hidden)
:: Using pythonw to avoid console window
cd backend
start "" /B python server.py > nul 2>&1
cd ..

:: 2. Start Electron Frontend (Hidden Console)
:: We use 'start /B' with 'call' to run without opening a new window if possible,
:: but acts as a launcher. Since we use 'npx electron .', it might pop a brief cmd.
:: Using 'electron .' starts the app.
:: Since we built the app, 'electron .' reads package.json -> main.cjs -> dist/index.html
start "" /B npx electron .
