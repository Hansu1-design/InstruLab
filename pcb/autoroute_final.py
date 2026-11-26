#!/usr/bin/env python3
"""KiCad PCB自动布线 — 读取绝对焊盘坐标并生成走线"""
import sys
sys.path.insert(0, 'G:/kicad/bin/Lib/site-packages')
import pcbnew
import uuid, re

board = pcbnew.LoadBoard('pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb')

# 读取所有焊盘的绝对坐标
pads_all = {}
for fp in board.GetFootprints():
    ref = fp.GetReference()
    fx = fp.GetPosition().x / 1e6  # 封装绝对X(mm)
    fy = fp.GetPosition().y / 1e6  # 封装绝对Y(mm)
    for pad in fp.Pads():
        pn = pad.GetNumber()
        px = (fp.GetPosition().x + pad.GetPosition().x) / 1e6
        py = (fp.GetPosition().y + pad.GetPosition().y) / 1e6
        pads_all[f'{ref}-{pn}'] = (px, py)

print('Absolute pad coordinates:')
for name, (x, y) in sorted(pads_all.items()):
    print(f'  {name:8s}: ({x:.2f}, {y:.2f})')

# 生成走线: SPI连接
# U1(AD7980) <-> J1(PMOD)
# U1-5(CNV) <- J1-1(CS), U1-3(SCK) <- J1-2(SCLK), U1-2(SDI) <- J1-3(MOSI), U1-4(SDO) -> J1-4(MISO)
connections = [
    ('J1-1',  'U1-5',  0.3),
    ('J1-2',  'U1-3',  0.3),
    ('J1-3',  'U1-2',  0.3),
    ('J1-4',  'U1-4',  0.3),
    ('J2-1',  'R1-1',  0.3),   # SMA -> R1
    ('R1-2',  'C1-1',  0.3),   # R1 -> C1
    ('C1-2',  'U1-10', 0.3),   # C1 -> U1 IN+
    ('U2-2',  'U1-7',  0.3),   # REF5050 Vout -> U1 VREF
    ('U2-6',  'U1-8',  0.3),   # REF5050 FB -> U1 input
]

# 生成走线segment
tracks_text = []
uid_num = 0
for src, dst, w in connections:
    if src not in pads_all or dst not in pads_all:
        print(f'WARN: Cannot find {src} or {dst}')
        continue
    x1, y1 = pads_all[src]
    x2, y2 = pads_all[dst]
    uid_num += 1
    uid = f'00000000-0000-0000-0000-{uid_num:012d}'
    # Manhattan routing: horizontal then vertical
    mx = (x1 + x2) / 2  # midpoint
    tracks_text.append(f'\t(segment (start {x1:.2f} {y1:.2f}) (end {mx:.2f} {y1:.2f}) (width {w}) (layer "F.Cu") (net "") (uuid "{uid}"))')
    tracks_text.append(f'\t(segment (start {mx:.2f} {y1:.2f}) (end {x2:.2f} {y2:.2f}) (width {w}) (layer "F.Cu") (net "") (uuid "{uid}"))')

# 读原PCB文件, 插入走线
pcb_path = 'pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb'
content = open(pcb_path).read()
content = re.sub(r'(\(embedded_fonts no\))', '\n'.join(tracks_text) + r'\n\1', content)
open(pcb_path, 'w').write(content)

print(f'\nGenberated {len(tracks_text)} track segments')
print(f'Total pads: {len(pads_all)}')
