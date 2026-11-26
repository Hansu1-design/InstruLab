"""正确生成KiCad 10.0兼容的原理图"""
from pathlib import Path

PRJ = Path("pcb/tdc_daughterboard")

# KiCad 10.0 S-expression格式原理图
# 注意: (symbol ...) 内必须用 lib_id, at, property("Reference" ...) 等
sch_content = """(kicad_sch (version 20240101) (generator "eeschema")

  (uuid 11111111-1111-1111-1111-111111111111)

  (title_block
    (title "TDC Daughterboard - TAC + ADC")
    (date "2026-07-18")
    (rev "1.0")
    (company "NUC-InstruLab")
  )

  (symbol (lib_id "Connector_Generic:Conn_02x10_Odd_Even") (at 25.4 101.6 0) (unit 1)
    (in_bom yes) (on_board yes)
    (property "Reference" "J1" (at 25.4 101.6 0) (effect (font (size 1.27 1.27)) (justify left)))
    (property "Value" "PMOD_Header" (at 25.4 101.6 0) (effect (font (size 1.27 1.27)) (justify left)))
    (property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm" (at 25.4 101.6 0) (effect (font (size 1.27 1.27)) (justify left) hide))
  )

  (symbol (lib_id "Connector_Coaxial:SMA" (at 50.8 50.8 0) (unit 1)
    (in_bom yes) (on_board yes)
    (property "Reference" "J2" (at 50.8 50.8 0) (effect (font (size 1.27 1.27)) (justify left)))
    (property "Value" "SMA" (at 50.8 50.8 0) (effect (font (size 1.27 1.27)) (justify left)))
    (property "Footprint" "Connector_Coaxial:SMA" (at 50.8 50.8 0) (effect (font (size 1.27 1.27)) (justify left) hide))
  )

  (symbol (lib_id "Device:R") (at 76.2 76.2 0) (unit 1)
    (in_bom yes) (on_board yes)
    (property "Reference" "R1" (at 76.2 76.2 0) (effect (font (size 1.27 1.27)) (justify left)))
    (property "Value" "100" (at 76.2 76.2 0) (effect (font (size 1.27 1.27)) (justify left)))
    (property "Footprint" "Resistor_SMD:R_0805" (at 76.2 76.2 0) (effect (font (size 1.27 1.27)) (justify left) hide))
  )

  (symbol (lib_id "Device:C") (at 76.2 101.6 0) (unit 1)
    (in_bom yes) (on_board yes)
    (property "Reference" "C1" (at 76.2 101.6 0) (effect (font (size 1.27 1.27)) (justify left)))
    (property "Value" "100pF" (at 76.2 101.6 0) (effect (font (size 1.27 1.27)) (justify left)))
    (property "Footprint" "Capacitor_SMD:C_0805" (at 76.2 101.6 0) (effect (font (size 1.27 1.27)) (justify left) hide))
  )

  (symbol (lib_id "Device:C_Small") (at 76.2 127.0 0) (unit 1)
    (in_bom yes) (on_board yes)
    (property "Reference" "C2" (at 76.2 127.0 0) (effect (font (size 1.27 1.27)) (justify left)))
    (property "Value" "10uF" (at 76.2 127.0 0) (effect (font (size 1.27 1.27)) (justify left)))
    (property "Footprint" "Capacitor_SMD:C_0805" (at 76.2 127.0 0) (effect (font (size 1.27 1.27)) (justify left) hide))
  )

  (symbol (lib_id "power:GND") (at 76.2 139.7 0) (unit 1)
    (in_bom yes) (on_board yes)
    (property "Reference" "#PWR" (at 76.2 139.7 0) (effect (font (size 1.27 1.27)) (justify left) hide))
    (property "Value" "GND" (at 76.2 139.7 0) (effect (font (size 1.27 1.27)) (justify left)))
  )

  (symbol (lib_id "power:+5V") (at 25.4 50.8 0) (unit 1)
    (in_bom yes) (on_board yes)
    (property "Reference" "#PWR" (at 25.4 50.8 0) (effect (font (size 1.27 1.27)) (justify left) hide))
    (property "Value" "+5V" (at 25.4 50.8 0) (effect (font (size 1.27 1.27)) (justify left)))
  )

  (symbol (lib_id "power:+3.3V") (at 25.4 25.4 0) (unit 1)
    (in_bom yes) (on_board yes)
    (property "Reference" "#PWR" (at 25.4 25.4 0) (effect (font (size 1.27 1.27)) (justify left) hide))
    (property "Value" "+3.3V" (at 25.4 25.4 0) (effect (font (size 1.27 1.27)) (justify left)))
  )

  (wire (pts (xy 25.4 50.8) (xy 25.4 76.2)) (stroke (width 0) (type default)) (layer "F.Cu") (net 1))
  (wire (pts (xy 25.4 76.2) (xy 50.8 76.2)) (stroke (width 0) (type default)) (layer "F.Cu") (net 1))
  (wire (pts (xy 50.8 76.2) (xy 76.2 76.2)) (stroke (width 0) (type default)) (layer "F.Cu") (net 1))
  (wire (pts (xy 76.2 88.9) (xy 76.2 101.6)) (stroke (width 0) (type default)) (layer "F.Cu") (net 1))
  (wire (pts (xy 76.2 114.3) (xy 76.2 127.0)) (stroke (width 0) (type default)) (layer "F.Cu") (net 1))
  (wire (pts (xy 76.2 139.7) (xy 76.2 152.4)) (stroke (width 0) (type default)) (layer "F.Cu") (net 0))

  (net (code 0) (name "GND"))
  (net (code 1) (name "+5V"))
  (net (code 2) (name "TAC_OUT"))
  (net (code 3) (name "SPI_CS"))
)
"""

