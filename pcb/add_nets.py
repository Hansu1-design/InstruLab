#!/usr/bin/env python3
"""为PCB文件添加网络分配 — 让KiCad导出DSN时有网络"""
import re

pcb_file = 'pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb'
content = open(pcb_file).read()

# 网络定义 (焊盘引用 → 网络名)
net_assign = {
    # SPI
    'J1-1': 'CS', 'U1-5': 'CS',
    'J1-2': 'SCLK', 'U1-3': 'SCLK',
    'J1-3': 'MOSI', 'U1-2': 'MOSI',
    'J1-4': 'MISO', 'U1-4': 'MISO',
    # 信号
    'J2-1': 'SIG', 'R1-1': 'SIG',
    'R1-2': 'TAC', 'C1-1': 'TAC',
    'C1-2': 'ADC_IN', 'U1-10': 'ADC_IN',
    # 基准
    'U2-2': 'VREF', 'U1-7': 'VREF',
    # 电源
    'J1-5': 'VDD', 'U3-2': 'VDD', 'U3-3': 'VDD', 'U1-6': 'VDD',
    'J1-6': 'V5V', 'C11-1': 'V5V', 'C11-2': 'V5V', 'U2-1': 'V5V',
    # 地
    'J2-2': 'GND', 'D2-1': 'GND', 'C1-2': 'GND',
}

# 去重网络名 → 编号
net_names = sorted(set(net_assign.values()))
net_num = {name: i+1 for i, name in enumerate(net_names)}  # net 0=未定义, 1+ = 定义的

# 为每个焊盘加(net n)属性
def add_net_to_pad(m):
    """在pad定义里插入(net n)"""
    pad_text = m.group(0)
    # 找焊盘引用名: (pad "n" smd roundrect ...
    ref_match = re.search(r'\(pad\s+"(\d+)"', pad_text)
    if not ref_match: return pad_text
    
    # 找这个焊盘属于哪个元件(通过向上搜索footprint)
    # 这里传入的是单个pad的匹配, 需要结合上下文
    # 用search方法找pad后面的(at ...)来确定位置
    return pad_text  # 暂不修改, 下面用整体处理

# 整体处理: 在每个footprint内, 为匹配的焊盘加上(net n)
# 对每个网络定义, 找到对应的焊盘并加net编号
for pad_ref, net_name in net_assign.items():
    # pad_ref = "U1-5", 分解为 ref="U1", pin="5"
    parts = pad_ref.rsplit('-', 1)
    if len(parts) != 2: continue
    ref, pin = parts
    
    # 找这个footprint里的这个pad
    # 格式: (footprint ... (property "Reference" "U1" ...) ... (pad "5" ...)
    pattern = rf'(\(footprint[^)]*(?:[^)]*\)[^)]*)*?\(property "Reference" "{ref}"[^)]*\)[\s\S]*?)(\(pad\s+"{pin}"[\s\S]*?\))'
    
    def add_net(m):
        prefix = m.group(1)
        pad_def = m.group(2)
        net_n = net_num[net_name]
        # 如果pad已经有net了就不加
        if f'(net {net_n})' in pad_def: return m.group(0)
        # 在pad的结束括号前插入(net n)
        # 找到pad定义的最后一个)并在之前插入
        if pad_def.rstrip().endswith(')'):
            # 在最后一个)前插入
            idx = pad_def.rstrip().rfind(')')
            pad_def = pad_def[:idx] + f'(net {net_n}) ' + pad_def[idx:]
        return prefix + pad_def
    
    new_content = re.sub(pattern, add_net, content, count=1)
    if new_content != content:
        content = new_content
    else:
        # 试试简化匹配
        pattern2 = rf'\(footprint[^)]*\(property "Reference" "{ref}"[\s\S]*?\(pad\s+"{pin}"[\s\S]*?\)'
        m = re.search(pattern2, content)
        if m:
            old = m.group(0)
            # 在最后加(net n)
            net_n = net_num[net_name]
            # 找最后一个完整的)
            idx = old.rfind(')')
            new = old[:idx] + f'(net {net_n})\n' + old[idx:]
            content = content.replace(old, new)

# 添加网络定义表 (在embedded_fonts前)
net_defs = '\n'.join([f'\t(net {n} "{name}")' for name, n in net_num.items()])
content = re.sub(r'(\(embedded_fonts no\))', net_defs + '\n\\1', content)

open(pcb_file, 'w').write(content)
print(f'Net assignments added: {len(net_assign)} pads, {len(net_names)} nets')
print(f'Nets: {net_names}')
