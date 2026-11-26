#!/usr/bin/env python3
"""生成PCB+网络+走线 — 一次搞定"""
from pathlib import Path
import re, uuid

LIB = Path("G:/kicad/share/kicad/footprints")
OUT = Path("pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb")

def gu(): return str(uuid.uuid4())

# 网络定义
nets = [
    (1, "CS"), (2, "SCLK"), (3, "MOSI"), (4, "MISO"),
    (5, "SIG"), (6, "TAC"), (7, "ADC_IN"), (8, "VREF"),
    (9, "VDD"), (10, "V5V"), (11, "GND"),
]

net_map = {
    'J1-1':1,'U1-5':1, 'J1-2':2,'U1-3':2, 'J1-3':3,'U1-2':3, 'J1-4':4,'U1-4':4,
    'J2-1':5,'R1-1':5, 'R1-2':6,'C1-1':6, 'C1-2':7,'U1-10':7,
    'U2-2':8,'U1-7':8,
    'J1-5':9,'U3-2':9,'U3-3':9,'U1-6':9,
    'J1-6':10,'U2-1':10,
    'J2-2':11,'D2-1':11,
}

comps = [
    ("R1","Resistor_SMD/R_0805_2012Metric","Resistor_SMD",70,75,0),
    ("C1","Capacitor_SMD/C_0805_2012Metric","Capacitor_SMD",75,80,0),
    ("U1","Package_SO/MSOP-10_3x3mm_P0.5mm","Package_SO",50,85,0),
    ("U2","Package_SO/SOIC-8_3.9x4.9mm_P1.27mm","Package_SO",35,85,0),
    ("U3","Package_TO_SOT_SMD/SOT-223-3_TabPin2","Package_TO_SOT_SMD",90,60,0),
    ("U4","Package_SO/SOIC-8_3.9x4.9mm_P1.27mm","Package_SO",70,90,0),
    ("J1","Connector_PinHeader_2.54mm/PinHeader_2x10_P2.54mm_Vertical","Connector_PinHeader_2.54mm",25,100,0),
    ("J2","Connector_Coaxial/SMA_Amphenol_132134_Vertical","Connector_Coaxial",50,65,0),
    ("D1","Diode_SMD/D_SOD-123","Diode_SMD",60,75,0),
    ("D2","Diode_SMD/D_SOD-123","Diode_SMD",55,70,0),
    ("Q1","Package_TO_SOT_SMD/SOT-23","Package_TO_SOT_SMD",65,70,0),
    ("F1","Fuse/Fuse_1206_3216Metric","Fuse",90,70,0),
    ("TP1","TestPoint/TestPoint_2Pads_Pitch2.54mm_Drill0.8mm","TestPoint",90,85,0),
    ("L1","Inductor_SMD/L_0805_2012Metric","Inductor_SMD",85,60,0),
    ("L2","Inductor_SMD/L_0805_2012Metric","Inductor_SMD",80,100,0),
]
for i in range(1,11): comps.append((f"C{i+1}","Capacitor_SMD/C_0805_2012Metric","Capacitor_SMD",20+i*3,70+i%3*5,0))
for i in range(1,9): comps.append((f"R{i+1}","Resistor_SMD/R_0805_2012Metric","Resistor_SMD",30+i*2,85+i%4*3,0))

# 生成PCB
content = []
def L(s): content.append(s)

L('(kicad_pcb')
L('\t(version 20260206)')
L('\t(generator "pcbnew") (generator_version "10.0")')
L('\t(general (thickness 1.6) (legacy_teardrops no))')
L('\t(paper "A4")')
L('\t(layers (0 "F.Cu" signal) (2 "B.Cu" signal)')
L('\t\t(5 "F.SilkS" user "F.Silkscreen") (7 "B.SilkS" user "B.Silkscreen")')
L('\t\t(1 "F.Mask" user) (3 "B.Mask" user)')
L('\t\t(25 "Edge.Cuts" user) (31 "F.CrtYd" user "F.Courtyard") (29 "B.CrtYd" user "B.Courtyard")')
L('\t\t(35 "F.Fab" user) (33 "B.Fab" user))')
L('\t(setup (pad_to_mask_clearance 0) (allow_soldermask_bridges_in_footprints no)')
L('\t\t(tenting (front yes) (back yes)) (capping no) (filling no)')
L('\t\t(pcbplotparams (outputformat 1) (drillshape 1) (outputdirectory "")))')

for ref, fp_name, lib, x, y, rot in comps:
    # 只搜文件名, 不管目录
    fp_name_short = fp_name.split('/')[-1]
    found = list(LIB.rglob(f"*{fp_name_short}*.kicad_mod"))
    if not found: continue
    fp_content = found[0].read_text(encoding='utf-8')
    fp_content = re.sub(r'\(version \d+\)\s*\(generator "[^"]*\)', '', fp_content)
    fp_content = re.sub(r'\(property "Reference" "[^"]*"', f'(property "Reference" "{ref}"', fp_content)
    fp_content = re.sub(r'\(at [-\d.]+ [-\d.]+ [-\d.]+\)', f'(at {x} {y} {rot})', fp_content, count=1)
    # 为焊盘添加网络
    for pad_key, net_n in net_map.items():
        pad_ref, pin = pad_key.split('-')
        if pad_ref == ref:
            # 在pad定义中添加(net n)
            fp_content = re.sub(
                rf'(\(pad\s+"{pin}"[\s\S]*?\))\)',
                lambda m: m.group(1) + f' (net {net_n}))',
                fp_content
            )
    L(fp_content)

# 网络定义
for n, name in nets:
    L(f'\t(net {n} "{name}")')

# 板框
for sx,sy,ex,ey in [(0,0,120,0),(120,0,120,100),(120,100,0,100),(0,100,0,0)]:
    L(f'\t(gr_line (start {sx} {sy}) (end {ex} {ey}) (stroke (width 0.2) (type default)) (layer "Edge.Cuts") (uuid "{gu()}"))')
L('\t(embedded_fonts no)')
L(')')

OUT.write_text('\n'.join(content))
b = '\n'.join(content).count('(') == '\n'.join(content).count(')')
print(f'PCB: {OUT.stat().st_size} bytes, Brackets: {"OK" if b else "MISMATCH"}')
print(f'Nets assigned: {len(net_map)} pads, {len(nets)} nets')
print(f'\n打开KiCad → PCB编辑器 → 文件 → 导出 → Specctra DSN')
print(f'然后Freerouting打开DSN → 自动布线')
