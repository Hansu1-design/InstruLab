#!/usr/bin/env python3
"""可布线PCB — 合理布局, 留出走线通道"""
from pathlib import Path
import re, uuid

LIB = Path("G:/kicad/share/kicad/footprints")
OUT = Path("pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb")

def gu(): return str(uuid.uuid4())
def fp(name):
    found = list(LIB.rglob(f"*{name}*.kicad_mod"))
    return found[0] if found else None

# 元件布局 (x, y) — 留出走线空间
comps = [
    # === 连接器(边缘) ===
    ("J1", "PinHeader_2x10_P2.54mm_Vertical", "Connector_PinHeader_2.54mm", 10, 95, 0),
    ("J2", "SMA_Amphenol_132134_Vertical", "Connector_Coaxial", 50, 130, 0),
    
    # === 电源(左上角) ===
    ("U3", "SOT-223-3_TabPin2", "Package_TO_SOT_SMD", 15, 15, 0),
    ("C11","C_0805_2012Metric", "Capacitor_SMD", 30, 10, 0),
    ("C12","C_0805_2012Metric", "Capacitor_SMD", 40, 10, 0),
    ("C13","C_0805_2012Metric", "Capacitor_SMD", 30, 25, 0),
    ("C14","C_0805_2012Metric", "Capacitor_SMD", 40, 25, 0),
    ("L1", "L_0805_2012Metric", "Inductor_SMD", 50, 15, 0),
    
    # === TAC和信号调理(右中) ===
    ("D2", "D_SOD-123", "Diode_SMD", 75, 115, 0),
    ("D1", "D_SOD-123", "Diode_SMD", 85, 115, 0),
    ("R1", "R_0805_2012Metric", "Resistor_SMD", 65, 105, 0),
    ("C1", "C_0805_2012Metric", "Capacitor_SMD", 65, 95, 0),
    ("Q1", "SOT-23", "Package_TO_SOT_SMD", 55, 105, 0),
    
    # === ADC核心(右下) ===
    ("U1", "MSOP-10_3x3mm_P0.5mm", "Package_SO", 105, 95, 0),
    ("U2", "SOIC-8_3.9x4.9mm_P1.27mm", "Package_SO", 110, 75, 0),
    ("C2", "C_0805_2012Metric", "Capacitor_SMD", 95, 85, 0),
    ("C3", "C_0805_2012Metric", "Capacitor_SMD", 100, 100, 0),
    ("C4", "C_0805_2012Metric", "Capacitor_SMD", 105, 70, 0),
    ("C5", "C_0805_2012Metric", "Capacitor_SMD", 115, 70, 0),
    ("R2", "R_0805_2012Metric", "Resistor_SMD", 120, 85, 0),
    ("R3", "R_0805_2012Metric", "Resistor_SMD", 120, 95, 0),
    
    # === 运放驱动(左下) ===
    ("U4", "SOIC-8_3.9x4.9mm_P1.27mm", "Package_SO", 10, 55, 0),
    ("C6", "C_0805_2012Metric", "Capacitor_SMD", 25, 50, 0),
    ("C7", "C_0805_2012Metric", "Capacitor_SMD", 25, 60, 0),
    ("R4", "R_0805_2012Metric", "Resistor_SMD", 25, 70, 0),
    ("R5", "R_0805_2012Metric", "Resistor_SMD", 35, 70, 0),
    ("R6", "R_0805_2012Metric", "Resistor_SMD", 45, 70, 0),
    
    # === 辅助去耦(分散) ===
    ("C8", "C_0805_2012Metric", "Capacitor_SMD", 120, 110, 0),
    ("C9", "C_0805_2012Metric", "Capacitor_SMD", 120, 12, 0),
    ("C10","C_0805_2012Metric", "Capacitor_SMD", 95, 110, 0),
    ("C15","C_0805_2012Metric", "Capacitor_SMD", 50, 10, 0),
    ("C16","C_0805_2012Metric", "Capacitor_SMD", 50, 25, 0),
    ("F1", "Fuse_1206_3216Metric", "Fuse", 55, 12, 0),
    ("L2", "L_0805_2012Metric", "Inductor_SMD", 5, 75, 0),
    ("R7", "R_0805_2012Metric", "Resistor_SMD", 120, 105, 0),
    ("R8", "R_0805_2012Metric", "Resistor_SMD", 95, 70, 0),
    ("R9", "R_0805_2012Metric", "Resistor_SMD", 55, 12, 0),
    ("R10","R_0805_2012Metric", "Resistor_SMD", 60, 12, 0),
    ("TP1","TestPoint_2Pads_Pitch2.54mm_Drill0.8mm", "TestPoint", 130, 120, 0),
]

print("搜索封装...")
comps_ok = []
for ref, name, lib, x, y, rot in comps:
    p = fp(name)
    if p:
        comps_ok.append((ref, str(p.relative_to(LIB)), lib, x, y, rot))
    else:
        print(f"  MISS: {ref}")

print(f"元件: {len(comps_ok)}/{len(comps)}")

lines = []
L = lines.append
board_w, board_h = 150, 145

L('(kicad_pcb')
L('\t(version 20260206)')
L('\t(generator "pcbnew") (generator_version "10.0")')
L('\t(general (thickness 1.6) (legacy_teardrops no))')
L('\t(paper "A4")')
L('\t(layers (0 "F.Cu" signal) (4 "In1.Cu" signal) (6 "In2.Cu" signal) (2 "B.Cu" signal)')
L('\t\t(5 "F.SilkS" user "F.Silkscreen") (7 "B.SilkS" user "B.Silkscreen")')
L('\t\t(1 "F.Mask" user) (3 "B.Mask" user)')
L('\t\t(25 "Edge.Cuts" user)')
L('\t\t(31 "F.CrtYd" user "F.Courtyard") (29 "B.CrtYd" user "B.Courtyard")')
L('\t\t(35 "F.Fab" user) (33 "B.Fab" user))')
L('\t(setup (pad_to_mask_clearance 0) (allow_soldermask_bridges_in_footprints no)')
L('\t\t(tenting (front yes) (back yes)) (capping no) (filling no)')
L('\t\t(pcbplotparams (outputformat 1) (drillshape 1) (outputdirectory "")))')

for ref, fp_rel, lib, x, y, rot in comps_ok:
    content = (LIB / fp_rel).read_text(encoding='utf-8')
    content = re.sub(r'\(version \d+\)\s*\(generator "[^"]*\)', '', content)
    content = re.sub(r'\(property "Reference" "[^"]*"', f'(property "Reference" "{ref}"', content)
    content = re.sub(r'\(at [-\d.]+ [-\d.]+ [-\d.]+\)', f'(at {x} {y} {rot})', content, count=1)
    L(content)

for sx,sy,ex,ey in [(0,0,board_w,0),(board_w,0,board_w,board_h),(board_w,board_h,0,board_h),(0,board_h,0,0)]:
    L(f'\t(gr_line (start {sx} {sy}) (end {ex} {ey}) (stroke (width 0.2) (type default)) (layer "Edge.Cuts") (uuid "{gu()}"))')
L('\t(embedded_fonts no)')
L(')')

OUT.write_text('\n'.join(lines), encoding='utf-8')
sz = OUT.stat().st_size
pads = '\n'.join(lines).count('(pad "')
print(f'PCB: {sz} bytes, {len(comps_ok)} comps, {pads} pads, {board_w}x{board_h}mm')
