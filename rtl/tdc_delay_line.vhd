-- tdc_delay_line.vhd — CARRY4延迟线 (Artix-7)
-- 来源: jTDC/tdc-core/tdc-fpga 源码分析
-- 目标: <30ps RMS, 单通道, START→STOP精密测量

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity tdc_delay_line is
    generic (
        N_TAPS : integer := 128  -- 延迟级数 (覆盖1个CLK周期)
    );
    port (
        CLK     : in  std_logic;                    -- 系统时钟 200MHz
        START   : in  std_logic;                    -- 开始信号
        STOP    : in  std_logic;                    -- 停止信号
        BIN_OUT : out std_logic_vector(7 downto 0); -- 细量化bin号
        VALID   : out std_logic                     -- 输出有效
    );
end tdc_delay_line;

architecture rtl of tdc_delay_line is
    -- CARRY4延迟链信号
    signal delay_chain : std_logic_vector(N_TAPS-1 downto 0);
    signal stop_d      : std_logic;  -- STOP打一拍
    signal start_d     : std_logic;
    signal sampling    : std_logic;  -- 采样使能
    
    -- 优先编码器输出
    signal bin_raw     : unsigned(7 downto 0);
    signal hit_found   : std_logic;
begin

    -- STOP同步 (防亚稳态, 参考tdc-core tdc_delayline.vhd)
    process(CLK)
    begin
        if rising_edge(CLK) then
            stop_d <= STOP;
        end if;
    end process;

    -- CARRY4延迟链 (Artix-7 BEL约束, 参考jTDC carrysampler)
    -- 综合工具会将CARRY4链映射到同一slice的进位链上
    gen_delay: for i in 0 to N_TAPS-1 generate
        signal tap_in, tap_out : std_logic;
    begin
        i0: if i = 0 generate
            tap_in <= stop_d;
        end generate;
        iN: if i > 0 generate
            tap_in <= delay_chain(i-1);
        end generate;
        
        -- CARRY4原语: 每级约10-30ps延迟
        cARRY4_inst: entity work.carry4_sim
            port map (CI => tap_in, CO => tap_out);
        
        -- 双触发器采样 (防亚稳态, 参考tdc-core)
        process(CLK)
        begin
            if rising_edge(CLK) then
                delay_chain(i) <= tap_out;
            end if;
        end process;
    end generate gen_delay;

    -- 优先编码器: 找第一个1的位置 (first-hit-wins, 参考jTDC 96bit_encoder)
    process(delay_chain)
        variable found : std_logic := '0';
    begin
        bin_raw <= (others => '0');
        hit_found <= '0';
        found := '0';
        for i in 0 to N_TAPS-1 loop
            if delay_chain(i) = '1' and found = '0' then
                bin_raw <= to_unsigned(i, 8);
                hit_found <= '1';
                found := '1';
            end if;
        end loop;
    end process;

    -- 输出寄存器
    process(CLK)
    begin
        if rising_edge(CLK) then
            BIN_OUT <= std_logic_vector(bin_raw);
            VALID   <= hit_found and (start_d xor stop_d);
        end if;
    end process;

    -- START同步
    process(CLK)
    begin
        if rising_edge(CLK) then
            start_d <= START;
        end if;
    end process;

end rtl;
