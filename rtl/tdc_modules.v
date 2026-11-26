// ============================================================
// 粗计数器 — 49bit @ 400MHz (赵雪鹏TDC硕士论文)
// 量程: 2^49/400MHz ≈ 391小时
// ============================================================
module coarse_counter (
    input  wire        clk,     // 400MHz
    input  wire        rst_n,
    input  wire        start,
    input  wire        stop,
    output reg  [48:0] count
);
    // 同步复位: 在 rst_n 为低时复位 (对应 rst_sys 电平)
    // 修复 v2.1: 原 async reset (negedge rst_n) 依赖 rst_n 负跳变,
    //   但 rst_sys 从 0→1 仅正跳变, 导致复位从未触发, count 始终为 x。
    //   改为同步复位后, 在 clk 上升沿采样 rst_n, 只要 rst_n=0 就复位。
    always @(posedge clk) begin
        if (!rst_n)
            count <= 0;
        else if (start)
            count <= count + 1;
        else if (stop)
            count <= count;  // 锁存
    end
endmodule

// ============================================================
// 触发同步与抖动消除 (升级版)
// 来源: 梁东飞、苏淑靖《消除触发抖动》(2023)
//
// 功能:
//   - 3级触发器同步 (优于原来的2级)
//   - 实时抖动测量 (利用CARRY4进位链)
//   - 数字补偿输出
//   - 外触发/内触发模式选择
// ============================================================
module trig_sync (
    input  wire        clk,           // 系统时钟
    input  wire        rst_n,         // 复位(低有效)
    input  wire        trig_in,       // 外触发输入 (被测信号)
    input  wire        trig_mode,     // 触发模式: 0=外触发, 1=内触发
    input  wire        manual_trig,   // 内触发(手动/软件触发)
    input  wire [4:0]  carry4_fine,   // 来自CARRY4 TDC的细码 (抖动测量用)
    input  wire        carry4_valid,  // CARRY4有效信号
    output reg         trig_out,      // 同步后的触发输出
    output reg  [4:0]  jitter_comp,   // 抖动补偿值 (数字补偿)
    output reg         jitter_valid   // 抖动补偿有效
);

    // ============================================================
    // 3级触发器同步 (metastability hardener)
    // 比2级有更好的MTBF
    // ============================================================
    reg [2:0] sync_chain;  // 3级同步链
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sync_chain <= 0;
        end else begin
            sync_chain <= {sync_chain[1:0], trig_in};
        end
    end

    // ============================================================
    // 触发模式选择: 外触发 / 内触发
    // ============================================================
    reg ext_trig_d1;  // 外触发边沿检测
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            ext_trig_d1 <= 0;
        end else begin
            ext_trig_d1 <= sync_chain[2];  // 同步后的外触发
        end
    end
    
    wire ext_trig_edge = sync_chain[2] & ~ext_trig_d1;  // 外触发上升沿
    wire int_trig_edge = manual_trig;                     // 内触发边沿
    
    // 选择触发源
    reg trig_source;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            trig_source <= 0;
        end else begin
            if (trig_mode)
                trig_source <= int_trig_edge;
            else
                trig_source <= ext_trig_edge;
        end
    end

    // ============================================================
    // 触发输出 (整形脉冲)
    // ============================================================
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            trig_out <= 0;
        end else begin
            trig_out <= trig_source;
        end
    end

    // ============================================================
    // 实时抖动测量与数字补偿
    //
    // 原理 (梁东飞论文):
    //   外触发信号与FPGA时钟异步, 触发边沿可能落在
    //   时钟周期的任意位置 → 产生±1时钟周期的抖动
    //   
    //   利用CARRY4 TDC实时测量触发边沿在时钟周期内的
    //   相位位置, 作为抖动补偿值输出
    //   
    //   补偿方式: jitter_comp = 5-bit细码
    //   后续数据融合时: 实际时间 = 粗计数 + jitter_comp × 66ps
    // ============================================================
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            jitter_comp  <= 0;
            jitter_valid <= 0;
        end else begin
            // 当外触发到达时, 锁存当前的CARRY4细码作为抖动
            if (ext_trig_edge && !trig_mode) begin
                jitter_comp  <= carry4_fine;
                jitter_valid <= carry4_valid;
            end else if (int_trig_edge && trig_mode) begin
                // 内触发无抖动
                jitter_comp  <= 0;
                jitter_valid <= 1;
            end else begin
                jitter_valid <= 0;
            end
        end
    end

endmodule

// ============================================================
// TAC控制器 — 时间幅度转换 (分辨率1.5ps~5ps)
// 来源: 赵雪鹏硕士论文《高分辨率时间间隔测量》(2022)
//
// 功能升级:
//   - 真实的AD7980 SPI读取 (原为模拟计数器)
//   - TAC充放电时序控制 (start/stop)
//   - 与ADC接口对接
// ============================================================
module tac_controller (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        start,          // TAC启动 (触发信号)
    input  wire        stop,           // TAC停止
    input  wire [15:0] adc_read_data,  // 来自AD7980的读数
    input  wire        adc_read_done,  // AD7980转换完成
    output reg         adc_conv_start, // 启动ADC转换
    output reg  [15:0] adc_value       // 细测量结果
);

    // TAC状态机
    localparam TAC_IDLE   = 2'b00;
    localparam TAC_CHARGE = 2'b01;   // 恒流源充电 (t1/t2期间)
    localparam TAC_READ   = 2'b10;   // 等待ADC读取
    localparam TAC_DONE   = 2'b11;   // 完成

    reg [1:0] state, next_state;

    always @(*) begin
        next_state = state;
        case (state)
            TAC_IDLE: begin
                if (start)
                    next_state = TAC_CHARGE;
            end
            TAC_CHARGE: begin
                if (stop)
                    next_state = TAC_READ;
            end
            TAC_READ: begin
                if (adc_read_done)
                    next_state = TAC_DONE;
            end
            TAC_DONE: begin
                next_state = TAC_IDLE;
            end
        endcase
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state          <= TAC_IDLE;
            adc_conv_start <= 0;
            adc_value      <= 0;
        end else begin
            state <= next_state;
            case (state)
                TAC_IDLE: begin
                    adc_conv_start <= 0;
                end
                TAC_CHARGE: begin
                    // TAC电容充电期间
                end
                TAC_READ: begin
                    // 启动ADC读取
                    adc_conv_start <= 1;
                    // 锁存ADC结果
                    if (adc_read_done)
                        adc_value <= adc_read_data;
                end
                TAC_DONE: begin
                    adc_conv_start <= 0;
                end
            endcase
        end
    end

endmodule
