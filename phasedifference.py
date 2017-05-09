#Socket client example in python
 
import socket   #for sockets
import sys  #for exit
import struct
import time
import numpy as np
from math import pow, sqrt
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

C = 2.15 # F1F2 = 2C
lamda = 34.65 # wave length 3*10^8/865700

raw_input('\nPut the tag to the middle of 2 antenna to calibrate ')
recv_timeout(0.1)
info_calibrate = recv_timeout(1.5)
if info_calibrate:
    print info_calibrate
    phases_1_calib = []
    phases_2_calib = []
    for line in info_calibrate.splitlines():
        EPC, temps, RSSI, count, ant, freq, phase = (item.strip() for item in line.split('\t'))
        if int(ant) == 1:
            phases_1_calib.append(int(phase))
        elif int(ant) == 2:
            phases_2_calib.append(int(phase))  
    print "phases ant 1: " + str(phases_1_calib)
    print "\nphases ant 2: " + str(phases_2_calib)
    delta_phase_cal = [a_i - b_i for a_i, b_i in zip(phases_1_calib,  phases_2_calib)]
    offset = round(np.median(delta_phase_cal))
    print str(len(delta_phase_cal)) + " delta phase: " + str(delta_phase_cal) 
    print "average offset: " + str(offset) + '\n'

while 1:
    command = raw_input(" \n- choose the command (r:read, e:exit) ")
    if command == 'r':
        Y = raw_input('Distance from Tag to antenna in Y: ')
        Y = int(Y)
        X = raw_input('Distance from Tag to antenna in X: ')
        X = int(X)
        # Theoretical Value
        MF1 = sqrt(pow(Y,2)+pow(X-C,2))
        MF2 = sqrt(pow(Y,2)+pow(X+C,2))
        delta_distance_theo = MF1-MF2
        delta_phase_theo = delta_distance_theo*4*180/lamda

        phases_1 = []
        phases_2 = []
        delta_phase = []
        recv_timeout(0.1) # Flush the buffer
        input_file = recv_timeout(3)
        if input_file:
            print input_file
            for line in input_file.splitlines():
                EPC, temps, RSSI, count, ant, freq, phase = (item.strip() for item in line.split('\t'))
                if int(ant) == 1:
                    phases_1.append(int(phase))
                elif int(ant) == 2:
                    phases_2.append(int(phase))  
            print "phases ant 1: " + str(phases_1)
            print "\nphases ant 2: " + str(phases_2)
            print "\nTheoretial value of delta phase: " + str(round(delta_phase_theo)) + '\n'
            delta_phase = [a_i - b_i for a_i, b_i in zip(phases_1,  phases_2)]
            print str(len(delta_phase)) + " delta phase: " + str(delta_phase) 
            print "Offset: " + str(offset) + '\n'
            print "average delta phase: " + str(int(np.median(delta_phase))-offset) + '\n'
            save_data = raw_input('Do you want to save this data: (y:yes,n:no)  ')
            if save_data=='y':
                timestr = time.strftime("%Y%m%d-%H%M%S-")
                file = open('2ant-' + timestr + 'Y-' + str(Y) + '-X-' + str(X) + '.csv',"w")
                file.write('phases 1, ' + str(phases_1)[1:-1] + '\n')
                file.write('phases 2, ' + str(phases_2)[1:-1] + '\n')
                file.write('Theoretical, ' + str(round(delta_phase_theo)) + '\n')
                file.write('Offset, ' + str(offset) + '\n')
                file.write('average delta phase, ' + str(int(np.median(delta_phase))-offset) + '\n')
                file.write('delta_phase, ' + str(delta_phase)[1:-1])
                file.close()
    if command == 'e':
        print "\nFinish Getting Data"   
        s.close()
        break

