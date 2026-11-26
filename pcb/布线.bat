@echo off
chcp 65001 >nul
echo ================================================
echo   TDC子板 — 一键布线引导
echo ================================================
echo.
echo 当前PCB: G:\System\InstruLab\pcb\tdc_daughterboard\tdc_daughterboard.kicad_pro
echo.
echo 第1步: 打开KiCad PCB编辑器
echo   文件 → 导出 → Specctra DSN
echo   保存到: G:\System\InstruLab\pcb\tdc_daughterboard\tdc_daughterboard.dsn
echo.
pause
echo.
echo 第2步: 桌面 Freerouting → 文件 → 打开
echo   选刚才的DSN → ⭐自动布线
echo   等布线完成 → 文件 → 导出 → SES
echo   保存到: G:\System\InstruLab\pcb\tdc_daughterboard\tdc_daughterboard.ses
echo.
pause
echo.
echo 第3步: 回到KiCad → 文件 → 导入 → Specctra SES
echo   选刚才的SES → 确定
echo.
pause
echo.
echo 第4步: Ctrl+S保存 → 文件 → 制造输出 → Gerber
echo   选 gerber_final 目录 → 确定
echo.
echo 第5步: 把gerber_final里所有文件打包发嘉立创
echo.
pause
echo 完成!
