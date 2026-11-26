// ============================================================
// FPGA-TDC 仿真测试平台 (升级版 v2.0)
//
// 测试用例:
//   1. 时钟与PLL锁定测试
//   2. 粗计数路径验证 (基本触发)
//   3. CARRY4路径基本功能验证
//   4. AD7980 SPI读取时序验证 (模拟ADC)
//   5. 双模式切换验证 (TAC/CARRY4)
//   6. 触发抖动测量验证
//   7. 多通道扩展接口验证
//
// 来源: 赵雪鹏TDC论文 + 梁东飞CARRY4论文
// ============================================================

`timescale 1ns / 1ps

module tdc_tb;

    // ---- 系统信号 ----
    reg clk;                // 100MHz 板载时钟
    reg rst_n;              // 复位
    reg trig_in;            // 外触发
    reg start;              // 开始测量
    reg trig_mode;          // 触发模式
    reg mode_select;        // 模式选择
    
    // ---- 输出 ----
    wire [48:0] coarse_time;
    wire [15:0] fine_tac;
    wire [4:0]  fine_carry4;
    wire        carry4_valid;
    wire [64:0] tdc_result;
    wire        valid;
    wire [4:0]  jitter_comp;
    wire        jitter_valid;
    
    // ---- AD7980 SPI (模拟ADC) ----
    wire        adc_cnv;
    wire        adc_sck;
    wire        adc_sdo;
    
    // ---- SPI从机 ----
    reg         spi_cs;
    reg         spi_clk;
    reg         spi_mosi;
    wire        spi_miso;
    
    // ---- 扩展通道 ----
    reg  [3:0]  ext_trig;
    wire [3:0]  ext_trig_rdy;
    reg  [3:0]  ext_mode;
    
    // ---- 温度传感器 (预留) ----
    wire temp_sda, temp_scl;


    // ============================================================
    // 实例化待测模块
    // ============================================================
    tdc_top uut (
        .clk           (clk),
        .rst_n         (rst_n),
        .trig_in       (trig_in),
        .start         (start),
        .trig_mode     (trig_mode),
        .mode_select   (mode_select),
        .coarse_time   (coarse_time),
        .fine_tac      (fine_tac),
        .fine_carry4   (fine_carry4),
        .carry4_valid  (carry4_valid),
        .tdc_result    (tdc_result),
        .valid         (valid),
        .jitter_comp   (jitter_comp),
        .jitter_valid  (jitter_valid),
        .adc_cnv       (adc_cnv),
        .adc_sck       (adc_sck),
        .adc_sdo       (adc_sdo),
        .spi_cs        (spi_cs),
        .spi_clk       (spi_clk),
        .spi_mosi      (spi_mosi),
        .spi_miso      (spi_miso),
        .ext_trig      (ext_trig),
        .ext_trig_rdy  (ext_trig_rdy),
        .ext_mode      (ext_mode),
        .temp_sda      (temp_sda),
        .temp_scl      (temp_scl)
    );

    // ============================================================
    // 时钟产生: 100MHz (10ns周期)
    // ============================================================
    always #5 clk = ~clk;

    // ============================================================
    // 模拟AD7980行为 (使用独立的module, 避免驱动冲突)
    // CNV↑ → 转换 → 710ns后SDO有效 → 在SCK沿移出16位
    // ============================================================
    reg [15:0] adc_sim_data = 16'hA5A5;
    
    adc_sim_model #(.CONV_DELAY(710)) u_adc_sim (
        .cnv       (adc_cnv),
        .sck       (adc_sck),
        .data_in   (adc_sim_data),
        .sdo       (adc_sdo)
    );

    // ============================================================
    // 主测试序列
    // ============================================================
    integer i;
    
    initial begin
        // ---- 初始化 ----
        clk         = 0;
        rst_n       = 0;
        trig_in     = 0;
        start       = 0;
        trig_mode   = 0;   // 外触发
        mode_select = 0;   // TAC模式
        spi_cs      = 1;
        spi_clk     = 0;
        spi_mosi    = 0;
        ext_trig    = 0;
        ext_mode    = 0;
        
        $display("");
        $display("============================================");
        $display(" FPGA-TDC v2.0 精密时间间隔测量仿真");
        $display(" 升级: CARRY4进位链 + AD7980接口 + 双模式");
        $display("============================================");
        $display("");
        
        // ---- 释放复位 ----
        #20 rst_n = 1;
        $display("[%0t ps] 复位释放, 等待PLL锁定...", $time);
        
        // ---- 测试1: PLL锁定检测 ----
        #2000;
        if (uut.pll_locked)
            $display("[%0t ps] ✓ PLL已锁定", $time);
        else
            $display("[%0t ps] ✗ PLL未锁定 (仿真模型可能不产生精确400MHz)", $time);
        
        // ============================================================
        // 测试2: 粗计数路径 (TAC模式, 外触发)
        // ============================================================
        $display("");
        $display("--- 测试2: 粗计数路径 (TAC模式, 外触发) ---");
        
        mode_select = 0;   // TAC模式
        trig_mode   = 0;   // 外触发
        
        #100 start = 1; #20 start = 0;
        #50 trig_in = 1; #20 trig_in = 0;
        
        // 等待结果 — 轮询coarse_time(稳态,非脉冲)
        #100;
        for (i = 0; i < 200 && coarse_time == 0; i = i + 1)
            #100;
        if (coarse_time != 0) begin
            $display("[%0t ps] ✓ TAC模式测量完成", $time);
            $display("    coarse=%0d, fine_tac=0x%04h, carry4=%0d, result=0x%016h",
                     coarse_time, fine_tac, fine_carry4, tdc_result);
        end else
            $display("[%0t ps] ⚠ TAC模式超时 (coarse不变)", $time);
        
        // ============================================================
        // 测试3: CARRY4路径 (快速模式)
        // ============================================================
        $display("");
        $display("--- 测试3: CARRY4快速模式 ---");
        
        mode_select = 1;   // CARRY4模式
        
        #200 start = 1; #20 start = 0;
        #30 trig_in = 1; #20 trig_in = 0;
        
        #500;
        if (carry4_valid) begin
            $display("[%0t ps] ✓ CARRY4路径测量完成", $time);
            $display("    coarse=%0d, fine_carry4=%0d, jitter=%0d",
                     coarse_time, fine_carry4, jitter_comp);
        end else begin
            $display("[%0t ps] ✗ CARRY4路径无输出", $time);
        end
        
        // ============================================================
        // 测试4: 不同相位触发 (验证CARRY4位置变化)
        // ============================================================
        $display("");
        $display("--- 测试4: 不同相位触发 ---");
        
        for (i = 0; i < 5; i = i + 1) begin
            #200 start = 1; #20 start = 0;
            // 在不同的时间点触发, 得到不同的CARRY4相位
            #(10 + i*25) trig_in = 1; #20 trig_in = 0;
            #300;
            if (carry4_valid)
                $display("  触发%0d: coarse=%0d, carry4=%0d, jitter=%0d @ %0t ps",
                         i+1, coarse_time, fine_carry4, jitter_comp, $time);
        end
        
        // ============================================================
        // 测试5: 内触发模式
        // ============================================================
        $display("");
        $display("--- 测试5: 内触发模式 ---");
        
        mode_select = 1;   // CARRY4模式
        trig_mode   = 1;   // 内触发
        
        #200 start = 1; #20 start = 0;
        #300;
        if (carry4_valid)
            $display("[%0t ps] ✓ 内触发: coarse=%0d, carry4=%0d",
                     $time, coarse_time, fine_carry4);
        
        // ============================================================
        // 测试6: AD7980 SPI时序验证 (TAC模式, 外触发)
        // 先复位TAC状态机到IDLE
        // ============================================================
        $display("");
        $display("--- 测试6: AD7980 SPI读取 ---");
        
        mode_select = 0;   // TAC模式 (需要ADC)
        trig_mode   = 0;   // 外触发
        adc_sim_data = 16'hBEEF;  // 改变模拟ADC数据
        
        // 确保TAC回到IDLE
        #500 start = 1; #20 start = 0;
        #500 trig_in = 1; #20 trig_in = 0;
        
        // 轮询等待AD7980读取 — 最大20μs超时
        #100;
        for (i = 0; i < 200 && uut.u_tac.adc_value != 16'hBEEF; i = i + 1)
            #100;
        if (uut.u_tac.adc_value == 16'hBEEF)
            $display("[%0t ps] ✓ AD7980读取正确: 0x%04h", $time, uut.u_tac.adc_value);
        else
            $display("[%0t ps] ⚠ AD7980读取: 0x%04h (期望0xBEEF)", $time, uut.u_tac.adc_value);
        
        // ============================================================
        // 测试7: 多通道扩展接口
        // ============================================================
        $display("");
        $display("--- 测试7: 多通道扩展接口 ---");
        
        // 触发扩展通道0
        ext_trig[0] = 1; #20 ext_trig[0] = 0;
        #100;  // 足够时间让同步链传播(3级×20ns=60ns)
        if (ext_trig_rdy[0])
            $display("[%0t ps] ✓ 扩展通道0: 触发同步正常", $time);
        else
            $display("[%0t ps] ✗ 扩展通道0: 无同步输出", $time);
        
        // ============================================================
        // 测试8: SPI从机读取
        // ============================================================
        $display("");
        $display("--- 测试8: SPI从机数据读取 ---");
        
        // 模拟SPI主机读取 (65位数据)
        spi_cs = 0;  // 片选有效
        #20;
        for (i = 0; i < 65; i = i + 1) begin
            spi_clk = 1; #10;
            spi_clk = 0; #10;
        end
        spi_cs = 1;  // 片选释放
        $display("[%0t ps] ✓ SPI读取完成", $time);
        
        // ============================================================
        $display("");
        $display("============================================");
        $display(" 仿真完成");
        $display("============================================");
        $display("");
        $finish;
    end

    // ============================================================
    // 波形输出
    // ============================================================
    initial begin
        $dumpfile("tdc_sim_v2.vcd");
        $dumpvars(0, tdc_tb);
    end

endmodule

// ============================================================
// AD7980仿真模型 (仅用于testbench)
// 使用系统时钟同步, 避免SCK边沿竞争
// 行为: CNV↑ → 等待CONV_DELAY ns → MSB输出 → 每SCK↑移出1位
// ============================================================
module adc_sim_model #(
    parameter CONV_DELAY = 710  // 转换时间 (ns)
) (
    input  wire        cnv,
    input  wire        sck,
    input  wire [15:0] data_in,
    output reg         sdo
);

    reg [15:0] shift;
    reg        data_ready;
    reg        prev_sck;
    
    // CNV上升沿: 启动转换
    always @(posedge cnv) begin
        shift <= data_in;
        data_ready <= 0;
        sdo <= 0;
        #CONV_DELAY;
        data_ready <= 1;
        sdo <= data_in[15];
    end
    
    // SCK上升沿检测: 移出下一位 (用延迟赋值避免竞争)
    always @(posedge sck) begin
        if (data_ready) begin
            #1;  // 延迟1ps, 确保host侧先完成捕获
            shift <= {shift[14:0], 1'b0};
            sdo <= shift[14];
        end
    end

endmodule
