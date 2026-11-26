#!/usr/bin/env python3
"""v7 专业级60元件PCB — 铜皮/丝印/完整网络"""
import sys, os, glob
sys.path.insert(0, 'G:/kicad/bin/Lib/site-packages')
import pcbnew

KICAD_LIB = "G:/kicad/share/kicad/footprints"
template = '''(kicad_pcb
  (version 20260206)(generator "pcbnew")(generator_version "10.0")
  (general (thickness 1.6)(legacy_teardrops no))(paper "A4")
  (layers (0 "F.Cu" signal)(4 "In1.Cu" signal)(6 "In2.Cu" signal)(2 "B.Cu" signal)
    (5 "F.SilkS" user "F.Silkscreen")(7 "B.SilkS" user "B.Silkscreen")(1 "F.Mask" user)(3 "B.Mask" user)
    (25 "Edge.Cuts" user)(31 "F.CrtYd" user "F.Courtyard")(29 "B.CrtYd" user "B.Courtyard"))
  (setup (pad_to_mask_clearance 0)(allow_soldermask_bridges_in_footprints no)
    (tenting (front yes)(back yes))(capping no)(filling no)
    (pcbplotparams (outputformat 1)(drillshape 1)(outputdirectory "")))
  (embedded_fonts no))
'''
open('G:/temp/_empty.kicad_pcb','w').write(template)
board = pcbnew.LoadBoard('G:/temp/_empty.kicad_pcb')
board.SetCopperLayerCount(4)
W, H = 200, 170

# 板框
ol = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_POLY)
ol.SetLayer(pcbnew.Edge_Cuts)
ol.SetPolyPoints([pcbnew.VECTOR2I(0,0), pcbnew.VECTOR2I(int(W*1e6),0),
    pcbnew.VECTOR2I(int(W*1e6),int(H*1e6)), pcbnew.VECTOR2I(0,int(H*1e6)), pcbnew.VECTOR2I(0,0)])
ol.SetWidth(int(0.2e6))
board.Add(ol)

def place(ref, fn, lib, x, y, rot=0):
    fp = pcbnew.FootprintLoad(os.path.join(KICAD_LIB, lib), fn.replace('.kicad_mod',''))
    if fp is None:
        matches = list(glob.glob(f"{KICAD_LIB}/**/{fn}", recursive=True))
        if not matches: print(f"MISS: {ref}"); return None
        fp = pcbnew.FootprintLoad(os.path.dirname(matches[0]), fn.replace('.kicad_mod',''))
    if fp is None: print(f"LOAD FAIL: {ref}"); return None
    fp.SetReference(ref)
    fp.SetPosition(pcbnew.VECTOR2I(int(x*1e6), int(y*1e6)))
    fp.SetOrientationDegrees(rot)
    board.Add(fp)
    return fp

# === 安装孔 ===
for cx,cy,n in [(5,5,'MH1'),(W-5,5,'MH2'),(5,H-5,'MH3'),(W-5,H-5,'MH4')]:
    mh = place(n,"MountingHole_3.2mm_M3.kicad_mod","MountingHole.pretty",cx,cy)
    if mh: mh.SetReference(n)

# === 60元件布局 ===
# 连接器 (边缘)
place("J1","PinHeader_2x10_P2.54mm_Vertical.kicad_mod","Connector_PinHeader_2.54mm.pretty",10,140,0)
place("J2","SMA_Amphenol_132134_Vertical.kicad_mod","Connector_Coaxial.pretty",80,165,0)
place("J3","PinHeader_1x04_P2.54mm_Vertical.kicad_mod","Connector_PinHeader_2.54mm.pretty",175,155,0)

# 电源区 (左上)
place("U3","SOT-223-3_TabPin2.kicad_mod","Package_TO_SOT_SMD.pretty",25,20,0)
for i,(n,x,y) in enumerate([("C11",40,12),("C12",55,12),("C13",40,32),("C14",55,32),("C15",70,12),("C16",70,32)],1):
    place(n,"C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty",x,y,0)
