#!/usr/bin/env python3
"""从模板创建干净PCB → 导入SES走线"""
import re, uuid, os, shutil

pcb_file = 'pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb'
ses_file = 'pcb/tdc_daughterboard/tdc_daughterboard.ses'

# 干净模板(无走线, 无封装)
template = '''(kicad_pcb
  (version 20260206)(generator "pcbnew")(generator_version "10.0")
  (general (thickness 1.6)(legacy_teardrops no))(paper "A4")
  (layers (0 "F.Cu" signal)(4 "In1.Cu" signal)(6 "In2.Cu" signal)(2 "B.Cu" signal)
    (5 "F.SilkS" user "F.Silkscreen")(7 "B.SilkS" user "B.Silkscreen")(1 "F.Mask" user)(3 "B.Mask" user)
    (25 "Edge.Cuts" user)(31 "F.CrtYd" user "F.Courtyard")(29 "B.CrtYd" user "B.Courtyard"))
  (setup (pad_to_mask_clearance 0)(allow_soldermask_bridges_in_footprints no)
    (tenting (front yes)(back yes))(capping no)(filling no)
    (pcbplotparams (outputformat 1)(drillshape 1)(outputdirectory "")))
  (embedded_fonts no)
)'''

# 用KiCad Python API生成完整PCB(含元件)
import subprocess
result = subprocess.run([
    'G:/kicad/bin/python.exe', 'pcb/generate_v6_pro.py'
], capture_output=True, text=True)
print(result.stdout.strip())

# 读取生成的PCB
pcb = open(pcb_file).read()
# 去掉所有segment和via行
pcb = re.sub(r'\t(segment [^\n]*\n?)', '', pcb)
pcb = re.sub(r'\t(via [^\n]*\n?)', '', pcb)
pcb = re.sub(r'\t(gr_line [^\n]*\n?)', '', pcb)  # 也清除板框线
open(pcb_file, 'w').write(pcb)
cnt = pcb.count('(segment ')
print(f'After cleanup: {cnt} segments')

# 导入SES
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

print(f'SES parsed: {len(segments)} items')

# 加回板框
board_w, board_h = 180, 150
for i, (sx,sy,ex,ey) in enumerate([(0,0,board_w,0),(board_w,0,board_w,board_h),(board_w,board_h,0,board_h),(0,board_h,0,0)]):
    uid = str(uuid.uuid4())
    segments.append(f'\t(gr_line (start {sx} {sy}) (end {ex} {ey}) (stroke (width 0.2) (type default)) (layer "Edge.Cuts") (uuid "{uid}"))')

# 写入
pcb = open(pcb_file).read()
pcb = re.sub(r'(\(embedded_fonts no\))', '\n'.join(segments) + '\n\\1', pcb)
open(pcb_file, 'w').write(pcb)

o = pcb.count('('); c = pcb.count(')')
s = pcb.count('(segment '); v = pcb.count('(via '); g = pcb.count('(gr_line ')
print(f'Final: {s} segments, {v} vias, {g} outlines, brackets {"OK" if o==c else "MISMATCH"}')
