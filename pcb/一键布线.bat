@echo off
REM InstruLab 一键自动布线脚本
REM 前置条件: KiCad PCB编辑器已打开 tdc_daughterboard.kicad_pcb
REM 这个脚本会自动: 导出DSN → Freerouting自动布线 → 导入SES

echo ========================================
echo  InstruLab 一键自动布线 v1.0
echo ========================================
echo.
echo 确保: KiCad PCB编辑器已打开 tdc_daughterboard.kicad_pcb
echo 并且 Freerouting v2.2.4 已安装
echo.
pause

:: ===== 第1步: 生成完整PCB(含网络) =====
echo.
echo [1/4] 生成含网络的PCB文件...
python pcb/generate_with_nets.py
if %errorlevel% neq 0 goto ERROR

:: ===== 第2步: KiCad导出DSN(键盘自动化) =====
echo.
echo [2/4] 正在导出DSN...
echo   请在KiCad PCB编辑器中按以下操作:
echo   Alt+F → 导出 → Specctra DSN → 保存
echo.
echo 或者用自动化(将激活KiCad窗口):
powershell -Command "
$wshell = New-Object -ComObject wscript.shell
$wshell.AppActivate('tdc_daughterboard')
Start-Sleep 1
$wshell.SendKeys('%%f')
Start-Sleep 0.5
$wshell.SendKeys('e')
Start-Sleep 0.5
$wshell.SendKeys('{DOWN 4}')
Start-Sleep 0.5
$wshell.SendKeys('{ENTER}')
Start-Sleep 1
for($i=0; $i -lt 60; $i++) { $wshell.SendKeys('{BACKSPACE}') }
Start-Sleep 0.3
$wshell.SendKeys('tdc_daughterboard.dsn')
Start-Sleep 0.3
$wshell.SendKeys('{ENTER}')
echo DSN导出完成
"

:: ===== 第3步: Freerouting自动布线 =====
echo.
echo [3/4] Freerouting自动布线...
start "" "freerouting/tdc_daughterboard.dsn(相对路径)" "G:\System\InstruLab\pcb\tdc_daughterboard\tdc_daughterboard.dsn"
echo   等待Freerouting加载...
ping 127.0.0.1 -n 5 >nul

powershell -Command "
$wshell = New-Object -ComObject wscript.shell
Start-Sleep 2
$wshell.AppActivate('Freerouting')
Start-Sleep 1
:: 点自动布线按钮(快捷键待确认)
$wshell.SendKeys('{ENTER}')
echo 自动布线启动
"

echo   等待布线完成...
ping 127.0.0.1 -n 10 >nul

:: 导出SES
powershell -Command "
$wshell = New-Object -ComObject wscript.shell
$wshell.AppActivate('Freerouting')
Start-Sleep 0.5
$wshell.SendKeys('%%f')
Start-Sleep 0.3
$wshell.SendKeys('e')
Start-Sleep 0.3
$wshell.SendKeys('{ENTER}')
Start-Sleep 1
$wshell.SendKeys('tdc_daughterboard.ses')
Start-Sleep 0.3
$wshell.SendKeys('{ENTER}')
echo SES导出完成
"

:: ===== 第4步: KiCad导入SES =====
echo.
echo [4/4] 导入布线到KiCad...
powershell -Command "
$wshell = New-Object -ComObject wscript.shell
$wshell.AppActivate('tdc_daughterboard')
Start-Sleep 1
$wshell.SendKeys('%%f')
Start-Sleep 0.3
$wshell.SendKeys('i')
Start-Sleep 0.3
$wshell.SendKeys('s')
Start-Sleep 0.3
$wshell.SendKeys('{ENTER}')
Start-Sleep 1
$wshell.SendKeys('tdc_daughterboard.ses')
Start-Sleep 0.3
$wshell.SendKeys('{ENTER}')
echo 导入完成
"

echo.
echo ========================================
echo  一键布线完成!
echo  请检查KiCad PCB编辑器中的布线结果
echo  然后: 文件 → 制造输出 → Gerber
echo ========================================
pause
goto END

:ERROR
echo.
echo ❌ 出错! 请检查上述输出
pause

:END
