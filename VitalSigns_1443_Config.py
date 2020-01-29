import serial
import time
import numpy as np
import struct

# ------------------------------------------------------------------
# Function to configure the serial ports and send the data from
# the configuration file to the radar
def alpha_factor(prev_input, current_input, alpha):
        return (alpha*prev_input + (1-alpha)*current_input)

def hex_to_float(dataSrc):
        data = ['{0:08b}'.format(int.from_bytes(s, byteorder='little')) for s in dataSrc]
        data = "".join(data)
        data = int(data,2)
        data = struct.unpack('f', struct.pack('I', data))[0]
        return data


def serialConfig(configFileName):
    
    # Open the serial ports for the configuration and the data ports
    
    # Raspberry pi
    #CLIport = serial.Serial('/dev/ttyACM0', 115200)
    #Dataport = serial.Serial('/dev/ttyACM1', 921600)
    
    # Windows
    CLIport = serial.Serial('COM4', 115200)

    # Read the configuration file and send it to the board
    config = [line.rstrip('\r\n') for line in open(configFileName)]
    for i in config:
        CLIport.write((i+'\n').encode())
        print(i)
        time.sleep(0.01)


def processData(dataBin): #find a way to convert int8 to float, task for 31st Jul
    # Alter to x-byte data in array form 1 byte/element
#     dataBinproc = [int(i,8) for i in dataBin ]
    
    breathFFT = dataBin[100:104]
    breathFFT = breathFFT[::-1]
    heartFFT  = dataBin[76:80]
    heartFFT  = heartFFT[::-1]
    motion_flag = dataBin[132:136]
    motion_flag = motion_flag[::-1]

    dynVar = dataBin[128:132]
    dynVar = dynVar[::-1]

    
    heartFFT  = hex_to_float(heartFFT)
    breathFFT = hex_to_float(breathFFT)
    motion_flag = hex_to_float(motion_flag)
    dynVar = hex_to_float(dynVar)
    
    return breathFFT, heartFFT, motion_flag, dynVar

def readAndParseData(dataBin, Dataport): # Generates a running queue of data (FIFO), newest data gets appended and oldest data gets pushed out
    readBuffer = Dataport.read()
    dataBin = dataBin[1:]
    dataBin.append(readBuffer)
    return dataBin

    



# -------------------------    MAIN   -----------------------------------------  

# Configurate the serial port
# CLIport, Dataport = serialConfig(configFileName)

# print("reading")

# while True:
#     print(Dataport.in_waiting)
#     if Dataport.in_waiting > 0:
#         try:
#             readAndParseData(dataBin, Dataport)

#             if dataBin[0:8] == magicWord:
#                 breathFFT, heartFFT = processData(dataBin)
            
#                 print(breathFFT,heartFFT)
        
#         except KeyboardInterrupt:
#             CLIport.write(('sensorStop\n').encode())
#             CLIport.close()
#             Dataport.close()
    # else:
    #     print("Nothing Read")


