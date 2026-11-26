#!/usr/bin/env python3
"""用KiCad Python API添加网络 — 不破坏文件结构"""
import sys
sys.path.insert(0, 'G:/kicad/bin/Lib/site-packages')
import pcbnew

pcb_file = 'pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb'

# 载入PCB
board = pcbnew.LoadBoard(pcb_file)
print(f'Footprints: {len(list(board.GetFootprints()))}')

# 创建网络
net_names = ['CS','SCLK','MOSI','MISO','SIG','TAC','ADC_IN','VREF','VDD','V5V','GND']
net_map = {}

for i, name in enumerate(net_names):
    net = board.FindNet(name)
    if not net:
        net = pcbnew.NETINFO_ITEM(board, name)
        board.Add(net)
    net_map[name] = i+1
    print(f'  Net {i+1}: {name}')

# 为焊盘分配网络
assignments = [
    ('J1','1','CS'),('U1','5','CS'), ('J1','2','SCLK'),('U1','3','SCLK'),
    ('J1','3','MOSI'),('U1','2','MOSI'), ('J1','4','MISO'),('U1','4','MISO'),
    ('J2','1','SIG'),('R1','1','SIG'), ('R1','2','TAC'),('C1','1','TAC'),
    ('C1','2','ADC_IN'),('U1','10','ADC_IN'), ('U2','2','VREF'),('U1','7','VREF'),
    ('J1','5','VDD'),('U3','2','VDD'),('U3','3','VDD'),('U1','6','VDD'),
    ('J1','6','V5V'),('U2','1','V5V'), ('J2','2','GND'),('D2','1','GND'),
]

assigned = 0
for fp in board.GetFootprints():
    ref = fp.GetReference()
    for pad in fp.Pads():
        pnum = pad.GetNumber()
        for r, p, net_name in assignments:
            if ref == r and pnum == p:
                net_info = board.FindNet(net_name)
                if net_info:
                    pad.SetNet(net_info)
                    assigned += 1
                break

board.Save(pcb_file)
print(f'\nPads assigned: {assigned}')
print(f'PCB saved: {pcb_file}')
print(f'\nPCBB上的网络已就绪, 导出DSN即可')
