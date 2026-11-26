// ============================================================
// adc_ad7980_tb.v — AD7980 16位SPI接口模块验证
// SDO 驱动时机: 在 SCK 下降沿更新下一bit (AD7980真实协议)
//
// 模块捕获时机: bit_timer==0 (SCK低) 时 capture: shift_reg<={sr[14:0],sdo}
//   第k次capture 的 bit 进入 shift_reg[k]。
//   因此 capture[k]==test_data[k] (即先喂 test_data[0])
// SCK下降沿(bit_timer 2→3)后SCK保持低, 直到下次capture → 在下降沿设好sdo
// ============================================================
`timescale 1ns/1ps

module adc_ad7980_tb;
    reg  clk = 0;
    reg  rst_n = 0;
    reg  conv_start = 0;
    wire [15:0] adc_data;
    wire adc_done;
    reg  sdo = 1'b0;
    wire cnv, sck;

    adc_ad7980 uut (
        .clk(clk), .rst_n(rst_n),
        .conv_start(conv_start),
        .adc_data(adc_data), .adc_done(adc_done),
        .cnv(cnv), .sck(sck), .sdo(sdo)
    );

    always #5 clk = ~clk;   // 100MHz

    // ------- SDO 驱动: SCK 下降沿更新下一位 -------
    reg [15:0] test_data = 16'hA5A5;
    integer bit_idx = 0;
    reg sck_d1 = 0;

    always @(posedge clk) begin
        sck_d1 <= sck;
        // SCK 下降沿: sck 当前=0, 前一拍=1
        if (sck == 1'b0 && sck_d1 == 1'b1) begin
            if (bit_idx < 16) begin
                bit_idx = bit_idx + 1;      // 先自增: 本次下降沿准备"下一个"bit
                if (bit_idx < 16)
                    sdo = test_data[bit_idx];
            end
        end
    end

    integer pass = 0, fail = 0;
    task chk;
        input [255:0] name;
        input cond;
        begin
            if (cond) begin pass = pass + 1; $display("  [PASS] %0s", name); end
            else begin fail = fail + 1; $display("  [FAIL] %0s", name); end
        end
    endtask

    initial begin
        $dumpfile("adc_ad7980_test.vcd");
        $dumpvars(0, adc_ad7980_tb);

        $display("=== AD7980 SPI 接口模块验证 ===");

        // A1: 复位
        rst_n = 0; #20; rst_n = 1; #10;
        chk("A1 复位后 adc_done=0", (adc_done == 0));
        chk("A1b 复位后 adc_data=0", (adc_data == 16'h0000));

        // 启动转换
        conv_start = 1;
        @(posedge clk); conv_start = 0;
        #10;

        // A2: 进入CONV, CNV拉高
        wait (cnv === 1'b1);
        chk("A2 CNV 拉高 (启动转换)", (cnv == 1));

        // 等待SCK开始翻转 (READ), driver自动喂数据
        bit_idx = 0;
        sdo = test_data[0];   // 预置首bit
        wait (sck === 1'b1);

        // 等待转换完成
        wait (adc_done === 1'b1);
        #5;

        $display("  读到 adc_data=0x%04x 期望 0x%04x", adc_data, test_data);
        chk("A3 读到完整16位数据", (adc_data === test_data));
        chk("A4 adc_done=1", (adc_done == 1));

        // A5: 回IDLE (adc_done 拉低; 窗口观察)
        begin : a5block
            integer k;
            reg saw_low;
            saw_low = 0;
            for (k = 0; k < 10; k = k + 1) begin
                @(posedge clk);
                if (adc_done == 0) saw_low = 1;
            end
            chk("A5 转完后 adc_done 回到0", (saw_low == 1));
        end
        chk("A5b CNV=0", (cnv == 0));

        $display("=== 结果: PASS %0d / FAIL %0d ===", pass, fail);
        if (fail == 0) $display("ALL PASS");
        else           $display("HAS FAIL");
        $finish;
    end
endmodule
