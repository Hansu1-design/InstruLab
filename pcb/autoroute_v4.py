#!/usr/bin/env python3
"""PCB自动布线 v4 — 修复多行焊盘解析"""
import re

pcb_file = 'pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb'
content = open(pcb_file).read()

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
    
    # 多行pad格式: (pad "n" type \n (at x y) ...)
    # 用[\s\S]跨行匹配
    for pm in re.finditer(r'\(pad\s+"(\d+)"[\s\S]*?\(at\s+([\d.-]+)\s+([\d.-]+)', fp):
        px, py = float(pm.group(2)) + fx, float(pm.group(3)) + fy
        pads[f'{ref}-{pm.group(1)}'] = (px, py)

print(f'Found {len(pads)} pads:')
for name,(x,y) in sorted(pads.items()):
    print(f'  {name:8s}: ({x:.2f}, {y:.2f})')
