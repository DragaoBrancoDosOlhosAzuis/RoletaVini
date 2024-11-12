@echo off
REM Script para instalar as dependências do projeto

REM Verificar se o Python está instalado
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python não está instalado. Por favor, instale o Python e tente novamente.
    pause
    exit /b 1
)

REM Instalar o pip se não estiver instalado
python -m ensurepip --default-pip

REM Instalar dependências do projeto
pip install kivy==2.3.0 kivymd==0.104.2

REM Mensagem de finalização
echo As dependências foram instaladas com sucesso.
pause
