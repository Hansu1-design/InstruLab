@echo off
REM TDC子板 Gerber生成脚本
REM 打开KiCad → PCB Editor → 文件 → 制造输出 → Gerber文件
REM 或者用kicad-cli:
REM kicad-cli pcb export gerbers tdc_daughterboard.kicad_pcb

echo ============================
echo TDC Daughterboard - Gerber
echo ============================
echo 需要生成的Gerber层:
echo   1. F_Cu (顶层铜)
echo   2. B_Cu (底层铜)
echo   3. GND (内层GND)
echo   4. PWR (内层电源)
echo   5. F_Mask (顶层阻焊)
echo   6. B_Mask (底层阻焊)
echo   7. F_SilkS (顶层丝印)
echo   8. Edge_Cuts (板框)
echo   9. Drill (钻孔)
echo 10. NPTH (非金属化孔)
echo.
echo 生成后压缩为: tdc_daughterboard_v1.0.zip
echo 发给PCB厂商(嘉立创/华秋)打样
echo.
echo 板子参数: 50x40mm, 4层, FR4, 1.6mm, 1oz
echo BOM成本: ~$20
pause
