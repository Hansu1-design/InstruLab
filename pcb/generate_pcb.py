#!/usr/bin/env python3
"""TDC子板PCB设计 — TAC+ADC电路"""
import os
from pathlib import Path

# KiCad项目根目录
PRJ = Path("pcb/tdc_daughterboard")
PRJ.mkdir(parents=True, exist_ok=True)

# 电路参数(来自C验证)
C_TAC = 100e-12  # TAC电容 100pF
R_BIAS = 100     # 恒流源电阻 100Ohm → 10mA
ADC_REF = 5.0    # ADC基准电压
VDRV = 3.3       # FPGA IO电压

# 生成KiCad项目文件
proj_content = f"""
(version 4)
(generator "InstruLab TDC Daughterboard")
(uuid "auto")
(kicad_sch_version 20240101)
(project
  (title "TDC-TAC Daughterboard")
  (company "NUC-InstruLab")
  (rev "1.0")
  (date "2026-07-18")
  (comment 1 "TAC + AD7980 ADC + SPI Interface")
  (comment 2 "For Basys3/Nexys4 FPGA Board")
)
"""

# Schematic 主要器件
components = """
# TAC电路
R1: 100Ohm 0805 — 恒流源设置 (I=10mA, Vref=5V-0.7V=4.3V, I=4.3V/430Ohm=10mA)
C1: 100pF NP0 0805 — TAC积分电容 (dV/dt = I/C = 10mA/100pF = 100V/us)
D1: BAS316 — 保护二极管
Q1: BSS83 — 放电开关

# 信号调理
U1: AD7980 (16bit ADC, 1MSPS, SPI)
  VIO=3.3V(FPGA), VDD=5V, REF=5V
  IN+: 来自TAC
  IN-: GND

# 电源
U2: ADP150 LDO (3.3V, 150mA) — 模拟供电
U3: REF5050 (5V基准, 3ppm/C)

# 连接器
J1: 2x10 pin header — Basys3 PMOD/JA接口
  SPI: CS, SCLK, MOSI, MISO
  Control: TAC_RST, TAC_START, ADC_BUSY
J2: SMA — 触发输入

# 无源器件(C1 C2等)
C2: 10uF 0805 — 电源去耦
C3: 100nF 0805 — ADC去耦
R2: 10kOhm 0805 — 上拉
"""

# PCB层叠
pcb_stackup = """
4层板:
  L1: Top (信号+元件)
  L2: GND (完整地平面)
  L3: Power (3.3V/5V)
  L4: Bottom (信号)
FR4, 1.6mm, 1oz铜
差分阻抗控制: 100Ohm LVDS (如有)
"""

# BOM
bom = """
| Ref | Qty | 描述 | 封装 | 厂商 |
|-----|-----|------|------|------|
| C1 | 1 | 100pF NP0 50V | 0805 | Murata |
| C2 | 2 | 10uF X7R 10V | 0805 | Murata |
| C3 | 3 | 100nF X7R 50V | 0805 | Murata |
| R1 | 1 | 100Ohm 1% | 0805 | Yageo |
| R2 | 2 | 10kOhm 1% | 0805 | Yageo |
| U1 | 1 | AD7980 16bit ADC | MSOP-10 | ADI |
| U2 | 1 | ADP150 LDO 3.3V | WLCSP-4 | ADI |
| U3 | 1 | REF5050 5V Ref | SO-8 | TI |
| J1 | 1 | 2x10 Pin Header | 2.54mm | Samtec |
| J2 | 1 | SMA Connector | Edge | Amphenol |
| D1 | 1 | BAS316 | SOD-323 | NXP |
| Q1 | 1 | BSS83 | SOT-23 | NXP |
"""

print("="*50)
print("TDC TAC+ADC 子板 PCB 设计")
print("="*50)
print(f"\n项目路径: {PRJ}")
print(f"\n电路概要:")
print(components)
print(f"PCB层叠:")
print(pcb_stackup)
print(f"\nBOM物料清单:")
print(bom)
print(f"预计BOM成本: ~$15-25 (不含PCB打样)")
print(f"预估PCB尺寸: 50x40mm (适配Basys3 PMOD)")

# 保存设计文件
PRJ.mkdir(parents=True, exist_ok=True)
(PRJ / "tdc_daughterboard.kicad_pro").write_text(proj_content)
(PRJ / "BOM.md").write_text(bom)
(PRJ / "design_notes.md").write_text(f"# TDC子板设计说明\n\nTAC电容: {C_TAC*1e12:.0f}pF\n恒流源: {VDRV/R_BIAS*1e3:.0f}mA\nADC: 16bit, {ADC_REF}Vref\n")
print(f"\n设计文件已生成:")
for f in PRJ.iterdir():
    print(f"  {f.name}")
print(f"\n下一步: 打开KiCad → 新建原理图 → 按BOM放置器件 → 布局布线")
PYEOF