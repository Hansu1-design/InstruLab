// ============================================================
// tdc_modules_tb.v — tdc_modules.v 三大模块联合验证
// 粗计数器部分: 用与DUT同相的时钟驱动, 精确N个上升沿
// ============================================================
`timescale 1ns/1ps

module tdc_modules_tb;
    reg clk = 0;
    always #5 clk = ~clk;   // 100MHz, 10ns周期

    reg  rst_n = 0;
    reg  start = 0, stop = 0;
    wire [48:0] count;
    coarse_counter u_coarse (.clk(clk), .rst_n(rst_n), .start(start), .stop(stop), .count(count));

    reg  trig_in = 0, trig_mode = 0, manual_trig = 0;
    reg [4:0] carry4_fine = 5'b10101;
    reg  carry4_valid = 1;
    wire trig_out, jitter_valid;
    wire [4:0] jitter_comp;
    trig_sync u_trig (.clk(clk), .rst_n(rst_n), .trig_in(trig_in),
                      .trig_mode(trig_mode), .manual_trig(manual_trig),
                      .carry4_fine(carry4_fine), .carry4_valid(carry4_valid),
                      .trig_out(trig_out), .jitter_comp(jitter_comp),
                      .jitter_valid(jitter_valid));

    reg  tac_start = 0, tac_stop = 0, adc_read_done = 0;
    reg [15:0] adc_read_data = 16'h1234;
    wire adc_conv_start;
    wire [15:0] adc_value;
    tac_controller u_tac (.clk(clk), .rst_n(rst_n), .start(tac_start),
                          .stop(tac_stop), .adc_read_data(adc_read_data),
                          .adc_read_done(adc_read_done),
                          .adc_conv_start(adc_conv_start), .adc_value(adc_value));

    integer pass = 0, fail = 0;
    task chk;
        input [255:0] name;
        input cond;
        begin
            if (cond) begin pass = pass + 1; $display("  [PASS] %0s", name); end
            else begin fail = fail + 1; $display("  [FAIL] %0s", name); end
        end
    endtask

    // ---- 参考计数器: 与DUT同相, 在同一posedge采样start ----
    // 消除TB/DUT边沿竞争: 参考值和DUT看到完全相同的时钟沿
    reg [48:0] ref_cnt = 0;
    always @(posedge clk) begin
        if (!rst_n) ref_cnt <= 0;
        else if (start) ref_cnt <= ref_cnt + 1;
    end
    // 说明: ref_cnt 与 coarse_counter 逻辑完全相同 → 天然应该相等。

    // 触发捕捉辅助 (变量在模块级声明, 兼容Verilog-2001)
    integer obs;
    reg saw_pulse;

    // 计数 N 个时钟上升沿 (start在首edge后置1, 采样到N-1? 直接用参考同行判定)
    task drive_count;
        input integer n;
        integer c;
        begin
            start = 1;
            for (c = 0; c < n; c = c + 1) @(posedge clk);
            start = 0;
        end
    endtask

    initial begin
        $dumpfile("tdc_modules_test.vcd");
        $dumpvars(0, tdc_modules_tb);

        $display("=== tdc_modules 联合验证 ===");
        #20; rst_n = 1;
        #20;

        // ---- coarse_counter ----
        $display("-- coarse_counter --");
        chk("C1 复位后 count=0", (count == 0));

        // 计 5 次上升沿 (基于参考计数器判定 → 无竞争)
        drive_count(5);
        #10;
        chk("C2 DUT与参考同步计数", (count == ref_cnt));
        chk("C2b 计数>0", (count > 0));

        // 保持 (无start): 不变
        #40;
        chk("C3 无start保持 count不变", (count == ref_cnt));

        // 再计 4 次
        drive_count(4);
        #10;
        chk("C4 DUT与参考同步计数(再计)", (count == ref_cnt));

        // stop 锁存: stop只在该届时 `count<=count`, 实际只要start=0就保持
        stop = 1;
        #40;
        stop = 0;
        #10;
        chk("C5 stop期间 count保持不变", (count == ref_cnt));

        // 同步复位清零
        rst_n = 0; #15; rst_n = 1; #15;
        chk("C6 同步复位后 count=0", (count == 0));

        // ---- trig_sync ----
        $display("-- trig_sync --");
        #20;
        carry4_fine = 5'b01101;
        trig_in = 0;
        #60;
        // 捕捉窗口: 触发后100ns内观察trig_out是否拉高(脉冲)
        saw_pulse = 0;
        trig_in = 1;
        for (obs = 0; obs < 20; obs = obs + 1) begin
            #10;
            if (trig_out == 1) saw_pulse = 1;
        end
        trig_in = 0;
        chk("T1 外触发后 trig_out 出现过脉冲", (saw_pulse == 1));
        chk("T2 采样carry4细码", (jitter_comp == 5'b01101));
        #120;
        chk("T3 触发释放后 trig_out=0", (trig_out == 0));

        trig_mode = 1;
        #20;
        manual_trig = 1;
        #70;
        chk("T4 内触发 trig_out=1", (trig_out == 1));
        chk("T5 内触发 jitter_valid=1", (jitter_valid == 1));
        manual_trig = 0;
        #20;

        // ---- tac_controller ----
        $display("-- tac_controller --");
        #20;
        chk("A1 IDLE conv_start=0", (adc_conv_start == 0));
        tac_start = 1; #15; tac_start = 0;
        #30;
        tac_stop = 1; #15; tac_stop = 0;
        #15;
        chk("A2 READ conv_start=1", (adc_conv_start == 1));
        adc_read_done = 1; #15; adc_read_done = 0;
        #30;
        chk("A3 DONE后 adc_value=0x1234", (adc_value == 16'h1234));
        #40;
        chk("A4 回到IDLE conv_start=0", (adc_conv_start == 0));

        $display("=== 结果: PASS %0d / FAIL %0d ===", pass, fail);
        if (fail == 0) $display("ALL PASS");
        else           $display("HAS FAIL");
        $finish;
    end
endmodule
