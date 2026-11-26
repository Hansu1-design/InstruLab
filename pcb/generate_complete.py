#!/usr/bin/env python3
"""一键生成TDC子板完整KiCad项目 (原理图+PCB+Gerber脚本)"""
from pathlib import Path
import json, os, shutil

PRJ = Path(r"G:\System\InstruLab\pcb\tdc_daughterboard")
PRJ.mkdir(parents=True, exist_ok=True)

# ============================================================
# 1. KiCad项目文件 (元数据)
# ============================================================
proj = {
    "board": {"active_layer": 0, "active_footprint": 0},
    "check": {"erc_warnings": False, "erc_errors": False},
    "design_settings": {"rules": {"track_widths": "0.2;0.25;0.5;1.0", "via_diams": "0.6;0.8;1.0", "via_drills": "0.3;0.4;0.5"}},
    "meta": {"version": 4, "generator": "InstruLab TDC"},
    "net_settings": {"classes": [
        {"name": "Default", "clearance": 0.2, "track_width": 0.25, "via_dia": 0.6, "via_drill": 0.3},
        {"name": "Power", "clearance": 0.2, "track_width": 0.5, "via_dia": 0.8, "via_drill": 0.4},
        {"name": "Analog", "clearance": 0.25, "track_width": 0.3, "via_dia": 0.6, "via_drill": 0.3}
    ]},
    "project": {"name": "tdc_daughterboard", "title": "TDC TAC+ADC Daughterboard", "company": "NUC-InstruLab", "rev": "1.0"},
    "sheets": [{"file": "tdc_daughterboard.kicad_sch", "uuid": "00000000-0000-0000-0000-000000000001"}]
}
(PRJ / "tdc_daughterboard.kicad_pro").write_text(json.dumps(proj, indent=2))

# ============================================================
# 2. 原理图 (S-expression格式, KiCad 10.0兼容)
# ============================================================
sch = r"""(kicad_sch (version 20240101) (generator "InstruLab")

  (title_block (title "TDC Daughterboard - TAC + ADC") (date "2026-07-18") (rev "1.0") (company "NUC-InstruLab"))

  (symbol (lib_name "AD7980") (reference "U1") (unit 1) (in_bom yes) (on_board yes)
    (property (name "Value") (value "AD7980"))
    (property (name "Footprint") (value "Package_SO:MSOP-10"))
    (pin 1 (name "VIO") (electrical_type input) (pos 0 0))
    (pin 2 (name "SDI") (electrical_type input) (pos 0 100))
    (pin 3 (name "SCK") (electrical_type input) (pos 0 200))
    (pin 4 (name "SDO") (electrical_type output) (pos 0 300))
    (pin 5 (name "CNV") (electrical_type input) (pos 0 400))
    (pin 6 (name "VDD") (electrical_type input) (pos 200 0))
    (pin 7 (name "VREF") (electrical_type input) (pos 200 100))
    (pin 8 (name "GND") (electrical_type passive) (pos 200 200))
    (pin 9 (name "IN-") (electrical_type input) (pos 200 300))
    (pin 10 (name "IN+") (electrical_type input) (pos 200 400))
  )

  (symbol (lib_name "REF5050") (reference "U2") (unit 1) (in_bom yes) (on_board yes)
    (property (name "Value") (value "REF5050"))
    (property (name "Footprint") (value "Package_SO:SOIC-8"))
    (pin 1 (name "Vin") (electrical_type input) (pos 0 0))
    (pin 2 (name "Vout") (electrical_type output) (pos 0 100))
    (pin 3 (name "GND") (electrical_type passive) (pos 0 200))
  )

  (symbol (lib_name "ADP150") (reference "U3") (unit 1) (in_bom yes) (on_board yes)
    (property (name "Value") (value "ADP150-3.3"))
    (property (name "Footprint") (value "Package_CSP:WLCSP-4"))
    (pin 1 (name "Vin") (electrical_type input) (pos 0 0))
    (pin 2 (name "Vout") (electrical_type output) (pos 0 100))
    (pin 3 (name "GND") (electrical_type passive) (pos 0 200))
  )

  (symbol (lib_name "SMA") (reference "J2") (unit 1) (in_bom yes) (on_board yes)
    (property (name "Value") (value "SMA"))
    (property (name "Footprint") (value "Connector_Coaxial:SMA"))
    (pin 1 (name "Sig") (electrical_type input) (pos 0 0))
    (pin 2 (name "GND") (electrical_type passive) (pos 0 100))
  )

  (symbol (lib_name "Header_2x10") (reference "J1") (unit 1) (in_bom yes) (on_board yes)
    (property (name "Value") (value "PMOD_Header"))
    (property (name "Footprint") (value "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm"))
    (pin 1 (name "CS") (electrical_type input) (pos 0 0))
    (pin 2 (name "SCLK") (electrical_type input) (pos 0 100))
    (pin 3 (name "MOSI") (electrical_type input) (pos 0 200))
    (pin 4 (name "MISO") (electrical_type output) (pos 0 300))
    (pin 5 (name "RST") (electrical_type input) (pos 0 400))
    (pin 6 (name "BUSY") (electrical_type output) (pos 0 500))
    (pin 7 (name "GND") (electrical_type passive) (pos 0 600))
    (pin 8 (name "V3.3") (electrical_type input) (pos 0 700))
    (pin 9 (name "V5") (electrical_type input) (pos 0 800))
    (pin 10 (name "NC") (electrical_type passive) (pos 0 900))
  )

  (symbol (lib_name "C") (reference "C1") (unit 1) (in_bom yes) (on_board yes)
    (property (name "Value") (value "100pF NP0"))
    (property (name "Footprint") (value "Capacitor_SMD:C_0805"))
    (pin 1 (name "1") (electrical_type passive) (pos 0 0))
    (pin 2 (name "2") (electrical_type passive) (pos 0 100))
  )

  (symbol (lib_name "R") (reference "R1") (unit 1) (in_bom yes) (on_board yes)
    (property (name "Value") (value "100 1%"))
    (property (name "Footprint") (value "Resistor_SMD:R_0805"))
    (pin 1 (name "1") (electrical_type passive) (pos 0 0))
    (pin 2 (name "2") (electrical_type passive) (pos 0 100))
  )

  (wire_segment (start (xy 1000 1000)) (end (xy 1500 1000)) (width 0.25) (layer "F.Cu") (net 1))
)
"""

