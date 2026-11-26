#!/usr/bin/env python3
"""完整42元件数据采集板 — 对标目标规格板"""
from pathlib import Path
import re, uuid

LIB = Path("G:/kicad/share/kicad/footprints")
OUT = Path("pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb")

def gu(): return str(uuid.uuid4())

def fp(name):
    """找封装文件, 递归搜索"""
    found = list(LIB.rglob(f"*{name}*"))
    if found: return found[0]
    print(f"⚠ 未找到: {name}")
    return None

comps = [
    # (位号, 封装文件搜索关键词, 库名, X, Y, 旋转)
    
    # === 电源部分 (12个) ===
    ("U3", "SOT-223-3_TabPin2", "Package_TO_SOT_SMD", 90, 60, 0),  # 3.3V LDO
    ("C11","C_0805_2012Metric", "Capacitor_SMD", 95, 65, 0),  # 10uF
    ("C12","C_0805_2012Metric", "Capacitor_SMD", 100, 60, 0),  # 100nF
    ("C13","C_0805_2012Metric", "Capacitor_SMD", 95, 55, 0),  # 10uF
    ("C14","C_0805_2012Metric", "Capacitor_SMD", 100, 50, 0),  # 100nF
    ("L1", "L_0805_2012Metric", "Inductor_SMD", 85, 60, 0),  # 铁氧体磁珠
    
    # === TAC部分 (6个) ===
    ("R1", "R_0805_2012Metric", "Resistor_SMD", 70, 75, 0),   # 100Ω 恒流设置
    ("C1", "C_0805_2012Metric", "Capacitor_SMD", 75, 80, 0),  # 100pF NP0
    ("Q1", "SOT-23", "Package_TO_SOT_SMD", 65, 70, 0),  # 放电开关
    ("D1", "D_SOD-123", "Diode_SMD", 60, 75, 0),  # 保护二极管
    
    # === ADC核心 (8个) ===
    ("U1", "MSOP-10_3x3mm_P0.5mm", "Package_SO", 50, 85, 0),  # AD7980
    ("U2", "SOIC-8_3.9x4.9mm_P1.27mm", "Package_SO", 35, 85, 0),  # REF5050
    ("C2", "C_0805_2012Metric", "Capacitor_SMD", 55, 80, 0),  # ADC去耦
    ("C3", "C_0805_2012Metric", "Capacitor_SMD", 55, 90, 0),  # ADC去耦
    ("C4", "C_0805_2012Metric", "Capacitor_SMD", 30, 80, 0),  # 基准去耦
    ("C5", "C_0805_2012Metric", "Capacitor_SMD", 30, 90, 0),  # 基准去耦
    ("R2", "R_0805_2012Metric", "Resistor_SMD", 40, 95, 0),  # SPI上拉
    ("R3", "R_0805_2012Metric", "Resistor_SMD", 45, 95, 0),  # SPI上拉
    
    # === 运放驱动 (6个) ===
    ("U4", "SOIC-8_3.9x4.9mm_P1.27mm", "Package_SO", 70, 90, 0),  # ADC驱动运放
    ("C6", "C_0805_2012Metric", "Capacitor_SMD", 75, 95, 0),  # 运放去耦
    ("C7", "C_0805_2012Metric", "Capacitor_SMD", 65, 95, 0),  # 运放去耦
    ("R4", "R_0805_2012Metric", "Resistor_SMD", 75, 85, 0),  # 反馈电阻
    ("R5", "R_0805_2012Metric", "Resistor_SMD", 65, 85, 0),  # 输入电阻
    ("R6", "R_0805_2012Metric", "Resistor_SMD", 60, 95, 0),  # 偏置电阻
    
    # === 接口 (6个) ===
    ("J1", "PinHeader_2x10_P2.54mm_Vertical", "Connector_PinHeader_2.54mm", 25, 100, 0),  # PMOD
    ("J2", "SMA_Amphenol_132134_Vertical", "Connector_Coaxial", 50, 65, 0),  # 触发输入
    ("J3", "PinHeader_1x04_P2.54mm_Vertical", "Connector_PinHeader_2.54mm", 85, 100, 0),  # 调试口
    
    # === 保护 (4个) ===
    ("D2", "D_SOD-123", "Diode_SMD", 55, 70, 0),  # TVS保护
    ("D3", "D_SOD-123", "Diode_SMD", 50, 75, 0),  # TVS保护
    ("F1", "Fuse_1206_3216Metric", "Fuse", 90, 70, 0),  # 保险丝
    ("L2", "L_0805_2012Metric", "Inductor_SMD", 80, 100, 0),  # 电源滤波
    
    # === 额外去耦 (10个) ===
    ("C8", "C_0805_2012Metric", "Capacitor_SMD", 45, 75, 0),
    ("C9", "C_0805_2012Metric", "Capacitor_SMD", 40, 80, 0),
    ("C10","C_0805_2012Metric", "Capacitor_SMD", 35, 75, 0),
    ("C15","C_0805_2012Metric", "Capacitor_SMD", 80, 65, 0),
    ("C16","C_0805_2012Metric", "Capacitor_SMD", 80, 70, 0),
    ("R7", "R_0805_2012Metric", "Resistor_SMD", 55, 95, 0),
    ("R8", "R_0805_2012Metric", "Resistor_SMD", 60, 100, 0),
    ("R9", "R_0805_2012Metric", "Resistor_SMD", 65, 100, 0),
    ("R10","R_0805_2012Metric", "Resistor_SMD", 70, 100, 0),
    ("TP1","TestPoint_2Pads_Pitch2.54mm_Drill0.8mm", "TestPoint", 90, 85, 0),
]

