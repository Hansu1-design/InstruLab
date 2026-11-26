-- tdc_encoder.vhd — 温度计码→二进制编码器
-- 来源: jTDC 96bit_encoder + tdc-fpga priority_encoder
-- 方式: 优先编码器(first-hit-wins) + 2级流水

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity tdc_encoder is
    generic ( N_TAPS : integer := 128 );
    port (
        CLK     : in  std_logic;
        THERM   : in  std_logic_vector(N_TAPS-1 downto 0); -- 温度计码
        BIN_OUT : out std_logic_vector(7 downto 0);
        VALID   : out std_logic
    );
end tdc_encoder;

architecture rtl of tdc_encoder is
    signal bin_pipe : unsigned(7 downto 0) := (others => '0');
    signal hit_pipe : std_logic := '0';
begin
    -- 第1级: 组合逻辑找first-1
    process(THERM)
        variable found : std_logic := '0';
    begin
        bin_pipe <= (others => '0');
        hit_pipe <= '0';
        found := '0';
        for i in 0 to N_TAPS-1 loop
            if THERM(i) = '1' and found = '0' then
                bin_pipe <= to_unsigned(i, 8);
                hit_pipe <= '1';
                found := '1';
            end if;
        end loop;
    end process;

    -- 第2级: 输出寄存
    process(CLK)
    begin
        if rising_edge(CLK) then
            BIN_OUT <= std_logic_vector(bin_pipe);
            VALID   <= hit_pipe;
        end if;
    end process;
end rtl;
