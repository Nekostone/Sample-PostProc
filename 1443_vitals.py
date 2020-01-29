import serial
import time
import numpy as np
from VitalreadAndParseDataSigns_1443 import , processData, serialConfig, alpha_factor

# Parse config file into CLI to activate sensor
serialConfig('profile_2d_VitalSigns_20fps.cfg')

time.sleep(5)

byteBuffer = np.zeros(2**15,dtype = 'uint8')
byteBufferLength = 0
dataBin = [None] * 288

breath_alpha = 0.5
heart_alpha = 0.2

breath_prev = 0
heart_prev = 0

magicWord = [2, 1, 4, 3, 6, 5, 8, 7]
magicWord = [bytes([i]) for i in magicWord]

Dataport = serial.Serial('COM5', 921600)

current = time.time()
state = ''
activation = 0

# Calibration/Stability monitor
count = 0

while True:
    # if activation == 1 or state == 'scan':
    dataBin = readAndParseData(dataBin, Dataport)

    # If first 8 bytes match magic word, process data
    if dataBin[0:8] == magicWord:
        breathFFT, heartFFT, motion_flag, dynVar = processData(dataBin)

        # Perform exponential smoothening to filter high-frequency noise
        breathFFT = round(alpha_factor(breath_prev, breathFFT, breath_alpha))
        heartFFT  = round(alpha_factor(heart_prev, heartFFT, heart_alpha))
        motion_flag = round(motion_flag)

        if motion_flag == 0: 
            if abs(current - time.time()) < 0.6 and abs(current - time.time()) > 0.4:
                # print("Difference: " + str(abs(heartFFT-heart_prev)))
                if heartFFT <= heart_prev + 4 and heartFFT >= heart_prev - 4 and heartFFT >= 60:
                    if count < 10:
                        print("Calibrating." + count*".")
                    count += 1
                    current = time.time()
                    if count >= 10:
                        print("BreathFFT: " + str(breathFFT))
                        print("HeartFFT: " + str(heartFFT))
                        print("Motion Flag: " + str(motion_flag) + "\n")
                        print("Dynamic Var: " + str(dynVar) + "\n")
                else:
                    count = 0
                    print("Count: " + str(count) + "\n")
                    current = time.time()
                [breath_prev, heart_prev] = [breathFFT, heartFFT]

        elif motion_flag == 1:
            if abs(current - time.time()) < 0.6 and abs(current - time.time()) > 0.4:
                print("BreathFFT: --")
                print("HeartFFT: --")
                print("Motion Flag: " + str(motion_flag) + "\n")
                print("Dynamic Var: " + str(dynVar) + "\n")
                current = time.time()
                count = 0
            None
        # time.sleep(0.05)
    # elif activation == 0 and state == 'scan':
        # state = 'inactive'
    # else:
    #     continue