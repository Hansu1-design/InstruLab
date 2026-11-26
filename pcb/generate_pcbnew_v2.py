#!/usr/bin/env python3
"""用KiCad API规范布局PCB — 读库→放元件→配网络→出Gerber"""
import sys, os, uuid
sys.path.insert(0, 'G:/kicad/bin/Lib/site-packages')
import pcbnew

# KiCad库路径
KICAD_LIB = "G:/kicad/share/kicad/footprints"
os.environ['KICAD10_FOOTPRINT_DIR'] = KICAD_LIB

# 创建空板
import tempfile
# 先建一个最小PCB文件, 然后加载
min_pcb = '''(kicad_pcb
  (version 20260206)
  (generator "pcbnew") (generator_version "10.0")
  (general (thickness 1.6) (legacy_teardrops no))
  (paper "A4")
  (layers (0 "F.Cu" signal) (4 "In1.Cu" signal) (6 "In2.Cu" signal) (2 "B.Cu" signal))
  (setup (pad_to_mask_clearance 0) (allow_soldermask_bridges_in_footprints no)
    (tenting (front yes) (back yes)) (capping no) (filling no)
    (pcbplotparams (outputformat 1) (drillshape 1) (outputdirectory "")))
  (embedded_fonts no)
)
'''
tmp = 'G:/temp/_empty_board.kicad_pcb'
open(tmp,'w').write(min_pcb)
board = pcbnew.LoadBoard(tmp)
board.SetCopperLayerCount(4)

W, H = 150, 130  # mm

# ===== 板框 =====
ol = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_POLY)
ol.SetLayer(pcbnew.Edge_Cuts)
pts = [pcbnew.VECTOR2I(0,0), pcbnew.VECTOR2I(int(W*1e6),0),
       pcbnew.VECTOR2I(int(W*1e6),int(H*1e6)), pcbnew.VECTOR2I(0,int(H*1e6)), pcbnew.VECTOR2I(0,0)]
ol.SetPolyPoints(pts)
ol.SetWidth(int(0.2e6))
board.Add(ol)

# ===== 放置元件 =====
# 格式: (位号, 封装路径(相对LIB), Xmm, Ymm, 旋转)

