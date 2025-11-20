@echo off
cd /d "%~dp0"
echo Activating Anaconda environment...
call C:\Users\%USERNAME%\anaconda3\Scripts\activate.bat base
echo Launching Global Financial Intelligence Dashboard...
python -m streamlit run app.py
pause
