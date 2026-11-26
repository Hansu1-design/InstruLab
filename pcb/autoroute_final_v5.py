#!/usr/bin/env python3
"""PCB自动布线 v5 — 生成最终走线"""
import re

pcb_file = 'pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb'
content = open(pcb_file).read()

# 解析焊盘
fps = re.split(r'(?=\(footprint )', content)
pads = {}
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
        pads[f'{ref}-{pm.group(1)}'] = (px, py)

print(f'Pads: {len(pads)}')

# 连接定义 (源, 目标, 线宽mm)
conns = [
    # J1(PMOD) -> U1(AD7980) SPI
    ('J1-1','U1-5',0.25),  # CS -> CNV
    ('J1-2','U1-3',0.25),  # SCLK -> SCK
    ('J1-3','U1-2',0.25),  # MOSI -> SDI
    ('J1-4','U1-4',0.25),  # MISO <- SDO
    
    # J2(SMA) -> R1 -> C1 -> U1(ADC输入)
    ('J2-1','R1-1',0.3),   # SMA信号 -> R1
    ('R1-2','C1-1',0.3),   # R1 -> C1
    ('C1-2','U1-10',0.3),  # C1 -> U1 IN+
    
    # U2(REF5050) -> U1(ADC基准)
    ('U2-2','U1-7',0.25),  # REF Vout -> U1 VREF
    
    # 电源 (来自J1)
    ('J1-5','U1-6',0.5),   # 3.3V -> U1 VDD
    ('J1-6','U2-1',0.5),   # 5V -> U2 Vin
    ('J1-7','U2-3',0.25),  # EN/控制
    ('J1-8','U1-1',0.25),  # 控制
]

# 生成走线 (曼哈顿布线)
tracks = []
nid = 0
for s,d,w in conns:
    if s not in pads or d not in pads:
        print(f'MISS: {s}({s in pads}) -> {d}({d in pads})')
        continue
    x1,y1 = pads[s]; x2,y2 = pads[d]
    nid += 1
    uid = f'r{nid:04d}-0000-0000-0000-{nid:04d}'
    mx = (x1+x2)/2
    tracks.append(f'\t(segment (start {x1:.4f} {y1:.4f}) (end {mx:.4f} {y1:.4f}) (width {w}) (layer "F.Cu") (net "") (uuid "{uid}"))')
    tracks.append(f'\t(segment (start {mx:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f}) (width {w}) (layer "F.Cu") (net "") (uuid "{uid}"))')

# 写入PCB
new_content = re.sub(r'(\(embedded_fonts no\))', '\n'.join(tracks) + '\n\\1', content)
open(pcb_file, 'w').write(new_content)
print(f'Tracks: {len(tracks)} segments, {len(conns)} connections')
print(f'PCB file written: {len(new_content)} bytes')
