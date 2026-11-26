@echo off
REM 知识库阶段性归档脚本
REM 每次手动或定时运行，创建带时间戳的备份

set TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set SRC=G:\Claudek\知识库\supervisor_kb
set DST=G:\Claudek\知识库\存档\snapshot_%TIMESTAMP%

echo [%date% %time%] 开始归档知识库...
echo  源: %SRC%
echo  目标: %DST%

mkdir "%DST%" 2>nul

REM 复制所有精读/碰撞/MOC/苏淑靖笔记
xcopy "%SRC%\精读-*.md" "%DST%\" /C /Y /Q >nul
xcopy "%SRC%\碰撞-*.md" "%DST%\" /C /Y /Q >nul
xcopy "%SRC%\MOC-*.md" "%DST%\" /C /Y /Q >nul
xcopy "%SRC%\苏淑靖-*.md" "%DST%\" /C /Y /Q >nul
xcopy "%SRC%\公开实盘研究\*.md" "%DST%\公开实盘研究\" /C /Y /Q >nul

REM 统计
set /a COUNT=0
for /f %%f in ('dir /b "%DST%\*.md" 2^>nul') do set /a COUNT+=1
echo [%date% %time%] 归档完成: %COUNT% 篇笔记
echo  路径: %DST%
