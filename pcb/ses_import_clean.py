#!/usr/bin/env python3
"""强制生成干净PCB + 导入SES走线"""
from pathlib import Path
import re, uuid

pcb_file = 'pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb'
ses_file = 'pcb/tdc_daughterboard/tdc_daughterboard.ses'

# 1. 先生成干净PCB
exec(open('pcb/generate_v6_pro.py').read().split('# === 铜皮跳过')[0])

# 2. 读取刚生成的PCB
pcb = open(pcb_file).read()
cnt = pcb.count('(segment ')
print(f'Before SES import: {cnt} segments')

# 3. 解析SES
ses = open(ses_file).read()
nets = re.split(r'\(net\s+', ses)[1:]

segments = []
layer_map = {'F.Cu':'F.Cu','In1.Cu':'In1.Cu','In2.Cu':'In2.Cu','B.Cu':'B.Cu'}

for net_block in nets:
    net_name = net_block.split()[0]
    for wire_m in re.finditer(r'\(path\s+(\S+)\s+(\d+)([\s\d.-]+)\)', net_block):
        layer = wire_m.group(1)
        w = float(wire_m.group(2)) / 1000
        coords = list(map(float, wire_m.group(3).strip().split()))
        for i in range(0, len(coords)-2, 2):
            x1 = coords[i]/1000; y1 = -coords[i+1]/1000
            x2 = coords[i+2]/1000; y2 = -coords[i+3]/1000
            uid = str(uuid.uuid4())
            segments.append(f'\t(segment (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f}) (width {w:.4f}) (layer "{layer_map.get(layer,layer)}") (net "") (uuid "{uid}"))')
    
    for via_m in re.finditer(r'\(via\s+"[^"]*"\s+([\d.-]+)\s+([\d.-]+)\)', net_block):
        x = float(via_m.group(1))/1000; y = -float(via_m.group(2))/1000
        uid = str(uuid.uuid4())
        segments.append(f'\t(via (at {x:.4f} {y:.4f}) (size 0.6) (drill 0.3) (layers "F.Cu" "In1.Cu" "In2.Cu" "B.Cu") (net "") (uuid "{uid}"))')

print(f'SES parsed: {len(segments)} tracks/vias')
pcb = open(pcb_file).read()
pcb = re.sub(r'(\(embedded_fonts no\))', '\n'.join(segments) + '\n\\1', pcb)
open(pcb_file, 'w').write(pcb)

o = pcb.count('('); c = pcb.count(')')
s = pcb.count('(segment '); v = pcb.count('(via ')
print(f'Final: {s} segments, {v} vias, brackets {"OK" if o==c else "MISMATCH"}')
