#!/usr/bin/env python3
"""给PCB焊盘添加网络引用(v2)"""
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
cur = None
buf = []
num = None
inpad = False

for line in lines:
    m = re.search(r'\(property "Reference" "([^"]+)"', line)
    if m: cur = m.group(1)
    
    pm = re.search(r'\(pad "(\d+)"', line)
    if pm:
        inpad = True
        buf = [line]
        num = pm.group(1)
        continue
    
    if inpad:
        buf.append(line)
        if line.strip() == ')':
            inpad = False
            txt = '\n'.join(buf)
            key = (cur, num)
            n = net_map.get(key)
            if n:
                rs = txt.rstrip()
                if rs.endswith(')'):
                    i = rs.rfind(')')
                    txt = rs[:i] + ' (net ' + str(n) + ')' + rs[i:]
            output.append(txt)
            buf = []
            num = None
        continue
    
    output.append(line)

r = '\n'.join(output)
open(pcb_file, 'w').write(r)
print('Nets assigned:', len(net_map))
o = r.count('(')
c = r.count(')')
print('Brackets:', o, c, 'OK' if o==c else 'MISMATCH')
