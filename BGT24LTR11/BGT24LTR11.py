from typing import Optional

from BGT24LTR11.constants import *


class Radar:
    """
    The class the same functionality as the original Arduino
    library available on the radar's website: https://wiki.seeedstudio.com/Grove-Doppler-Radar/

    Documentation related to the communication: https://files.seeedstudio.com/wiki/Grove-Doppler-Radar/Grove_DopplerRadar(BGT24LTR11)Radar_module_communication_protocol_v1.1.pdf
    Documentation of the radar chip: https://www.infineon.com/dgdl/Infineon-AN598_Sense2GOL_Pulse-ApplicationNotes-v01_00-EN.pdf?fileId=5546d4626e651a41016e82b630bc1571
    """

    def __init__(self, serial_, verbose: bool = False):
        """
        :param serial_: Serial connection object. It must have read, write
            and is_open methods. The library was created with the PySerial's
            object in mind.
        :param verbose: Flag determining if additional
          information should be printed to console or not.
        """

        self._serial = serial_

        if self._serial.is_open:
            print("Status OK")
        else:
            print(f"The {self._serial.name}"
                  f"serial port is closed")

        self._verbose = verbose

    @staticmethod
    def _calculate_checksum(command):
        decimal_sum = sum(command)
        return decimal_sum.to_bytes(2, byteorder='big')

    def _build_command(self, command_code, data=None):
        CHECKSUM_LEN = 2

        command = bytearray([
            GBT24LTR11_MESSAGE_HEAD,
            GBT24LTR11_RECEIVE_ADDRESS,
            command_code
        ])

        data_len = CHECKSUM_LEN
        if data is not None:
            if not isinstance(data, list):
                data = [data]
            data_len += len(data)

        data_len_bytes = data_len.to_bytes(2, byteorder='big')
        command.extend(data_len_bytes)

        if data is not None:
            command.extend(bytearray(data))

        checksum = self._calculate_checksum(command)
        command.extend(checksum)

        return command

    def _read_response(self):
        BYTES_MAX = 100
        response = bytearray([])
        for i in range(BYTES_MAX):
            next_byte = self._serial.read(1)

            if next_byte == GBT24LTR11_MESSAGE_HEAD.to_bytes(1, 'big'):
                response.extend(next_byte)
                next_byte = self._serial.read(1)

                if next_byte == GBT24LTR11_SEND_ADDRESS.to_bytes(1, 'big'):
                    response.extend(next_byte)
                    command_code = self._serial.read(1)
                    response.extend(command_code)

                    data_len = self._serial.read(2)
                    data_len_dec = int.from_bytes(data_len, byteorder='big')

                    data = self._serial.read(data_len_dec - 2)
                    checksum = self._serial.read(2)

                    response.extend(data_len)
                    response.extend(data)

                    if int.from_bytes(checksum, byteorder='big') != sum(response):
                        print('Incorrect checksum')
                        return None

                    response.extend(checksum)
                    return {
                        'command': response,
                        'command_code': command_code,
                        'data': data
                    }

        return None

    def get_target_info(self) -> Optional[dict]:
        """Query the radar for speed and state of a detected target.
        Speed is expressed in m/s.
        State of the target can be one of the following:
        - 0: no target detected
        - 1: the target is moving further from the radar
        - 2: the target is moving towards the radar
        """

        command = self._build_command(command_code=GBT24LTR11_COMMAND_GET_TARGET)
        self._serial.write(command)

        response = self._read_response()
        if response:
            data = response['data']
            speed = int.from_bytes(data[:2], byteorder='big')
            state = int.from_bytes(data[2:3], byteorder='big')

            if self._verbose:
                if state == GBT24LTR11_TARGET_APPROACH:
                    print("Target is approaching")
                elif state == GBT24LTR11_TARGET_LEAVE:
                    print("Target is leaving")
                elif state == GBT24LTR11_TARGET_NONE:
                    print("Target not found")

            return {
                'speed': speed / 100,  # m/s
                'state': state
            }

        return None

    def get_target_state(self) -> Optional[int]:
        """
         State of the target can be one of the following:

         - 0: no target detected
         - 1: the target is moving further from the radar
         - 2: the target is moving towards the radar
         """

        verbosity = self._verbose
        self._verbose = False
        target_info = self.get_target_info()
        self._verbose = verbosity

        if target_info:
            return target_info['state']
        return None

    def get_target_speed(self):
        """Speed expressed in m/s.
        """

        verbosity = self._verbose
        self._verbose = False
        target_info = self.get_target_info()
        self._verbose = verbosity

        if target_info:
            return target_info['speed']
        return None

    def get_IQADC(self) -> Optional[dict]:
        """Query IQ components of the signal. The output must be
        further processed to obtain direction and speed of the target
        if any target is detected.
        """

        command = self._build_command(
            command_code=GBT24LTR11_COMMAND_GET_IQADC)
        self._serial.write(command)

        response = self._read_response()
        if response:
            data = response['data']
            I = data[::2]
            Q = data[1::2]

            return {
                'I': [int.from_bytes([b], byteorder='big') for b in I],
                'Q': [int.from_bytes([b], byteorder='big') for b in Q]
            }

        return None

    @staticmethod
    def _parse_speed_range_data(data):
        max_speed = int.from_bytes(data[:2], byteorder='big')
        min_speed = int.from_bytes(data[2:], byteorder='big')

        return {
            'min_speed': min_speed / 100.,  # m/s
            'max_speed': max_speed / 100.  # m/s
        }

    def get_speed_detection_range(self) -> Optional[dict]:
        """
        Query the currently setup speed detection range.
        Radar will be less sensible to targets moving with any speed outside this range.
        """
        command = self._build_command(
            command_code=GBT24LTR11_COMMAND_GET_SPEED_SCOPE)
        self._serial.write(command)

        response = self._read_response()
        if response:
            data = response['data']
            return self._parse_speed_range_data(data)

        return None

    def set_speed_detection_range(self, min_speed: float = 0.5, max_speed: float = 10):
        """
        Specify speed detection range.
        Radar will be less sensible to targets moving with any speed outside this range.
        """
        speed_range = bytearray([])
        min_speed = int(min_speed * 100).to_bytes(2, byteorder='big')
        max_speed = int(max_speed * 100).to_bytes(2, byteorder='big')
        speed_range.extend(max_speed)
        speed_range.extend(min_speed)

        command = self._build_command(
            command_code=GBT24LTR11_COMMAND_SET_SPEED_SCOPE,
            data=[int.from_bytes([byte], byteorder='big')
                  for byte in speed_range]
        )
        self._serial.write(command)
        response = self._read_response()
        if response:
            data = response['data']
            return self._parse_speed_range_data(data)

        return None

    def get_mode(self) -> Optional[int]:
        """
        Query the working mode of the radar. There are two modes:

        - 0: Target detection:
            controller returns info about the
            target's speed and direction of movement or informs that
            no target was detected.
            IQADC signals shouldn't be accessible in this mode.
        - 1: IQADC:
            controller returns digitized IQ components of the signal.
            From it a user can calculate speed, direction of motion and determine
            if any target is in the radar's range at all.
            In this mode target detection info is unreliable.
        """
        command = self._build_command(command_code=GBT24LTR11_COMMAND_GET_MODE)
        self._serial.write(command)

        response = self._read_response()
        if response:
            mode = response['data']
            mode = int.from_bytes(mode, byteorder='big')

            if self._verbose:
                if mode == GBT24LTR11_MODE_TARGET:
                    print('Radar is in the "target mode".\n'
                          'It can detect a target\'s speed and'
                          'the direction of movement')
                elif mode == GBT24LTR11_MODE_IQADC:
                    print('Radar is in the "IQADC mode."\n'
                          'It return IQ data from which one can calculate'
                          'distance to target and its speed')

            return mode

        return None

    def set_mode_target(self) -> Optional[int]:
        """
        Set the working mode of the radar to the 'target detection'.
        """
        command =self._build_command(
            command_code=GBT24LTR11_COMMAND_SET_MODE,
            data=GBT24LTR11_MODE_TARGET
        )

        self._serial.write(command)
        response = self._read_response()
        if response:
            return int.from_bytes(response['data'], byteorder='big')
        return None

    def set_mode_IQADC(self) -> Optional[int]:
        """
        Set the working mode of the radar to the 'IQADC'.
        """
        command = self._build_command(
            command_code=GBT24LTR11_COMMAND_SET_MODE,
            data=GBT24LTR11_MODE_IQADC
        )

        self._serial.write(command)
        response = self._read_response()
        if response:
            return int.from_bytes(response['data'], byteorder='big')
        return None

    def get_detection_threshold(self) -> Optional[int]:
        """
        Query the currently setup detection threshold. Units are unknown,
        should be related to the power of received signal.
        """
        command = self._build_command(
            command_code=GBT24LTR11_COMMAND_GET_THRESHOLD)
        self._serial.write(command)

        response = self._read_response()
        if response:
            return int.from_bytes(response['data'], byteorder='big')

        return None

    def set_detection_threshold(self, threshold: int = 200) -> Optional[int]:
        """
        Set the detection threshold. Units are unknown,
        should be related to the power of received signal.
        """
        command = self._build_command(
            command_code=GBT24LTR11_COMMAND_SET_THRESHOLD,
            data=[int.from_bytes([byte], byteorder='big')
                  for byte in threshold.to_bytes(4, byteorder='big')]
        )
        self._serial.write(command)
        response = self._read_response()
        if response:
            return int.from_bytes(response['data'], byteorder='big')

        return None
