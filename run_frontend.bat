@echo off
title ProofGraph AI - Frontend Server
echo Starting ProofGraph AI React Frontend on http://localhost:3000...
cd /d "%~dp0frontend"
set Path=C:\Program Files\nodejs;C:\Users\HP\.local\bin;%Path%
npm.cmd run dev
pause
