// ============================================================
// tdc_extra_tb.v — tdc_extra.v 模块验证 (data_fusion + spi_slave)
//   D1: data_fusion 锁存 coarse|fine 到 result, valid=1
//   S1: spi_slave CS下降沿锁存 data_in
//   S2: SCLK下降沿移出 data_latched 的 bit (MSB first)
//   S3: 读回全部65bit
// ============================================================
`timescale 1ns/1ps

module tdc_extra_tb;
    reg clk = 0;
    always #5 clk = ~clk;

    // ---- data_fusion ----
    reg rst_n = 0;
    reg [48:0] coarse = 49'h12345;
    reg [15:0] fine = 16'hABCD;
    wire fusion_valid, fusion_result_valid;
    wire [64:0] fusion_result;
    data_fusion u_fusion (.clk(clk), .rst_n(rst_n), .coarse(coarse), .fine(fine),
                          .valid(fusion_valid), .result(fusion_result));

    // ---- spi_slave ----
    reg cs = 1, sclk = 0, mosi = 0;
    wire miso;
    reg [64:0] data_in = 65'h1_2345_ABCDE;
    wire [7:0] data_out;
    spi_slave u_spi (.clk(clk), .cs(cs), .sclk(sclk), .mosi(mosi), .miso(miso),
                     .data_in(data_in), .data_out(data_out));

    integer pass = 0, fail = 0;
    integer spi_k;
    reg spi_got_all;
    task chk;
        input [255:0] name;
        input cond;
        begin
            if (cond) begin pass = pass + 1; $display("  [PASS] %0s", name); end
            else begin fail = fail + 1; $display("  [FAIL] %0s", name); end
        end
    endtask

    initial begin
        $dumpfile("tdc_extra_test.vcd");
        $dumpvars(0, tdc_extra_tb);

        $display("=== tdc_extra 模块验证 (data_fusion + spi_slave) ===");

        // ---- data_fusion ----
        rst_n = 0; #20; rst_n = 1;
        #25;
        chk("D1 result={coarse,fine}", (fusion_result == {coarse, fine}));
        chk("D2 valid=1", (fusion_valid == 1));

        // ---- spi_slave ----
        // CS 拉低 → 锁存 data_in
        cs = 1; sclk = 0;
        #40;
        cs = 0;       // CS下降沿, 锁存
        #40;
        // 连续 65 个 SCLK下降沿, 每个移出 data_latched 的一位 (MSB first)
        // bit_cnt: 0,1,...,64 → miso = data_latched[64-bit_cnt]
        spi_got_all = 1;
        for (spi_k = 0; spi_k < 65; spi_k = spi_k + 1) begin
            sclk = 1; #20;      // SCLK上升
            sclk = 0; #20;      // SCLK下降 → 移位输出
            // 该次下降沿后 miso 反映 data_latched[64-bit_cnt]
            #1;
            if (miso !== data_in[64-spi_k]) spi_got_all = 0;
        end
        chk("S1 移出全部65位正确", (spi_got_all == 1));
        cs = 1;
        #20;

        $display("=== 结果: PASS %0d / FAIL %0d ===", pass, fail);
        if (fail == 0) $display("ALL PASS");
        else           $display("HAS FAIL");
        $finish;
    end
endmodule
