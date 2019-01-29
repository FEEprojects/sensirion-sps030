"""
    Wrapper classes for the Honeywell HPMA115S0.
    Florentin Bulot
    15/01/2019
    based on https://github.com/FEEprojects/plantower
"""

import logging
import struct
from datetime import datetime, timedelta
from time import sleep
from serial import Serial, SerialException

DEFAULT_SERIAL_PORT = "/dev/ttyUSB0" # Serial port to use if no other specified
DEFAULT_BAUD_RATE = 115200 # Serial baud rate to use if no other specified
DEFAULT_SERIAL_TIMEOUT = 2 # Serial timeout to use if not specified
DEFAULT_READ_TIMEOUT = 1 #How long to sit looking for the correct character sequence.

DEFAULT_LOGGING_LEVEL = logging.WARN

MSG_START_STOP = b'\x7E'

CMD_ADDR = b'\x00'
CMD_START_MEASUREMENT = b'\x00' #Execute
CMD_STOP_MEASUREMENT = b'\x01' #Execute
CMD_READ_MEASUREMENT = b'\x03' #Read
CMD_READ_WRITE_AUTOCLEAN_INTERVAL = b'\x80' #Read/Write
CMD_START_FAN_CLEANING = b'\x56' #Execute
CMD_DEVICE_INFORMATION = b'\xD0' #Read
CMD_RESET = b'\xD3' #Execute
SUBCMD_START_MEASUREMENT_1 = b'\x01'
SUBCMD_START_MEASUREMENT_2 = b'\x03'

RX_DELAY_S = 0.02 # How long to wait between sending the read command and getting data (seconds)

class SensirionReading(object):
    """
        Describes a single reading from the Sensirion sensor
    """
    def __init__(self, line):
        """
            Takes a line from the Sensirion serial port and converts it into
            an object containing the data
        """
        self.timestamp = datetime.utcnow()
        self.pm1 = struct.unpack('f', line[6:9])
        self.pm25 = struct.unpack('f', line[10:13])
        self.pm4 = struct.unpack('f', line[14:17])
        self.pm10 = struct.unpack('f', line[18:21])
        self.n05 = struct.unpack('f', line[22:25])
        self.n1 = struct.unpack('f', line[26:29])
        self.n25 = struct.unpack('f', line[30:33])
        self.n4 = struct.unpack('f', line[34:37])
        self.n10 = struct.unpack('f', line[38:41])
        self.tps = struct.unpack('f', line[42:43])


    def __str__(self):
        return (
            "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" %
            (self.timestamp, self.pm1, self.pm25,
             self.pm4, self.pm10, self.n05,
             self.n1, self.n25, self.n4,
             self.n10, self.tps))

class SensirionException(Exception):
    """
        Exception to be thrown if any problems occur
    """
    pass

