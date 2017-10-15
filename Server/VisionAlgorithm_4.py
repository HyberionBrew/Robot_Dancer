# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 15:31:27 2017

@author: Fabian
"""

import numpy as np
import cv2
from line_merge import line_interpreter
from numpy import linalg as la
from Scanner import Scanner,Pointer
import math
from scipy.misc import comb
import time
from movement_handling import InterpretLines,movement

class VisionAlgorithm4(object):
    
    def __init__(self,t1,con):
        self.t1 = t1
        self.con = con
        self.movement = InterpretLines()
        self.movementStop = movement()
    def Test_Unit(self):
        for i in range(0,15):
            print("Current Position {}".format(i))
            self.i = i
            self.main()
        cv2.destroyAllWindows()
    
    def post_processing(self,img):
        """
        Removes the upper part of the image
        and colors the image grey 
        """
        try:
            self.width = int(tuple(np.shape(self.get_img()))[1])
            self.height = int(tuple(np.shape(self.get_img()))[0])
            img = img[self.height//2:self.height,0:self.width]
            gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return (gray_image, True)
        except:
            print("Couldnt post Process the Image Line 39 in VisionAlgorithm_main, could be that there is no image")
            return (None,False)
    
    def get_img(self):
        return self.con.get_frame()
    
    def main(self):
        """
        Main part of the Programm
        First: gets the iqmage from the function get_img, 
        Second: makes the image grey and only takes the lower part of the image // Done in Postprocessing
        Third: Aplies the function scanner to the image, returns an list of the two most possible lanes
        Last: Applies linear regression to the Points to get 0-2 Lanes
        """
        while True:
            startTime = time.time()
            img = self.get_img()
            post_processed, couldProcess = self.post_processing(img)
            if couldProcess == True:
                #leftlane
                scannerLeft = Scanner(post_processed,t1=15,steps = 6,mirrorvertical = False)
                laneleftPoints, foundLane = scannerLeft.run()
                laneleftPoints = self.AdjustPoints(laneleftPoints)
                leftLane = self.linearRegression(laneleftPoints)
                #right lane
                scannerRight = Scanner(post_processed,t1=15,steps = 6,mirrorvertical = True)
                lanerightPoints, foundLane = scannerRight.run()
                lanerightPoints = self.reverseFliping(lanerightPoints)
                lanerightPoints = self.AdjustPoints(lanerightPoints)
                rightLane = self.linearRegression(lanerightPoints)
                #self.linearRegression(lanerightPoints+laneleftPoints)
                #drawing
                newLane = self.checkLaneDisctance(leftLane,rightLane)
                #TODO!
                lines = None
                if newLane != None:
                    lines = [newLane]
                elif leftLane!= None and rightLane != None:
                    lines = [leftLane,rightLane]
                elif leftLane!= None and rightLane == None:
                    lines = [leftLane]
                elif leftLane== None and rightLane != None:
                    lines = [rightLane]
                try:
                    print("Number of Lines:",len(lines))
                except:
                    print("NONE")
                lines = self.adjustFormatLines(lines)
#                print(lines)
                #self.con.lineQueue.write_temp(lines)
                self.con.PointQueue.write_temp([(lanerightPoints,[0,0,255]),(laneleftPoints,[255,0,0])])
                #self.con.PointQueue.write_temp()
                
            self.movement.currMov(lines,self.height,self.width)
            endTime = time.time()- startTime 
#            print("Operation took", endTime)           
            data_type = "Visual_1"
            
            if self.con.dataQ.get_qsize() != 0:
                data, data_type = self.con.dataQ.read_temp()
            if data_type != "Visual_1":
                self.movementStop.stop()
                break
            
    def adjustFormatLines(self,lines):
        try:
            newLines = []
            for line in lines:
                newLine = [[line[0][0],line[0][1],line[1][0],line[1][1]]]
                newLines.append(newLine)
            return newLines
        except:
            lines = None
            return lines
    def checkLaneDisctance(self,leftLane,rightLane,h1 = 180):
        """
        Takes in 2 Lanes and checks the distance on the Top and the bottom of the window
        adds the distances and if those are below h1 they get joined
        """
        try:
        
            topDistance = abs(leftLane[0][0]-rightLane[0][0])
            botDistance = abs(leftLane[1][0]-rightLane[1][0])
            print(topDistance,botDistance)
            allDistance = topDistance+botDistance 
            print("Distance:",allDistance)
            if allDistance < h1:
                newLane = self.joinLanes(leftLane,rightLane)
                return newLane
        except TypeError:
            pass
    def joinLanes(self,leftLane,rightLane):
        newTopX = (leftLane[0][0]+rightLane[0][0])//2
        newBotX = (leftLane[1][0]+rightLane[1][0])//2
        return [(newTopX,leftLane[0][1]),(newBotX,leftLane[1][1])]
    
    def linearRegression(self,Points):
        """
        Apllies linear regression too the Points
        """
        try:
            if len(Points)>5:
                
                PointsX = np.array([p[0] for p in Points])
                PointsY = np.array([p[1] for p in Points])
                PointsX = np.vstack([PointsX,np.ones(len(PointsX))]).T
                k,d = np.linalg.lstsq(PointsX,PointsY)[0]
                x1 = (-d)/k
                x2 = (self.height - d) /k
                return [(int(x1),0),(int(x2),self.height)]
        except TypeError:
            return None
    
    def reverseFliping(self,laneright):
        """
        The right lane gets calculated by flipping the image and apliing the same alg.
        as for the left lane this flipping has to be reversed
        """
        try:
            newPoints = []
            for Point in laneright:
                newPoint = (self.width-Point[0],Point[1])
                newPoints.append(newPoint)
            return newPoints
        except TypeError:
            print("NO lane right")
    def AdjustPoints(self,Points):
        """
        The points have to get adjusted after getting them from the Alg.
        because there the image is cropped in half this has to be reversed back again
        """
        try:
            allPoints = []
            for Point in Points:
                
                PointAdjusted = (Point[0],Point[1]+self.height//2)
                allPoints.append(PointAdjusted)
                
            return allPoints
        except TypeError:
            pass
        
    def draw_lane(self,lane,img_draw,color):
        try:
            for Point in lane:
                img_draw = self.draw_section(img_draw,Point,color,steps =6)
        except TypeError:
            print("No lane left")
            
    def draw_section(self,img,point,color,steps):
        x = point[0]
        y = point[1]
        top_left = (x,y-steps)
        bottom_right = (x+steps,y)
        cv2.rectangle(img,top_left,bottom_right,color,1)
        return img
    
#    def postProcessLanes(self,leftLane,rightLane):
#        """
#        Takes in the Points that make up the lanes as leftLane and rightLane
#        and returns a fitted bezier curve
#        """
#        ptsl = self.fittBezier(leftLane)
#        ptsr = self.fittBezier(rightLane)
#        return (ptsl,ptsr)

#    def fittBezier(self,points):
#        if points == None:
#            return None,None
#        def bernstein_poly(i,n,t):
#            """
#            @stackoverflow.com/questions/12643079/bezier-curve-fitting-with-scipy
#            """
#            return comb(n,i)*(t**(n-i))*(1-t)**i
#        def bezier_curve(points, nTimes = 10):
#            
#            nPoints = len(points)
#            xPoints = np.array([p[0] for p in points])
#            yPoints = np.array([p[1] for p in points])
#            t = np.linspace(0.0,1.0, nTimes)
#            polynomial_array = np.array([bernstein_poly(i,nPoints-1,t) for i in range(0,nPoints)])
#            xvals = np.dot(xPoints,polynomial_array)
#            yvals = np.dot(yPoints,polynomial_array)
#            return xvals,yvals
#        xvals,yvals = bezier_curve(points)
#        Vertices = []
#        for i,Pointx in enumerate(xvals):    
#            Vertices.append([xvals[i],yvals[i]])
#        Vertices = np.array(Vertices, np.int32)
#        Vertices = Vertices.reshape(-1,1,2)
#        return Vertices
#            
if __name__ == "__main__":
    VA = VisionAlgorithm(15)
    VA.Test_Unit()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
