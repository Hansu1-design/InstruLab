#!/usr/bin/env python3
"""生成完整DSN文件供Freerouting自动布线"""
import re
from pathlib import Path

pcb_file = 'pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb'
dsn_file = 'pcb/tdc_daughterboard/tdc_daughterboard.dsn'
content = open(pcb_file).read()

# 解析所有焊盘和连接
fps = re.split(r'(?=\(footprint )', content)
pads = {}; components = []; net_id = 0; nets = {}

for fp in fps:
    if not fp.startswith('(footprint'): continue
    ref_m = re.search(r'\(property "Reference" "([^"]+)"', fp)
    if not ref_m: continue
    ref = ref_m.group(1)
    at_m = re.search(r'\(at\s+([\d.-]+)\s+([\d.-]+)\s+[\d.-]+\)', fp)
    if not at_m: continue
    fx, fy = float(at_m.group(1)), float(at_m.group(2))
    
    fp_pads = []
    for pm in re.finditer(r'\(pad\s+"(\d+)"[\s\S]*?\(at\s+([\d.-]+)\s+([\d.-]+)', fp):
        px, py = float(pm.group(2)) + fx, float(pm.group(3)) + fy
        pn = f'{ref}-{pm.group(1)}'
        pads[pn] = (px, py)
        fp_pads.append((pm.group(1), px, py))
    components.append((ref, fx, fy, fp_pads))

# 定义网络连接
conns = [
    ('J1-1','U1-5','CS'),('J1-2','U1-3','SCLK'),('J1-3','U1-2','MOSI'),('J1-4','U1-4','MISO'),
    ('J2-1','R1-1','SIG'),('R1-2','C1-1','SIG2'),('C1-2','U1-10','ADC_IN'),
    ('U2-2','U1-7','VREF'),('J1-5','U1-6','VDD_3V3'),('J1-6','U3-1','VIN_5V'),
    ('U3-2','U1-1','VDD_3V3'),('J1-7','U3-3','EN'),
    ('C11-1','C12-1','VDD_3V3'),('C13-1','C14-1','VIN_5V'),
]

# 写DSN
dsn = []
dsn.append('(dsn_version 3.0)')
dsn.append('(version 1.0)')
dsn.append('(identifier tdc_daughterboard)')
dsn.append('(resolution mm 4)')
dsn.append('(unit mm)')
dsn.append('')

# Library
dsn.append('(library')
for ref, fx, fy, fp_pads in components:
    dsn.append(f'  (image "{ref}" (side front)')
    dsn.append(f'    (pin_names "")')
    for pn, px, py in fp_pads:
        dsn.append(f'    (pin "{ref}-{pn}")')
    dsn.append(f'  )')
dsn.append(')')
dsn.append('')

# Board
dsn.append('(board')
dsn.append('  (place')
for ref, fx, fy, fp_pads in components:
    dsn.append(f'    (component "{ref}"')
    dsn.append(f'      (place (place_number 1) (position {fx:.4f} {fy:.4f}) (rotation 0)))')
dsn.append('  )')
dsn.append('')

# Nets
dsn.append('  (wiring')
net_n = 0
for s, d, name in conns:
    if s not in pads or d not in pads:
        print(f'MISS: {s}->{d}')
        continue
    net_n += 1
    x1, y1 = pads[s]; x2, y2 = pads[d]
    dsn.append(f'    (net "{name}" (route (path (pt {x1:.4f} {y1:.4f}) (pt {x2:.4f} {y2:.4f})))))')
dsn.append('  )')
dsn.append(')')

open(dsn_file, 'w').write('\n'.join(dsn))
print(f'DSN written: {dsn_file}')
print(f'  Components: {len(components)}, Nets: {net_n}')
print(f'  打开Freerouting → 文件 → 打开 → tdc_daughterboard.dsn')
print(f'  然后点⭐(自动布线)按钮')
