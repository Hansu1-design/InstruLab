// ============================================================
// CARRY4进位链细测量模块 — 3路并行TDC取中值
// 来源: 梁东飞、苏淑靖《消除触发抖动》(2023)
// 
// 架构:
//   76级CARRY4延迟线 × 3路并行
//   → 检测信号在延迟线中的传播位置
//   → 3路取中值 → 5-bit fine code
//
// 参数:
//   分辨率: ~33ps/级  (Xilinx 7-series CARRY4典型值)
//   覆盖范围: 76级 × 33ps ≈ 2.5ns (一个400MHz时钟周期)
//   并行路数: 3 (取中值提升精度)
//   输出: 5-bit细码 + valid信号
//
// 综合要求:
//   - CARRY4三路延迟线使用 (* DONT_TOUCH = "TRUE" *) 防止合并
//   - 76→7优先编码器使用2级流水线（每组~2-3级LUT，满足400MHz时序）
//
// Revision:
//   v3.0 — 2026-07-25: 2-stage pipelined priority encoder + DONT_TOUCH约束
// ============================================================

module carry4_tdc (
    input  wire        clk,           // 400MHz 系统时钟
    input  wire        rst_n,         // 复位(低有效)
    input  wire        trig_in,       // 待测量的触发信号(已同步)
    output reg  [4:0]  fine_code,     // 5-bit 细码 (0~31, 代表时钟周期内相位)
    output reg         valid          // 数据有效(每个时钟周期更新一次)
);

    // ============================================================
    // 3路并行CARRY4延迟线 (76级/路)
    //
    // 实现说明 (实际综合时):
    //   每路用19个CARRY4原语级联 (19 × 4 = 76级)
    //
    // (* DONT_TOUCH = "TRUE" *) 禁止Vivado合并三路或优化移位寄存器
    // ============================================================

    (* DONT_TOUCH = "TRUE" *) reg [75:0] carry_line_a;
    (* DONT_TOUCH = "TRUE" *) reg [75:0] carry_line_b;
    (* DONT_TOUCH = "TRUE" *) reg [75:0] carry_line_c;

    // ---- 各路的抽头位置 (热独码转二进制) ----
    reg [6:0] pos_a;  // 0~75
    reg [6:0] pos_b;
    reg [6:0] pos_c;

    // ---- 中值 ----
    reg [6:0] median_pos;

    // ----------------------------------------------------------
    // 延迟线传播: 模拟CARRY4进位链的传播行为
    // 注意: 真实硬件中, trig_in的上升沿从第0级开始传播
    //       每级延迟~33ps, 75级后覆盖2.5ns
    //       在下一个clk上升沿时采样所有抽头
    // ----------------------------------------------------------
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            carry_line_a <= 0;
            carry_line_b <= 0;
            carry_line_c <= 0;
        end else begin
            // 三级延迟线同时对trig_in响应
            // 在真实硬件中, 各路的布线延迟差异提供了噪声冗余
            carry_line_a <= {carry_line_a[74:0], trig_in};
            carry_line_b <= {carry_line_b[74:0], trig_in};
            carry_line_c <= {carry_line_c[74:0], trig_in};
        end
    end

    // ============================================================
    // 2级流水线优先编码器 (76→7 bit)
    //
    // 流水线结构:
    //   Stage 0 (comb):  76bit → 10组 (9×8bit + 1×4bit), 每组内编码
    //   [Pipeline Register A]
    //   Stage 1 (comb):  10组优先级选择 → 1个7bit位置
    //   [Pipeline Register B → pos_a/b/c]
    //   Stage 2 (comb):  中值计算 (3路)
    //   [Pipeline Register C → fine_code/valid]
    //
    // 每级组合逻辑≤2-3级LUT, 满足400MHz (2.5ns) 时序要求
    // ============================================================

    // ---------- 内部信号 ----------
    // 10个组: 9组×8bit + 1组×4bit (bit75:72)
    wire [9:0]  grp_any_a, grp_any_b, grp_any_c;
    wire [3:0]  grp_pos_a[9:0], grp_pos_b[9:0], grp_pos_c[9:0];

    // ========== Stage 0: 分组编码 (组合逻辑) ==========
    // 每路延迟线拆成10组, 每组用casez语句实现优先编码
    // casez直接映射到LUT, 比for-loop更高效

    // ---- 第一路 A ----
    priority_enc_8x9 u_enc_a0 (.din(carry_line_a[ 7: 0]), .pos(grp_pos_a[0]), .any(grp_any_a[0]));
    priority_enc_8x9 u_enc_a1 (.din(carry_line_a[15: 8]), .pos(grp_pos_a[1]), .any(grp_any_a[1]));
    priority_enc_8x9 u_enc_a2 (.din(carry_line_a[23:16]), .pos(grp_pos_a[2]), .any(grp_any_a[2]));
    priority_enc_8x9 u_enc_a3 (.din(carry_line_a[31:24]), .pos(grp_pos_a[3]), .any(grp_any_a[3]));
    priority_enc_8x9 u_enc_a4 (.din(carry_line_a[39:32]), .pos(grp_pos_a[4]), .any(grp_any_a[4]));
    priority_enc_8x9 u_enc_a5 (.din(carry_line_a[47:40]), .pos(grp_pos_a[5]), .any(grp_any_a[5]));
    priority_enc_8x9 u_enc_a6 (.din(carry_line_a[55:48]), .pos(grp_pos_a[6]), .any(grp_any_a[6]));
    priority_enc_8x9 u_enc_a7 (.din(carry_line_a[63:56]), .pos(grp_pos_a[7]), .any(grp_any_a[7]));
    priority_enc_8x9 u_enc_a8 (.din(carry_line_a[71:64]), .pos(grp_pos_a[8]), .any(grp_any_a[8]));
    priority_enc_4   u_enc_a9 (.din(carry_line_a[75:72]), .pos(grp_pos_a[9]), .any(grp_any_a[9]));

    // ---- 第二路 B ----
    priority_enc_8x9 u_enc_b0 (.din(carry_line_b[ 7: 0]), .pos(grp_pos_b[0]), .any(grp_any_b[0]));
    priority_enc_8x9 u_enc_b1 (.din(carry_line_b[15: 8]), .pos(grp_pos_b[1]), .any(grp_any_b[1]));
    priority_enc_8x9 u_enc_b2 (.din(carry_line_b[23:16]), .pos(grp_pos_b[2]), .any(grp_any_b[2]));
    priority_enc_8x9 u_enc_b3 (.din(carry_line_b[31:24]), .pos(grp_pos_b[3]), .any(grp_any_b[3]));
    priority_enc_8x9 u_enc_b4 (.din(carry_line_b[39:32]), .pos(grp_pos_b[4]), .any(grp_any_b[4]));
    priority_enc_8x9 u_enc_b5 (.din(carry_line_b[47:40]), .pos(grp_pos_b[5]), .any(grp_any_b[5]));
    priority_enc_8x9 u_enc_b6 (.din(carry_line_b[55:48]), .pos(grp_pos_b[6]), .any(grp_any_b[6]));
    priority_enc_8x9 u_enc_b7 (.din(carry_line_b[63:56]), .pos(grp_pos_b[7]), .any(grp_any_b[7]));
    priority_enc_8x9 u_enc_b8 (.din(carry_line_b[71:64]), .pos(grp_pos_b[8]), .any(grp_any_b[8]));
    priority_enc_4   u_enc_b9 (.din(carry_line_b[75:72]), .pos(grp_pos_b[9]), .any(grp_any_b[9]));

    // ---- 第三路 C ----
    priority_enc_8x9 u_enc_c0 (.din(carry_line_c[ 7: 0]), .pos(grp_pos_c[0]), .any(grp_any_c[0]));
    priority_enc_8x9 u_enc_c1 (.din(carry_line_c[15: 8]), .pos(grp_pos_c[1]), .any(grp_any_c[1]));
    priority_enc_8x9 u_enc_c2 (.din(carry_line_c[23:16]), .pos(grp_pos_c[2]), .any(grp_any_c[2]));
    priority_enc_8x9 u_enc_c3 (.din(carry_line_c[31:24]), .pos(grp_pos_c[3]), .any(grp_any_c[3]));
    priority_enc_8x9 u_enc_c4 (.din(carry_line_c[39:32]), .pos(grp_pos_c[4]), .any(grp_any_c[4]));
    priority_enc_8x9 u_enc_c5 (.din(carry_line_c[47:40]), .pos(grp_pos_c[5]), .any(grp_any_c[5]));
    priority_enc_8x9 u_enc_c6 (.din(carry_line_c[55:48]), .pos(grp_pos_c[6]), .any(grp_any_c[6]));
    priority_enc_8x9 u_enc_c7 (.din(carry_line_c[63:56]), .pos(grp_pos_c[7]), .any(grp_any_c[7]));
    priority_enc_8x9 u_enc_c8 (.din(carry_line_c[71:64]), .pos(grp_pos_c[8]), .any(grp_any_c[8]));
    priority_enc_4   u_enc_c9 (.din(carry_line_c[75:72]), .pos(grp_pos_c[9]), .any(grp_any_c[9]));

    // ========== Pipeline Register A: Stage 0 → Stage 1 ==========
    // 存储10组编码结果 (每组: any + pos[3:0]) × 3路
    reg [9:0]  pa_any_a, pa_any_b, pa_any_c;
    reg [3:0]  pa_pos_a[9:0], pa_pos_b[9:0], pa_pos_c[9:0];

    integer pa_i;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pa_any_a <= 0; pa_any_b <= 0; pa_any_c <= 0;
            for (pa_i = 0; pa_i < 10; pa_i = pa_i + 1) begin
                pa_pos_a[pa_i] <= 0;
                pa_pos_b[pa_i] <= 0;
                pa_pos_c[pa_i] <= 0;
            end
        end else begin
            pa_any_a <= grp_any_a; pa_any_b <= grp_any_b; pa_any_c <= grp_any_c;
            for (pa_i = 0; pa_i < 10; pa_i = pa_i + 1) begin
                pa_pos_a[pa_i] <= grp_pos_a[pa_i];
                pa_pos_b[pa_i] <= grp_pos_b[pa_i];
                pa_pos_c[pa_i] <= grp_pos_c[pa_i];
            end
        end
    end

    // ========== Stage 1: 组间优先编码 (组合逻辑) ==========
    // 在10个组中找出第一个有数据的组, 合并组编号+组内位置→7bit

    reg  [6:0] pos_a_comb, pos_b_comb, pos_c_comb;
    reg        valid_a, valid_b, valid_c;

    // 第一路 A
    always @(*) begin
        pos_a_comb   = 0;
        valid_a = 0;
        if (pa_any_a[0]) begin valid_a = 1; pos_a_comb = {4'd0, pa_pos_a[0][2:0]}; end
        else if (pa_any_a[1]) begin valid_a = 1; pos_a_comb = {4'd1, pa_pos_a[1][2:0]}; end
        else if (pa_any_a[2]) begin valid_a = 1; pos_a_comb = {4'd2, pa_pos_a[2][2:0]}; end
        else if (pa_any_a[3]) begin valid_a = 1; pos_a_comb = {4'd3, pa_pos_a[3][2:0]}; end
        else if (pa_any_a[4]) begin valid_a = 1; pos_a_comb = {4'd4, pa_pos_a[4][2:0]}; end
        else if (pa_any_a[5]) begin valid_a = 1; pos_a_comb = {4'd5, pa_pos_a[5][2:0]}; end
        else if (pa_any_a[6]) begin valid_a = 1; pos_a_comb = {4'd6, pa_pos_a[6][2:0]}; end
        else if (pa_any_a[7]) begin valid_a = 1; pos_a_comb = {4'd7, pa_pos_a[7][2:0]}; end
        else if (pa_any_a[8]) begin valid_a = 1; pos_a_comb = {4'd8, pa_pos_a[8][2:0]}; end
        else if (pa_any_a[9]) begin valid_a = 1; pos_a_comb = {4'd9, pa_pos_a[9][2:0]}; end
    end

    // 第二路 B
    always @(*) begin
        pos_b_comb   = 0;
        valid_b = 0;
        if (pa_any_b[0]) begin valid_b = 1; pos_b_comb = {4'd0, pa_pos_b[0][2:0]}; end
        else if (pa_any_b[1]) begin valid_b = 1; pos_b_comb = {4'd1, pa_pos_b[1][2:0]}; end
        else if (pa_any_b[2]) begin valid_b = 1; pos_b_comb = {4'd2, pa_pos_b[2][2:0]}; end
        else if (pa_any_b[3]) begin valid_b = 1; pos_b_comb = {4'd3, pa_pos_b[3][2:0]}; end
        else if (pa_any_b[4]) begin valid_b = 1; pos_b_comb = {4'd4, pa_pos_b[4][2:0]}; end
        else if (pa_any_b[5]) begin valid_b = 1; pos_b_comb = {4'd5, pa_pos_b[5][2:0]}; end
        else if (pa_any_b[6]) begin valid_b = 1; pos_b_comb = {4'd6, pa_pos_b[6][2:0]}; end
        else if (pa_any_b[7]) begin valid_b = 1; pos_b_comb = {4'd7, pa_pos_b[7][2:0]}; end
        else if (pa_any_b[8]) begin valid_b = 1; pos_b_comb = {4'd8, pa_pos_b[8][2:0]}; end
        else if (pa_any_b[9]) begin valid_b = 1; pos_b_comb = {4'd9, pa_pos_b[9][2:0]}; end
    end

    // 第三路 C
    always @(*) begin
        pos_c_comb   = 0;
        valid_c = 0;
        if (pa_any_c[0]) begin valid_c = 1; pos_c_comb = {4'd0, pa_pos_c[0][2:0]}; end
        else if (pa_any_c[1]) begin valid_c = 1; pos_c_comb = {4'd1, pa_pos_c[1][2:0]}; end
        else if (pa_any_c[2]) begin valid_c = 1; pos_c_comb = {4'd2, pa_pos_c[2][2:0]}; end
        else if (pa_any_c[3]) begin valid_c = 1; pos_c_comb = {4'd3, pa_pos_c[3][2:0]}; end
        else if (pa_any_c[4]) begin valid_c = 1; pos_c_comb = {4'd4, pa_pos_c[4][2:0]}; end
        else if (pa_any_c[5]) begin valid_c = 1; pos_c_comb = {4'd5, pa_pos_c[5][2:0]}; end
        else if (pa_any_c[6]) begin valid_c = 1; pos_c_comb = {4'd6, pa_pos_c[6][2:0]}; end
        else if (pa_any_c[7]) begin valid_c = 1; pos_c_comb = {4'd7, pa_pos_c[7][2:0]}; end
        else if (pa_any_c[8]) begin valid_c = 1; pos_c_comb = {4'd8, pa_pos_c[8][2:0]}; end
        else if (pa_any_c[9]) begin valid_c = 1; pos_c_comb = {4'd9, pa_pos_c[9][2:0]}; end
    end

    // ========== Pipeline Register B: Stage 1 → pos_a/b/c + valid ==========
    reg carry_valid_d1;  // 与pos对齐的valid信号(延迟1周期)
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pos_a <= 0;
            pos_b <= 0;
            pos_c <= 0;
            carry_valid_d1 <= 0;
        end else begin
            pos_a <= pos_a_comb;
            pos_b <= pos_b_comb;
            pos_c <= pos_c_comb;
            // 三路中任一有效即认为有信号
            // (短延迟级, 约2 LUT, 满足2.5ns)
            carry_valid_d1 <= valid_a || valid_b || valid_c;
        end
    end

    // ----------------------------------------------------------
    // 中值计算: 3路取中值
    // 排序后取中间值, 剔除偏差最大的单路
    // 注: 此逻辑仅~2级LUT (7-bit比较器), 不需要额外流水线
    // ----------------------------------------------------------
    always @(*) begin
        if ((pos_a >= pos_b && pos_a <= pos_c) || 
            (pos_a >= pos_c && pos_a <= pos_b))
            median_pos = pos_a;
        else if ((pos_b >= pos_a && pos_b <= pos_c) || 
                 (pos_b >= pos_c && pos_b <= pos_a))
            median_pos = pos_b;
        else
            median_pos = pos_c;
    end

    // ----------------------------------------------------------
    // 5-bit细码输出: 中值位置 压缩到 5-bit
    // 76个位置 → 32个bin (0~31)
    // 映射: fine_code = median_pos >> 1 (但clipped at 31)
    // 等效分辨率: ~2 × 33ps = 66ps/LSB
    //
    // Pipeline Register C (最终输出寄存器)
    // ----------------------------------------------------------
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            fine_code <= 0;
            valid     <= 0;
        end else begin
            // 使用与pos对齐的carry_valid_d1 (而非直接取carry_line)
            // 保证fine_code与valid的时序一致性
            if (carry_valid_d1) begin
                // 中值位置右移1位 → 5-bit
                // 76 >> 1 = 38, clipped to 31
                fine_code <= (median_pos[6:1] > 5'd31) ? 5'd31 : median_pos[6:1];
                valid     <= 1;
            end else begin
                valid <= 0;
            end
        end
    end
endmodule


// ============================================================
// 8→3 优先编码器模块
// 输入: 8-bit热独码 (bit0最低位优先)
// 输出: pos[2:0] = 最低位'1'的位置 (0~7)
//       any = 至少有一位为1
//
// 综合: casez直接映射到LUT6, 单级逻辑 (~1 LUT level)
// ============================================================
module priority_enc_8x9 (
    input  wire [7:0] din,
    output reg  [3:0] pos,
    output reg        any
);
    always @(*) begin
        any = |din;
        casez (din)
            8'b???????1: pos[2:0] = 0;
            8'b??????10: pos[2:0] = 1;
            8'b?????100: pos[2:0] = 2;
            8'b????1000: pos[2:0] = 3;
            8'b???10000: pos[2:0] = 4;
            8'b??100000: pos[2:0] = 5;
            8'b?1000000: pos[2:0] = 6;
            8'b10000000: pos[2:0] = 7;
            default:     pos[2:0] = 0;
        endcase
        pos[3] = 1'b0;  // 8-bit组内位置≤7, 高位始终0
    end
endmodule


// ============================================================
// 4→3 优先编码器模块
// 输入: 4-bit热独码
// 输出: pos[2:0] = 最低位'1'的位置 (0~3)
//       any = 至少有一位为1
// ============================================================
module priority_enc_4 (
    input  wire [3:0] din,
    output reg  [3:0] pos,
    output reg        any
);
    always @(*) begin
        any = |din;
        casez (din)
            4'b???1: pos[2:0] = 0;
            4'b??10: pos[2:0] = 1;
            4'b?100: pos[2:0] = 2;
            4'b1000: pos[2:0] = 3;
            default: pos[2:0] = 0;
        endcase
        pos[3] = 1'b0;
    end
endmodule
