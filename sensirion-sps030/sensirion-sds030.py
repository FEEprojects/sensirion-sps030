"""
    Wrapper classes for the Honeywell HPMA115S0.
    Florentin Bulot
    15/01/2019
    based on https://github.com/FEEprojects/plantower 
"""

import logging
from datetime import datetime, timedelta
from serial import Serial, SerialException
from time import sleep

DEFAULT_SERIAL_PORT = "/dev/ttyUSB0" # Serial port to use if no other specified
DEFAULT_BAUD_RATE = 115200 # Serial baud rate to use if no other specified
DEFAULT_SERIAL_TIMEOUT = 2 # Serial timeout to use if not specified
DEFAULT_READ_TIMEOUT = 1 #How long to sit looking for the correct character sequence.

DEFAULT_LOGGING_LEVEL = logging.WARN

MSG_CHAR_1 = b'\x42' # First character to be recieved in a valid packet
MSG_CHAR_2 = b'\x4d' # Second character to be recieved in a valid packet
MSG_START_STOP = b'\x7E'

CMD_ADDR = b'\x00'
CMD_START_MEASUREMENT = b'\x00' #Execute
CMD_STOP_MEASUREMENT = b'\x01' #Execute
CMD_READ_MEASUREMENT = b'\x03' #Read
CMD_READ_WRITE_AUTOCLEAN_INTERVAL = b'\x80' #Read/Write
CMD_START_FAN_CLEANING = b'\x56' #Execute
CMD_DEVICE_INFORMATION = b'\xD0' #Read
CMD_RESET = b'\xD3' #Execute
SUBCMD_START_MEASUREMENT_1= b'\x01'
SUBCMD_START_MEASUREMENT_2= b'\x03'

RX_DELAY_S = 0.02 

class SensirionReading(object):
    """
        Describes a single reading from the Honeywell sensor
    """
   def __init__(self, line):
        """
            Takes a line from the Honeywell serial port and converts it into
            an object containing the data
        """
        self.timestamp = datetime.utcnow()
        self.pm10 = line[8] * 256 + line[9]
        self.pm25 = line[6] * 256 + line[7]
        

    def __str__(self):
        return (
            "%s,%s,%s" %
            (self.timestamp, self.pm10, self.pm25))

class SensirionException(Exception):
    """
        Exception to be thrown if any problems occur
    """
    pass

