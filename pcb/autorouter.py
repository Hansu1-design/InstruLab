#!/usr/bin/env python3
"""KiCad PCB 自动布线器 — 读取焊盘坐标 → 生成走线 → 写回PCB文件"""
import re, uuid
from pathlib import Path

PCB = Path("pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb")
content = PCB.read_text(encoding='utf-8')

# 1. 读取所有封装及其焊盘坐标
# 格式: (footprint "lib:name" ... (at x y) ... (pad "n" smd rect (at x y) (size w h) ...) ...)
footprints = []
fp_pattern = re.compile(r'\(footprint\s+"([^"]+)"[^)]*\(layer\s+"([^"]+)\)(?:\s*\(uuid\s+"([^"]+)\))?\s*\(at\s+([\d.-]+\s+[\d.-]+)')
at_pattern = re.compile(r'\(at\s+([\d.-]+)\s+([\d.-]+)')
pad_pattern = re.compile(r'\(pad\s+"(\d+)"\s+(\w+)\s+(\w+)\s*\(at\s+([\d.-]+)\s+([\d.-]+)\s*\)\s*\(size\s+([\d.-]+)\s+([\d.-]+)\)')

# 按footprint分割
segments = re.split(r'(?=\(footprint)', content)
for seg in segments:
    if not seg.startswith('(footprint'):
        continue
    name_m = re.search(r'\(footprint\s+"([^"]+)"', seg)
    at_m = re.search(r'\(at\s+([\d.-]+)\s+([\d.-]+)', seg)
    if not name_m or not at_m:
        continue
    fp_x, fp_y = float(at_m.group(1)), float(at_m.group(2))
    pads = []
    for pm in pad_pattern.finditer(seg):
        px, py = float(pm.group(4)) + fp_x, float(pm.group(5)) + fp_y
        pads.append({"num": pm.group(1), "x": px, "y": py, "type": pm.group(2)})
    footprints.append({"name": name_m.group(1), "x": fp_x, "y": fp_y, "pads": pads})

print(f"找到 {len(footprints)} 个封装:")
for fp in footprints:
    name_short = fp['name'].split(':')[-1]
    print(f"  {name_short:30s} @({fp['x']:.1f}, {fp['y']:.1f}) {len(fp['pads'])}焊盘")

# 打印所有焊盘坐标(用于布线)
print(f"\n所有焊盘坐标:")
for fp in footprints:
    for p in fp['pads']:
        print(f"  {fp['name'].split(':')[-1]:20s} 焊盘{p['num']:>2s}: ({p['x']:.2f}, {p['y']:.2f})")
