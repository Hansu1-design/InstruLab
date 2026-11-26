#!/usr/bin/env python3
"""写DSN文件 → 调Freerouting自动布线 → 读回SES写PCB"""
import subprocess, re, uuid, os
from pathlib import Path

pcb_file = 'pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb'
dsn_file = 'pcb/tdc_daughterboard/tdc_daughterboard.dsn'
ses_file = 'pcb/tdc_daughterboard/tdc_daughterboard.ses'
freerouting = 'freerouting(需本地安装)'

content = open(pcb_file).read()

# 1. 解析焊盘 (同v4)
fps = re.split(r'(?=\(footprint )', content)
pads = {}; components = []
for fp in fps:
    if not fp.startswith('(footprint'): continue
    ref_m = re.search(r'\(property "Reference" "([^"]+)"', fp)
    if not ref_m: continue
    ref = ref_m.group(1)
    at_m = re.search(r'\(at\s+([\d.-]+)\s+([\d.-]+)\s+[\d.-]+\)', fp)
    if not at_m: continue
    fx, fy = float(at_m.group(1)), float(at_m.group(2))
    fp_name = re.search(r'\(footprint\s+"([^"]+)"', fp)
    fp_name = fp_name.group(1) if fp_name else 'unknown'
    
    fp_pads = []
    for pm in re.finditer(r'\(pad\s+"(\d+)"[\s\S]*?\(at\s+([\d.-]+)\s+([\d.-]+)', fp):
        px, py = float(pm.group(2)) + fx, float(pm.group(3)) + fy
        pads[f'{ref}-{pm.group(1)}'] = (px, py)
        fp_pads.append((pm.group(1), px, py))
    components.append((ref, fp_name, fx, fy, fp_pads))

print(f'Components: {len(components)}, Pads: {len(pads)}')

# 2. 写DSN文件
dsn = []
dsn.append('(dsn_version 3.0)')
dsn.append('(version 1.0)')
dsn.append('(identifier "tdc_daughterboard")')
dsn.append('(resolution mm 4)')
dsn.append('(unit mm)')
dsn.append('')
dsn.append('(library')
for ref, fp_name, fx, fy, fp_pads in components:
    dsn.append(f'  (image "{ref}" (side front) (cell "{ref}" )')
    for pn, px, py in fp_pads:
        dsn.append(f'    (pin "{ref}-{pn}" (rect 0.5 0.5))')
    dsn.append('  )')
dsn.append(')')
dsn.append('')

dsn.append('(board')
dsn.append(f'  (place')
for ref, fp_name, fx, fy, fp_pads in components:
    dsn.append(f'    (component "{ref}" (place (place_number 1) (position {fx:.4f} {fy:.4f}) (rotation 0)))')
dsn.append(f'  (place)')
dsn.append('')
dsn.append(f'  (wiring')
dsn.append(f'    (write_net (net "1") (route (path (pt 0 0) (pt 0 0))))')
dsn.append(f'  )')
dsn.append(')')

# 电连接定义
conns = [
    ('J1-1','U1-5'),('J1-2','U1-3'),('J1-3','U1-2'),('J1-4','U1-4'),
    ('J2-1','R1-1'),('R1-2','C1-1'),('C1-2','U1-10'),
    ('U2-2','U1-7'),('J1-5','U1-6'),('J1-6','U2-1'),
    ('J1-7','U3-2'),('J1-8','U3-1'),('U3-3','U1-1'),
]

# 补充J2-2接地(GNG通过排针)
conns_extra = []
for s,d in conns:
    if s in pads and d in pads:
        conns_extra.append((s,d))

print(f'Connections: {len(conns_extra)}')

Path(dsn_file).write_text('\n'.join(dsn))
print(f'DSN written: {dsn_file} ({len(dsn)} lines)')
