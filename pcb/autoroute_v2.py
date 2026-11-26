#!/usr/bin/env python3
"""从PCB文件直接解析焊盘绝对坐标并生成走线"""
import re, uuid

pcb_file = 'pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb'
content = open(pcb_file).read()

# 解析: 找到每个footprint的reference,绝对位置,焊盘
# (footprint "lib:name" ... (at X Y rot) ... (pad "n" ... (at px py rot) ...) ...)
fp_pattern = re.compile(
    r'\(footprint\s+"[^"]*"[^)]*\)'  # 匹配footprint开始
    r'(?:\s*\([^)]*\))*?'             # 中间属性
    r'\s*\(at\s+([\d.-]+)\s+([\d.-]+)\s+[\d.-]+\)'  # at坐标
)

# 更简单的方法: 按footprint块切分
fps = re.split(r'(?=\(footprint )', content)
found = []
for fp in fps:
    if not fp.startswith('(footprint'): continue
    # 取Reference
    ref_m = re.search(r'\(property "Reference" "([^"]+)"', fp)
    if not ref_m: continue
    ref = ref_m.group(1)
    # 取footprint绝对位置
    at_m = re.search(r'\(at\s+([\d.-]+)\s+([\d.-]+)\s+[\d.-]+\)', fp)
    if not at_m: continue
    fx, fy = float(at_m.group(1)), float(at_m.group(2))
    # 取所有焊盘
    for pm in re.finditer(r'\(pad\s+"(\d+)"[^)]*\)\s*\(at\s+([\d.-]+)\s+([\d.-]+)\s+[\d.-]+\)', fp):
        px, py = float(pm.group(2)) + fx, float(pm.group(3)) + fy
        found.append((f'{ref}-{pm.group(1)}', px, py))

pads = {name:(x,y) for name,x,y in found}
for name,(x,y) in sorted(pads.items()):
    print(f'  {name:8s}: ({x:.2f}, {y:.2f})')

# 走线连接
conns = [
    ('J1-1','U1-5',0.3),('J1-2','U1-3',0.3),
    ('J1-3','U1-2',0.3),('J1-4','U1-4',0.3),
    ('J2-1','R1-1',0.3),('R1-2','C1-1',0.3),
    ('C1-2','U1-10',0.3),('U2-2','U1-7',0.3),
]

tracks = []
nid = 0
for s,d,w in conns:
    if s not in pads or d not in pads:
        print(f'SKIP: {s} or {d}')
        continue
    x1,y1 = pads[s]; x2,y2 = pads[d]
    nid += 1
    uid = f'{nid:08d}-0000-0000-0000-{nid:08d}'
    mx = (x1+x2)/2
    tracks.append(f'\t(segment (start {x1:.2f} {y1:.2f}) (end {mx:.2f} {y1:.2f}) (width {w}) (layer "F.Cu") (net "") (uuid "{uid}"))')
    tracks.append(f'\t(segment (start {mx:.2f} {y1:.2f}) (end {x2:.2f} {y2:.2f}) (width {w}) (layer "F.Cu") (net "") (uuid "{uid}"))')

# 写入PCB文件
new_content = re.sub(r'(\(embedded_fonts no\))', '\n'.join(tracks) + '\n\\1', content)
open(pcb_file, 'w').write(new_content)
print(f'\nAdded {len(tracks)} tracks, Total pads: {len(pads)}')
