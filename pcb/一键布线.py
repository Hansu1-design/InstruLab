#!/usr/bin/env python3
"""一键布线: KiCad导出DSN → Freerouting布 → 导回KiCad"""
import pyautogui, time, subprocess, os
pyautogui.FAILSAFE = False

# 文件路径
dsn = r"G:\System\InstruLab\pcb\tdc_daughterboard\tdc_daughterboard.dsn"
ses = r"G:\System\InstruLab\pcb\tdc_daughterboard\tdc_daughterboard.ses"
fr_exe = r"freerouting/tdc_daughterboard.dsn(相对路径)"

# Step 1: KiCad导出DSN
print("[1/4] 激活KiCad, 导出DSN...")
for w in pyautogui.getAllWindows():
    if 'kicad' in w.title.lower() or 'tdc_daughterboard' in w.title.lower():
        w.restore(); w.activate(); w.maximize()
        break
time.sleep(2)

# 点击PCB编辑器图标
pyautogui.click(100, 300); time.sleep(1)
# Ctrl+S保存
pyautogui.hotkey('ctrl', 's'); time.sleep(2)

# Alt+F → 导出 → Specctra DSN
pyautogui.hotkey('alt', 'f'); time.sleep(1)
for _ in range(4): pyautogui.press('down'); time.sleep(0.1)
pyautogui.press('enter'); time.sleep(1)
for _ in range(5): pyautogui.press('down'); time.sleep(0.1)
pyautogui.press('enter'); time.sleep(1)

# 输入DSN文件名
pyautogui.hotkey('ctrl', 'a'); time.sleep(0.2)
pyautogui.write(dsn, interval=0.02); time.sleep(0.5)
pyautogui.press('enter'); time.sleep(2)
print("  DSN导出完成")

# Step 2: 启动Freerouting
print("[2/4] 启动Freerouting...")
subprocess.Popen([fr_exe])
time.sleep(4)

# 最大化Freerouting窗口
for w in pyautogui.getAllWindows():
    if 'free' in w.title.lower():
        w.restore(); w.activate(); w.maximize()
        break
time.sleep(1)

# Step 3: Freerouting打开DSN
print("[3/4] 加载DSN...")
pyautogui.hotkey('alt', 'f'); time.sleep(0.5)
pyautogui.press('o'); time.sleep(1)
pyautogui.write(dsn, interval=0.02); time.sleep(0.5)
pyautogui.press('enter'); time.sleep(3)

# 点击自动布线(魔棒图标大概在工具栏中间)
pyautogui.click(250, 50); time.sleep(1)
print("  自动布线启动, 等待15秒...")
time.sleep(15)

# 导出SES
pyautogui.hotkey('alt', 'f'); time.sleep(0.5)
pyautogui.press('e'); time.sleep(0.5)
pyautogui.press('enter'); time.sleep(1)
pyautogui.write(ses, interval=0.02); time.sleep(0.3)
pyautogui.press('enter'); time.sleep(2)
print(f"  SES导出: {ses}")

# 关闭Freerouting
subprocess.run(['taskkill', '/f', '/im', 'freerouting.exe'], capture_output=True)

# Step 4: KiCad导入SES
print("[4/4] KiCad导入SES...")
for w in pyautogui.getAllWindows():
    if 'kicad' in w.title.lower():
        w.restore(); w.activate()
        break
time.sleep(2)

pyautogui.hotkey('alt', 'f'); time.sleep(0.5)
for _ in range(2): pyautogui.press('down'); time.sleep(0.1)
for _ in range(2): pyautogui.press('right'); time.sleep(0.1)
pyautogui.press('down'); time.sleep(0.1)
pyautogui.press('enter'); time.sleep(1)

# 选择SES文件
pyautogui.write(ses, interval=0.02); time.sleep(0.3)
pyautogui.press('enter'); time.sleep(3)

# Ctrl+S保存
pyautogui.hotkey('ctrl', 's'); time.sleep(1)

# 验证
if os.path.exists(ses):
    print(f"\n✅ 布线完成! SES大小: {os.path.getsize(ses)//1024}KB")
    print(f"   在KiCad PCB编辑器中查看布线结果")
else:
    print(f"\n❌ SES文件未生成, 可能需要手动操作")

print("\n如果自动导入失败, 手动操作:")
print("1. KiCad → 文件 → 导入 → Specctra SES")
print(f"   选: {ses}")
