import serial
import time
ser=serial.Serial('/dev/ttyUSB0',baudrate=9600,timeout=1)


buf = '/1A15000R\r'
ser.write(buf.encode('utf-8'))
time.sleep(1)
readedText = ser.readline()
print(readedText.decode('utf-8'))
ser.close()