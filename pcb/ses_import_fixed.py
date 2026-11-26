#!/usr/bin/env python3
"""SES导入 — 只替换最后一次embedded_fonts"""
import re, uuid

pcb_file = 'pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb'
ses_file = 'pcb/tdc_daughterboard/tdc_daughterboard.ses'

pcb = open(pcb_file).read()
ses = open(ses_file).read()
nets = re.split(r'\(net\s+', ses)[1:]

FACTOR = 10000.0
segments = []
layer_map = {'F.Cu':'F.Cu','In1.Cu':'In1.Cu','In2.Cu':'In2.Cu','B.Cu':'B.Cu'}

for nb in nets:
    name = nb.split()[0].strip('"')
    for wm in re.finditer(r'\(path\s+(\S+)\s+(\d+)([\s\d.-]+)\)', nb):
        l = wm.group(1); w = float(wm.group(2))/FACTOR
        cs = [float(x)/FACTOR for x in wm.group(3).strip().split()]
        for i in range(0, len(cs)-2, 2):
            u = str(uuid.uuid4())
            segments.append(f'\t(segment (start {cs[i]:.4f} {-cs[i+1]:.4f}) (end {cs[i+2]:.4f} {-cs[i+3]:.4f}) (width {w:.4f}) (layer "{layer_map.get(l,l)}") (net "") (uuid "{u}"))')
    for vm in re.finditer(r'\(via\s+"[^"]*"\s+([\d.-]+)\s+([\d.-]+)', nb):
        x = float(vm.group(1))/FACTOR; y = -float(vm.group(2))/FACTOR
        u = str(uuid.uuid4())
        segments.append(f'\t(via (at {x:.4f} {y:.4f}) (size 0.6) (drill 0.3) (layers "F.Cu" "In1.Cu" "In2.Cu" "B.Cu") (net "") (uuid "{u}"))')

print(f'SES items: {len(segments)}')

# 只替换最后一次出现的(embedded_fonts no)
marker = '(embedded_fonts no)'
last_pos = pcb.rfind(marker)
if last_pos > 0:
    new_content = '\n'.join(segments)
    pcb = pcb[:last_pos] + new_content + '\n' + marker + pcb[last_pos + len(marker):]
    open(pcb_file, 'w').write(pcb)
    print('Replaced last occurrence')
else:
    print('ERROR: marker not found')

o = pcb.count('('); c = pcb.count(')')
s = pcb.count('(segment '); v = pcb.count('(via ')
print(f'Final: {s} segments, {v} vias, brackets {"OK" if o==c else "MISMATCH"}')
