import sensirion_sps030
from time import sleep
from argparse import ArgumentParser
import logging

def test(sensor_port, console_log_level):
    RX_DELAY_S = 0.02 

    SPS030 = sensirion_sps030.Sensirion(
    	port=sensor_port, log_level=console_log_level)

    sleep(RX_DELAY_S)
    mess=SPS030.read_measurement()

    SPS030.logger.info("reading: %s",mess)

if __name__ == "__main__":
    ARG_PARSER = ArgumentParser(
        description="Return one reading from the SPS030 sensor attached to the speficied serial port")
    LOGGING_OUTPUT = ARG_PARSER.add_mutually_exclusive_group()
    LOGGING_OUTPUT.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress most ouput")
    LOGGING_OUTPUT.add_argument(
         "-v",
         "--verbose",
         action="store_true",
         help="Maximum verbosity output on command line")
    ARG_PARSER.add_argument(
       "sensor_port",
        action="store",
        help="Port to which the sensor is connected")
    ARGS = ARG_PARSER.parse_args()
    CONSOLE_LOG_LEVEL = logging.INFO
    if ARGS.quiet:
        CONSOLE_LOG_LEVEL = logging.ERROR
    elif ARGS.verbose:
        CONSOLE_LOG_LEVEL = logging.DEBUG
    
    test(ARGS.sensor_port, CONSOLE_LOG_LEVEL)

