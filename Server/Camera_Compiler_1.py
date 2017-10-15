# -*- coding: utf-8 -*-
"""
Created on Sun Apr 16 15:58:52 2017

@author: Fabian
"""

from line_merge import line_interpreter
import cv2
import numpy as np
from connection_handling import lineQueue

class camera_interpretation(object):
    def __init__(self,cam = "http://192.168.2.110:9090/stream/video.mjpeg"):
        self.cam = cam
        
        #clearfile
        #self.new_file= open("output.txt","w")

    def draw_lines(self,img,lines,color):
        for line in lines:
            coords = line[0]
            cv2.line(img, (int(coords[0]), int(coords[1])), (int(coords[2]), int(coords[3])), color, 3)
    
    def writetofile(self,direction,value):
        """
        Writes to file that gets opened by classTest and interpeted by it
        """
        output = str("{},{} \n".format(direction,value))
        self.new_file.write(output)
        
    def masking(self,img,vertices):
        
        mask = np.zeros_like(img)
        cv2.fillPoly(mask, vertices, 255)
        masked = cv2.bitwise_and(img, mask)
        return masked
    
    def first_processing(self,img):
        """
        MAsks the image; makes it Grey;Blurs it, applies Canny edge detection; 
        and returns lines with HoughLines
        """
        
        processed_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        #cv2.imshow('Balc',processed_img)
        #vertices = np.array([[0,480],[0,200],[640,200], [640,480] ], np.int32)
        #processed_img = self.masking(processed_img,[vertices])
        processed_img =  cv2.Canny(processed_img, threshold1 = 50, threshold2=100)
        processed_img = cv2.GaussianBlur(processed_img,(5,5),0)
        #masking image (only below 200px cheight processing--> no horizont is detected)
        #cv2.imshow('2',processed_img)
        lines = cv2.HoughLinesP(processed_img, 1, np.pi/180, 180,np.array([]),100, 30)
        return lines
        
    def image(self,img):
        #cam = "http://192.168.2.110:9090/stream/video.mjpeg"
        #original_cap = cv2.VideoCapture(self.cam)
        angle = 0.2
        number_lines = 2
        lines = self.first_processing(img)
        #self.draw_lines(img,lines,[240,240,29])
        lm = line_interpreter(lines,angle) #angle @ which is joined
        lines = lm.rem_horizontal_lines(lines)
        self.draw_lines(img,lines,[240,240,29])
        #self.draw_lines(img,lines,[250,240,29])
        lines = lm.merge_same(lines)
        
        #print("Lines @1:",np.shape(lines))
        lines = lm.reduction(number_lines,lines)
        #print(lines)
        #print("Lines @2:",np.shape(lines))
        extend_lines = lm.extend_lines(lines)
        #print("Lines @3:",np.shape(lines))
        orientation_lines = lm.orientation_lines(extend_lines,img)
        direction, value = lm.interpret_orientation(orientation_lines)
        
        lineQueue.write_temp(orientation_lines)
        if lines == None or orientation_lines == None or extend_lines == None:
            lines = np.array([0,0,0,0]).reshape(1,1,4)
        return direction,value,orientation_lines, extend_lines,lines
    
    def process(self,value,direction):
        if int(value) > 50 or int(value)< -50:
            #print(direction)
            if direction ==  "right":
                print("Right")
                return 60,40
            if direction == "left":
                print("left")
                return 40,60
        else:
            return 60,60
    def get_cam(self):
        return self.cam



if __name__ == '__main__':
    """
    For testing without GUI
    """
    camera = camera_interpretation()
    original_cap = cv2.VideoCapture(camera.get_cam())
    
    while True:
        ret,img = original_cap.read()
        direction,value,orientation_lines,extend_lines,lines = camera.image(img)
        #camera.draw_lines(img,lines,[20,240,29])
        camera.draw_lines(img,orientation_lines,[240,240,29])
        camera.draw_lines(img,extend_lines,[240,29,29])
        #print(direction,value)
        cv2.imshow('Window_Original',img)
        
        #print(value)
        #print(direction)
        left_speed, right_speed = camera.process(direction,value)
        #print(left_speed,right_speed)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        print(left_speed, right_speed)
    cv2.destroyAllWindows()
    
    
#        self.draw_lines(img,orientation_lines,[240,240,29])
#        self.draw_lines(img,extend_lines,[240,29,29])
        #draw_lines(img,lines)
#        cv2.imshow('Window_Original',img)
#        cv2.imshow('Processed',processed_img)
        
        #self.new_file.write(str(direction),str(value),+"\n")
#        self.writetofile(direction,value)
#        if cv2.waitKey(1) & 0xFF == ord('q'):
#            break
#        cv2.destroyAllWindows()
        #finally:
         #   self.new_file.close()




#This exists for testing porpuses with an image
#angle = 0.2
#number_lines = 2
#img = cv2.imread('cam.jpg')
#processed_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#processed_img =  cv2.Canny(processed_img, threshold1 = 200, threshold2=300)
#processed_img = cv2.GaussianBlur(processed_img,(5,5),0)
#lines = cv2.HoughLinesP(processed_img, 1, np.pi/180, 180,np.array([]),100, 30)
##print(np.shape(lines))
#
#
#lm = line_merge(lines,angle)
#lines = lm.main_loop()
#
#if lines == None:
#    print("Error Lines Returned NONE")
#    lines = np.array([0,0,0,0]).reshape(1,1,4)
#lines = lm.reduction(number_lines,lines)
#extend_lines = lm.extend_lines(lines,img)
#print(extend_lines)
#orientation_line = lm.orientation_line(img,lines,number_lines)
##print(lines)
##cv2.line(img, (0, 435), (172, 169), [240,29,29], 3)
##ol = oriantation_line()
##orientation_lines()
#cv2.imshow('image_Original_HoughLines',processed_img)
#draw_lines(img,extend_lines)
#cv2.imshow('Processed',img)
#cv2.waitKey(0)
##    
#print(np.shape(lines))
#cv2.destroyAllWindows()
