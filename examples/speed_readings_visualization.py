"""
Simple scrip that plots radar detection info.
Movements away from the radar are denoted with negative speed values.
"""

import matplotlib.pyplot as plt
import serial

from BGT24LTR11.BGT24LTR11 import Radar

serial_ = serial.Serial('/dev/ttyACM0', baudrate=115200, timeout=2)
radar = Radar(serial_, verbose=False)
radar.set_detection_threshold(2000)
radar.set_mode_target()

plt.style.use('ggplot')
fig = plt.figure()
plt.ion()

for _ in range(200):
    try:
        info = radar.get_target_info()
        speed = info['speed']

        color = 'r'
        if info['state'] == 1:
            speed *= -1
            color = 'g'

        plt.suptitle("Target detection demo")
        plt.title(f'Target\'s speed: {speed} m/s')
        plt.bar(1, speed, color=color)
        axes = plt.gca()
        axes.set_xlim([0, 2])
        axes.set_ylim([-5, 5])
        plt.xticks([])
        plt.pause(0.02)
        fig.clf()

    except KeyboardInterrupt:
        break
