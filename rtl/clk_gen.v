// ============================================================
// 时钟发生器模块 (升级版)
//
// 功能:
//   100MHz板载参考时钟 → PLL倍频 → 400MHz系统时钟
//   输出: 系统主时钟(400MHz) + 慢速时钟(100MHz)
//
// 来源:
//   - 韩文革硕士论文《基于三阶锁相环频率合成技术的时钟源设计》(2018)
//   - Xilinx 7-series MMCM/PLL用户指南
//
// 实现方案:
//   方案A: Xilinx MMCM原语 (推荐, 用于实际硬件)
//   方案B: 行为级仿真模型 (用于iverilog仿真)
//
// Xilinx MMCM配置 (方案A):
//   CLKIN1_PERIOD = 10.000  (100MHz)
//   CLKFBOUT_MULT_F = 8.0   (VCO = 800MHz)
//   CLKOUT0_DIVIDE_F = 2.0  → 400MHz
//   CLKOUT1_DIVIDE = 8      → 100MHz (同频但经PLL整形)
//   实际频率: 100MHz × 8 / 2 = 400MHz
//
// 注意:
//   实际综合时需取消注释MMCM原语, 注释掉仿真逻辑
// ============================================================

module clk_gen (
    input  wire  clk_100m_in,     // 100MHz 板载参考时钟
    input  wire  rst_n,           // 复位(低有效)
    output wire  clk_400m,        // 400MHz 系统主时钟 (TDC粗计数+进位链)
    output wire  clk_100m,        // 100MHz 慢速时钟 (SPI+控制逻辑)
    output wire  clk_200m,        // 200MHz 中间时钟 (可选)
    output wire  pll_locked       // PLL锁定指示
);

`ifdef USE_XILINX_MMCM
    // ============================================================
    // 方案A: Xilinx MMCM原语 (实际硬件综合)
    // 适用于 Vivado 2017.3+
    // ============================================================
    
    wire clk_feedback;
    wire mmcm_locked;
    
    MMCME2_BASE #(
        .BANDWIDTH          ("OPTIMIZED"),
        .CLKIN1_PERIOD      (10.000),      // 100MHz输入
        .CLKFBOUT_MULT_F    (8.000),       // VCO = 800MHz
        .CLKOUT0_DIVIDE_F   (2.000),       // 400MHz
        .CLKOUT1_DIVIDE     (8),           // 100MHz
        .CLKOUT2_DIVIDE     (4),           // 200MHz
        .CLKOUT0_PHASE      (0.000),
        .CLKOUT1_PHASE      (0.000),
        .CLKOUT2_PHASE      (0.000),
        .DIVCLK_DIVIDE      (1),
        .REF_JITTER1        (0.010),
        .CLKOUT4_CASCADE    ("FALSE"),
        .STARTUP_WAIT       ("FALSE")
    ) u_mmcm (
        .CLKIN1             (clk_100m_in),
        .CLKFBOUT           (clk_feedback),
        .CLKOUT0            (clk_400m),
        .CLKOUT1            (clk_100m),
        .CLKOUT2            (clk_200m),
        .LOCKED             (mmcm_locked),
        .PWRDWN             (1'b0),
        .RST                (~rst_n),
        .CLKFBIN            (clk_feedback)
    );
    
    assign pll_locked = mmcm_locked;

`else
    // ============================================================
    // 方案B: 行为级仿真模型 (用于iverilog)
    //
    // 用组合逻辑和简单的行为模型模拟PLL行为
    // 不产生精确的400MHz, 但满足功能仿真需求
    // ============================================================
    
    reg clk_400m_r = 0;
    reg clk_200m_r = 0;
    reg pll_locked_r = 0;
    
    // 模拟PLL锁定时间 (~1μs = 100个100MHz周期)
    reg [6:0] lock_cnt;
    always @(posedge clk_100m_in or negedge rst_n) begin
        if (!rst_n) begin
            lock_cnt <= 0;
            pll_locked_r <= 0;
        end else if (lock_cnt < 100) begin
            lock_cnt <= lock_cnt + 1;
        end else begin
            pll_locked_r <= 1;
        end
    end
    
    // 400MHz: 从100MHz 4倍频 (simplified for simulation)
    // 注意: 这是仿真行为, 不是可综合逻辑
    // 实际综合时使用上面的MMCM原语
    always @(posedge clk_100m_in or negedge rst_n) begin
        if (!rst_n)
            clk_400m_r <= 0;
        else if (pll_locked_r)
            clk_400m_r <= ~clk_400m_r;  // 100MHz → 200MHz (T/2)
    end
    
    // 200MHz: 100MHz 2倍频
    always @(posedge clk_100m_in or negedge rst_n) begin
        if (!rst_n)
            clk_200m_r <= 0;
        else if (pll_locked_r)
            clk_200m_r <= ~clk_200m_r;
    end
    
    // 真正的400MHz需要更复杂的建模
    // 这里用clk_400m_r的上升沿作为200MHz参考
    // 实际400MHz在综合时通过MMCM产生
    
    assign clk_400m   = clk_400m_r;    // 200MHz (仿真)
    assign clk_200m   = clk_200m_r;    // 100MHz (仿真)
    assign clk_100m   = clk_100m_in;
    assign pll_locked = pll_locked_r;

`endif

endmodule