comps_pos = [
    # 连接器 (边缘)
    ("J1", "Connector_PinHeader_2.54mm.pretty/PinHeader_2x10_P2.54mm_Vertical.kicad_mod", 10, 95, 0),
    ("J2", "Connector_Coaxial.pretty/SMA_Amphenol_132134_Vertical.kicad_mod", 50, 125, 0),
    
    # 电源 (左上)
    ("U3", "Package_TO_SOT_SMD.pretty/SOT-223-3_TabPin2.kicad_mod", 20, 15, 0),
    ("C11","Capacitor_SMD.pretty/C_0805_2012Metric.kicad_mod", 30, 10, 0),
    ("C12","Capacitor_SMD.pretty/C_0805_2012Metric.kicad_mod", 40, 10, 0),
    ("C13","Capacitor_SMD.pretty/C_0805_2012Metric.kicad_mod", 30, 25, 0),
    ("C14","Capacitor_SMD.pretty/C_0805_2012Metric.kicad_mod", 40, 25, 0),
    ("L1", "Inductor_SMD.pretty/L_0805_2012Metric.kicad_mod", 50, 15, 0),
    ("F1", "Fuse.pretty/Fuse_1206_3216Metric.kicad_mod", 55, 12, 0),
    
    # TAC (中右)
    ("R1", "Resistor_SMD.pretty/R_0805_2012Metric.kicad_mod", 70, 95, 0),
    ("C1", "Capacitor_SMD.pretty/C_0805_2012Metric.kicad_mod", 70, 105, 0),
    ("Q1", "Package_TO_SOT_SMD.pretty/SOT-23.kicad_mod", 60, 95, 0),
    ("D1", "Diode_SMD.pretty/D_SOD-123.kicad_mod", 60, 105, 0),
    ("D2", "Diode_SMD.pretty/D_SOD-123.kicad_mod", 85, 105, 0),
    
    # ADC核心 (右下)
    ("U1", "Package_SO.pretty/MSOP-10_3x3mm_P0.5mm.kicad_mod", 105, 90, 0),
    ("U2", "Package_SO.pretty/SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod", 115, 75, 0),
    ("C2", "Capacitor_SMD.pretty/C_0805_2012Metric.kicad_mod", 95, 85, 0),
    ("C3", "Capacitor_SMD.pretty/C_0805_2012Metric.kicad_mod", 100, 100, 0),
    ("C4", "Capacitor_SMD.pretty/C_0805_2012Metric.kicad_mod", 105, 70, 0),
    ("C5", "Capacitor_SMD.pretty/C_0805_2012Metric.kicad_mod", 120, 75, 0),
    ("R2", "Resistor_SMD.pretty/R_0805_2012Metric.kicad_mod", 120, 90, 0),
    ("R3", "Resistor_SMD.pretty/R_0805_2012Metric.kicad_mod", 120, 100, 0),
    
    # 运放 (左下)
    ("U4", "Package_SO.pretty/SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod", 15, 50, 0),
    ("C6", "Capacitor_SMD.pretty/C_0805_2012Metric.kicad_mod", 30, 45, 0),
    ("C7", "Capacitor_SMD.pretty/C_0805_2012Metric.kicad_mod", 30, 55, 0),
    ("R4", "Resistor_SMD.pretty/R_0805_2012Metric.kicad_mod", 30, 65, 0),
    ("R5", "Resistor_SMD.pretty/R_0805_2012Metric.kicad_mod", 40, 65, 0),
    ("R6", "Resistor_SMD.pretty/R_0805_2012Metric.kicad_mod", 50, 65, 0),
    
    # 辅助去耦(散放)
    ("C8", "Capacitor_SMD.pretty/C_0805_2012Metric.kicad_mod", 90, 75, 0),
    ("C9", "Capacitor_SMD.pretty/C_0805_2012Metric.kicad_mod", 95, 110, 0),
    ("C10","Capacitor_SMD.pretty/C_0805_2012Metric.kicad_mod", 130, 95, 0),
    ("C15","Capacitor_SMD.pretty/C_0805_2012Metric.kicad_mod", 130, 85, 0),
    ("C16","Capacitor_SMD.pretty/C_0805_2012Metric.kicad_mod", 10, 110, 0),
    ("L2", "Inductor_SMD.pretty/L_0805_2012Metric.kicad_mod", 10, 75, 0),
    ("R7", "Resistor_SMD.pretty/R_0805_2012Metric.kicad_mod", 130, 105, 0),
    ("R8", "Resistor_SMD.pretty/R_0805_2012Metric.kicad_mod", 10, 30, 0),
    ("R9", "Resistor_SMD.pretty/R_0805_2012Metric.kicad_mod", 130, 115, 0),
    ("TP1","TestPoint.pretty/TestPoint_2Pads_Pitch2.54mm_Drill0.8mm.kicad_mod", 130, 20, 0),
]

placed = 0
for ref, fp_path, x, y, rot in comps_pos:
    full_path = os.path.join(KICAD_LIB, fp_path)
    if not os.path.exists(full_path):
        # 递归搜索
        import glob
        matches = list(glob.glob(f"{KICAD_LIB}/**/{os.path.basename(fp_path)}", recursive=True))
        if not matches:
            print(f"MISS: {ref} — {fp_path}")
            continue
        full_path = matches[0]
    
    fp = pcbnew.FootprintLoad(os.path.dirname(full_path), os.path.basename(full_path).replace('.kicad_mod',''))
    if fp is None:
        print(f"LOAD FAIL: {ref}")
        continue
    
    fp.SetReference(ref)
    fp.SetPosition(pcbnew.VECTOR2I(int(x*1e6), int(y*1e6)))
    fp.SetOrientationDegrees(rot)
    board.Add(fp)
    placed += 1

print(f"Placed: {placed}/{len(comps_pos)}")

# ===== 网络分配 =====
net_map = {
    ('J1','1'):'CS',('U1','5'):'CS', ('J1','2'):'SCLK',('U1','3'):'SCLK',
    ('J1','3'):'MOSI',('U1','2'):'MOSI', ('J1','4'):'MISO',('U1','4'):'MISO',
    ('J2','1'):'SIG',('R1','1'):'SIG', ('R1','2'):'TAC',('C1','1'):'TAC',
    ('C1','2'):'ADC_IN',('U1','10'):'ADC_IN', ('U2','2'):'VREF',('U1','7'):'VREF',
    ('J1','5'):'VDD',('U3','2'):'VDD',('U3','3'):'VDD',('U1','6'):'VDD',
    ('J1','6'):'V5V',('U2','1'):'V5V', ('J2','2'):'GND',('D2','1'):'GND',
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

print(f"Nets assigned: {assigned}")

# 保存
save_path = 'pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb'
board.Save(save_path)
print(f"Saved: {save_path}")
print(f"Footprints: {len(list(board.GetFootprints()))}")
print(f"Nets: {assigned}")
