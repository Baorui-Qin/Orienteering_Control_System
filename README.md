# Orienteering Control System

面向定向越野赛事的本地计时与读卡管理系统。项目提供一个桌面控制面板，用于通过串口连接 S3 设备，管理赛事基础数据、读卡记录、路线与成绩，并导出 Excel 报表。

## 功能概览

- 串口连接 S3 网关/读卡设备，支持 COM 口与波特率配置
- 实时接收刷卡、心跳和节点状态数据
- 管理选手、单位、分组、出发通道、检查点和路线
- 支持普通卡、起点卡、途经卡、终点卡、清除卡、校时卡等制卡指令
- 自动计算成绩、分段成绩和原始流水
- 导出成绩总榜、分段成绩、原始流水、出发时刻表和导入模板
- 使用 SQLite 在本地保存赛事数据

## 项目结构

```text
.
├── s3_control_panel.py      # 程序入口
├── calculation.py           # 成绩计算相关逻辑
├── test_calculation.py      # 计算逻辑测试
├── requirements.txt         # Python 依赖
├── s3_panel/                # 桌面控制面板主体代码
│   ├── app.py
│   ├── runtime.py
│   ├── serial_io.py
│   ├── storage.py
│   └── ...
├── 串口.py                  # 串口调试脚本
└── 修卡.py                  # 卡片维护脚本
```

## 环境要求

- Python 3.10 或更高版本
- Windows 系统
- 可用的串口设备
- S3 网关/读卡设备

## 安装

```bash
pip install -r requirements.txt
```

依赖包括：

- `pyserial`
- `customtkinter`
- `openpyxl`

## 运行

```bash
python s3_control_panel.py
```

启动后在界面中选择对应 COM 口，默认波特率为 `115200`。

## 数据说明

程序运行时会在项目根目录生成本地数据库文件：

```text
attendance.db
```

该文件用于保存赛事、选手、刷卡记录和成绩等本地数据。仓库默认不会上传数据库文件，避免公开真实赛事数据。

## 常用串口指令

控制面板会向设备发送形如 `CMD:...` 的命令，例如：

```text
CMD:GET_STATUS
CMD:SET_WIFI:<SSID>,<PASSWORD>
CMD:MAKE_NORMAL
CMD:MAKE_START
CMD:MAKE_MID
CMD:MAKE_END
CMD:MAKE_CLEAR
CMD:MAKE_SYNC
CMD:MAKE_REPORT
CMD:RESET_MODE
```

设备状态响应示例：

```text
STATUS:WIFI=<0/1>,SSID=<name>,TIME=<unix_timestamp>
```

## 测试

```bash
python -m unittest test_calculation.py
```

## 备注

- 请先确认 S3 设备已连接电脑，并能在系统中识别出正确的 COM 口。
- 如果串口连接失败，优先检查设备占用、波特率、USB 驱动和线缆连接。
- Excel 导出功能依赖 `openpyxl`。
