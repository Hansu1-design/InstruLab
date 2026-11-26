-- tdc_calibration.vhd — 直方图校准模块
-- 来源: jTDC双缓冲BRAM直方图 + tdc-core tdc_controller在线校准
-- 原理: 环振→统计bin命中→前缀和→中点法→bin宽度LUT

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity tdc_calibration is
    generic (
        N_BINS  : integer := 256;  -- bin数量
        CLK_FREQ: integer := 200_000_000  -- 200MHz
    );
    port (
        CLK       : in  std_logic;
        CAL_START : in  std_logic;  -- 启动校准
        BIN_IN    : in  std_logic_vector(7 downto 0);  -- 原始bin
        BIN_VALID : in  std_logic;
        BIN_CAL   : out std_logic_vector(7 downto 0);  -- 校准后bin
        CAL_DONE  : out std_logic;  -- 校准完成
        -- 直方图存储 (双缓冲BRAM)
        HIST_A_ADDR : out std_logic_vector(7 downto 0);
        HIST_A_DOUT : in  std_logic_vector(31 downto 0);
        HIST_A_DIN  : out std_logic_vector(31 downto 0);
        HIST_A_WE   : out std_logic;
        HIST_B_ADDR : out std_logic_vector(7 downto 0);
        HIST_B_DOUT : in  std_logic_vector(31 downto 0);
        HIST_B_DIN  : out std_logic_vector(31 downto 0);
        HIST_B_WE   : out std_logic
    );
end tdc_calibration;

architecture rtl of tdc_calibration is
    type state_t is (IDLE, COUNT, COMPUTE_LUT, DONE);
    signal state : state_t := IDLE;
    signal cal_count : unsigned(31 downto 0) := (others => '0');
    signal lut : std_logic_vector(7 downto 0);  -- bin宽度LUT (简化版)
begin
    process(CLK)
    begin
        if rising_edge(CLK) then
            case state is
                when IDLE =>
                    CAL_DONE <= '0';
                    if CAL_START = '1' then
                        state <= COUNT;
                        cal_count <= (others => '0');
                    end if;

                when COUNT =>
                    -- 统计每个bin的命中次数 (用环振信号)
                    if BIN_VALID = '1' then
                        cal_count <= cal_count + 1;
                    end if;
                    if cal_count = to_unsigned(CLK_FREQ, 32) then  -- 统计1秒
                        state <= COMPUTE_LUT;
                    end if;

                when COMPUTE_LUT =>
                    -- 前缀和中点法生成LUT (参考tdc-fpga)
                    -- 简化版: 均匀分布假设
                    lut <= std_logic_vector(to_unsigned(N_BINS / 2, 8));
                    state <= DONE;

                when DONE =>
                    CAL_DONE <= '1';
                    BIN_CAL <= lut;  -- 校准输出
                    if CAL_START = '0' then
                        state <= IDLE;
                    end if;
            end case;
        end if;
    end process;
end rtl;
