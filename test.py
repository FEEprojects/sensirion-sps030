import sensirion_sps030
from time import sleep


RX_DELAY_S = 0.02 

SPS030 = sensirion_sps030.Sensirion(
	port="/dev/ttyUSB_SPS030-60762402-3", log_level="DEBUG")

SPS030.sensirion_start_measurement()
SPS030._sensirion_tx(b'\x00', b'\x03')
sleep(RX_DELAY_S)
mess=SPS030.serial.read(30)

print(mess)

