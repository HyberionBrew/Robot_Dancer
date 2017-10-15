# -*- coding: utf-8 -*-
"""
Created on Tue May 30 09:43:22 2017

@author: Fabian
"""

import numpy as np
import cv2
from line_merge import line_interpreter

#from movement_handling import movement
from connection_handling import connection

class VisionAlgorithm(object):
    
    def __init__(self,con):
        self.con = con
        self.i = 1
        self.img = self.get_img()
        self.width = int(tuple(np.shape(self.img))[1])
        self.height = int(tuple(np.shape(self.img))[0])

    def masking(self,img):
        img = img[self.height/2:self.height,0:self.width]
        #cv2.imshow('2',img)
        return img
    
    def post_processing(self,img):
        crop_img = self.masking(img)
        gray_image = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
        #cv2.imshow('1',gray_image)
        
        equ_img = cv2.equalizeHist(gray_image)
        blur = cv2.GaussianBlur(equ_img,(5,5),0)
        #cv2.imshow('2',blur)
        post_processed_img = cv2.Canny(blur,80,150)
        return post_processed_img
    
    def extend_lines_VA(self,lines,lm):
        new_lines = []
        for line in lines:
            x = lm.extend_line(line,self.height/2)
            x[1] = x[1] + self.height/2
            x[3] = x[3] + self.height/2
            new_lines.append(x)
        new_lines_n = np.array(new_lines)
        number_lines  = np.shape(new_lines_n)[0]
        new_lines_n = new_lines_n.reshape(number_lines,1,4)
        return new_lines_n,new_lines
    
    def main(self):
        i = 0
        while True:
            
            img = self.img
            self.post_processed = self.post_processing(img)
            minLineLength = 80
            maxLineGap = 30
            lines = cv2.HoughLinesP(self.post_processed,1,np.pi/180,20,minLineLength,maxLineGap)
            if lines == None:
                print("No lines")
                lines = np.array([0,0,0,0]).reshape(1,1,4)
            #print(lines)
            lm = line_interpreter(lines,0.3)
            lines = lm.merge_same(lines)
            #y_axis = np.array([[0,0,self.width,0]]) 
            new_lines_n,new_lines = self.extend_lines_VA(lines,lm)
            
            indicator = 0
            for line in new_lines:
                cv2.line(img,(int(line[0]),int(line[1]+self.height/2)),(int(line[2]),int(line[3]+self.height/2)),(255,255,0),3)
                indicator +=  (int(line[0])-int(line[2]))
                
            #print(indicator)
            try:
                #this is used for consitency (AM is taken of the last 5 measuerements) 
                #it is getting acted according to those
                if indicator < 700 or indicator > - 700:
                    prev_indicators.append(indicator)
                self.indicator_Am = sum(prev_indicators)/len(prev_indicators)
                i += 1
                if i == 5:
                    print(self.indicator_Am)
                    i = 0
                if len(prev_indicators) == 10:
                    prev_indicators = prev_indicators[1:]
                    #if there are already some measuerements remove the first one
            except NameError:
                prev_indicators = [indicator]
                
            self.con.lineQueue.write_temp(lines)
            self.img = self.get_img()

#    def Test_Unit(self):
#        print("Called")
#        for i in range(1,7):
#            self.i = i
#            print(i)
#            self.main()
#            cv2.imshow('Window_Original',self.img)
#            cv2.waitKey(0)
#        cv2.destroyAllWindows()
    
    def get_img(self):
        return self.con.get_frame()
        
#if __name__ == "__main__":
#    VA = VisionAlgorithm()
#    VA.Test_Unit()
    