#!/usr/bin/env python3
"""生成正确格式的DSN文件 — 含完整网络定义"""
import re
from pathlib import Path

pcb_file = 'pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb'
dsn_file = 'pcb/tdc_daughterboard/tdc_daughterboard.dsn'
content = open(pcb_file).read()

# 解析焊盘坐标和元件
fps = re.split(r'(?=\(footprint )', content)
pads = {}; all_pins = []
for fp in fps:
    if not fp.startswith('(footprint'): continue
    ref_m = re.search(r'\(property "Reference" "([^"]+)"', fp)
    if not ref_m: continue
    ref = ref_m.group(1)
    at_m = re.search(r'\(at\s+([\d.-]+)\s+([\d.-]+)\s+[\d.-]+\)', fp)
    if not at_m: continue
    fx, fy = float(at_m.group(1)), float(at_m.group(2))
    for pm in re.finditer(r'\(pad\s+"(\d+)"[\s\S]*?\(at\s+([\d.-]+)\s+([\d.-]+)', fp):
        px, py = float(pm.group(2)) + fx, float(pm.group(3)) + fy
        pn = f'{ref}-{pm.group(1)}'
        pads[pn] = (px, py)
        all_pins.append((ref, pm.group(1), px, py))

# 网络定义: (源, 目标, 网络名)
conns = [
    ('J1-1','U1-5','CS'),('J1-2','U1-3','SCLK'),('J1-3','U1-2','MOSI'),('J1-4','U1-4','MISO'),
    ('J2-1','R1-1','SIG'),('R1-2','C1-1','TAC'),('C1-2','U1-10','ADC_IN'),
    ('U2-2','U1-7','VREF'),('U1-8','U2-7','REF_GND'),
    ('J1-5','U3-2','VDD'),('U3-3','U1-6','VDD'),
    ('J1-6','C11-1','V5V'),('C11-2','U2-1','V5V'),
    ('J2-2','D2-1','GND'),('C1-2','D2-2','GND'),
]

# 去重网络名
net_map = {}
for s,d,name in conns:
    if name not in net_map: net_map[name] = []
    if s in pads: net_map[name].append(s)
    if d in pads: net_map[name].append(d)

# 写DSN
dsn = []
dsn.append('(dsn_version 3.0)')
dsn.append('(version 1.0)')
dsn.append(f'(identifier "tdc_daughterboard")')
dsn.append('(resolution mm 4)')
dsn.append('(unit mm)')
dsn.append('')

# Library — 只声明引脚存在
dsn.append('(library')
for ref in set(p[0] for p in all_pins):
    fp_pins = [p for p in all_pins if p[0] == ref]
    dsn.append(f'  (image "{ref}" (side front))')
dsn.append(')')
dsn.append('')

# Board + Placement
dsn.append('(board')
dsn.append('  (place')
for ref in set(p[0] for p in all_pins):
    x,y = (25.4, 101.6)  # default
    for ref2, pn, px, py in all_pins:
         if ref2 == ref:
             x, y = px, py
             break
    dsn.append(f'    (component "{ref}"')
    dsn.append(f'      (place (place_number 1) (position {x:.4f} {y:.4f}) (rotation 0)))')
dsn.append('  )')
dsn.append('')

# Nets — 关键！必须用(pin ...)定义
dsn.append('  (wiring')
for name, pins in net_map.items():
    pins_uniq = list(set(pins))  # 去重
    pin_str = ' '.join([f'(pin "{p}")' for p in pins_uniq])
    dsn.append(f'    (net "{name}" {pin_str})')
dsn.append('  )')
dsn.append(')')

open(dsn_file, 'w').write('\n'.join(dsn))
net_count = len(net_map)
pin_count = sum(len(v) for v in net_map.values())
print(f'DSN: {dsn_file}')
print(f'  Components: {len(set(p[0] for p in all_pins))}')
print(f'  Pads: {len(all_pins)}')
print(f'  Nets: {net_count} ({pin_count} pins)')
print(f'')
print(f'现在Freerouting打开DSN后应该能识别网络了')
print(f'然后点⭐自动布线即可')
