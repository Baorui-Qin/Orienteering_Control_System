import serial

# 根据你的电脑实际情况修改 COM 口号
ser = serial.Serial('COM3', 115200) 

print("正在监听 S3 网关的数据...")

while True:
    if ser.in_waiting > 0:
        # 读取串口发来的一行数据，并解码
        line = ser.readline().decode('utf-8').strip()
        
        # 解析数据
        if line.startswith("LOCAL_SCAN:"):
            uid = line.split(":")[1]
            print(f"管理员在本地录入新卡，卡号：{uid}")
            # 这里可以写代码把 uid 存进数据库
            
        elif line.startswith("NODE_SCAN:"): # 未来留给 ESP-NOW 接收节点数据的接口
            # 处理 C3 发来的数据...
            pass