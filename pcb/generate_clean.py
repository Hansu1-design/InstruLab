#!/usr/bin/env python3
"""最终版: 从零生成PCB + 走线"""
from pathlib import Path
import re, uuid

LIB = Path("G:/kicad/share/kicad/footprints")
OUT = Path("pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb")

comps = [
    ("R1","Resistor_SMD.pretty/R_0805_2012Metric.kicad_mod","Resistor_SMD",76.2,76.2,90),
    ("C1","Capacitor_SMD.pretty/C_0805_2012Metric.kicad_mod","Capacitor_SMD",76.2,101.6,90),
    ("U1","Package_SO.pretty/MSOP-10_3x3mm_P0.5mm.kicad_mod","Package_SO",50.8,25.4,0),
    ("U2","Package_SO.pretty/SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod","Package_SO",76.2,25.4,0),
    ("U3","Package_SO.pretty/SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod","Package_SO",25.4,50.8,0),  # U3=ADP150 LDO
    ("J1","Connector_PinHeader_2.54mm.pretty/PinHeader_2x10_P2.54mm_Vertical.kicad_mod","Connector_PinHeader_2.54mm",25.4,101.6,0),
    ("J2","Connector_Coaxial.pretty/SMA_Amphenol_132134_Vertical.kicad_mod","Connector_Coaxial",50.8,50.8,0),
]

def gu(): return str(uuid.uuid4())

lines = []
def L(s): lines.append(s)

L('(kicad_pcb')
L('\t(version 20260206)')
L('\t(generator "pcbnew") (generator_version "10.0")')
L('\t(general (thickness 1.6) (legacy_teardrops no))')
L('\t(paper "A4")')
L('\t(layers')
L('\t\t(0 "F.Cu" signal) (2 "B.Cu" signal)')
L('\t\t(5 "F.SilkS" user "F.Silkscreen") (7 "B.SilkS" user "B.Silkscreen")')
L('\t\t(1 "F.Mask" user) (3 "B.Mask" user)')
L('\t\t(25 "Edge.Cuts" user)')
L('\t\t(31 "F.CrtYd" user "F.Courtyard") (29 "B.CrtYd" user "B.Courtyard")')
L('\t\t(35 "F.Fab" user) (33 "B.Fab" user))')
L('\t(setup')
L('\t\t(pad_to_mask_clearance 0)')
L('\t\t(allow_soldermask_bridges_in_footprints no)')
L('\t\t(tenting (front yes) (back yes))')
L('\t\t(capping no) (filling no)')
L('\t\t(pcbplotparams')
L('\t\t\t(layerselection 0x00000000_00000000_55555555_5755f5ff)')
L('\t\t\t(outputformat 1) (mirror no) (drillshape 1) (scaleselection 1)')
L('\t\t\t(outputdirectory "")))')

# 插入封装
fp_positions = {}
for ref, fp_file, lib_name, x, y, rot in comps:
    content = (LIB / fp_file).read_text(encoding='utf-8')
    content = re.sub(r'\(version \d+\)\s*\(generator "[^"]*\)', '', content)
    content = re.sub(r'\(property "Reference" "[^"]*"', '(property "Reference" "' + ref + '"', content)
    content = re.sub(r'\(at [-\d.]+ [-\d.]+ [-\d.]+\)', '(at ' + str(x) + ' ' + str(y) + ' ' + str(rot) + ')', content, count=1)
    fp_positions[ref] = (x, y, rot)
    L(content)

# 解析焊盘(从已生成的PCB内容中)
pads = {}
full_content = '\n'.join(lines)
for fp_match in re.finditer(r'\(footprint "([^"]*)"[\s\S]*?\(property "Reference" "([^"]+)"[\s\S]*?\(at\s+([\d.-]+)\s+([\d.-]+)[\s\S]*?(?=\(footprint|\(gr_line|\(embedded)', full_content):
    ref = fp_match.group(2)
    fx, fy = float(fp_match.group(3)), float(fp_match.group(4))
    fp_text = fp_match.group(0)
    for pm in re.finditer(r'\(pad\s+"(\d+)"[\s\S]*?\(at\s+([\d.-]+)\s+([\d.-]+)', fp_text):
        px, py = float(pm.group(2)) + fx, float(pm.group(3)) + fy
        pads[f'{ref}-{pm.group(1)}'] = (px, py)

print(f'Pads parsed: {len(pads)}')

# 连接
conns = [
    ('J1-1','U1-5',0.25),('J1-2','U1-3',0.25),('J1-3','U1-2',0.25),('J1-4','U1-4',0.25),
    ('J2-1','R1-1',0.3),('R1-2','C1-1',0.3),('C1-2','U1-10',0.3),
    ('U2-2','U1-7',0.25),('U1-8','U2-7',0.25),
    ('J1-5','U1-6',0.5),('J1-6','U2-1',0.5),
    ('J1-7','U3-2',0.25),('J1-8','U3-1',0.25),('U3-3','U1-1',0.25),
]

track_count = 0
for s,d,w in conns:
    if s not in pads or d not in pads:
        print(f'MISS: {s}->{d}')
        continue
    x1,y1 = pads[s]; x2,y2 = pads[d]
    track_count += 1
    uid = gu()
    mx = (x1+x2)/2
    L(f'\t(segment (start {x1:.4f} {y1:.4f}) (end {mx:.4f} {y1:.4f}) (width {w}) (layer "F.Cu") (net "") (uuid "{uid}"))')
    L(f'\t(segment (start {mx:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f}) (width {w}) (layer "F.Cu") (net "") (uuid "{uid}"))')

# 板框
for sx,sy,ex,ey in [(0,0,50,0),(50,0,50,40),(50,40,0,40),(0,40,0,0)]:
    L(f'\t(gr_line (start {sx} {sy}) (end {ex} {ey}) (stroke (width 0.2) (type default)) (layer "Edge.Cuts") (uuid "{gu()}"))')
L('\t(embedded_fonts no)')
L(')')

OUT.write_text('\n'.join(lines), encoding='utf-8')
sz = OUT.stat().st_size
t = '\n'.join(lines).count('(segment ')
p = '\n'.join(lines).count('(pad "')
print(f'PCB: {sz} bytes, {len(comps)} footprints, {p} pads, {t} segments')
