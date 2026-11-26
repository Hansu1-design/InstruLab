"""生成最简KiCad 10.0可打开的原理图+PCB"""
from pathlib import Path

PRJ = Path("pcb/tdc_daughterboard")

# 最简原理图 — 只放一个电阻+一个电容+GND
sch = """(kicad_sch (version 20240101) (generator "eeschema")
  (uuid 00000000-0000-0000-0000-000000000001)
  (title_block
    (title "TDC Daughterboard")
    (date "2026-07-18") (rev "1.0") (company "NUC-InstruLab"))

  (symbol (lib_id "Device:R") (at 50.8 50.8 0) (unit 1)
    (in_bom yes) (on_board yes)
    (property "Reference" "R1" (at 50.8 50.8 0)
      (effect (font (size 1.27 1.27)) (justify left)))
    (property "Value" "100" (at 50.8 50.8 0)
      (effect (font (size 1.27 1.27)) (justify left)))
    (property "Footprint" "Resistor_SMD:R_0805" (at 50.8 50.8 0)
      (effect (font (size 1.27 1.27)) (justify left) hide)))

  (symbol (lib_id "Device:C") (at 50.8 88.9 0) (unit 1)
    (in_bom yes) (on_board yes)
    (property "Reference" "C1" (at 50.8 88.9 0)
      (effect (font (size 1.27 1.27)) (justify left)))
    (property "Value" "100pF" (at 50.8 88.9 0)
      (effect (font (size 1.27 1.27)) (justify left)))
    (property "Footprint" "Capacitor_SMD:C_0805" (at 50.8 88.9 0)
      (effect (font (size 1.27 1.27)) (justify left) hide)))

  (symbol (lib_id "power:GND") (at 50.8 114.3 0) (unit 1)
    (in_bom yes) (on_board yes)
    (property "Reference" "#PWR" (at 50.8 114.3 0)
      (effect (font (size 1.27 1.27)) (justify left) hide))
    (property "Value" "GND" (at 50.8 114.3 0)
      (effect (font (size 1.27 1.27)) (justify left))))

  (wire (pts (xy 50.8 63.5) (xy 50.8 88.9)) (stroke (width 0) (type default)) (layer "F.Cu") (net 1))
  (wire (pts (xy 50.8 101.6) (xy 50.8 114.3)) (stroke (width 0) (type default)) (layer "F.Cu") (net 0))

  (net (code 0) (name "GND"))
  (net (code 1) (name "NET1"))
)
"""

(PRJ / "tdc_daughterboard.kicad_sch").write_text(sch, encoding='utf-8')

# 最简PCB
pcb = """(kicad_pcb (version 20240101) (generator "pcbnew")
  (uuid 00000000-0000-0000-0000-000000000002)
  (paper "A4")
  (layers
    (0 "F.Cu" signal)
    (31 "B.Cu" signal))
  (setup
    (stackup
      (layer (name "F.Cu") (type copper) (thickness 0.035))
      (layer (name "dielectric 1") (type prepreg) (thickness 1.6))
      (layer (name "B.Cu") (type copper) (thickness 0.035))))
  (footprint (lib_id "Resistor_SMD:R_0805") (at 50.8 50.8 0)
    (property "Reference" "R1" (at 50.8 50.8 0) (effect (font (size 1 1))))
    (property "Value" "100" (at 50.8 50.8 0) (effect (font (size 1 1))))
    (attr board_only))
  (footprint (lib_id "Capacitor_SMD:C_0805") (at 50.8 88.9 0)
    (property "Reference" "C1" (at 50.8 88.9 0) (effect (font (size 1 1))))
    (property "Value" "100pF" (at 50.8 88.9 0) (effect (font (size 1 1))))
    (attr board_only))
)
"""

(PRJ / "tdc_daughterboard.kicad_pcb").write_text(pcb, encoding='utf-8')

print("✅ 最简KiCad 10.0文件已生成")
print("打开路径: G:\\System\\InstruLab\\pcb\\tdc_daughterboard\\tdc_daughterboard.kicad_pro")
print("如果还报错, 可能是库路径问题。打开KiCad后:")
print("  设置 → 管理符号库 → 添加默认库")
PYEOF