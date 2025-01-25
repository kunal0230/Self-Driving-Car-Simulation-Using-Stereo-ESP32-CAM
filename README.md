This repository contains code and data related to a project that is currently under review for publication. Due to intellectual property considerations and publication requirements, the source code and certain assets are not publicly available at this time.


```
my_self_driving_sim/
├── carla_simulator/
│   ├── CarlaUE4.exe               # The CARLA executable/binaries (Windows)
│   ├── config/                    
│   │   └── carla_settings.ini     # Custom CARLA settings, if needed
│   ├── start_carla.bat            # Script to launch CARLA with specific args
│   └── (other CARLA files...)
│
├── esp32_firmware/
│   ├── camera_firmware_cam1/
│   │   ├── camera_firmware_cam1.ino
│   │   └── ...
│   └── camera_firmware_cam2/
│       └── ...
│
├── python/
│   ├── env/                       # Virtual environment (e.g., conda or venv)
│   ├── requirements.txt           
│   ├── scripts/
│   │   ├── capture_stream.py      # Demo script to capture from ESP32 cams
│   │   ├── data_collection.py     #  data capture for ML
│   │   ├── model.py               # ML model definitions
│   │   ├── inference.py           # Real-time inference and control
│   │   ├── control_interface.py   # Utility functions to send commands to CARLA
│   │   └── stereo_vision.py       # Optional stereo vision code
│   ├── notebooks/
│   │   └── training_notebook.ipynb
│   └── __init__.py
│
├── doc/
│   ├── readme.md
│   └── hardware_setup.md
│
└── .gitignore                   







```

```
                +-------------------------+
                |   Windows PC (RTX3050) |
                |-------------------------|
                | - CARLA Simulator      |
                | - Python (CV/ML)       |
                | - Receives Camera Feeds|
                | - Controls Carla via   |
                |   Python API           |
                +-----------+------------+
                            |
(Physical World)            | Ethernet/Wi-Fi
   +----------------+       |
   |   Monitor w/   | <-----+
   |  CARLA Window  |
   | (Full Screen)  |
   +----------------+
        ^     ^
        |     |
        |     +---- (ESP32-CAM #2)
        |
        +---------- (ESP32-CAM #1)




