#!/usr/bin/env python3
"""用KiCad API创建4层板"""
import sys
sys.path.insert(0, 'G:/kicad/bin/Lib/site-packages')
import pcbnew

pcb_file = 'pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb'
board = pcbnew.LoadBoard(pcb_file)

# 获取层数
print(f'Current layers: {board.GetCopperLayerCount()}')
# KiCad PCB: 设置4层
board.SetCopperLayerCount(4)
board.Save(pcb_file)
print(f'Set to 4 layers and saved')
