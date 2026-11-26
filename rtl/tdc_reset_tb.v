// ============================================================
// TDC 复位行为专用验证测试平台
// 验证: coarse_counter 同步复位 + rst_sys 延迟释放修复
//
// 测试序列:
//   1. 上电复位阶段 (rst_n=0)
//   2. PLL锁定 + rst_sys 延迟释放
//   3. coarse 非 x 验证
//   4. 计数功能验证
//   5. 触发测量验证
// ============================================================

`timescale 1ns / 1ps

module tdc_reset_tb;

    // ---- 系统信号 ----
    reg         clk;
    reg         rst_n;
    reg         trig_in;
    reg         start;
    reg         trig_mode;
    reg         mode_select;

    // ---- 输出 ----
    wire [48:0] coarse_time;
    wire [15:0] fine_tac;
    wire [4:0]  fine_carry4;
    wire        carry4_valid;
    wire [64:0] tdc_result;
    wire        valid;

    // ---- AD7980 SPI (未用, 但需要连接) ----
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

    // ---- 温度传感器 ----
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
        .jitter_comp   (),
        .jitter_valid  (),
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
    // 时钟: 100MHz (10ns周期)
    // ============================================================
    always #5 clk = ~clk;


    // ============================================================
    // 主测试序列
    // ============================================================
    initial begin
        // ---- 初始化 ----
        clk         = 0;
        rst_n       = 0;
        trig_in     = 0;
        start       = 0;
        trig_mode   = 0;
        mode_select = 0;
        spi_cs      = 1;
        spi_clk     = 0;
        spi_mosi    = 0;
        ext_trig    = 0;
        ext_mode    = 0;

        $display("");
        $display("============================================");
        $display(" TDC 复位行为验证测试");
        $display(" 修复: coarse_counter 同步复位 + rst_sys 延迟释放");
        $display("============================================");
        $display("");
        $display("   clk_400m 仿真频率: ~50MHz (20ns周期)");
        $display("   PLL锁定模拟: ~1μs (100个100MHz周期)");
        $display("   rst_sys延迟释放: 3个100MHz周期 (30ns)");
        $display("");

        // ----------------------------------------------------------
        // 阶段1: 上电复位
        // ----------------------------------------------------------
        $display("--- 阶段1: 上电复位 (rst_n=0) ---");
        #20;
        $display("  @%0t ps: rst_n=%b, pll_locked=%b, rst_sys=%b",
                 $time, rst_n, uut.pll_locked, uut.rst_sys);
        $display("  @%0t ps: coarse=0x%h", $time, coarse_time);

        // ----------------------------------------------------------
        // 阶段2: 释放 rst_n, PLL 锁定中
        // ----------------------------------------------------------
        $display("");
        $display("--- 阶段2: 释放 rst_n, PLL 锁定中 ---");
        #10 rst_n = 1;
        $display("  @%0t ps: rst_n=%b → PLL开始锁定 (约1μs)", $time, rst_n);

        // ----------------------------------------------------------
        // 阶段3: 等待 PLL 锁定 + rst_sys 延迟释放
        // ----------------------------------------------------------
        // PLL 锁定需要 ~1000ns, 再给 500ns 余量
        #1500;
        $display("");
        $display("--- 阶段3: PLL锁定 + rst_sys延迟释放 ---");
        $display("  @%0t ps: pll_locked=%b, rst_sys=%b",
                 $time, uut.pll_locked, uut.rst_sys);
        $display("  @%0t ps: coarse=0x%h", $time, coarse_time);

        // 再等 500ps 确保 rst_sys 释放完成
        #500;
        $display("  @%0t ps: pll_locked=%b, rst_sys=%b (释放后)",
                 $time, uut.pll_locked, uut.rst_sys);
        $display("  @%0t ps: coarse=0x%h", $time, coarse_time);

        // ----------------------------------------------------------
        // 验证1: coarse 不是 x
        // ----------------------------------------------------------
        $display("");
        $display("============================================");
        if (^coarse_time === 1'bx) begin
            $display(" ❌ 失败: coarse 仍为 x, 复位修复无效!");
            $display("    coarse=0x%h (至少有一位是 x)", coarse_time);
        end else begin
            $display(" ✅ 通过: coarse 不再是 x!");
            $display("    coarse=0x%h (全部49bits有效)", coarse_time);
        end
        $display("============================================");

        // ----------------------------------------------------------
        // 阶段4: 计数验证 — 观察 coarse 是否递增
        // ----------------------------------------------------------
        $display("");
        $display("--- 阶段4: 计数验证 ---");
        #200;
        $display("  @%0t ps: coarse=0x%h (%0d)", $time, coarse_time, coarse_time);
        #200;
        $display("  @%0t ps: coarse=0x%h (%0d)", $time, coarse_time, coarse_time);
        #200;
        $display("  @%0t ps: coarse=0x%h (%0d)", $time, coarse_time, coarse_time);

        // ----------------------------------------------------------
        // 阶段5: 触发测量验证
        // ----------------------------------------------------------
        $display("");
        $display("--- 阶段5: 触发测量 ---");
        #100 start = 1; #20 start = 0;
        #50 trig_in = 1; #20 trig_in = 0;
        #500;

        if (coarse_time != 0) begin
            $display("  @%0t ps: ✅ 触发后 coarse=%0d (计数正常)", $time, coarse_time);
        end else begin
            $display("  @%0t ps: ⚠ coarse=%0d (触发后未改变)", $time, coarse_time);
        end

        // ----------------------------------------------------------
        // 最终总结
        // ----------------------------------------------------------
        $display("");
        $display("============================================");
        $display(" 复位验证完成");
        $display("============================================");
        $display("");
        $finish;
    end

    // ============================================================
    // 波形输出
    // ============================================================
    initial begin
        $dumpfile("tdc_reset_test.vcd");
        $dumpvars(0, tdc_reset_tb);
    end

endmodule