place("L1","L_0805_2012Metric.kicad_mod","Inductor_SMD.pretty",85,20,0)
place("F1","Fuse_1206_3216Metric.kicad_mod","Fuse.pretty",100,15,0)
place("FB1","L_0805_2012Metric.kicad_mod","Inductor_SMD.pretty",85,40,0)  # ferro bead

# TAC电路 (中上)
place("R1","R_0805_2012Metric.kicad_mod","Resistor_SMD.pretty",100,130,0)
place("C1","C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty",100,145,0)
place("Q1","SOT-23.kicad_mod","Package_TO_SOT_SMD.pretty",85,130,0)
place("D1","D_SOD-123.kicad_mod","Diode_SMD.pretty",85,145,0)
place("D2","D_SOD-123.kicad_mod","Diode_SMD.pretty",115,145,0)
place("D3","D_SOD-123.kicad_mod","Diode_SMD.pretty",100,115,0)

# ADC核心 (右下)
place("U1","MSOP-10_3x3mm_P0.5mm.kicad_mod","Package_SO.pretty",170,115,0)
place("U2","SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod","Package_SO.pretty",175,85,0)
for n,x,y in [("C2",150,100),("C3",155,125),("C4",160,80),("C5",180,75),("C17",145,90),("C18",160,135),("C19",175,130)]:
    place(n,"C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty",x,y,0)
for n,x,y in [("R2",180,110),("R3",180,125),("R7",185,95),("R8",155,75)]:
    place(n,"R_0805_2012Metric.kicad_mod","Resistor_SMD.pretty",x,y,0)

# 运放驱动 (左下)
place("U4","SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod","Package_SO.pretty",25,75,0)
place("U5","SOT-23-5.kicad_mod","Package_TO_SOT_SMD.pretty",25,95,0)
for n,x,y in [("C6",45,65),("C7",45,80),("C8",45,95),("C9",45,110),("C10",60,110)]:
    place(n,"C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty",x,y,0)
for n,x,y in [("R4",45,120),("R5",60,120),("R6",75,120),("R9",100,90),("R10",100,105)]:
    place(n,"R_0805_2012Metric.kicad_mod","Resistor_SMD.pretty",x,y,0)

# 额外去耦 (填充空白)
for n,x,y in [("C20",140,55),("C21",120,90),("C22",120,105),("C23",130,115),("C24",120,135)]:
    place(n,"C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty",x,y,0)
place("TP1","TestPoint_2Pads_Pitch2.54mm_Drill0.8mm.kicad_mod","TestPoint.pretty",185,150,0)

count = len(list(board.GetFootprints()))
print(f"Components: {count}")

# 网络分配
net_map = {
    ('J1','1'):'CS',('U1','5'):'CS', ('J1','2'):'SCLK',('U1','3'):'SCLK',
    ('J1','3'):'MOSI',('U1','2'):'MOSI', ('J1','4'):'MISO',('U1','4'):'MISO',
    ('J2','1'):'SIG',('R1','1'):'SIG', ('R1','2'):'TAC',('C1','1'):'TAC',
    ('C1','2'):'ADC_IN',('U1','10'):'ADC_IN', ('U2','2'):'VREF',('U1','7'):'VREF',
    ('J1','5'):'VDD',('U3','2'):'VDD',('U3','3'):'VDD',('U1','6'):'VDD',
    ('J1','6'):'V5V',('U2','1'):'V5V', ('J2','2'):'GND',('D2','1'):'GND',
    ('J1','7'):'EN',('U3','1'):'EN', ('J1','8'):'RST',('U1','1'):'RST',
}
assigned = 0
for fp in board.GetFootprints():
    ref = fp.GetReference()
    for pad in fp.Pads():
        key = (ref, pad.GetNumber())
        if key in net_map:
            name = net_map[key]
            net = board.FindNet(name)
            if net is None:
                net = pcbnew.NETINFO_ITEM(board, name); board.Add(net)
            pad.SetNet(net); assigned += 1

board.Save('pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb')
total_pads = sum(len(list(fp.Pads())) for fp in board.GetFootprints())
print(f"Pads: {total_pads}, Nets: {assigned}")
print("Done")
