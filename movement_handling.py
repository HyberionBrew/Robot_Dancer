# -*- coding: utf-8 -*-
"""
Created on Thu May  4 12:52:12 2017

@author: Fabian
"""
import gopigo
import atexit
from gopigo import *
import time

class movement(object):
    def __init__(self):
        gopigo.stop()
        atexit.register(gopigo.stop)
    
    def main(self,motor1,motor2):
        """
        Takes in 2 ints and rotates accordingly
        """
        gopigo.set_left_speed(motor1)
        gopigo.set_right_speed(motor2)
        
        if motor1 >= 0 and motor2 >= 0:
            
            gopigo.fwd()
        else:
            gopigo.bwd()
    def stop(self):
        gopigo.stop()

class InterpretLines(movement):
    """
    This class takes in 
    """
    def __init__(self):
        self.prevMoves = []
#        Logfile = open("LOGFILE.txt","w+")
#        Logfile.write("LETS GO")
#        Logfile.close()
#        Logfile = open("LOGFILE2.txt","w+")
#        Logfile.write("LETS GO")
#        Logfile.close()
        
    def currMov(self,lines,height,width):
        
        if lines == None:
            move = self.calcFromPrev()    
        else:
            print("Normal")
            move = self.interpretLines(lines,height,width)
#            print("MOVE: ",move)
            self.prevMoves.append(move)
            try:
                fp = open('logfile.dat','a')
            except IOError:
                print("CREATED FILE")
                fp = open('logfile.dat','a+')
            string = str(move[0])+str(",")+str(move[1])+str("|")+str(time.time())
            fp.write(string+"\n")
            print("WROTE",move)
            fp.close()
        
#        LOGFILE = open("LOGFILE2.txt","w+")
#        LOGFILE.write(str(move))
#        LOGFILE.close()   
        self.main(move[0],move[1])
        
    def initLog(self,filename):
        Logfile = open(filename,"w")
        Logfile.write("LETS GO")
        Logfile.close()
    def createLog(self,filename,move):
        
        LOGFILE = open(filename,"a")
        LOGFILE.write(str(move))
        LOGFILE.close()
        
        
    def calcFromPrev(self):
        #first look if there are Prev moves
        prevLeft = []
        prevRight = []
        if len(self.prevMoves) > 2:
            prev = self.prevMoves[-3:]
            for i in prev:
                prevLeft.append(i[0])
                prevRight.append(i[1])
            newLeft = sum(prevLeft)//3 
            newRight = sum(prevRight)//3
            return (newLeft,newRight)
        else:
            
            return (0,0)
            
            
            
    def interpretLines(self,lines,height,width):
        value = 0
        diff = 0
        for line in lines:
            line = line[0]
            diff = line[0]-line[2]
            #value @ the end  signals what direction the lanes are facing (if both are left then go left....etc.)
            if diff >= 0:
                #lane is right leaning 
                value += 1
            elif diff < 0:
                #lane is left leaning \
                value -= 1
        #if both lanes face in different direction e.g. they are straight (perspective!) value = 0
#        print("VALUE IS ", value)
        if value == 0:
            #calc the crossingPoint of the lanes and use this to determine the new diection
            x11 = lines[0][0][0]
            x12 = lines[0][0][2]
            x21 = lines[1][0][0]
            x22 = lines[1][0][2]
            # P + s * X  = P + t *X"
            # x11 + s *(x12-x11) = x21 + s *(x22-x21)
            # s *(x12-x11) - s *(x22-x21) = x21 -x11
            # 0 + s* (200-0) = 0 + t *(200-0)
            s = (x21-x11) /((x12 -x11) - (x22-x21))
            X = x11 + s *(x12-x11) 
#            print("X is @ ",X)
            offset = width//6
            if ((width//2) -offset)> X:
                #left side
                print("LEFTS",(width//2) -offset)
                return (100,80)
            elif ((width//2)+offset)>X:
                print("RightS",(width//2) -offset)
                return (80,100)
            else:
                return (80,80)
            
        if abs(value) == 1:
            #has to be only one lane new
            line = lines[0][0]
            middleLine = [line[0],0, line[0],height]
            botDiff = middleLine[2]-line[2]
            if abs(botDiff) < 150:
                print("Straight")
                return (80,80)
        if value >= 1:
            print("left")
            return (50,100)
        elif value <= -1:
            print("right")
            return (100,50)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        