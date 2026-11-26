# InstruLab — FPGA-based Precision Time-Interval Measurement (TDC)

A Field-Programmable-Gate-Array Time-to-Digital Converter (TDC) instrument for
picosecond-resolution time-interval measurement, combining a coarse counter,
a Time-to-Amplitude Converter (TAC) fine-measurement stage and a trigger-jitter
elimination front end.

## Architecture

```
Ext. trigger → Jitter elimination → Coarse counter (49-bit @ 400 MHz) → Data fusion → USB/SPI → PC
                                 → TAC fine measurement (1.5 ps) → 16-bit ADC ↗
```

Design targets are grounded in published TDC research (see References below):
sub-10 ps system jitter, ~5 ps single-shot resolution on the fine stage.

## Repository Layout

```
rtl/        FPGA sources (Verilog/VHDL) + testbenches
             tdc_top.v / tdc_modules.v / tdc_extra.v   top level, coarse+TAC+jitter, fusion+SPI
             carry4_tdc.v  carry-chain TDC core
             adc_ad7980.v / clk_gen.v                  ADC driver, clocking
software/   PC host tools (Python): CLI/GUI controller (tdc_controller.py),
            calibration program (tdc_calibration.py)
pcb/        KiCad automation toolchain: board generation, net assignment,
            freerouting DSN export/import (one-click routing scripts included),
            TDC daughterboard project (BOM / design notes / manual)
data/       Calibration LUT + measurement CSV
docs/       PCB design rules, power tree, constraints (XDC)
```

## Quick Start

```bash
cd software
python tdc_controller.py        # CLI mode
```

Simulation: each RTL module ships with a `*_tb.v` testbench (runs under
Icarus Verilog / Vivado XSIM).

## Verification Status

- FPGA top-level: compiles under iverilog
- Coarse counter: 49-bit range (~391 hours @ 400 MHz)
- Jitter elimination: C-model cross-check, RSS deviation 0.3%
- TAC resolution: 0.76 ps (theoretical) / 1.5 ps (circuit level)
- Data fusion: 65-bit SPI output frame
- Host tools: CLI mode functional

## References

1. Zhao Xuepeng, *Research and Implementation of High-Resolution Time-Interval
   Measurement Technology* [D], 2022. (in Chinese)
2. Liang Dongfei et al., "A method for eliminating trigger jitter in pulsed
   delay generators" [J], *Chinese Journal of Electron Devices*.
3. "A high-precision pulse delay circuit design" [J], *China Measurement*, 2025.

## License

MIT — see [LICENSE](LICENSE).
