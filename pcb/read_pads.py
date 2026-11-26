#!/usr/bin/env python3
"""KiCad PCB自动布线脚本 — 通过Python API直接写走线"""
import sys
sys.path.insert(0, 'G:/kicad/bin/Lib/site-packages')
import pcbnew

board = pcbnew.LoadBoard('pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb')

# 读取所有焊盘坐标
fpads = []
for fp in board.GetFootprints():
    ref = fp.GetReference()
    for pad in fp.Pads():
        pos = pad.GetPosition()
        fpads.append((ref, pad.GetNumber(), pos.x/1e6, pos.y/1e6))

print(f'Found {len(fpads)} pads:')
for ref, num, x, y in fpads:
    print(f'  {ref}-{num}: ({x:.2f}, {y:.2f})')
