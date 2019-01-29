import sensirion_sps030

SPS030 = sensirion_sps030.Sensirion(port="/dev/ttyUSB_SPS030-60762402-3",log_level="DEBUG")

SPS030.sensirion_start_measurement()
print(SPS030.sensirion_read_measurement())
