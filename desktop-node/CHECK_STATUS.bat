@echo off
REM One-shot status check against the public Active Capacity API.
python acn_node.py status || py acn_node.py status
pause
