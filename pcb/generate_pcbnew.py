#!/usr/bin/env python3
"""用KiCad Python API按规范生成PCB — 全新布局"""
import sys
sys.path.insert(0, 'G:/kicad/bin/Lib/site-packages')
import pcbnew
import os, uuid

BOARD = pcbnew.LoadBoard()  # 创建空板
# 设4层
BOARD.SetCopperLayerCount(4)

# 板框尺寸
W, H = 130, 110  # mm

# ===== 创建板框(Edge.Cuts) =====
outline = pcbnew.PCB_SHAPE(BOARD, pcbnew.SHAPE_T_POLY)
outline.SetLayer(pcbnew.Edge_Cuts)
# KiCad坐标是纳米单位: 1mm = 1e6 nm
outline.SetPolyPoints([
    pcbnew.VECTOR2I(0, 0),
    pcbnew.VECTOR2I(int(W*1e6), 0),
    pcbnew.VECTOR2I(int(W*1e6), int(H*1e6)),
    pcbnew.VECTOR2I(0, int(H*1e6)),
    pcbnew.VECTOR2I(0, 0),
])
outline.SetWidth(int(0.2e6))
BOARD.Add(outline)

print(f"Board: {W}x{H}mm, 4 layers")

# 保存
save_path = 'pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb'
BOARD.Save(save_path)
print(f"Saved: {save_path}")
print("NOTE: This is a pcbnew-generated board. Components must be placed via KiCad GUI.")
