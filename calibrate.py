
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
 #make socket non blocking
s.setblocking(0)
 
def recv_timeout(timeout=1):
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
            data = s.recv(8192)
            if data:
                total_data.append(data)
        except:
            pass

    return ''.join(total_data)
 
recv_timeout(0.1) # To ignore the first input
Y = raw_input('Distance from Tag to antenna in Y: ')
raw_input('\nPut the tag to position of 1 antenna to get Initial phase and Press enter to continue: ')
recv_timeout(0.1)# to flush the previous data
info_calibrate = recv_timeout(1.5)
if info_calibrate:
    phases_init = []
    print "calibrate information\n" + info_calibrate
    for line in info_calibrate.splitlines():
        EPC, temps, RSSI, count, ant, freq, phase = (item.strip() for item in line.split('\t'))
        phases_init.append(int(phase))  
    print "phases_init: " + str(phases_init)
    phase_init = int(np.median(phases_init))
    print "Data Counts: " + str(len(phases_init))
    print "average of calibrated phase: " + str(phase_init)
phase_n_1 = phase_init
phase_n  = phase_init

while 1:
    command = raw_input(" \n- choose the command (r:read, e:exit) ")
    if command == 'r':
        X = raw_input('Distance from Tag to antenna in X:   ')
        timestr = time.strftime("%Y%m%d-%H%M%S-")
        file = open(timestr + 'Y-' + Y + '-X-' + X + '.csv',"w")
        phases = []
        recv_timeout(0.1)# to flush the previous data
        input_file = recv_timeout(1.5)
        if input_file:
            print input_file
            for line in input_file.splitlines():
                EPC, temps, RSSI, count, ant, freq, phase = (item.strip() for item in line.split('\t'))
                phases.append(int(phase)-phase_init)
            print "phase_initial:  " + str(phase_init)
            print "phases - phases_initial:  " + str(phases)
            print "Data Counts: " + str(len(phases))
            file.write(str(phases)[1:-1])
            print "average delta phase: " + str(int(np.median(phases)))
    if command == 'e':
        print "\nFinish Getting Data"   
        file.close()
        s.close()
        break

