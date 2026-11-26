#!/usr/bin/env python3
"""DSN v3 — 正确格式: 库内有pin定义, 网络引用pin"""
import re
from pathlib import Path

pcb_file = 'pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb'
dsn_file = 'pcb/tdc_daughterboard/tdc_daughterboard.dsn'
content = open(pcb_file).read()

# 解析
fps = re.split(r'(?=\(footprint )', content)
pads = {}; comp_pins = {}  # 每个元件的引脚列表
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
        if ref not in comp_pins: comp_pins[ref] = []
        comp_pins[ref].append((pm.group(1), px, py))

# 网络
conns = [
    ('J1-1','U1-5','CS'),('J1-2','U1-3','SCLK'),('J1-3','U1-2','MOSI'),('J1-4','U1-4','MISO'),
    ('J2-1','R1-1','SIG'),('R1-2','C1-1','TAC'),('C1-2','U1-10','ADC_IN'),
    ('U2-2','U1-7','VREF'),
    ('J1-5','U3-2','VDD'),('U3-3','U1-6','VDD'),
    ('J1-6','C11-1','V5V'),('C11-2','U2-1','V5V'),
    ('J2-2','D2-1','GND'),
]

nets = {}
for s,d,name in conns:
    if name not in nets: nets[name] = []
    if s in pads: nets[name].append(s)
    if d in pads: nets[name].append(d)

# 写DSN
dsn = []
dsn.append('(dsn_version 3.0)')
dsn.append('(version 1.0)')
dsn.append('(identifier "tdc_daughterboard")')
dsn.append('(resolution mm 4)')
dsn.append('(unit mm)')

# Library — 每个image内必须有pin定义
dsn.append('')
dsn.append('(library')
for ref, pins in sorted(comp_pins.items()):
    dsn.append(f'  (image "{ref}" (side front)')
    for pn, px, py in pins:
        dsn.append(f'    (pin "{ref}-{pn}")')
    dsn.append('  )')
dsn.append(')')

# Board — 放置元件
dsn.append('')
dsn.append('(board')
dsn.append('  (place')
for ref, pins in sorted(comp_pins.items()):
    px = sum(p[1] for p in pins)/len(pins)
    py = sum(p[2] for p in pins)/len(pins)
    dsn.append(f'    (component "{ref}"')
    dsn.append(f'      (place (place_number 1) (position {px:.4f} {py:.4f}) (rotation 0)))')
dsn.append('  )')

# 网络定义 (必须是 (net name (pin ...) (pin ...)) 格式)
dsn.append('')
dsn.append('  (wiring')
for name, pin_list in sorted(nets.items()):
    pin_list = list(set(pin_list))
    # Freerouting要求: (net "name" (pin "ref-pin") ...)
    pins_str = ' '.join([f'(pin "{p}")' for p in pin_list])
    dsn.append(f'    (net "{name}" {pins_str})')
dsn.append('  )')
dsn.append(')')

open(dsn_file, 'w').write('\n'.join(dsn))
all_nets = sum(len(v) for v in nets.values())
print(f'DSN v3: {dsn_file}')
print(f'  Components: {len(comp_pins)}, Library pins: {sum(len(v) for v in comp_pins.values())}')
print(f'  Nets: {len(nets)}, Total pin refs: {all_nets}')
print(f'')
print(f'Freerouting现在应该能识别网络了')
print(f'如果还是"0 unrouted nets", 试试手动点一下:')
print(f'  文件 → 打开 → 选 DSN')
print(f'  然后 ⭐自动布线')
