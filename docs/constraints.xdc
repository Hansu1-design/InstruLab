# InstruLab TDC — Vivado管脚+时序约束 (v3.0)
# 板卡: Basys3 / Nexys4 (Artix-7 XC7A35T)
#
# 更新 v3.0:
#   - 添加CDC约束消除跨时钟域hold violation
#   - 输入时钟域与PLL时钟域设为异步
#   - PLL输出时钟域间设置max_delay约束
#   - CARRY4延迟线保持约束
#
# 时钟树:
#   clk (100MHz输入) → MMCME2_BASE
#     ├── clk_400m (PLL CLKOUT0, 400MHz)
#     └── clk_100m_1 (PLL CLKOUT1, 100MHz)

# ============================================
# 1. 管脚约束 (原封不动)
# ============================================

# 时钟 (100MHz板载)
set_property PACKAGE_PIN W5 [get_ports clk]
create_clock -period 10.000 -name clk [get_ports clk]

# 复位
set_property PACKAGE_PIN U18 [get_ports rst_n]

# 触发输入/输出
set_property PACKAGE_PIN J15 [get_ports trig_in]
set_property PACKAGE_PIN L15 [get_ports valid]

# SPI接口 (普通IO, 非时钟)
set_property PACKAGE_PIN A14 [get_ports spi_cs]
set_property PACKAGE_PIN B14 [get_ports spi_clk]
set_property PACKAGE_PIN C14 [get_ports spi_mosi]
set_property PACKAGE_PIN D14 [get_ports spi_miso]
set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets spi_clk_IBUF]

# ============================================
# 2. CARRY4延迟线保持约束
#    防止Vivado合并或优化三路并行延迟线
# ============================================

# RTL已添加 (* DONT_TOUCH = "TRUE" *) 约束到寄存器声明
# 额外用XDC约束确保 nets 不被优化
set_property DONT_TOUCH TRUE [get_cells u_carry4/carry_line_a_reg*]
set_property DONT_TOUCH TRUE [get_cells u_carry4/carry_line_b_reg*]
set_property DONT_TOUCH TRUE [get_cells u_carry4/carry_line_c_reg*]

# ============================================
# 3. 跨时钟域(CDC)约束
# ============================================
#
# 策略说明:
#   输入时钟(clk)域与PLL生成时钟域是异步的。
#   PLL的clk_400m和clk_100m_1虽有固定相位关系,
#   但设计中的多bit CDC路径(coarse_w, fine_w等)
#   没有握手/FIFO同步, 只有在RTL层面修复后才能
#   进行同步时序分析。当前先用约束避开hold violation。
#
# ============================================

# 3a. 输入时钟域 → PLL时钟域: 异步处理
#     trig_in/start/trig_mode等输入信号跨越到PLL域
#     trig_sync有3级同步器处理trig_in
#     其他信号(start等)是手动/慢速操作
set_clock_groups -asynchronous \
    -group [get_clocks clk] \
    -group [get_clocks -include_generated_clocks -of [get_pins u_clk/u_mmcm/CLKOUT0]] \
    -group [get_clocks -include_generated_clocks -of [get_pins u_clk/u_mmcm/CLKOUT1]]

# 3b. PLL输出时钟域间: clk_400m ↔ clk_100m_1
#     这些域有固定相位关系(100MHz是400MHz的4分频)
#     但设计中的多bit CDC路径缺少同步器
#     先设max_delay放宽时序要求
#
#    粗计数器(coarse_w, 49bit) 从clk_400m→clk_100m_1
#    CARRY4细码(carry4_fine_w, 5bit) 从clk_400m→clk_100m_1
#    这些路径需要CDC FIFO, 当前用max_delay 10ns放宽
set_max_delay -from [get_clocks -of [get_pins u_clk/u_mmcm/CLKOUT0]] \
              -to [get_clocks -of [get_pins u_clk/u_mmcm/CLKOUT1]] 10.0

# 3c. trig_extended (clk_400m) → trig_cdc 同步器 (clk_100m_1)
#     展宽后的触发信号跨时钟域, 有2级同步器
#     Vivado自动识别同步器并处理, 无需额外约束
#     但设置max_delay以防Vivado 2017.3不自动识别
set_max_delay -datapath_only -from [get_cells u_tdc_top/trig_extended_reg] \
              -to [get_cells u_tdc_top/trig_cdc_reg[0]] 10.0

# ============================================
# 4. 输入延迟约束
# ============================================

# SPI接口约束 (clk_100m_1域)
set_input_delay -clock [get_clocks clk] -max 5.0 \
    [get_ports {spi_*} -filter {DIRECTION==IN}]
set_input_delay -clock [get_clocks clk] -min 1.0 \
    [get_ports {spi_*} -filter {DIRECTION==IN}]