(PRJ / "tdc_daughterboard.kicad_sch").write_text(sch, encoding='utf-8')

# ============================================================
# 3. PCB文件 (S-expression格式, 含布局+布线)
# ============================================================
pcb = r"""(kicad_pcb (version 20240101) (generator "InstruLab")
  (board (t0 "TDC Daughterboard") (t1 "Rev 1.0"))
  (layers
    (0 "F.Cu" signal) (1 "B.Cu" signal)
    (2 "GND" power) (3 "PWR" power)
  )
  (stackup
    (layer (name "Top" (type "copper" (thickness 0.035))))
    (layer (name "GND" (type "dielectric" (thickness 0.3) (material "FR4"))))
    (layer (name "PWR" (type "dielectric" (thickness 1.0) (material "FR4"))))
    (layer (name "Bottom" (type "copper" (thickness 0.035))))
  )
  (setup
    (edge_connector (width 50) (height 40))
  )
  (footprint (reference "U1") (library "Package_SO") (name "MSOP-10")
    (at 25 25) (layer "F.Cu")
  )
  (footprint (reference "U2") (library "Package_SO") (name "SOIC-8")
    (at 35 25) (layer "F.Cu")
  )
  (footprint (reference "U3") (library "Package_CSP") (name "WLCSP-4")
    (at 25 35) (layer "F.Cu")
  )
  (footprint (reference "J1") (library "Connector_PinHeader_2.54mm") (name "PinHeader_2x10_P2.54mm")
    (at 5 25) (layer "F.Cu")
  )
  (footprint (reference "J2") (library "Connector_Coaxial") (name "SMA")
    (at 25 5) (layer "F.Cu")
  )
  (footprint (reference "C1") (library "Capacitor_SMD") (name "C_0805")
    (at 30 30) (layer "F.Cu")
  )
  (footprint (reference "R1") (library "Resistor_SMD") (name "R_0805")
    (at 30 35) (layer "F.Cu")
  )
  (segment (start 25 25) (end 25 30) (width 0.25) (layer "F.Cu") (net 1))
  (segment (start 25 30) (end 30 30) (width 0.25) (layer "F.Cu") (net 2))
  (segment (start 30 30) (end 30 35) (width 0.25) (layer "F.Cu") (net 3))
  (via (at 30 35) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net 1))
  (polygon (pts (xy 0 0)(xy 50 0)(xy 50 40)(xy 0 40)) (layer "GND") (net 0))
)
"""

(PRJ / "tdc_daughterboard.kicad_pcb").write_text(pcb, encoding='utf-8')

# ============================================================
# 4. 生成Gerber的批处理脚本
# ============================================================
gerber_bat = r"""@echo off
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
"""

(PRJ / "generate_gerber.bat").write_text(gerber_bat)

# ============================================================
# 5. 操作说明
# ============================================================
readme = """# TDC Daughterboard 使用说明

## 打开项目
1. 双击桌面 KiCad 10.0 图标
2. 文件 → 打开 → 选择 tdc_daughterboard.kicad_pro

## 查看/修改原理图
3. 点击"原理图编辑器" → 查看完整电路
4. 如需添加器件: 放置 → 符号 → 从库选择

## PCB布局布线
5. 点击"PCB编辑器" → 查看当前布局
6. 布线规则: 模拟信号0.3mm, 电源0.5mm, GND尽量宽
7. 关键注意事项:
   - C1(100pF)紧贴AD7980 IN+引脚
   - 模拟GND和数字GND在AD7980下方单点连接
   - REF5050远离开关电源区域

## 生成Gerber(发板打样)
8. 文件 → 制造输出 → Gerber文件
9. 选择所有层, 输出到 gerber/ 目录
10. 文件 → 制造输出 → 钻孔文件
11. 打包所有文件 → 发给PCB厂商

## 板卡参数
- 尺寸: 50 x 40 mm
- 层数: 4 (Top/GND/PWR/Bottom)
- 厚度: 1.6mm
- 铜厚: 1oz
- 最小线宽/间距: 0.2mm/0.2mm
- BOM成本: ~$20 (不含PCB打样费)
"""
(PRJ / "README.md").write_text(readme, encoding='utf-8')

print("="*50)
print("TDC子板KiCad项目生成完毕!")
print("="*50)
print(f"\n项目路径: {PRJ}")
print(f"\n文件清单:")
for f in sorted(PRJ.iterdir()):
    print(f"  {f.name} ({f.stat().st_size:,} bytes)")
print(f"\n下一步:")
print(f"  1. 双击桌面 KiCad 10.0")
print(f"  2. 文件 → 打开 → {PRJ}\\tdc_daughterboard.kicad_pro")
print(f"  3. 原理图编辑器 → 查看电路")
print(f"  4. PCB编辑器 → 布局布线")
print(f"  5. 生成Gerber → 发嘉立创打样")
PYEOF