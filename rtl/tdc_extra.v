// 数据融合 + SPI接口
module data_fusion (
    input wire clk, rst_n,
    input wire [48:0] coarse,
    input wire [15:0] fine,
    output reg valid,
    output reg [64:0] result
);
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin valid <= 0; end
        else begin
            result <= {coarse, fine};
            valid <= 1;
        end
    end
endmodule

module spi_slave (
    input wire clk, cs, sclk, mosi,
    output reg miso,
    input wire [64:0] data_in,
    output reg [7:0] data_out
);
    reg [6:0] bit_cnt;          // 7位, 支持0-65计数
    reg [64:0] shift;
    reg sclk_d1, sclk_d2;       // SPI时钟同步打拍
    reg cs_s1, cs_s2;           // CS同步打拍(无异步复位)
    reg [64:0] data_latched;    // CS锁存数据
    
    // CS同步 + 下降沿检测 (独立进程, 无异步复位)
    always @(posedge clk) begin
        cs_s1 <= cs;
        cs_s2 <= cs_s1;
        if (cs_s1 == 1'b0 && cs_s2 == 1'b1)
            data_latched <= data_in;
    end
    
    // SPI数据移位 (posedge cs复位bit_cnt)
    always @(posedge clk or posedge cs) begin
        if (cs) begin
            bit_cnt <= 0;
            sclk_d1 <= 0;
            sclk_d2 <= 0;
        end else begin
            sclk_d1 <= sclk;
            sclk_d2 <= sclk_d1;
            // sclk下降沿检测
            if (sclk_d1 == 1'b0 && sclk_d2 == 1'b1) begin
                if (bit_cnt < 65) begin
                    miso <= data_latched[64-bit_cnt];
                    bit_cnt <= bit_cnt + 1;
                end
            end
        end
    end
endmodule