class Sensirion(object):
    """
        Actual interface to the Sensirion SPS030 sensor
    """
    def __init__(
            self, port=DEFAULT_SERIAL_PORT, baud=DEFAULT_BAUD_RATE,
            serial_timeout=DEFAULT_SERIAL_TIMEOUT,
            read_timeout=DEFAULT_READ_TIMEOUT,
            log_level=DEFAULT_LOGGING_LEVEL):
        """
            Setup the interface for the sensor
        """
        self.logger = logging.getLogger("SPS030 Interface")
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
        self.logger.setLevel(log_level)
        self.port = port
        self.logger.info("Serial port: %s", self.port)
        self.baud = baud
        self.logger.info("Baud rate: %s", self.baud)
        self.serial_timeout = serial_timeout
        self.logger.info("Serial Timeout: %s", self.serial_timeout)
        self.read_timeout = read_timeout
        self.logger.info("Read Timeout: %s", self.read_timeout)
        try:
            self.serial = Serial(
                port=self.port, baudrate=self.baud,
                timeout=self.serial_timeout)
            self.logger.debug("Port Opened Successfully")
        except SerialException as exp:
            self.logger.error(str(exp))
            raise SensirionException(str(exp))


    def set_log_level(self, log_level):
        """
            Enables the class logging level to be changed after it's created
        """
        self.logger.setLevel(log_level)

    def _sensirion_verify(self, recv):
        """
            Uses the last 2 bytes of the data packet from the Honeywell sensor
            to verify that the data recived is correct
        """
        calc = _calculate_checksum(recv[1] + recv[2] + recv[3] + recv[4], recv[5:-2])
        sent = recv[-2]
        if sent != calc:
            self.logger.error("Checksum failure %d != %d", sent, calc)
            raise SensirionException("Checksum failure")

    def sensirion_start_measurement(self):
        """
            Send the command to start the sensor reading data
        """
        self._sensirion_tx(
            CMD_ADDR, CMD_START_MEASUREMENT,
            SUBCMD_START_MEASUREMENT_1 + SUBCMD_START_MEASUREMENT_2)

    def sensirion_stop_measurement(self):
        """
            Send the command to stop the sensor reading data
        """
        self._sensirion_tx(CMD_ADDR, CMD_STOP_MEASUREMENT, [])

    def _sensirion_rx(self, addr, cmd, perform_flush=True):
        """
            Recieve and process a message from the sensor
        """
        recv = b''
        start = datetime.utcnow() #Start timer
        if perform_flush:
            self.serial.flush() #Flush any data in the buffer
        while(
                datetime.utcnow() <
                (start + timedelta(seconds=self.read_timeout))):
            inp = self.serial.read() # Read a character from the input
            self.logger.debug("Start byte 0x%02x",ord(inp))
            if inp == MSG_START_STOP: # check it matches
                recv += inp # if it does add it to recieve string
                inp = self.serial.read() # read the next character
                self.logger.debug("Addr byte 0x%02x",ord(inp))
                if inp == addr:
                    recv += inp
                    inp = self.serial.read()
                    self.logger.debug("Cmd byte 0x%02x",ord(inp))
                    if inp == cmd:
                        recv += inp
                        inp = self.serial.read()
                        self.logger.debug("Error state byte 0x%02x",ord(inp))
                        if inp != b'\x00':
                            self.logger.error("State error 0x%02x", ord(inp))
                            raise SensirionException(inp)
                        else:
                            recv += inp
                            inp = self.serial.read()
                            while inp != MSG_START_STOP: #read remaining data until the end byte
                                recv += inp
                                inp = self.serial.read()
                            return recv
                    else:
                        self.logger.error(
                            "Wrong command received 0x%02x, was expecting 0x%02x", ord(inp), ord(cmd))
                        self.logger.debug("Message received 0x%02x", int.from_bytes(recv,byteorder="big"))
                        raise SensirionException("Wrong command")

        raise SensirionException("Message incomplete")

    def _sensirion_check_length(self, data):
        """
            Verify that the length of the data unstuffed
            corresponds to the length sent by the sensor
        """
        data_length = data[4]
        if data_length == len(data[5:-2]):
            return True
        else:
            self.logger.error(
                "Wrong data length %d, was expecting %d", len(data[5:-2]), data_length)
            raise SensirionException("Wrong data length")

    def sensirion_read_measurement(self):
        """
            Read a measurement from the device
        """
        self._sensirion_tx(CMD_ADDR, CMD_READ_MEASUREMENT)
        sleep(RX_DELAY_S)
        recv = self._sensirion_rx(CMD_ADDR, CMD_READ_MEASUREMENT)
        recv_unstuffed = _sensirion_unstuff_bytes(recv)
        self._sensirion_check_length(recv_unstuffed)
        self._sensirion_verify(recv_unstuffed) # verify the checksum
        return SensirionReading(recv_unstuffed)


    def _sensirion_tx(self, addr, cmd, data=[]):
        """
            Build the message to send to the sensor.
            addr = b'\x01'
            cmd = b'\x01'
            data = [b'\x01',b\'x08',b'\xae', ....]
        """
        checksum = _calculate_checksum(
            addr + cmd + bytes([len(data)]), data) #checksum calculated before byte_stuffing
        message = MSG_START_STOP
        message += self._sensirion_stuff_bytes(addr)
        message += self._sensirion_stuff_bytes(cmd)
        message += self._sensirion_stuff_bytes(bytes([len(data)])) # Length
        message += self._sensirion_stuff_bytes(data)
        message += self._sensirion_stuff_bytes(checksum)
        message += MSG_START_STOP
        self.logger.debug("Message sent: %s", str(message))
        return self.serial.write(message)

    def _sensirion_stuff_bytes(self, data):
        """
            Covert the data into the stuffed format required for transmission
        """
        data_stuffed = b''
        data_len = 0
        for i in data:
            self.logger.debug("Bytes : 0x%02x --------", i)
            if bytes([i]) == b'\x7E':
                data_stuffed += b'\x7D' + b'\x5E'
                data_len += 2
            elif bytes([i]) == b'\x7D':
                data_stuffed += b'\x7D' + b'\x5D'
                data_len += 2
            elif bytes([i]) == b'\x11':
                data_stuffed += b'\x7D' + b'\x31'
                data_len += 2
            elif bytes([i]) == b'\x13':
                data_stuffed += b'\x7D' + b'\x33'
                data_len += 2
            else:
                data_stuffed += bytes([i])
                data_len += 1
        return data_stuffed

def _calculate_checksum(header, data):
    """
        Sum all the bytes between MSG_START_STOP (included) and the Checksum
    """
    sum_bytes = bytes([sum(data) + sum(header)])
    # Take the LSB
    lsb = (ord(sum_bytes) >> 0)
    # Invert it to get the checksum
    return bytes([255 - lsb])


def _sensirion_unstuff_bytes(data):
    """
        Reverse the data stuffing used on the serial protocol
    """
    data_unstuffed = b''
    i = 0
    while i < len(data):
        if bytes([data[i]]) == b'\x7D':
            if bytes([data[i + 1]]) == b'\x5e':
                data_unstuffed += b'\x7e'
                i += 2
            elif bytes(data[i]) == b'\x5d':
                data_unstuffed += b'\x7d'
                i += 2
            elif bytes(data[i]) == b'\x31':
                data_unstuffed += b'\x11'
                i += 2
            elif bytes(data[i]) == b'\x33':
                data_unstuffed += b'\x13'
                i += 2
        else:
            data_unstuffed += bytes(data[i])
            i += 1
    return data_unstuffed
