// ============================================================
// FPGA-TDC精密时间间隔测量仪 — 顶层设计 (升级版 v2.0)
//
// 架构升级:
//   1. 双模式: TAC高精度模式(1.5ps) / CARRY4快速模式(33ps)
//   2. 新增CARRY4进位链细测量 (梁东飞论文)
//   3. 新增AD7980 16bit ADC SPI接口 (赵雪鹏论文)
//   4. 多通道扩展接口预留
//   5. 温度传感器接口预留 (亢叶飞测温方案)
//   6. 3级触发同步 + 实时抖动补偿
//
// 时钟方案:
//   单时钟域: 100MHz板载参考
//   PLL倍频: 100MHz → 400MHz (粗计数+进位链时钟)
//            MMCME2_BASE原语 (Vivado 2017.3+)
//
// 来源论文:
//   [1] 赵雪鹏《高分辨率时间间隔测量技术》(2022)
//   [2] 梁东飞《消除触发抖动》(2023)
//   [3] 亢叶飞《离子色谱柱温箱高精度测温电路》(2023)
//   [4] 韩文革《三阶锁相环频率合成技术的时钟源》(2018)
// ============================================================

module tdc_top (
    // ---- 系统接口 ----
    input  wire        clk,              // 100MHz 板载时钟
    input  wire        rst_n,            // 复位(低有效)
    
    // ---- 触发接口 ----
    input  wire        trig_in,          // 外触发输入(被测信号)
    input  wire        start,            // 开始测量
    input  wire        trig_mode,        // 触发模式: 0=外触发, 1=内触发(软件)
    
    // ---- 模式选择 ----
    input  wire        mode_select,      // 0=TAC高精度模式, 1=CARRY4快速模式
    
    // ---- TAC测量结果 (TAC模式) ----
    output wire [48:0] coarse_time,      // 粗计数结果
    output wire [15:0] fine_tac,         // TAC细测量结果 (16bit)
    
    // ---- CARRY4测量结果 (CARRY4模式) ----
    output wire [4:0]  fine_carry4,      // CARRY4细码 (5bit)
    output wire        carry4_valid,     // CARRY4有效
    
    // ---- 融合结果 ----
    output wire [64:0] tdc_result,       // 最终融合结果 (49bit粗+16bit细)
    output wire        valid,            // 数据有效
    
    // ---- 抖动补偿 ----
    output wire [4:0]  jitter_comp,      // 抖动补偿值
    output wire        jitter_valid,     // 抖动补偿有效
    
    // ---- AD7980 SPI接口 (TAC模式下连接外部ADC) ----
    output wire        adc_cnv,          // ADC转换启动
    output wire        adc_sck,          // ADC SPI时钟
    input  wire        adc_sdo,          // ADC SPI数据
    
    // ---- SPI从机接口 (上位机通信) ----
    input  wire        spi_cs,           // SPI片选
    input  wire        spi_clk,          // SPI时钟
    input  wire        spi_mosi,         // SPI主机输出/从机输入
    output wire        spi_miso,         // SPI从机输出
    
    // ---- 多通道扩展接口 (预留) ----
    input  wire [3:0]  ext_trig,         // 扩展通道外触发 (4路预留)
    output wire [3:0]  ext_trig_rdy,     // 扩展通道就绪
    input  wire [3:0]  ext_mode,         // 扩展通道模式
    
    // ---- 温度传感器接口 (预留, 亢叶飞2023测温方案) ----
    // Pt1000四线制比例测量法, 采用I2C或1-Wire接口的Σ-Δ ADC
    inout              temp_sda,         // 温度传感器数据线 (I2C)
    inout              temp_scl          // 温度传感器时钟线 (I2C)
);

    // ============================================================
    // 内部信号声明
    // ============================================================
    
    // 时钟与复位
    wire clk_400m;          // PLL输出的400MHz主时钟
    wire clk_100m;          // 100MHz慢速时钟
    wire clk_200m;          // 200MHz中间时钟
    wire pll_locked;        // PLL锁定
    wire rst_sys;           // 系统复位 (含PLL锁定条件)
    
    // 触发路径
    wire trig_sync_out;     // 同步后的触发
    wire [4:0] jitter_comp_w;
    wire jitter_valid_w;
    
    // TAC路径
    wire [48:0] coarse_w;   // 粗计数结果
    wire [15:0] tac_fine_w; // TAC细测结果
    
    // CARRY4路径
    wire [4:0]  carry4_fine_w;
    wire        carry4_valid_w;
    
    // ADC接口
    wire [15:0] adc_data_w;
    wire        adc_done_w;
    wire        adc_conv_start_w;
    
    // 模式选择输出
    reg  [64:0] mode_result;     // 按模式选择的最终结果
    reg         mode_valid;      // 模式选择的valid
    reg  [15:0] mode_fine_tac;   // 模式选择的TAC细值
    reg  [4:0]  mode_fine_carry4; // 模式选择的CARRY4细值
    
    // 数据融合输出 (从data_fusion来)
    wire [64:0] fusion_result_w;
    wire        fusion_valid_w;

    // ---- 系统复位 (PLL锁定后延迟释放) ----
    // 修复 v2.1: rst_sys 在 PLL 锁定后额外保持低电平 3 个 100MHz 周期 (~30ns),
    //   保证 clk_400m 在 rst_sys 释放前已开始运行, coarse_counter 的同步复位
    //   在 clk_400m 第一个上升沿就能正确清零, 不再遗存 'x'。
    reg [1:0] rst_release_cnt;
    reg       rst_sys_r;
    
    always @(posedge clk_100m or negedge rst_n) begin
        if (!rst_n) begin
            rst_release_cnt <= 0;
            rst_sys_r       <= 0;
        end else begin
            if (pll_locked && !rst_sys_r) begin
                if (rst_release_cnt < 2'd2)
                    rst_release_cnt <= rst_release_cnt + 1;
                else
                    rst_sys_r <= 1;
            end
        end
    end
    
    assign rst_sys = rst_sys_r;

    // ============================================================
    // 时钟发生器: 100MHz → 400MHz + 200MHz
    // ============================================================
    clk_gen u_clk (
        .clk_100m_in  (clk),
        .rst_n        (rst_n),
        .clk_400m     (clk_400m),
        .clk_200m     (clk_200m),
        .clk_100m     (clk_100m),
        .pll_locked   (pll_locked)
    );

    // ============================================================
    // 触发同步 (3级触发器 + 抖动补偿)
    // 来源: 梁东飞论文
    // ============================================================
    trig_sync u_trig (
        .clk           (clk_400m),
        .rst_n         (rst_sys),
        .trig_in       (trig_in),
        .trig_mode     (trig_mode),
        .manual_trig   (start),
        .carry4_fine   (carry4_fine_w),
        .carry4_valid  (carry4_valid_w),
        .trig_out      (trig_sync_out),
        .jitter_comp   (jitter_comp_w),
        .jitter_valid  (jitter_valid_w)
    );

    // ============================================================
    // 脉冲展宽: trig_sync_out (400MHz域, 2.5ns脉冲) → 展宽为≥10ns
    // 保证100MHz域的CDC能可靠捕获
    // 展宽后恢复为边沿信号给TAC控制器
    // ============================================================
    reg [3:0] pulse_ext;         // 展宽计数器 (400MHz域)
    reg       trig_extended;     // 展宽后的触发 (400MHz域)
    
    always @(posedge clk_400m or negedge rst_sys) begin
        if (!rst_sys) begin
            pulse_ext     <= 0;
            trig_extended <= 0;
        end else begin
            if (trig_sync_out)
                pulse_ext <= 4'd8;          // 加载计数器 (8 × 2.5ns = 20ns = 2个100MHz周期)
            else if (|pulse_ext)
                pulse_ext <= pulse_ext - 1; // 递减
                
            if (trig_sync_out)
                trig_extended <= 1;          // 置高
            else if (pulse_ext == 1)
                trig_extended <= 0;          // 计数到1时释放 (确保已够20ns)
        end
    end
    
    // ============================================================
    // CDC: trig_extended (clk_400m) → trig_sync_100m (clk_100m)
    // 展宽后的信号≥20ns, 2级同步器可可靠捕获
    // 传递电平信号(非边沿)因为TAC控制器需要start/stop电平
    // ============================================================
    reg [1:0] trig_cdc;
    reg       trig_sync_100m;
    
    always @(posedge clk_100m or negedge rst_sys) begin
        if (!rst_sys) begin
            trig_cdc        <= 0;
            trig_sync_100m  <= 0;
        end else begin
            // 2级同步器 - 传递电平
            trig_cdc        <= {trig_cdc[0], trig_extended};
            trig_sync_100m  <= trig_cdc[1];
        end
    end

    // ============================================================
    // CARRY4进位链细测量 (双模式中均运行, 用于抖动测量)
    // ============================================================
    carry4_tdc u_carry4 (
        .clk       (clk_400m),
        .rst_n     (rst_sys),
        .trig_in   (trig_in),
        .fine_code (carry4_fine_w),
        .valid     (carry4_valid_w)
    );

    // ============================================================
    // 粗计数器 (49bit @ 400MHz)
    // 来源: 赵雪鹏硕士论文
    // ============================================================
    coarse_counter u_coarse (
        .clk    (clk_400m),
        .rst_n  (rst_sys),
        .start  (trig_sync_out),
        .stop   (~trig_sync_out),
        .count  (coarse_w)
    );

    // ============================================================
    // AD7980 SPI接口 (TAC模式用)
    // ============================================================
    adc_ad7980 u_adc (
        .clk         (clk_100m),
        .rst_n       (rst_sys),
        .conv_start  (adc_conv_start_w),
        .adc_data    (adc_data_w),
        .adc_done    (adc_done_w),
        .cnv         (adc_cnv),
        .sck         (adc_sck),
        .sdo         (adc_sdo)
    );

    // ============================================================
    // TAC控制器 (TAC高精度模式, clk_100m域)
    // ============================================================
    tac_controller u_tac (
        .clk            (clk_100m),
        .rst_n          (rst_sys),
        .start          (trig_sync_100m),
        .stop           (~trig_sync_100m),
        .adc_read_data  (adc_data_w),
        .adc_read_done  (adc_done_w),
        .adc_conv_start (adc_conv_start_w),
        .adc_value      (tac_fine_w)
    );

    // ============================================================
    // 双模式选择: TAC高精度 / CARRY4快速
    // ============================================================
    always @(posedge clk_100m or negedge rst_sys) begin
        if (!rst_sys) begin
            mode_result      <= 0;
            mode_valid       <= 0;
            mode_fine_tac    <= 0;
            mode_fine_carry4 <= 0;
        end else begin
            case (mode_select)
                1'b0: begin  // TAC高精度模式
                    mode_result      <= {coarse_w, tac_fine_w};
                    mode_fine_tac    <= tac_fine_w;
                    mode_fine_carry4 <= carry4_fine_w;
                    mode_valid       <= adc_done_w;
                end
                1'b1: begin  // CARRY4快速模式
                    // CARRY4模式下, 将5-bit细码放在低位, 高11位填0
                    mode_result      <= {coarse_w, 11'd0, carry4_fine_w};
                    mode_fine_tac    <= 0;
                    mode_fine_carry4 <= carry4_fine_w;
                    mode_valid       <= carry4_valid_w;
                end
            endcase
        end
    end

    // ============================================================
    // 数据融合 (打包最终结果)
    // data_fusion的valid/output是输出, mode_valid/mode_result
    // 是输入数据, 融合模块重新打包为最终格式
    // ============================================================
    data_fusion u_fusion (
        .clk    (clk_100m),
        .rst_n  (rst_sys),
        .coarse (coarse_w),
        .fine   (mode_fine_tac),
        .valid  (fusion_valid_w),    // data_fusion输出valid
        .result (fusion_result_w)    // data_fusion输出result
    );

    // ============================================================
    // SPI从机接口 (上位机数据读取)
    // ============================================================
    spi_slave u_spi (
        .clk      (clk_100m),
        .cs       (spi_cs),
        .sclk     (spi_clk),
        .mosi     (spi_mosi),
        .miso     (spi_miso),
        .data_in  (mode_result),      // 模式选择的结果送SPI
        .data_out ()                   // 未用 (上位机只读)
    );

    // ============================================================
    // 多通道扩展接口 (预留)
    // 预留4路扩展通道, 每路可独立配置触发模式
    // ============================================================
    genvar ch;
    generate
        for (ch = 0; ch < 4; ch = ch + 1) begin : gen_ext_ch
            reg [2:0] ext_sync;
            reg       ext_sync_d2;
            reg       ext_rdy_r;
            always @(posedge clk_400m or negedge rst_sys) begin
                if (!rst_sys) begin
                    ext_sync    <= 0;
                    ext_sync_d2 <= 0;
                    ext_rdy_r   <= 0;
                end else begin
                    ext_sync    <= {ext_sync[1:0], ext_trig[ch]};
                    ext_sync_d2 <= ext_sync[2];
                    // 边沿检测: 锁存输出, 保持到主机读取
                    if (ext_sync[2] & ~ext_sync_d2)
                        ext_rdy_r <= 1;
                end
            end
            assign ext_trig_rdy[ch] = ext_rdy_r;
        end
    endgenerate

    // ============================================================
    // 输出赋值
    // ============================================================
    assign coarse_time  = coarse_w;
    assign fine_tac     = mode_fine_tac;
    assign fine_carry4  = mode_fine_carry4;
    assign carry4_valid = carry4_valid_w;
    assign tdc_result   = mode_result;
    assign valid        = mode_valid;
    assign jitter_comp  = jitter_comp_w;
    assign jitter_valid = jitter_valid_w;

endmodule
