#!/usr/bin/env python3
"""生成完整TDC子板PCB — 走线+铺铜"""
from pathlib import Path
import re, uuid

LIB = Path("G:/kicad/share/kicad/footprints")
OUT = Path("pcb/tdc_daughterboard/tdc_daughterboard.kicad_pcb")

comps = [
    ("R1","Resistor_SMD.pretty/R_0805_2012Metric.kicad_mod","Resistor_SMD",76.2,76.2,90),
    ("C1","Capacitor_SMD.pretty/C_0805_2012Metric.kicad_mod","Capacitor_SMD",76.2,101.6,90),
    ("U1","Package_SO.pretty/MSOP-10_3x3mm_P0.5mm.kicad_mod","Package_SO",50.8,25.4,0),
    ("U2","Package_SO.pretty/SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod","Package_SO",76.2,25.4,0),
    ("J1","Connector_PinHeader_2.54mm.pretty/PinHeader_2x10_P2.54mm_Vertical.kicad_mod","Connector_PinHeader_2.54mm",25.4,101.6,0),
    ("J2","Connector_Coaxial.pretty/SMA_Amphenol_132134_Vertical.kicad_mod","Connector_Coaxial",50.8,50.8,0),
]

def gu():
    return str(uuid.uuid4())

# Build header
lines = []
lines.append('(kicad_pcb')
lines.append('\t(version 20260206)')
lines.append('\t(generator "pcbnew") (generator_version "10.0")')
lines.append('\t(general (thickness 1.6) (legacy_teardrops no))')
lines.append('\t(paper "A4")')
lines.append('\t(layers')
lines.append('\t\t(0 "F.Cu" signal) (2 "B.Cu" signal)')
lines.append('\t\t(5 "F.SilkS" user "F.Silkscreen") (7 "B.SilkS" user "B.Silkscreen")')
lines.append('\t\t(1 "F.Mask" user) (3 "B.Mask" user)')
lines.append('\t\t(25 "Edge.Cuts" user)')
lines.append('\t\t(31 "F.CrtYd" user "F.Courtyard") (29 "B.CrtYd" user "B.Courtyard")')
lines.append('\t\t(35 "F.Fab" user) (33 "B.Fab" user))')
lines.append('\t(setup')
lines.append('\t\t(pad_to_mask_clearance 0)')
lines.append('\t\t(allow_soldermask_bridges_in_footprints no)')
lines.append('\t\t(tenting (front yes) (back yes))')
lines.append('\t\t(capping no) (filling no)')
lines.append('\t\t(pcbplotparams')
lines.append('\t\t\t(layerselection 0x00000000_00000000_55555555_5755f5ff)')
lines.append('\t\t\t(outputformat 1) (mirror no) (drillshape 1) (scaleselection 1)')
lines.append('\t\t\t(outputdirectory "")))')

# Insert footprints
for ref, fp_file, lib_name, x, y, rot in comps:
    content = (LIB / fp_file).read_text(encoding='utf-8')
    content = re.sub(r'\(version \d+\)\s*\(generator "[^"]*"\)', '', content)
    content = re.sub(r'\(property "Reference" "[^"]*"', '(property "Reference" "' + ref + '"', content)
    content = re.sub(r'\(at [-\d.]+ [-\d.]+ [-\d.]+\)', '(at ' + str(x) + ' ' + str(y) + ' ' + str(rot) + ')', content, count=1)
    lines.append(content)

# Tracks (F.Cu, 0.3mm)
tracks_data = [
    (28.0,101.6,35.0,101.6,0.3),(35.0,101.6,35.0,28.0,0.3),(35.0,28.0,50.8,28.0,0.3),
    (28.0,104.14,38.0,104.14,0.3),(38.0,104.14,38.0,27.5,0.3),(38.0,27.5,50.8,27.5,0.3),
    (28.0,106.68,41.0,106.68,0.3),(41.0,106.68,41.0,27.0,0.3),(41.0,27.0,50.8,27.0,0.3),
    (28.0,109.22,44.0,109.22,0.3),(44.0,109.22,44.0,31.0,0.3),(44.0,31.0,50.8,31.0,0.3),
]
for sx,sy,ex,ey,w in tracks_data:
    lines.append('\t(segment (start ' + str(sx) + ' ' + str(sy) + ') (end ' + str(ex) + ' ' + str(ey) + ') (width ' + str(w) + ') (layer "F.Cu") (net "") (uuid "' + gu() + '"))')

# Board outline
for sx,sy,ex,ey in [(0,0,50,0),(50,0,50,40),(50,40,0,40),(0,40,0,0)]:
    lines.append('\t(gr_line (start ' + str(sx) + ' ' + str(sy) + ') (end ' + str(ex) + ' ' + str(ey) + ') (stroke (width 0.2) (type default)) (layer "Edge.Cuts") (uuid "' + gu() + '"))')

lines.append('\t(embedded_fonts no)')
lines.append(')')

OUT.write_text('\n'.join(lines), encoding='utf-8')
tracks = len(tracks_data)
pads = '\n'.join(lines).count('(pad "')
print('PCB generated: ' + str(OUT.stat().st_size) + ' bytes')
print('Footprints: ' + str(len(comps)) + ', Pads: ' + str(pads) + ', Tracks: ' + str(tracks))
