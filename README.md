# InstruLab — FPGA-TDC精密时间间隔测量仪器

## 项目概述
基于FPGA的精密时间间隔测量仪器，融合公开文献调研TDC方向核心成果：
- 赵雪鹏(硕士): 高分辨率TDC(5ps/60ps)
- 梁东飞: 触发抖动消除(19.3ps系统抖动)
- 脉冲延迟电路(10ps精度/10⁵s量程)

## 硬件架构
```
外触发 → 抖动消除 → 粗计数(49bit@400MHz) → 数据融合 → USB/SPI → PC
                  → TAC细测量(1.5ps) → 16bit ADC →┘
```

## 目录结构
```

├── rtl/               # FPGA源码(Verilog/VHDL,含testbench)
│   ├── tdc_modules.v / tdc_extra.v      # 粗计数+TAC+抖动消除+数据融合+SPI
│   ├── carry4_tdc.v / adc_ad7980.v / clk_gen.v   # TDC进位链/ADC/时钟
│   └── *_tb.v                          # 各模块仿真testbench
├── software/          # PC上位机
│   ├── tdc_controller.py    # CLI+GUI控制程序
│   └── tdc_calibration.py   # 校准程序
├── pcb/               # KiCad自动化脚本与TDC子板工程(dsn/BOM/操作手册)
├── data/              # 校准LUT与测量数据
├── docs/              # 设计规则/电源树/PCB规范
└── README.md          # 本文件
```

## 一键运行
```bash
cd software
python tdc_controller.py
```

## 验证状态
- FPGA顶层设计: ✅ iverilog编译通过
- 粗计数器49bit: ✅ 量程391h
- 抖动消除: ✅ C验证RSS 0.3%偏差
- TAC分辨率: ✅ 0.76ps(理论)/1.5ps(电路级)
- 数据融合: ✅ SPI 65bit输出
- 上位机: ✅ CLI模式通过

## 论文支撑
1. 赵雪鹏. 高分辨率时间间隔测量技术研究与实现[D]. 中北大学, 2022.
2. 梁东飞, 苏淑靖等. 一种用于脉冲延时发生器中消除触发抖动的方法[J]. 电子器件.
3. 苏淑靖组. 一种高精度脉冲延迟电路设计[J]. 中国测试, 2025.
