# -*- coding: utf-8 -*-
"""
Created on Thu May  4 11:48:35 2017

@author: Fabian
"""
import time
from threading import Thread
from connection_handling import connection#,StreamVideo
from simple_control import remote_c,UV_c
from image_control import image_c1
from VisionAlgorithm_main import VisionAlgorithm
from VisionAlgorithm_4 import VisionAlgorithm4


HOST = "192.168.0.11"#
PORT = 8889
#create connection
con = connection(HOST,PORT)
print("Trying to connect to client!")
vb = con.connection_start()
print("Connection sucessfull")
#start streaming to client, current frame gets outputed to con.get_frame()
streamThread = Thread(target = con.send_stream).start()
#start listening for commands, commands get outputed to con.dataQ()
receiveThread = Thread(target = con.receive).start()

#try:
while True:
    if con.dataQ.get_qsize() != 0:
        #if queue is not empty, do this
        msg = con.dataQ.read_temp()
        data,data_type = msg    
        print("Received:{}{}".format(data,data_type))
        
        if data_type == "remote_control":
            rem = remote_c(con,data_type,data)
            data, data_type = rem.main()
            
        if data_type == "UV_control":
            UV = UV_c(con,data_type)
            data, data_type = UV.main()
        
#        if data_type == "image_control_1":
#            visual1 = image_c1(con)
#            data_data_type = visual1.main()
        if data_type == "image_control_1":
            VisionAlgorithm4 = VisionAlgorithm4(15,con)
            data_data_type = VisionAlgorithm4.main()
        if data_type == "image_control_2":
            visual2 = VisionAlgorithm(con)
            data_data_type = visual2.main()
            
        if data_type == "close":
            #not functional
            vb.close()

    else:
        continue
con.receive_send.change_receiving()
con.receive_send.change_sending()
time.sleep(0.2)
vb.close()

#except KeyboardInterrupt:
#    print("KeyboardInterrupt")
    #vb.close()
#except:
#    print("Something else went wrong".format(sys.exc_info()[0]))
#finally:
#    print("Finally")
#    vb.close()
