@echo off
REM Active Capacity Network - Capacity Node preview (read-only). No mining, no rewards.
where python >nul 2>nul || where py >nul 2>nul || (echo Python 3 not found. See README_WINDOWS.md & pause & exit /b 1)
echo Starting Active Capacity CAPACITY preview node (Ctrl+C to stop)...
python acn_node.py run --role capacity || py acn_node.py run --role capacity
pause
