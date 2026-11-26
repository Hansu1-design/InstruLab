@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul
cd /d G:\System\InstruLab\software
cl density_test.c /Fe:density_test.exe
density_test.exe
