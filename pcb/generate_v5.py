#!/usr/bin/env python3
"""v5 PCB — 大幅放大空间, 让Freerouting一次布通"""
import sys, os
sys.path.insert(0, 'G:/kicad/bin/Lib/site-packages')
import pcbnew

KICAD_LIB = "G:/kicad/share/kicad/footprints"
W, H = 200, 180  # mm — 空间给足

# 创建板
min_pcb = f'''(kicad_pcb
  (version 20260206)(generator "pcbnew")(generator_version "10.0")
  (general (thickness 1.6)(legacy_teardrops no))(paper "A4")
  (layers (0 "F.Cu" signal)(4 "In1.Cu" signal)(6 "In2.Cu" signal)(2 "B.Cu" signal)
    (5 "F.SilkS" user "F.Silkscreen")(7 "B.SilkS" user "B.Silkscreen")
    (1 "F.Mask" user)(3 "B.Mask" user)
    (25 "Edge.Cuts" user)(31 "F.CrtYd" user "F.Courtyard")(29 "B.CrtYd" user "B.Courtyard"))
  (setup (pad_to_mask_clearance 0)(allow_soldermask_bridges_in_footprints no)
    (tenting (front yes)(back yes))(capping no)(filling no)
    (pcbplotparams (outputformat 1)(drillshape 1)(outputdirectory "")))
  (embedded_fonts no)
)
'''
tmp = 'G:/temp/_empty.kicad_pcb'
open(tmp,'w').write(min_pcb)
board = pcbnew.LoadBoard(tmp)
board.SetCopperLayerCount(4)

# 板框
ol = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_POLY)
ol.SetLayer(pcbnew.Edge_Cuts)
ol.SetPolyPoints([pcbnew.VECTOR2I(0,0), pcbnew.VECTOR2I(int(W*1e6),0),
       pcbnew.VECTOR2I(int(W*1e6),int(H*1e6)), pcbnew.VECTOR2I(0,int(H*1e6)), pcbnew.VECTOR2I(0,0)])
ol.SetWidth(int(0.2e6))
board.Add(ol)

# 布局: 大间距, 功能区清晰
comps = [
    # 连接器 (边缘)
    ("J1","PinHeader_2x10_P2.54mm_Vertical.kicad_mod","Connector_PinHeader_2.54mm.pretty", 10, 140, 0),
    ("J2","SMA_Amphenol_132134_Vertical.kicad_mod","Connector_Coaxial.pretty", 80, 175, 0),
    
    # 电源 (左上)
    ("U3","SOT-223-3_TabPin2.kicad_mod","Package_TO_SOT_SMD.pretty", 20, 20, 0),
    ("C11","C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty", 35, 15, 0),
    ("C12","C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty", 50, 15, 0),
    ("C13","C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty", 35, 35, 0),
    ("C14","C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty", 50, 35, 0),
    ("L1","L_0805_2012Metric.kicad_mod","Inductor_SMD.pretty", 70, 20, 0),
    ("F1","Fuse_1206_3216Metric.kicad_mod","Fuse.pretty", 80, 15, 0),
    
    # TAC (中上)
    ("R1","R_0805_2012Metric.kicad_mod","Resistor_SMD.pretty", 100, 130, 0),
    ("C1","C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty", 100, 145, 0),
    ("Q1","SOT-23.kicad_mod","Package_TO_SOT_SMD.pretty", 85, 130, 0),
    ("D1","D_SOD-123.kicad_mod","Diode_SMD.pretty", 85, 145, 0),
    ("D2","D_SOD-123.kicad_mod","Diode_SMD.pretty", 115, 145, 0),
    
    # ADC核心 (右下)
    ("U1","MSOP-10_3x3mm_P0.5mm.kicad_mod","Package_SO.pretty", 155, 125, 0),
    ("U2","SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod","Package_SO.pretty", 170, 100, 0),
    ("C2","C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty", 140, 110, 0),
    ("C3","C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty", 145, 135, 0),
    ("C4","C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty", 155, 95, 0),
    ("C5","C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty", 175, 90, 0),
    ("R2","R_0805_2012Metric.kicad_mod","Resistor_SMD.pretty", 175, 120, 0),
    ("R3","R_0805_2012Metric.kicad_mod","Resistor_SMD.pretty", 175, 135, 0),
    
    # 运放 (左下)
    ("U4","SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod","Package_SO.pretty", 20, 75, 0),
    ("C6","C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty", 40, 65, 0),
    ("C7","C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty", 40, 80, 0),
    ("R4","R_0805_2012Metric.kicad_mod","Resistor_SMD.pretty", 40, 95, 0),
    ("R5","R_0805_2012Metric.kicad_mod","Resistor_SMD.pretty", 55, 95, 0),
    ("R6","R_0805_2012Metric.kicad_mod","Resistor_SMD.pretty", 70, 95, 0),
    
    # 去耦散放
    ("C8","C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty", 130, 85, 0),
    ("C9","C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty", 130, 150, 0),
    ("C10","C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty", 175, 150, 0),
    ("C15","C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty", 10, 50, 0),
    ("C16","C_0805_2012Metric.kicad_mod","Capacitor_SMD.pretty", 10, 110, 0),
    ("L2","L_0805_2012Metric.kicad_mod","Inductor_SMD.pretty", 10, 60, 0),
    ("TP1","TestPoint_2Pads_Pitch2.54mm_Drill0.8mm.kicad_mod","TestPoint.pretty", 180, 165, 0),
]

placed = 0
for ref, fn, lib, x, y, rot in comps:
    lib_path = os.path.join(KICAD_LIB, lib)
    fp = pcbnew.FootprintLoad(lib_path, fn.replace('.kicad_mod',''))
    if fp is None:
        # 递归搜
        import glob
        matches = list(glob.glob(f"{KICAD_LIB}/**/{fn}", recursive=True))
        if not matches:
            print(f"MISS: {ref}")
            continue
        lib_path = os.path.dirname(matches[0])
        fp = pcbnew.FootprintLoad(lib_path, fn.replace('.kicad_mod',''))
        if fp is None:
            print(f"LOAD FAIL: {ref}")
            continue
    fp.SetReference(ref)
    fp.SetPosition(pcbnew.VECTOR2I(int(x*1e6), int(y*1e6)))
    fp.SetOrientationDegrees(rot)
    board.Add(fp)
    placed += 1

print(f"Placed: {placed}/{len(comps)}")

# 网络
net_map = {
    ('J1','1'):'CS',('U1','5'):'CS',('J1','2'):'SCLK',('U1','3'):'SCLK',
    ('J1','3'):'MOSI',('U1','2'):'MOSI',('J1','4'):'MISO',('U1','4'):'MISO',
    ('J2','1'):'SIG',('R1','1'):'SIG',('R1','2'):'TAC',('C1','1'):'TAC',
    ('C1','2'):'ADC_IN',('U1','10'):'ADC_IN',('U2','2'):'VREF',('U1','7'):'VREF',
    ('J1','5'):'VDD',('U3','2'):'VDD',('U3','3'):'VDD',('U1','6'):'VDD',
    ('J1','6'):'V5V',('U2','1'):'V5V',('J2','2'):'GND',('D2','1'):'GND',
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
                net = pcbnew.NETINFO_ITEM(board, name)
                board.Add(net)
            pad.SetNet(net)
            assigned += 1

board.Save(f'pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb')
print(f"Saved! {W}x{H}mm, {placed} comps, {assigned} nets")
