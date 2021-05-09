Communication with the module
=============================
The radar board communicates via UART protocol. There are multiple ways of connecting the device to a host.

Hardware
--------
Whatever method you'll choose you have to make the following connections:

1. Radar VCC to device VCC (from 3.3 to 5V)
2. Radar GND to device GND.
3. Radar TX to device RX
4. Radar RX to device TX

1. GPIO pins with UART support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Many single board computers like Raspberry Pi or Nvidia Jetson offer GPIO pins that you can use for communicating with UART devices. Follow the instructions for your specific board on how to enable UART.

2. UART bridge with Arduino or similar device
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can use Arduino as bridge between the radar's module and your PC. This can be achieved with this very simple sketch for Arduino. Once you upload it to arduino you'll be able to connect it to your PC via USB and communicate with the radar module.

.. code-block:: C

    void setup()
    {
     delay(1000);
     SerialUSB.begin(115200);
     Serial1.begin(115200);
    }

    void loop()
    {
     if(SerialUSB.available()){
        Serial1.write(SerialUSB.read());
    }

    if(Serial1.available()){
        SerialUSB.write(Serial1.read());
     }
    }

3. UART <-> USB converter
~~~~~~~~~~~~~~~~~~~~~~~~~
You can buy dedicated converters to connect the radar to your PC.

Software
--------

1. Find the device's name on your system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Run:

.. code-block:: bash

    dmesg | grep --color 'tty'

twice, before and after plugging in your radar to check what name it gets in the system.
The newly appeared name is the name of your device.

On Linux you should see a line like this:

.. code-block:: bash

    [18090.927652] cdc_acm 1-5:1.0: ttyACM0: USB ACM device

ttyACM0 is the device's name and it's available at /dev/ttyACM0

2. PySerial library for serial communication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
On Linux serial communication can be performed by reading and writing to /dev/<your device name>.
To make things easier you can use an external library PySerial: https://pythonhosted.org/pyserial
which will be installed with this package.

Or, you can create your own library. Our library expects the connection object with the following methods:

1. write
2. read
3. is_open

Here's an example for establishing the communication with PySerial library:

.. code-block:: python

    import serial

    from BGT24LTR11.BGT24LTR11 import Radar

    serial_ = serial.Serial('/dev/ttyACM0', baudrate=115200, timeout=2)
    radar = Radar(serial_, verbose=False)
