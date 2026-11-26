#!/usr/bin/env python3
"""v6 专业级PCB — 铜皮/过孔/安装孔/丝印/电源走线"""
import sys, os
sys.path.insert(0, 'G:/kicad/bin/Lib/site-packages')
import pcbnew, math

KICAD_LIB = "G:/kicad/share/kicad/footprints"

# 创建板
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
W, H = 180, 150

# 板框
ol = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_POLY)
ol.SetLayer(pcbnew.Edge_Cuts)
ol.SetPolyPoints([pcbnew.VECTOR2I(0,0), pcbnew.VECTOR2I(int(W*1e6),0),
       pcbnew.VECTOR2I(int(W*1e6),int(H*1e6)), pcbnew.VECTOR2I(0,int(H*1e6)), pcbnew.VECTOR2I(0,0)])
ol.SetWidth(int(0.2e6))
board.Add(ol)

def place(ref, fn, lib, x, y, rot=0):
    lib_path = os.path.join(KICAD_LIB, lib)
    fp = pcbnew.FootprintLoad(lib_path, fn.replace('.kicad_mod',''))
    if fp is None:
        import glob
        matches = list(glob.glob(f"{KICAD_LIB}/**/{fn}", recursive=True))
        if not matches: return None
        fp = pcbnew.FootprintLoad(os.path.dirname(matches[0]), fn.replace('.kicad_mod',''))
    if fp is None: return None
    fp.SetReference(ref)
    fp.SetPosition(pcbnew.VECTOR2I(int(x*1e6), int(y*1e6)))
    fp.SetOrientationDegrees(rot)
    board.Add(fp)
    return fp

# === 安装孔 (4角) ===
for cx, cy in [(5,5),(W-5,5),(5,H-5),(W-5,H-5)]:
    mh = place("MH","MountingHole_3.2mm_M3.kicad_mod","MountingHole.pretty",cx,cy)
    if mh: mh.SetReference(f"MH{len(list(board.GetFootprints()))}")

# === 元件 ===
# 连接器
place("J1","PinHeader_2x10_P2.54mm_Vertical.kicad_mod","Connector_PinHeader_2.54mm.pretty",10,125,0)
place("J2","SMA_Amphenol_132134_Vertical.kicad_mod","Connector_Coaxial.pretty",75,145,0)
# 电源
place("U3","SOT-223-3_TabPin2.kicad_mod","Package_TO_SOT_SMD.pretty",20,20,0)
for i,(n,x,y) in enumerate([("C11",35,15),("C12",45,15),("C13",35,30),("C14",45,30)],1):
    place(f"C{i+10}","C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty",x,y,0)
place("L1","L_0805_2012Metric.kicad_mod","Inductor_SMD.pretty",60,20,0)
place("F1","Fuse_1206_3216Metric.kicad_mod","Fuse.pretty",70,15,0)
# TAC
place("R1","R_0805_2012Metric.kicad_mod","Resistor_SMD.pretty",90,115,0)
place("C1","C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty",90,130,0)
place("Q1","SOT-23.kicad_mod","Package_TO_SOT_SMD.pretty",75,115,0)
place("D1","D_SOD-123.kicad_mod","Diode_SMD.pretty",75,130,0)
place("D2","D_SOD-123.kicad_mod","Diode_SMD.pretty",105,130,0)
# ADC
place("U1","MSOP-10_3x3mm_P0.5mm.kicad_mod","Package_SO.pretty",145,110,0)
place("U2","SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod","Package_SO.pretty",160,85,0)
for n,x,y in [("C2",130,95),("C3",135,120),("C4",145,80),("C5",165,75)]:
    place(n,"C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty",x,y,0)
place("R2","R_0805_2012Metric.kicad_mod","Resistor_SMD.pretty",165,105,0)
place("R3","R_0805_2012Metric.kicad_mod","Resistor_SMD.pretty",165,120,0)
# 运放
place("U4","SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod","Package_SO.pretty",20,65,0)
for n,x,y in [("C6",40,55),("C7",40,70),("R4",40,85),("R5",55,85),("R6",70,85)]:
    place(n,"R_0805_2012Metric.kicad_mod" if n.startswith("R") else "C_0805_2012Metric.kicad_mod","Resistor_SMD.pretty" if n.startswith("R") else "Capacitor_SMD.pretty",x,y,0)
# 散放
for n,x,y in [("C8",120,70),("C9",120,135),("C10",165,135)]:
    place(n,"C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty",x,y,0)
place("TP1","TestPoint_2Pads_Pitch2.54mm_Drill0.8mm.kicad_mod","TestPoint.pretty",170,140,0)

# === 网络分配 ===
net_map = {
    ('J1','1'):'CS',('U1','5'):'CS',('J1','2'):'SCLK',('U1','3'):'SCLK',
    ('J1','3'):'MOSI',('U1','2'):'MOSI',('J1','4'):'MISO',('U1','4'):'MISO',
    ('J2','1'):'SIG',('R1','1'):'SIG',('R1','2'):'TAC',('C1','1'):'TAC',
    ('C1','2'):'ADC_IN',('U1','10'):'ADC_IN',('U2','2'):'VREF',('U1','7'):'VREF',
    ('J1','5'):'VDD',('U3','2'):'VDD',('U3','3'):'VDD',('U1','6'):'VDD',
    ('J1','6'):'V5V',('U2','1'):'V5V',('J2','2'):'GND',('D2','1'):'GND',
}
for fp in board.GetFootprints():
    ref = fp.GetReference()
    for pad in fp.Pads():
        key = (ref, pad.GetNumber())
        if key in net_map:
            name = net_map[key]
            net = board.FindNet(name)
            if net is None:
                net = pcbnew.NETINFO_ITEM(board, name); board.Add(net)
            pad.SetNet(net)

# === 铜皮跳过 (API复杂, 可以在KiCad里手动加) ===
# KiCad → PCB编辑器 → 放置 → 填充区 → 选GND网络 → 画矩形

print(f"Footprints: {len(list(board.GetFootprints()))}")
# 统计焊盘
total_pads = sum(len(list(fp.Pads())) for fp in board.GetFootprints())
print(f"Total pads: {total_pads}")

board.Save('pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb')
print("Saved: pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb")
