# Sensirion SPS03 Particulate Sensor Python interface
A basic python interface for interacting with the Sensirion SPS030 Particulate Matter sensor.  This code has been tested with the following devices: SPS030.
 
This wrapper is based on: https://github.com/FEEprojects/plantower

This wrapper has been developped as part of on-going work on the use of low-cost PM sensors to monitor air quality in urban areas.

The test.py script can be used to test that the sensor is working. If the sensor is plugged on /dev/ttyUSB0, then 
`python3 test.py /dev/ttyUSB0` will output:
```2019-11-15 14:48:28,222 - SPS030 Interface - 105 - INFO - Serial port: /dev/ttyUSB0
2019-11-15 14:48:28,223 - SPS030 Interface - 107 - INFO - Baud rate: 115200
2019-11-15 14:48:28,224 - SPS030 Interface - 109 - INFO - Serial Timeout: 2
2019-11-15 14:48:28,224 - SPS030 Interface - 111 - INFO - Read Timeout: 1
2019-11-15 14:48:28,225 - SPS030 Interface - 113 - INFO - Retries: 3
2019-11-15 14:48:28,291 - SPS030 Interface - 323 - WARNING - Trying to read too frequently - forcing delay
2019-11-15 14:48:29,308 - SPS030 Interface - 15 - INFO - reading: 2019-11-15 14:48:29, 3.3, 3.4, 3.4, 3.4, 24.1, 27.5, 27.6, 27.6, 27.6, 0.3
```

`python3 test.py /dev/ttyUSB0 -v` will output additional debugging messages.


The following persons have contributed to this library:
 * Philip J. Basford
 * Florentin M. J. Bulot
 * Simon J. Cox
 * Steven J. J. Ossont
