// ============================================================
// AD7980 16位ADC SPI接口模块 (v3 — 简化捕获逻辑)
// 来源: 赵雪鹏硕士论文《高分辨率时间间隔测量技术》(2022)
//       赵雪鹏、苏淑靖《一种高精度时间间隔测量电路的设计》(2022)
//
// AD7980特性:
//   - 16bit 逐次逼近SAR ADC
//   - 最高采样率: 1MSPS (1MHz CNV)
//   - 转换时间: 710ns (典型)
//   - SPI接口: 3线 (CNV, SCK, SDO)
//   - 支持菊花链连接
//   - 电源: 2.5V单电源
//
// SCK协议:
//   SCK每4个clk周期完成一个位周期 (40ns → 25MHz)
//   周期0: SCK=1 (上升沿, ADC更新SDO)
//   周期1: SCK=1 (等待数据稳定)
//   周期2: SCK=0 (下降沿)
//   周期3: SCK=0, 捕获sdo_s2 (延迟同步后的数据)
// ============================================================

module adc_ad7980 (
    input  wire        clk,           // 系统时钟 (100MHz)
    input  wire        rst_n,         // 复位(低有效)
    
    // 内部接口
    input  wire        conv_start,    // 转换触发 (上升沿有效)
    output reg  [15:0] adc_data,      // 16位ADC读数
    output reg         adc_done,      // 转换完成 (2周期宽)
    
    // AD7980 SPI物理接口
    output reg         cnv,           // 转换启动 (CNV引脚)
    output reg         sck,           // SPI时钟 (SCK引脚)
    input  wire        sdo            // 串行数据 (SDO引脚)
);

    // ============================================================
    // 状态机
    // ============================================================
    localparam IDLE       = 3'b000;
    localparam CONV       = 3'b001;   // CNV高, 等待ADC转换(720ns)
    localparam READ_BITS  = 3'b011;   // 读取16位 (4clk/位 = 640ns)
    localparam DONE1      = 3'b100;   // done第1周期
    localparam DONE2      = 3'b101;   // done第2周期

    reg [2:0] state, next_state;
    
    reg [7:0] timer;       // CONV状态计数器
    reg [1:0] bit_timer;   // READ_BITS逐位计数器 (0~3, 4clk/位)
    reg [4:0] bit_cnt;     // 位计数器 (0~15)
    
    // SDO数据锁存 (2级触发器同步, 防亚稳态)
    reg sdo_s1, sdo_s2;
    reg [15:0] shift_reg;

    // ============================================================
    // 状态机: 下一状态逻辑 (组合)
    // ============================================================
    always @(*) begin
        next_state = state;
        case (state)
            IDLE: begin
                if (conv_start)
                    next_state = CONV;
            end
            CONV: begin
                if (timer >= 71)        // 72周期 = 720ns > 710ns
                    next_state = READ_BITS;
            end
            READ_BITS: begin
                if (bit_cnt >= 16 && bit_timer >= 2)
                    next_state = DONE1;
            end
            DONE1:    next_state = DONE2;
            DONE2:    next_state = IDLE;
        endcase
    end

    // ============================================================
    // 状态机: 时序逻辑
    // ============================================================
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state     <= IDLE;
            timer     <= 0;
            bit_timer <= 0;
            bit_cnt   <= 0;
            cnv       <= 0;
            sck       <= 0;
            shift_reg <= 0;
            adc_data  <= 0;
            adc_done  <= 0;
            sdo_s1    <= 0;
            sdo_s2    <= 0;
        end else begin
            state <= next_state;
            
            // SDO同步打拍 (每个clk更新)
            sdo_s1 <= sdo;
            sdo_s2 <= sdo_s1;
            
            case (state)
                IDLE: begin
                    cnv       <= 0;
                    sck       <= 0;
                    timer     <= 0;
                    bit_timer <= 0;
                    bit_cnt   <= 0;
                    adc_done  <= 0;
                end
                
                CONV: begin
                    cnv   <= 1;              // CNV高 → 启动ADC
                    sck   <= 0;
                    timer <= timer + 1;
                end
                
                READ_BITS: begin
                    cnv <= 0;
                    // 每个位周期: bit_timer=0捕获, SCK高; =1保持; =2SCK低; =3保持
                    // 关键: 在SCK上升沿前捕获(此时sdo稳定)
                    if (bit_timer == 0) begin
                        // 捕获当前sdo (此时SCK=0, sdo稳定)
                        if (bit_cnt < 16) begin
                            shift_reg <= {shift_reg[14:0], sdo};
                            bit_cnt   <= bit_cnt + 1;
                        end
                        sck       <= 1;       // SCK上升沿: ADC更新下一位
                        bit_timer <= 1;
                    end else if (bit_timer == 1) begin
                        bit_timer <= 2;       // SCK保持高
                    end else if (bit_timer == 2) begin
                        sck       <= 0;       // SCK下降沿
                        bit_timer <= 3;
                    end else begin
                        bit_timer <= 0;       // SCK保持低, 准备下一次捕获
                    end
                end
                
                DONE1: begin
                    cnv      <= 0;
                    sck      <= 0;
                    adc_data <= shift_reg;   // 锁存16位结果
                    adc_done <= 1;           // 完成信号
                end
                
                DONE2: begin
                    adc_done <= 1;           // 保持第2周期
                end
            endcase
        end
    end

endmodule
