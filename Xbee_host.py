import matplotlib.pyplot as plt
import serial
import paho.mqtt.client as paho
import time
import numpy as np
mqttc = paho.Client()

# Settings for connection
host = "172.16.181.136"
topic= "Mbed"
port = 1883

# Callbacks
def on_connect(self, mosq, obj, rc):
    print("Connected rc: " + str(rc))

def on_message(mosq, obj, msg):
    print("[Received] Topic: " + msg.topic + ", Message: " + str(msg.payload) + "\n");

def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed OK")

def on_unsubscribe(mosq, obj, mid, granted_qos):
    print("Unsubscribed OK")

# Set callbacks
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
mqttc.on_unsubscribe = on_unsubscribe

# Connect and subscribe
print("Connecting to " + host + "/" + topic)
mqttc.connect(host, port=1883, keepalive=60)
mqttc.subscribe(topic, 0)

# XBee setting
serdev = '/dev/ttyUSB0'
s = serial.Serial(serdev, 9600)

s.write("+++".encode())
char = s.read(2)
print("Enter AT mode.")
print(char.decode())

s.write("ATMY 0x140\r\n".encode())
char = s.read(3)
print("Set MY 0x140.")
print(char.decode())

s.write("ATDL 0x240\r\n".encode())
char = s.read(3)
print("Set DL 0x240.")
print(char.decode())

s.write("ATID 0x1\r\n".encode())
char = s.read(3)
print("Set PAN ID 0x1.")
print(char.decode())

s.write("ATWR\r\n".encode())
char = s.read(3)
print("Write config.")
print(char.decode())

s.write("ATMY\r\n".encode())
char = s.read(4)
print("MY :")
print(char.decode())

s.write("ATDL\r\n".encode())
char = s.read(4)
print("DL : ")
print(char.decode())

s.write("ATCN\r\n".encode())
char = s.read(3)
print("Exit AT mode.")
print(char.decode())

print("start sending RPC")

t = np.arange(0,20,1)
collectednumber = np.arange(0,20,1)
X = np.arange(0,2,0.1)
Y = np.arange(0,2,0.1)
Z = np.arange(0,2,0.1)

'''
while True:
    mesg = "1"
    mqttc.publish(topic, mesg)
    print(mesg)
    time.sleep(1)
'''

s.write("\r".encode())
time.sleep(1)

for i in range(21):
    # send RPC to remote
    s.write("/getnumber/run\r".encode())
    
    char = s.readline()
    charnumber = char[27:30]
    charx = char[0:9]
    if i>0:
        X[i-1] = float(charx)
    chary = char[9:18]
    if i>0:
        Y[i-1] = float(chary)
    charz = char[18:27]
    if i>0:
        Z[i-1] = float(charz)
    if i>0:
        if abs(X[i-1])>0.5 or abs(Y[i-1])>0.5:
            mesg = "1"
            mqttc.publish(topic, mesg)
            print(mesg+"\n")
        else :
            mesg = "0"
            mqttc.publish(topic, mesg)
            print(mesg+"\n")

    print(char.decode())
    if i>0:
        collectednumber[i-1] = int(charnumber)
        
        
   

    time.sleep(1)

#for i in range(20):
  #  print(collectednumber[i] )
#for i in range(20):
 #   print(X[i] )
#for i in range(20):
  #  print(Y[i] )

fig, ax = plt.subplots(2, 1)

ax[0].plot(t,X,t,Y,t,Z)

ax[0].legend(('x','y','z'))

ax[0].set_xlabel('Time')

ax[0].set_ylabel('Acc Vector')

ax[1].plot(t,collectednumber) # plotting the spectrum

ax[1].set_xlabel('timestamp')

ax[1].set_ylabel('number')

plt.show()



s.close()