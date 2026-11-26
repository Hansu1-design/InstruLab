#!/usr/bin/env python3
"""智能45度走线引擎 — 写入PCB文件"""
import re, uuid, math
from pathlib import Path

PCB = Path("pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb")
content = PCB.read_text()

# 1. 解析焊盘
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

def route_45(x1, y1, x2, y2, width, layer, net):
    """生成45度走线(使用两个45度角, 避免直角)"""
    uid = str(uuid.uuid4())
    dx = x2 - x1
    dy = y2 - y1
    segments = []
    
    if abs(dx) > abs(dy):
        # 水平主导: 先水平走一半, 45度斜走, 再水平
        mx = (x1 + x2) / 2
        my = y1
        segments.append((x1, y1, mx, my, uid))
        # 45度斜走
        if dy != 0:
            # 从中间斜着到目标Y
            offset = min(abs(dx)/4, abs(dy))
            cx = mx + offset * (1 if dx > 0 else -1)
            cy = my + offset * (1 if dy > 0 else -1)
            segments.append((mx, my, cx, cy, uid))
            segments.append((cx, cy, x2, y2, uid))
        else:
            segments.append((mx, my, x2, y2, uid))
    else:
        # 垂直主导
        my = (y1 + y2) / 2
        mx = x1
        segments.append((x1, y1, mx, my, uid))
        if dx != 0:
            offset = min(abs(dy)/4, abs(dx))
            cx = mx + offset * (1 if dx > 0 else -1)
            cy = my + offset * (1 if dy > 0 else -1)
            segments.append((mx, my, cx, cy, uid))
            segments.append((cx, cy, x2, y2, uid))
        else:
            segments.append((mx, my, x2, y2, uid))
    
    result = []
    for sx, sy, ex, ey, u in segments:
        result.append(f'\t(segment (start {sx:.4f} {sy:.4f}) (end {ex:.4f} {ey:.4f}) (width {width}) (layer "{layer}") (net "{net}") (uuid "{u}"))')
    return result

# 连接定义 (源, 目标, 线宽mm, 网络名)
conns = [
    ('J1-1','U1-5',0.25,'CS'),   ('J1-2','U1-3',0.25,'SCLK'),
    ('J1-3','U1-2',0.25,'MOSI'), ('J1-4','U1-4',0.25,'MISO'),
    ('J2-1','R1-1',0.3,'SIG_IN'),('R1-2','C1-1',0.3,'TAC'),
    ('C1-2','U1-10',0.3,'ADC_IN'),
    ('U2-2','U1-7',0.25,'VREF'),('J1-5','U1-6',0.5,'VDD'),
    ('J1-6','U3-1',0.5,'VIN'),  ('U3-3','U1-1',0.3,'VDD'),
    ('U4-1','R4-1',0.25,'FB'),  ('R5-1','U4-2',0.25,'IN'),
    ('R6-1','U4-3',0.25,'BIAS'),
]

# 生成走线
all_tracks = []
for s, d, w, n in conns:
    if s not in pads or d not in pads:
        print(f'MISS: {s}->{d}')
        continue
    x1, y1 = pads[s]; x2, y2 = pads[d]
    tracks = route_45(x1, y1, x2, y2, w, 'F.Cu', n)
    all_tracks.extend(tracks)

print(f'Tracks: {len(all_tracks)} segments')

# 写入PCB(在embedded_fonts前插入)
tracks_text = '\n'.join(all_tracks)
new_content = re.sub(r'(\(embedded_fonts no\))', tracks_text + '\n\\1', content)
PCB.write_text(new_content)
print(f'PCB: {len(new_content)} bytes')
