#!/usr/bin/env python3
"""SES → KiCad PCB走线导入器"""
import re, uuid, os

pcb_file = 'pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb'
ses_file = 'pcb/tdc_daughterboard/tdc_daughterboard.ses'

ses = open(ses_file).read()
pcb = open(pcb_file).read()

# 按网络分割
nets = re.split(r'\(net\s+', ses)[1:]  # 跳过第一个

segments = []
vias = []

layer_map = {
    'F.Cu': 'F.Cu', 'In1.Cu': 'In1.Cu', 'In2.Cu': 'In2.Cu', 'B.Cu': 'B.Cu',
}

for net_block in nets:
    net_name = net_block.split()[0]
    # 找wire路径
    for wire_m in re.finditer(r'\(path\s+(\S+)\s+(\d+)([\s\d.-]+)\)', net_block):
        layer = wire_m.group(1)
        width = float(wire_m.group(2)) / 1000  # um → mm
        coords = list(map(float, wire_m.group(3).strip().split()))
        
        for i in range(0, len(coords)-2, 2):
            x1, y1 = coords[i]/1000, -coords[i+1]/1000  # SES Y轴反转
            x2, y2 = coords[i+2]/1000, -coords[i+3]/1000
            uid = str(uuid.uuid4())
            segments.append(f'\t(segment (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f}) (width {width:.4f}) (layer "{layer_map.get(layer, layer)}") (net "") (uuid "{uid}"))')
    
    # 找via
    for via_m in re.finditer(r'\(via\s+"[^"]*"\s+([\d.-]+)\s+([\d.-]+)\)', net_block):
        x, y = float(via_m.group(1))/1000, -float(via_m.group(2))/1000
        uid = str(uuid.uuid4())
        vias.append(f'\t(via (at {x:.4f} {y:.4f}) (size 0.6) (drill 0.3) (layers "F.Cu" "In1.Cu" "In2.Cu" "B.Cu") (net "") (uuid "{uid}"))')

print(f'Segments: {len(segments)}, Vias: {len(vias)}')

# 插入PCB文件
all_new = '\n'.join(segments + vias)
new_pcb = re.sub(r'(\(embedded_fonts no\))', all_new + '\n\\1', pcb)
open(pcb_file, 'w').write(new_pcb)

# 验证
o = new_pcb.count('('); c = new_pcb.count(')')
print(f'Brackets: {o}/{c} OK' if o==c else f'Brackets: {o}/{c} MISMATCH')
s_count = new_pcb.count('(segment ')
v_count = new_pcb.count('(via ')
print(f'Segments in PCB: {s_count}')
print(f'Vias in PCB: {v_count}')
