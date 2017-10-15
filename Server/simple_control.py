# -*- coding: utf-8 -*-
"""
Created on Thu May  4 12:25:14 2017

@author: Fabian
"""
import gopigo
import random
from time import *

from connection_handling import connection
from movement_handling import movement

class remote_c(object):
    """
    Data gets send and RPI acts according to it
    """
    def __init__(self,con,data_type,data):
        #start connection
        self.con = con
        self.data_type = data_type
        self.data = data
        
    def main(self):
        """
        Runs remote
        """
        data_type = self.data_type
        data = self.data
        mov = movement()
        
        while data_type == "remote_control":
            data_type = "remote_control"
            data_split = data[1:-1]
            data_split = data_split.split(",")
            mov.main(int(data_split[0]),int(data_split[1]))
            data, data_type = self.con.dataQ.read_temp()
            if data_type != "remote_control":
                return data, data_type

            
class UV_c(object):
    """
    IF controll name is wrong^^
    """
    def __init__(self,con,data_type):
    #start connection
        self.con = con
        self.data_type = data_type
        
    def main(self):
        """
        UV controll main
        first turn is random after the first one all subsequent turn in direct row are qual to the first one
        already moved checks if above applies
        """
        print("Executing UV_control")
        mov = movement()
        data_type = self.data_type
        min_distance = 50
        fast_distance = 50
        alreadymoved = True
        while True:
            #if dataQ is not zero checking if new command
            if self.con.dataQ.get_qsize() != 0:
                
                data, data_type = self.con.dataQ.read_temp()
            if data_type != "UV_control":
                break
            
            distance = gopigo.us_dist(15)
            
            if distance > min_distance or distance == 0:    
                mov.main(120,120)
                alreadymoved = True
            if distance > fast_distance or distance == 0:    
                mov.main(180,180)
                alreadymoved = True
            else:
                gopigo.stop()
                sleep(0.5)
                if alreadymoved == True:    
                    LoR = random.randrange(1,3)
                if LoR == 1: 
                    gopigo.left_rot()
                    alreadymoved = False
                else: 
                    gopigo.right_rot()
                    alreadymoved = False

                sleep(0.3)
                gopigo.stop()
                continue
            
        return data,data_type
        
    
            
        
