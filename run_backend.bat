@echo off
cd /d C:\Users\hp\Desktop\Mobitranz
set PYTHONPATH=.
start python -m uvicorn backend.main:app --port 8000 --reload