(PRJ / "tdc_daughterboard.kicad_sch").write_text(sch_content, encoding='utf-8')

# 重写PCB文件
pcb_content = """(kicad_pcb (version 20240101) (generator "pcbnew")

  (uuid 22222222-2222-2222-2222-222222222222)

  (general
    (thickness 1.6)
  )

  (paper "A4")
  (layers
    (0 "F.Cu" signal)
    (31 "B.Cu" signal)
  )

  (setup
    (stackup
      (layer (name "F.Cu") (type copper) (thickness 0.035))
      (layer (name "dielectric 1") (type prepreg) (thickness 1.524))
      (layer (name "B.Cu") (type copper) (thickness 0.035))
    )
  )

  (footprint (lib_id "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm") (at 25.4 101.6 0)
    (property "Reference" "J1" (at 25.4 101.6 0) (effect (font (size 1 1))))
    (property "Value" "PMOD_Header" (at 25.4 101.6 0) (effect (font (size 1 1))))
    (attr board_only)
  )

  (footprint (lib_id "Connector_Coaxial:SMA") (at 50.8 50.8 0)
    (property "Reference" "J2" (at 50.8 50.8 0) (effect (font (size 1 1))))
    (property "Value" "SMA" (at 50.8 50.8 0) (effect (font (size 1 1))))
    (attr board_only)
  )

  (footprint (lib_id "Resistor_SMD:R_0805") (at 76.2 76.2 0)
    (property "Reference" "R1" (at 76.2 76.2 0) (effect (font (size 1 1))))
    (property "Value" "100" (at 76.2 76.2 0) (effect (font (size 1 1))))
    (attr board_only)
  )

  (footprint (lib_id "Capacitor_SMD:C_0805") (at 76.2 101.6 0)
    (property "Reference" "C1" (at 76.2 101.6 0) (effect (font (size 1 1))))
    (property "Value" "100pF" (at 76.2 101.6 0) (effect (font (size 1 1))))
    (attr board_only)
  )

  (segment (start 25.4 50.8) (end 76.2 76.2) (width 0.25) (layer "F.Cu") (net 1))
  (via (at 76.2 76.2) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net 1))
)
"""

(PRJ / "tdc_daughterboard.kicad_pcb").write_text(pcb_content, encoding='utf-8')

print("KiCad 10.0兼容文件已生成")
print(f"原理图: {PRJ}/tdc_daughterboard.kicad_sch")
print(f"PCB: {PRJ}/tdc_daughterboard.kicad_pcb")
PYEOF