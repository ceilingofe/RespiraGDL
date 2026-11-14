@echo off
REM Respira GDL - prepara y levanta la API para verla en el navegador.
REM Uso: doble clic, o desde la terminal:  .\backend\iniciar_demo.bat
cd /d "%~dp0"

python --version >nul 2>nul
if errorlevel 1 (
  echo.
  echo [1/6] Python no esta instalado. Instalando Python 3.12 con winget...
  winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
  echo.
  echo Listo. CIERRA esta ventana y vuelve a abrir iniciar_demo.bat para continuar.
  pause
  exit /b
)

echo [1/6] Python encontrado:
python --version

if not exist ".venv\Scripts\python.exe" (
  echo [2/6] Creando entorno virtual .venv ...
  python -m venv .venv || goto :error
) else (
  echo [2/6] Entorno virtual ya existe.
)
call ".venv\Scripts\activate.bat"

echo [3/6] Instalando dependencias...
python -m pip install --upgrade pip -q
python -m pip install -r requirements.txt -q || goto :error

echo [4/6] Corriendo pruebas...
pushd ..
python -m pytest backend/tests -q -p no:cacheprovider
popd

echo [5/6] Cargando salones y lecturas SIMULADAS de la demo...
python -m scripts.cargar_demo --lecturas || goto :error

echo [6/6] Levantando la API en http://localhost:8000  (Ctrl+C para detener)
start "" cmd /c "timeout /t 5 >nul & start http://localhost:8000/docs"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
goto :eof

:error
echo.
echo Algo fallo. Copia el mensaje de arriba y mandaselo a Claude.
pause
