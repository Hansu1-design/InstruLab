#!/usr/bin/env python3
"""SES导入器 — 只追加不走线, 不修改已有内容"""
import re, uuid

pcb_file = 'pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb'
ses_file = 'pcb/tdc_daughterboard/tdc_daughterboard.ses'

# 读PCB
pcb = open(pcb_file).read()
print(f'PCB: {len(pcb)} bytes')

# 解析SES
ses = open(ses_file).read()
nets = re.split(r'\(net\s+', ses)[1:]

segments = []
layer_map = {'F.Cu':'F.Cu','In1.Cu':'In1.Cu','In2.Cu':'In2.Cu','B.Cu':'B.Cu'}

for nb in nets:
    name = nb.split()[0].strip('"')
    for wm in re.finditer(r'\(path\s+(\S+)\s+(\d+)([\s\d.-]+)\)', nb):
        l = wm.group(1); w = float(wm.group(2))/1000
        cs = [float(x)/1000 for x in wm.group(3).strip().split()]
        for i in range(0, len(cs)-2, 2):
            u = str(uuid.uuid4())
            segments.append(f'\t(segment (start {cs[i]:.4f} {-cs[i+1]:.4f}) (end {cs[i+2]:.4f} {-cs[i+3]:.4f}) (width {w:.4f}) (layer "{layer_map.get(l,l)}") (net "{name}") (uuid "{u}"))')
    for vm in re.finditer(r'\(via\s+"([^"]*)"\s+([\d.-]+)\s+([\d.-]+)\)', nb):
        x = float(vm.group(2))/1000; y = -float(vm.group(3))/1000
        u = str(uuid.uuid4())
        segments.append(f'\t(via (at {x:.4f} {y:.4f}) (size 0.6) (drill 0.3) (layers "F.Cu" "In1.Cu" "In2.Cu" "B.Cu") (net "{name}") (uuid "{u}"))')

print(f'SES items: {len(segments)} ({sum(1 for s in segments if "(segment" in s)} segments, {sum(1 for s in segments if "(via" in s)} vias)')

# 追加到PCB文件末尾(在embedded_fonts前)
new_content = '\n'.join(segments)
if '(embedded_fonts no)' in pcb:
    pcb = pcb.replace('(embedded_fonts no)', new_content + '\n(embedded_fonts no)')
else:
    pcb = pcb.rstrip(')\n ') + '\n' + new_content + '\n)'

open(pcb_file, 'w').write(pcb)

o = pcb.count('('); c = pcb.count(')')
s = pcb.count('(segment '); v = pcb.count('(via ')
print(f'Final: {s} segments, {v} vias, brackets {"OK" if o==c else "MISMATCH"}')
