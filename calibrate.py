#Socket client example in python
 
import socket   #for sockets
import sys  #for exit
import struct
import time
import numpy as np

#create an INET, STREAMing socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # default socket family and type, can lelf it blank  
except socket.error:
    print 'Failed to create socket'
    sys.exit()
     
print 'Socket Created'
 
host = socket.gethostname()
port = 9055;

try:
    remote_ip = socket.gethostbyname( host )
 
except socket.gaierror:
    #could not resolve
    print 'Hostname could not be resolved. Exiting'
    sys.exit()
 
#Connect to remote server
s.connect((remote_ip , port))
 
print 'Socket Connected to ' + host + ' on ip ' + remote_ip + ' at port ' + str(port)
 
 
def recv_timeout(the_socket,timeout=1):
    #make socket non blocking
    the_socket.setblocking(0)
     
    #total data partwise in an array
    total_data=[];
    data='';
     
    #beginning time
    begin=time.time()
    while 1:
        #if you got some data, then break after timeout
        if ((time.time()-begin) > timeout):
            break
        #recv something
        try:
            data = the_socket.recv(8192)
            if data:
                total_data.append(data)
        except:
            pass

    return ''.join(total_data)
 
recv_timeout(s) # To ignore the first input

raw_input('Put the tag to position of 1 antenna and Press enter to continue: ')
info_calibrate = recv_timeout(s)
if info_calibrate:
    phases_calib = []
    print "calibrate information\n" + info_calibrate
    for line in info_calibrate.splitlines():
        EPC, temps, RSSI, count, ant, freq, phase = (item.strip() for item in line.split('\t'))
        phases_calib.append(int(phase))  
    print "phases_calib: " + str(phases_calib)
    phase_calib = int(np.mean(phases_calib))
    print "average of calibrated phase: " + str(phase_calib)

raw_input('Put the tag to the position you want to calibrate')

while 1:
    try:
        phases = []
        input_file = recv_timeout(s)
        if input_file:
            print input_file
            for line in input_file.splitlines():
                EPC, temps, RSSI, count, ant, freq, phase = (item.strip() for item in line.split('\t'))
                phases.append(int(phase)-phase_calib)  
            print "phases - phases_calib:  " + str(phases)
    except KeyboardInterrupt:
        print "KeyboardInterrupt"   
        s.close()
        break

