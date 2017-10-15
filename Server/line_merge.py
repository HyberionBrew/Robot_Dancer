# -*- coding: utf-8 -*-
"""
Created on Sun Apr 16 15:10:35 2017

@author: Fabian
"""
import math
import numpy as np
import sys
import cv2
import time

class line_interpreter(object):
    
    def __init__(self,lines,angle):
        """
        Takes in lines
        """
        self.lines = lines
        self.angle = angle
        #self.main_loop()
        self.width = 240
        self.height = 200
        
        
        
    def create_vector(self,line):
        X = line[0][0]-line[0][2]
        Y = line[0][1]-line[0][3]
        return X,Y
    
    def lenght_vector(self,x,y):
        return math.sqrt((abs(x)**2) + (abs(y)**2))
    
    def normalize_vector(self,x,y):
        len_vector = self.lenght_vector(x,y)
        x = x / len_vector
        y = y / len_vector
        return x,y
    
    def delete_old_lines(self,lines,i1,i2):
        """
        Takes in all lines, and 2 index deletes those
        """
        if i1 > i2:
            lines = np.delete(lines,i1,axis = 0)
            lines = np.delete(lines,i2,axis = 0)
        else:
            lines = np.delete(lines,i2,axis = 0)
            lines = np.delete(lines,i1,axis = 0)
#        else:
#            print("Same index invalid command")
        return lines
    
    def new_line(self,line1,line2):
        """
        Takes in 2 lines and merges them to 1
        Returns as a numpy array (1,1,4) dimensions to be compatible
        
        """
        
        new_P1_x = (line1[0][0]+line2[0][0]) /2
        new_P1_y = (line1[0][1]+line2[0][1]) /2
        new_P2_x = (line1[0][2]+line2[0][2]) /2
        new_P2_y = (line1[0][3]+line2[0][3]) /2
        new_line = [int(new_P1_x),int(new_P1_y),int(new_P2_x),int(new_P2_y)]
        new_line = np.array(new_line).reshape(1,1,4)
        return new_line
    
    
    def new_line_x(self,line1,line2):
        """
        Takes in 2 lines and merges them to 1, doesnt deal with the y coordinate
        Returns as a numpy array (1,1,4) dimensions to be compatible
        
        """
        
        new_P1_x = (line1[0][0]+line2[0][0]) /2
        new_P2_x = (line1[0][2]+line2[0][2]) /2
        new_line = [int(new_P1_x),int(line1[0][1]),int(new_P2_x),int(line1[0][3])]
        new_line = np.array(new_line).reshape(1,1,4)
        return new_line
        
    def update_lines(self,lines,curr_index,other_index,curr_line,other_line):
        """
        Creates the new line 
        Deletes the 2 old ones
        Joins the new line with the other lines
        """
        new_line = self.new_line(curr_line,other_line)
        lines_del_old =  self.delete_old_lines(lines,curr_index,other_index)
        lines = np.append(lines_del_old,new_line,axis = 0)     
        return lines
    
    def rem_horizontal_lines(self,lines):
        try:
            x_axis = np.array([[0,0,240,0]])
            X1,Y1 = self.create_vector(x_axis)
            X1,Y1 = self.normalize_vector(X1,Y1)
            #should always be 1|0 but whatever (or -1|0)
            i = 0
            for line in lines:
                X2,Y2 = self.create_vector(line)
                X2,Y2 = self.normalize_vector(X2,Y2)
                Dot_P = X1 * X2 + Y1 * Y2
                try:
                    angle = math.acos(Dot_P)
                except:
                    Dot_P = 1
                    angle = math.acos(Dot_P)
                if angle < 0.4:
                    lines = np.delete(lines,i,axis = 0)
                    i -= 1
                    #print("REMS",line)
                i += 1
            return lines
        except (TypeError,ValueError) as e:
            return self.except_save()
                
    #def merge_
    def calculate_angle(self,line1,line2):
        
        X2,Y2 = self.create_vector(line1)
        X2,Y2 = self.normalize_vector(X2,Y2)
        X1,Y1 = self.create_vector(line2)
        X1,Y1 = self.normalize_vector(X1,Y1)
        Dot_P = X1 * X2 + Y1 * Y2
        try:
            angle = math.acos(Dot_P)
        except OverflowError:
            Dot_P = 1
            angle = math.acos(Dot_P)
        return angle
            
        
    def merge_same(self,lines):
        """
        The main loop for reducing and merging passsed on angle, there will be an aferage of ~7 remaining lanes 
        """
        self.lines = lines

        change = True
        self.starttime = time.time()
        
        while change == True:
            
            #introdcution of a dictionary might prove helpful if time consumed is to high
            change = False
            iteration = 0
            if lines == None:
                return None
            
            for curr_index, curr_line in enumerate(lines):
                
                X1,Y1 = self.create_vector(curr_line)
                X1,Y1 = self.normalize_vector(X1,Y1)
                for other_index, other_line in enumerate(lines):
                    if curr_index == other_index:
                        continue
                    else:
                        #create vector of curr_line and other_line
                        X2,Y2 = self.create_vector(other_line)
                        X2,Y2 = self.normalize_vector(X2,Y2)
                        Dot_P = X1 * X2 + Y1 * Y2
                        #print("K")
                        try:
                            angle = math.acos(Dot_P)
                        except:
                            Dot_P = 1
                            angle = math.acos(Dot_P)
                        #print("Between,",angle)    
                        if angle < self.angle:
                            lines = self.update_lines(lines,curr_index,other_index,curr_line,other_line)
                            change = True
                        
                        
                            #print(angle)
                            break
                        else:
                            continue
                    
                    if change == True:
                        break
                    else:
                        print("K")
                        iteration += 1
                        continue
                if change == True:
                    break
                
                else:
                    continue
        #print("Processing took: {}".format(time.time()-self.starttime))
        return lines 
    
    def reduction(self,number_final,lines):
        """
        Returns a number of final lines 
        picked by lenght
        """
        try:
            dis_lines = []
            for line in lines:
                x,y = self.create_vector(line)
                lenght = self.lenght_vector(x,y)
                dis_lines.append([line,lenght])
            sorted_dis = sorted(dis_lines, key=lambda lenght: lenght[1])
            #print(sorted_dis)
            sorted_dis.reverse()
            end_lines = sorted_dis[:number_final]
            #print(end_lines)
            final = []
            for i in end_lines:
                final.append(i[0])
            final = np.array(final)
            final = final.reshape(number_final,1,4)
            #print(final)
            return final
        except:
            return self.except_save()
        
    def except_save(self):
        return np.array([[[0,0,0,0]]]).reshape(1,1,4)
    
    def schnittpunkt(self,y_point,x_point,y_vector,X_vector,height):
        """
        Returns the schnittpunkt with axis (0|height)
        """
        t = (0 - y_point) / y_vector
        new_x = x_point +  (X_vector * t)

        t = (height - y_point) / y_vector
        new_x_2 = x_point + (X_vector * t)
        return new_x,new_x_2
    
    def extend_line(self,line,height):
            """
            Extends the line inputed to the give height
            """
            x_point = line[0][0]
            y_point = line[0][1]
            X_vector,y_vector = self.create_vector(line)
    
            new_x,new_x_2 = self.schnittpunkt(y_point,x_point,y_vector,X_vector,height)
            return [int(new_x),0,int(new_x_2),height]
        
    def extend_lines(self,lines):
        """
        Extends the lines so they touch the x axis and the x axis in height of the image (0|480)
        """

        
        try:
            x1 = self.extend_line(lines[0],self.height)
            x2 = self.extend_line(lines[1],self.height)
            ext_l = [x1,x2]
            ext_l = np.array(ext_l)
            #print(ext_l)
            
            ext_l = ext_l.reshape(2,1,4)
            return ext_l
        except:
            return self.except_save()
        
    def distance_lines(self,lines):
        """
        Orientationline is 0 and aim_line is 1
        """
        orientation_line = lines[0][0]
        aim_line = lines[1][0]
        distance = aim_line[0] - orientation_line[0] + (aim_line[2] - orientation_line[2])
        return distance
    
