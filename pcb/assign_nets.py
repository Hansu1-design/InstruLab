#!/usr/bin/env python3
"""给PCB焊盘添加网络引用 — 行解析方式"""
import re

pcb_file = 'pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb'
lines = open(pcb_file).read().split('\n')

net_map = {
    ('J1','1'):1,('U1','5'):1, ('J1','2'):2,('U1','3'):2,
    ('J1','3'):3,('U1','2'):3, ('J1','4'):4,('U1','4'):4,
    ('J2','1'):5,('R1','1'):5, ('R1','2'):6,('C1','1'):6,
    ('C1','2'):7,('U1','10'):7, ('U2','2'):8,('U1','7'):8,
    ('J1','5'):9,('U3','2'):9, ('U3','3'):9,('U1','6'):9,
    ('J1','6'):10,('U2','1'):10, ('J2','2'):11,('D2','1'):11,
}

output = []
current_ref = None
in_pad = False
pad_buffer = []
pad_num = None

for line in lines:
    # 跟踪当前footprint引用
    rm = re.search(r'\(property "Reference" "([^"]+)"', line)
    if rm:
        current_ref = rm.group(1)
    
    # 检测pad开始
    if re.search(r'\(pad\s+"(\d+)"', line):
        in_pad = True
        pad_buffer = [line]
        pm = re.search(r'\(pad\s+"(\d+)"', line)
        pad_num = pm.group(1) if pm else None
        continue
    
    if in_pad:
        pad_buffer.append(line)
        # pad结束(遇到只有)的行 或 下一个pad/属性开始)
        stripped = line.strip()
        if stripped == ')':
            in_pad = False
            pad_text = '\n'.join(pad_buffer)
            # 如果有网络定义, 在最后一个)前插入
            key = (current_ref, pad_num)
            net_n = net_map.get(key)
            if net_n:
                # 找最后一个完整的)
                pad_text_stripped = pad_text.rstrip()
                if pad_text_stripped.endswith(')'):
                    idx = pad_text_stripped.rfind(')')
                    pad_text = pad_text_stripped[:idx] + f' (net {net_n})' + pad_text_stripped[idx:]
            output.append(pad_text)
            pad_buffer = []
            pad_num = None
            continue
        continue
    
    output.append(line)

result = '\n'.join(output)
open(pcb_file, 'w').write(result)

assigned = len(net_map)
print(f'Net assignments: {assigned}')
print(f'Brackets: {result.count(\"(\")}/{result.count(\")\")} {\"OK\" if result.count(\"(\")==result.count(\")\") else \"MISMATCH\"}')
print(f'\n现在KiCad导出DSN时, Freerouting能识别网络了')
