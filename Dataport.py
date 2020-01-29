import serial
import time
import numpy as np
from VitalSigns_1443 import readAndParseData, processData, serialConfig, alpha_factor

# Parse config file into CLI to activate sensor
serialConfig('profile_2d_VitalSigns_20fps.cfg')

time.sleep(5)

byteBuffer = np.zeros(2**15,dtype = 'uint8')
byteBufferLength = 0;
dataBin = [None] * 288

breath_alpha = 0.5
heart_alpha = 0.5

breath_prev = 0
heart_prev = 0

magicWord = [2, 1, 4, 3, 6, 5, 8, 7]
magicWord = [bytes([i]) for i in magicWord]

Dataport = serial.Serial('COM5', 921600)

while True:
    dataBin = readAndParseData(dataBin, Dataport)

    # If first 8 bytes match magic word, process data
    if dataBin[0:8] == magicWord:

        breathFFT, heartFFT = processData(dataBin)

        # Perform exponential smoothening to filter high-frequency noise
        breathFFT = round(alpha_factor(breath_prev, breathFFT, breath_alpha))
        heartFFT  = round(alpha_factor(heart_prev, heartFFT, heart_alpha))

        print("BreathFFT: " + str(breathFFT))
        print(type(breathFFT))
        print("\nHeartFFT: " + str(heartFFT))

        [breath_prev, heart_prev] = [breathFFT, heartFFT]
        # time.sleep(0.05)