#    def extend_line2(self,line):
#        X_vector,y_vector = self.create_vector(line)
#        
#    
    def interpret_orientation(self,lines):
        try:
            distance = self.distance_lines(lines)
            if distance > 0:
                orientation = "right"
            elif distance <= 0:
                orientation = "left"
            #print("Distance,orientation:",distance,orientation)
            return distance,orientation
        except:
            return 0,0
        
    def orientation_lines(self,lines,img):
        """
        Creates Orientation Lines and returns the middle line (orientation line)
        Also draws them
        """
        #print(lines)

        def horizontal_line(line1,line2,S):
            """
            Creates 2 horizontal lines
            """
            #print(S)
            try:
                x_v, y_v = self.create_vector(line1)
                x_p = line1[0][0]
                y_p = line1[0][1]
                _, S_height = self.schnittpunkt(y_p,x_p,y_v,x_v,S)
                x_v, y_v = self.create_vector(line2)
                x_p = line2[0][0]
                y_p = line2[0][1]
                _, S_height_2 = self.schnittpunkt(y_p,x_p,y_v,x_v,S)
                
                #cv2.line(img, (int(S_height), S), (int(S_height_2), S), [240,29,29], 3)
                return [int(S_height), S,int(S_height_2), S]
            except IndexError:
                self.except_save()
        
        def vertical_line(horizontal_lines):
            """
            Takes the middle point of bothh lanes and creates a new line 
            """
            new_line = []

            for line in horizontal_lines:
                #print(line)
                line = line[0]
                new_P1_x = (line[0]+line[2]) /2
                new_P1_y = (line[1]+line[3]) /2
                new_line.append(new_P1_x)
                new_line.append(new_P1_y)
            return new_line
                
        try:
            Schnittpunkt = [100,120]
            line1 = lines[0]
            line2 = lines[1]
            orientation_lines = np.array([[[0,0,0,0]]]).reshape(1,1,4)
            for S in Schnittpunkt:
                x = horizontal_line(line1,line2,S)
                try:
                    orientation_lines_h = np.append(orientation_lines_h,[[x]],axis = 0)
                except UnboundLocalError:
                     orientation_lines_h = np.array([[x]]).reshape(1,1,4)    
                     
            orientation_line = vertical_line(orientation_lines_h)
            orientation_line =  np.array(orientation_line).reshape(1,1,4)
            #print(orientation_line)
            orientation_line = self.extend_line(orientation_line[0],self.height)
            orientation_line =  np.array(orientation_line).reshape(1,1,4)
            aim_line = np.array([self.width/2,0,self.width/2,self.height]).reshape(1,1,4)
            orientation_lines = np.append(orientation_line,aim_line,axis = 0)
            if orientation_lines == None:
                lines = np.array([0,0,0,0]).reshape(1,1,4)
            return orientation_lines
        except (IndexError, TypeError) as e:
            return self.except_save()
            
        


if __name__ == '__main__':
    linemerge = line_interpreter(lines,angle)
    linemerge.merge_same()