class Sensirion(object):
    """
        Actual interface to the HPMA115S0 sensor
    """
    def __init__(
            self, port=DEFAULT_SERIAL_PORT, baud=DEFAULT_BAUD_RATE,
            serial_timeout=DEFAULT_SERIAL_TIMEOUT,
            read_timeout=DEFAULT_READ_TIMEOUT,
            log_level=DEFAULT_LOGGING_LEVEL):
        """
            Setup the interface for the sensor
        """
        self.logger = logging.getLogger("SDS030 Interface")
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

    def _verify(self, recv):
        """
            Uses the last 2 bytes of the data packet from the Honeywell sensor
            to verify that the data recived is correct
        """
        calc = 0
        ord_arr = []
        for c in bytearray(recv[:-2]): #Add all the bytes together except the checksum bytes
            calc += c
            ord_arr.append(c)
        self.logger.debug(str(ord_arr))
        sent = (recv[-2] << 8) | recv[-1] # Combine the 2 bytes together
        if sent != calc:
            self.logger.error("Checksum failure %d != %d", sent, calc)
            raise HPMAException("Checksum failure")

    def _calculate_checksum(self, header, data):
        # Sum all the bytes between MSG_START_STOP (included) and the Checksum
        sumBytes = bytes([sum(data)+sum(header)])
        # Take the LSB
        LSB = (ord(sumBytes) >> 0)
        # Invert it to get the checksum
        return bytes([255-LSB])
    def _sensirion_tx(self):

    	recv = b''
        start = datetime.utcnow() #Start timer
        if perform_flush:
            self.serial.flush() #Flush any data in the buffer
        while(
                datetime.utcnow() <
                (start + timedelta(seconds=self.read_timeout))):
            inp = self.serial.read() # Read a character from the input
            if inp == CMD: # check it matches
                recv += inp # if it does add it to recieve string
                inp = self.serial.read() # read the next character
                if inp == MSG_CHAR_2: # check it's what's expected
                    recv += inp # att it to the recieve string
                    recv += self.serial.read(30) # read the remaining 30 bytes
                    self._verify(recv) # verify the checksum
                    return HoneywellReading(recv)
    def sensirion_start_measurement(self):
        
        _sensirion_tx(CMD_ADDR, CMD_START_MEASUREMENT,SUBCMD_START_MEASUREMENT_1+SUBCMD_START_MEASUREMENT_2)

    def sensirion_stop_measurement(self):
        
        self._sensirion_tx(CMD_ADDR, CMD_STOP_MEASUREMENT,[])

    def _sensirion_unstuff_byte(self,data):
    	
    def read(self, perform_flush=True):
        """
            Reads a line from the serial port and return
            if perform_flush is set to true it will flush the serial buffer
            before performing the read, otherwise, it'll just read the first
            item in the buffer
        """
        recv = b''
        start = datetime.utcnow() #Start timer
        if perform_flush:
            self.serial.flush() #Flush any data in the buffer
        while(
                datetime.utcnow() <
                (start + timedelta(seconds=self.read_timeout))):
            inp = self.serial.read() # Read a character from the input
            if inp == MSG_START_STOP: # check it matches
                recv += inp # if it does add it to recieve string
                inp = self.serial.read() # read the next character
                if inp == CMD_ADDR: # check it's what's expected
                    recv += inp # att it to the recieve string
                    recv += self.serial.read()
                    if inp == CMD_READ_MEASUREMENT:
                    	recv += inp # att it to the recieve string
                        inp += self.serial.read()
                        if inp != b'\x00':
                        	raise SensirionException(inp)
                        else:
                        	recv += inp # att it to the recieve string
                            inp += self.serial.read()
                            len(inp)+2
                    else:
                    	raise SensirionException("Wrong command")

                     # read the remaining 30 bytes
                    self._verify(recv) # verify the checksum

                    sensirion_shdlc_unstuff_byte

                    return HoneywellReading(recv) # convert to reading object
            #If the character isn't what we are expecting loop until timeout
        rais

    def sensirion_read_measurement(self):

        self._sensirion_tx(CMD_ADDR, CMD_READ_MEASUREMENT)
        sleep(RX_DELAY_S)
        recv=_sensirion_rx()

        return SensirionReading(recv)

    def _sensirion_tx(self, addr, cmd, data):
        # Build the message to send to the sensor.
        # addr = b'\x01'
        # cmd = b'\x01'
        # data = [b'\x01',b\'x08',b'\xae', ....]

        checksum = self._calculate_checksum(addr+cmd+bytes([len(data)]), data) # the checksum has to be calculated before the byte_stuffing
        message = MSG_START_STOP
        message+= self._sensirion_stuff_bytes(addr)
        message+= self._sensirion_stuff_bytes(cmd)
        message+= self._sensirion_stuff_bytes(bytes([len(data)])) # Length
        message+=self._sensirion_stuff_bytes(data)
        message+= self._sensirion_stuff_bytes(checksum)
        message+= MSG_START_STOP
        self.logger.debug("Message sent: {}".format(message))
        return self.serial.write(message)

    def _sensirion_stuff_bytes(self,data):
         data_stuffed = b''
         data_len = 0
        for b in data:
            self.logger.debug("Bytes : {} --------".format(b))
            if bytes([b]) == b'\x7E':
                data_stuffed+=b'\x7D'+b'\x5E'
                data_len+=2
            elif bytes([b]) == b'\x7D':
                data_stuffed+=b'\x7D'+b'\x5D'
                data_len+=2
            elif bytes([b]) == b'\x11':
                data_stuffed+=b'\x7D'+b'\x31'
                data_len+=2
            elif bytes([b]) == b'\x13':
                data_stuffed+=b'\x7D'+b'\x33'
                data_len+=2
            else:
                data_stuffed+=bytes([b]) 
                data_len+=1  
        return data_stuffed