print("搜索封装文件...")
comps_ok = []
for ref, name, lib, x, y, rot in comps:
    p = fp(name)
    if p:
        comps_ok.append((ref, str(p.relative_to(LIB)), lib, x, y, rot))
    else:
        print(f"  MISS: {ref} ({name})")

print(f"\n有效元件: {len(comps_ok)}/{len(comps)}")

# 生成PCB
lines = []
L = lines.append
L('(kicad_pcb')
L('\t(version 20260206)')
L('\t(generator "pcbnew") (generator_version "10.0")')
L('\t(general (thickness 1.6) (legacy_teardrops no))')
L('\t(paper "A4")')
L('	(layers (0 "F.Cu" signal) (2 "B.Cu" signal) (4 "In1.Cu" signal) (6 "In2.Cu" signal)')
L('		(5 "F.SilkS" user "F.Silkscreen") (7 "B.SilkS" user "B.Silkscreen")')
L('		(1 "F.Mask" user) (3 "B.Mask" user)')
L('		(25 "Edge.Cuts" user)')
L('\t\t(31 "F.CrtYd" user "F.Courtyard") (29 "B.CrtYd" user "B.Courtyard")')
L('\t\t(35 "F.Fab" user) (33 "B.Fab" user))')
L('\t(setup (pad_to_mask_clearance 0) (allow_soldermask_bridges_in_footprints no)')
L('\t\t(tenting (front yes) (back yes)) (capping no) (filling no)')
L('\t\t(pcbplotparams (outputformat 1) (drillshape 1) (outputdirectory "")))')

for ref, fp_rel, lib, x, y, rot in comps_ok:
    p = LIB / fp_rel
    content = p.read_text(encoding='utf-8')
    content = re.sub(r'\(version \d+\)\s*\(generator "[^"]*\)', '', content)
    content = re.sub(r'\(property "Reference" "[^"]*"', f'(property "Reference" "{ref}"', content)
    content = re.sub(r'\(at [-\d.]+ [-\d.]+ [-\d.]+\)', f'(at {x} {y} {rot})', content, count=1)
    L(content)

board_w, board_h = 110, 120
for sx,sy,ex,ey in [(0,0,board_w,0),(board_w,0,board_w,board_h),(board_w,board_h,0,board_h),(0,board_h,0,0)]:
    L(f'\t(gr_line (start {sx} {sy}) (end {ex} {ey}) (stroke (width 0.2) (type default)) (layer "Edge.Cuts") (uuid "{gu()}"))')
L('\t(embedded_fonts no)')
L(')')

OUT.write_text('\n'.join(lines), encoding='utf-8')
sz = OUT.stat().st_size
pads = '\n'.join(lines).count('(pad "')
print(f'\n✅ PCB生成: {OUT}')
print(f'   大小: {sz} bytes')
print(f'   元件: {len(comps_ok)}个, 焊盘: {pads}个')
print(f'   板框: {board_w}x{board_h}mm')
