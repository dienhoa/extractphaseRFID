#Socket client example in python
 
import socket   #for sockets
import sys  #for exit
import struct
import time
 
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
 
# EPCs, times, RSSIs, counts, ants, freqs, phases_1, phases_2 = ([] for i in range(8))
recv_timeout(s) # To ignore the first input
while 1:
    try:
        phases_1 = []
        phases_2 = []
        delta_phase = []
        input_file = recv_timeout(s)
        if input_file:
            print input_file
            for line in input_file.splitlines():
                EPC, temps, RSSI, count, ant, freq, phase = (item.strip() for item in line.split('\t'))
                if int(ant) == 1:
                    phases_1.append(int(phase))
                elif int(ant) == 2:
                    phases_2.append(int(phase))  
            print "phases ant 1: " + str(phases_1)
            print "phases ant 2: " + str(phases_2)
            delta_phase = [a_i - b_i for a_i, b_i in zip(phases_1, phases_2)]
            print str(len(delta_phase)) + " delta phase: " + str(delta_phase) 
    except KeyboardInterrupt:
        print "KeyboardInterrupt"   
        s.close()
        break

