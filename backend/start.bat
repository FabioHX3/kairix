@echo off
echo 🚀 Iniciando Kairix Backend...
echo.

REM Verificar se o ambiente virtual existe
if not exist "venv" (
    echo 📦 Criando ambiente virtual...
    python -m venv venv
)

REM Ativar ambiente virtual
echo 🔧 Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Instalar dependências
echo 📚 Instalando dependências...
pip install -r requirements.txt

REM Perguntar sobre popular banco
echo.
echo ⚙️  Deseja popular o banco com os planos iniciais? (s/n)
set /p response=
if /i "%response%"=="s" (
    echo 📋 Populando banco de dados...
    python populate_plans.py
)

REM Iniciar servidor
echo.
echo ✅ Iniciando servidor em http://localhost:8012
echo 📖 Documentação disponível em http://localhost:8012/docs
echo.
python main.py

pause
