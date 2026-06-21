"""程序入口：以 `python py/s3_control_panel.py` 启动控制台。"""

from pathlib import Path
import sys

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from s3_panel.app import S3ControlPanel, main

__all__ = ["S3ControlPanel", "main"]


if __name__ == "__main__":
    main()
