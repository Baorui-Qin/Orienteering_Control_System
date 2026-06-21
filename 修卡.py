import serial
import time

# 1. 连接到 S3 的串口 (注意修改你的 COM 口)
# 115200 是 ESP32 默认波特率，timeout=1 表示读取超时时间
ser = serial.Serial('COM5', 115200, timeout=1)
time.sleep(2) # 等待串口稳定

print("✅ 串口连接成功，准备下发制卡指令...")

# 2. 发送制作“校时卡 (0x01)”的指令
command = "CMD:MAKE_SYNC"
# 如果你想制作汇报卡，就改成 command = "CMD:MAKE_REPORT"

ser.write(command.encode('utf-8'))
print(f"指令 [{command}] 已发送！请将空白卡放到 S3 上。")

# 3. 持续读取 S3 返回的系统提示
try:
    while True:
        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            if response:
                print(f"S3_HUB 返回: {response}")
except KeyboardInterrupt:
    print("退出程序")
finally:
    ser.close()