from line_merge import line_interpreter
import cv2
import numpy as np
from movement_handling import movement

from connection_handling import connection
#from connection_handling import coonection

class image_c1(object):
    """
    Works with line_interpreter
    """
    def __init__(self,con):

        self.angle = 0.2
        self.number_lines = 2
        self.mov = movement()
        self.con = con
        
    def first_processing(self,processed_img):
        """
        MAsks the image; makes it Grey;Blurs it, applies Canny edge detection; 
        and returns lines with HoughLines
        """
        
        #processed_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        processed_img =  cv2.Canny(processed_img, threshold1 = 50, threshold2=200)
        processed_img = cv2.GaussianBlur(processed_img,(5,5),0)
        lines = cv2.HoughLinesP(processed_img, 1, np.pi/180, 180,np.array([]),20, 10)
        return lines
    
    def new_move(self,value,direction):
        if int(value) > 50 or int(value)< -50:
            #print(direction)
            if direction ==  "right":
                print("Right")
                self.mov.main(60,40)
            if direction == "left":
                print("left")
                self.mov.main(40,60)
        else:
            return 60,60
    def main(self):
#        try:
        """
        if i find time i get my first tryy also working :)
        (it worked on a little bit different overall server/client architecture, however it isnt to good @ finding correct lanes)
        especially in difficult lighning image_c2 should make this better
        """
        while True:
            
            img = self.con.get_frame()
            #print(img)
            #np.resize(img,)
            ##img = cv2.resize(img,(640, 480), interpolation = cv2.INTER_CUBIC)
            lines = self.first_processing(img)
            print("1",lines)
            lm = line_interpreter(lines,self.angle)
        #            lines = lm.rem_horizontal_lines(lines)
            print("2",lines)
        #            lines = lm.merge_same(lines)
            print("3",lines)
        #            lines = lm.reduction(self.number_lines,lines)
        #            extend_lines = lm.extend_lines(lines)
            #print("4",extend_lines)
        #            orientation_lines = lm.orientation_lines(extend_lines,img)
        #            print(orientation_lines)
            #send lines to client
        #            direction, value = lm.interpret_orientation(orientation_lines)
        #            if lines == None or orientation_lines == None or extend_lines == None:
        #                print("Got no lines,possible blurred")
        #                lines = np.array([0,0,0,0]).reshape(1,1,4)
        #            self.new_move(value,direction)
           # lines = lines + orientation_lines
            self.con.lineQueue.write_temp(lines)
            
            if self.con.dataQ.get_qsize() != 0:
                data, data_type = self.con.dataQ.read_temp()
                if data_type != "image_control_1":
                    return data, data_type
#        except:
#            return 0
