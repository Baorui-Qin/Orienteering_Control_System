# S3 Control Panel

A desktop panel for controlling S3 through UART and monitoring all S3 output in real time.

## Features

- Industrial dark-mode console built with CustomTkinter
- Left sidebar control center:
  - COM connect/disconnect
  - dynamic Wi-Fi push (`CMD:SET_WIFI:<SSID>,<PWD>`)
  - card-maker mode control (`CMD:MAKE_SYNC`, `CMD:MAKE_REPORT`, `CMD:RESET_MODE`)
  - custom command input
- Right-side dashboard:
  - S3 hardware online/offline
  - Wi-Fi status + SSID
  - NTP/system timestamp
- Real-time attendance board with columns:
  - timestamp, node ID, UID, person, status
- SQLite local storage (`py/attendance.db`)
- Export attendance report to Excel (`.xlsx`)
- Raw terminal log area (black background + terminal green text)

## Run

1. Install dependencies:

```bash
pip install -r py/requirements.txt
```

2. Start panel:

```bash
python py/s3_control_panel.py
```

## Notes

- Default baud rate is `115200`.
- Make sure S3 is connected to your PC and exposes the correct COM port.
- The panel sends `CMD:GET_STATUS` every second after serial connection.
- Expected S3 status response format:

```text
STATUS:WIFI=<0/1>,SSID=<name>,TIME=<unix_timestamp>
```
