
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
 
recv_timeout(0.1) # To ignore the first input
Y = raw_input('Distance from Tag to antenna in Y: ')
Y = int(Y)
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

C = 2.15 # F1F2 = 2C
lamda = 32.0 # wave length 3*10^8/865700 34.65

while 1:
    command = raw_input(" \n- choose the command (r:read, e:exit) ")
    if command == 'r':
        X = raw_input('Distance from Tag to antenna in X:   ')
        X = int(X)
        # Theoretical calculation
        Distance = sqrt(pow(Y,2)+pow(X,2))-Y
        Phase_theoretical = 4*180*Distance/lamda
        delta_phases = []
        phases = []
        recv_timeout(0.1)# to flush the previous data
        input_file = recv_timeout(1.5)
        if input_file:
            print input_file
            for line in input_file.splitlines():
                EPC, temps, RSSI, count, ant, freq, phase = (item.strip() for item in line.split('\t'))
                phases.append(int(phase))
                delta_phases.append(int(phase)-phase_init)
            print "phase_initial:  " + str(phase_init)
            print "phases - phases_initial:  " + str(delta_phases)
            print "Data Counts: " + str(len(delta_phases))
            print "Theoretical value of delta phase:  " + str(round(Phase_theoretical))
            print "average delta phase: " + str(int(np.median(delta_phases)))
            save_data = raw_input('Do you want to save this data: (y:yes,n:no)  ')
            if save_data=='y':
                timestr = time.strftime("%Y%m%d-%H%M%S-")
                file = open('1ant-' + timestr + 'Y-' + str(Y) + '-X-' + str(X) + '.csv',"w")
                file.write('phases, ' + str(phases)[1:-1] + '\n')
                file.write('phases_initial, '+ str(phase_init) + '\n')
                file.write('Theoretical, ' + str(round(Phase_theoretical)) + '\n')
                file.write('average delta phase, ' + str(int(np.median(delta_phases)) + '\n')
                file.write('delta_phase, ' + str(delta_phases)[1:-1])
                file.close()
    if command == 'e':
        print "\nFinish Getting Data"   
        s.close()
        break

