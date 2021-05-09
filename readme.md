[![Documentation Status](https://readthedocs.org/projects/grove-doppler-radar/badge/?version=latest)](https://grove-doppler-radar.readthedocs.io/en/latest/?badge=latest)

# Grove - Doppler Radar library
Python version of the library for communication with the Grove Doppler Radar is based on the BGT24LTR11. It's a simple continuous wave doppler radar capable of movement detection, speed measurement and direction of movement detection. More details and resources can be found in the official [product wiki](https://wiki.seeedstudio.com/Grove-Doppler-Radar/).

## Documentation
The documentation is available here: https://grove-doppler-radar.readthedocs.io/en/latest/

## Installation
While in this directory run:  
```pip3 install .```

## Usage
1. The radar board communicates via UART protocol. You could use it with GPIO pins on Raspberry or Jetson board. Alternativelly you can use Arduino (for example seeeduino XIAO) as UART <-> USB bridge and connect it to your PC. You can use [the provided sketch](scripts/uart_bridge.ino) for that purpose. Yet another alternative is pre-made USB <-> UART converter.
2. Run <code>dmesg | grep --color 'tty'</code> twice, before and after plugging in your radar to see what name it gets in the system.
3. In python script open the serial connection with [PySerial library](https://pythonhosted.org/pyserial).
   
### Example:
```python
import serial

from BGT24LTR11.BGT24LTR11 import Radar

serial_ =\
   serial.Serial('/dev/ttyACM0', baudrate=115200, timeout=2)

radar = Radar(serial_)
radar.set_mode_target()

target_info = radar.get_target_info()
if target_info['state'] != 0:
    print(f"Speed of the detected target is {target_info['speed']} m/s")
```
