#!/usr/bin/env python3
"""从KiCad封装库读真实数据，生成完整PCB（修正版）"""
from pathlib import Path
import re, uuid

LIB = Path("G:/kicad/share/kicad/footprints")
OUT = Path("pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb")

components = [
    ("R1", "Resistor_SMD.pretty/R_0805_2012Metric.kicad_mod", "Resistor_SMD", 76.2, 76.2, 90),
    ("C1", "Capacitor_SMD.pretty/C_0805_2012Metric.kicad_mod", "Capacitor_SMD", 76.2, 101.6, 90),
    ("U1", "Package_SO.pretty/JEITA_SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod", "Package_SO", 50.8, 25.4, 0),
    ("U2", "Package_SO.pretty/JEITA_SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod", "Package_SO", 76.2, 25.4, 0),
    ("J1", "Connector_PinHeader_2.54mm.pretty/PinHeader_2x10_P2.54mm_Vertical.kicad_mod", "Connector_PinHeader_2.54mm", 25.4, 101.6, 0),
    ("J2", "Connector_Coaxial.pretty/SMA_Amphenol_132134-10_Vertical.kicad_mod", "Connector_Coaxial", 50.8, 50.8, 0),
]

def gen_uuid():
    return str(uuid.uuid4())

# PCB 头部
pcb = f"""(kicad_pcb
	(version 20260206)
	(generator "pcbnew") (generator_version "10.0")
	(general (thickness 1.6) (legacy_teardrops no))
	(paper "A4")
	(layers
		(0 "F.Cu" signal) (2 "B.Cu" signal)
		(5 "F.SilkS" user "F.Silkscreen") (7 "B.SilkS" user "B.Silkscreen")
		(1 "F.Mask" user) (3 "B.Mask" user)
		(25 "Edge.Cuts" user) (27 "Margin" user)
		(31 "F.CrtYd" user "F.Courtyard") (29 "B.CrtYd" user "B.Courtyard")
		(35 "F.Fab" user) (33 "B.Fab" user)
		(13 "F.Paste" user) (15 "B.Paste" user))
	(setup
		(pad_to_mask_clearance 0)
		(allow_soldermask_bridges_in_footprints no)
		(tenting (front yes) (back yes)) (covering (front no) (back no))
		(capping no) (filling no)
		(pcbplotparams
			(layerselection 0x00000000_00000000_55555555_5755f5ff)
			(outputformat 1) (mirror no) (drillshape 1) (scaleselection 1)
			(outputdirectory "")))
"""

# 插入封装
for ref, fp_file, lib_name, x, y, rot in components:
    content = (LIB / fp_file).read_text(encoding='utf-8')
    
    # 删除版本/生成器行（第2-3行）
    lines = content.split('\n')
    cleaned = []
    for line in lines:
        # 跳过version/generator行
        if line.strip().startswith('(version ') or line.strip().startswith('(generator '):
            continue
        cleaned.append(line)
    content = '\n'.join(cleaned)
    
    # 修改引用
    content = re.sub(r'\(property "Reference" "[^"]*"', f'(property "Reference" "{ref}"', content)
    content = re.sub(r'\(property "Value" "[^"]*"', f'(property "Value" "{ref}"', content)
    
    # 设置位置 (第一行的(at ...))
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('(at ') and i < 5:
            lines[i] = f'\t\t(at {x} {y} {rot})'
            break
    content = '\n'.join(lines)
    
    # 添加uuid（第一个括号后）
    content = re.sub(r'(\(layer "F\.Cu"\))', f'\\1\n\t\t(uuid "{gen_uuid()}")', content, count=1)
    
    pcb += content + '\n'

# 板框
pcb += f"""	(gr_line (start 0 0) (end 50 0) (stroke (width 0.2) (type default)) (layer "Edge.Cuts")
		(uuid "{gen_uuid()}"))
	(gr_line (start 50 0) (end 50 40) (stroke (width 0.2) (type default)) (layer "Edge.Cuts")
		(uuid "{gen_uuid()}"))
	(gr_line (start 50 40) (end 0 40) (stroke (width 0.2) (type default)) (layer "Edge.Cuts")
		(uuid "{gen_uuid()}"))
	(gr_line (start 0 40) (end 0 0) (stroke (width 0.2) (type default)) (layer "Edge.Cuts")
		(uuid "{gen_uuid()}"))
	(embedded_fonts no)
)"""

OUT.write_text(pcb, encoding='utf-8')
sz = OUT.stat().st_size
print(f"✅ PCB生成成功: {sz} bytes")
print(f"   元件: {len(components)}个")
