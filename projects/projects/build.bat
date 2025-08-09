@echo off
echo Limpando builds anteriores...
rmdir /s /q dist 2> nul
rmdir /s /q build 2> nul
del Rust_Dice.spec 2> nul

echo Verificando assets...
if not exist data (
    echo ERRO: Pasta 'data' nao encontrada!
    pause
    exit /b 1
)

if not exist documentacao (
    echo ERRO: Pasta 'documentacao' nao encontrada!
    pause
    exit /b 1
)

if not exist game_settings.json (
    echo ERRO: Arquivo 'game_settings.json' nao encontrado!
    pause
    exit /b 1
)

echo Copiando banco de dados para dist...
mkdir dist\data 2> nul
copy data\database.db dist\data\database.db > nul

echo Copiando documentacao...
mkdir dist\documentacao 2> nul
copy documentacao\*.* dist\documentacao > nul

echo Iniciando nova build...
python -m PyInstaller main.py --onefile --name "Rust_Dice" ^
--add-data "data;data" ^
--add-data "game_settings.json;." ^
--add-data "documentacao;documentacao" ^
--hidden-import=game ^
--hidden-import=states ^
--hidden-import=data.data_tuples ^
--hidden-import=data.populate_db ^
--clean

echo.
echo Build completa! Executavel em: dist\Rust_Dice.exe
echo.
pause