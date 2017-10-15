# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 12:18:47 2017

@author: Fabian
"""
import numpy as np
import cv2
from numpy import linalg as la

class Scanner(object):
    """
    you can define the magnitude of a step, default is 6 (steps)
    steps = int
    """
    def __init__(self,img,t1 = 15,steps = 6,mirrorvertical = False):
        """
        If mirrow is True the picture just gets mirrowed around the y-axis
        This allows the exactly same algorithm to operate than before
        """
        global width
        width = int(tuple(np.shape(img))[1])
        global height
        height = int(tuple(np.shape(img))[0])
        self.width = width
        self.height = int(tuple(np.shape(img))[0])
        self.img = img
        self.t1 = 15
        self.stepsize = steps
        self.Points = Points()
        if mirrorvertical == True:
            self.img=cv2.flip(self.img,1)
            
    def run(self):
        """
        First init pointer to the lowest height/width
        THIS is a mess especially foundLane and reached_end do the same thing!
        """
        #Pointer_1 points @ the 1st current investigated Pixel(if there are already mutliple 6*6 fields under investigation it points @ the first one)
        img = np.copy(self.img)
        self.PointerMain = Pointer(self.Points,0,self.height,self.img,self.stepsize,isStartpoint = True)
        reached_end = False
        foundLane = False
        lane = None
        while reached_end == False:
            pos = self.PointerMain.get_Pos()
            curr_scan = self.PointerMain.get_section_value(pos)
            
            curr_value = curr_scan[0]
            reached_end = curr_scan[1]
            
            if reached_end == True:
                break
            if curr_value >= self.t1:
                """
                If initial Point is found, start looking for similar Points
                that are close by
                """
                startPoint = self.PointerMain.get_Pos()
                #img = self.PointerMain.draw_section(startPoint,(0,255,0))
#                cv2.imshow('Window_OriginalPoint',img)
#                cv2.waitKey(0)
                self.Points.add_Point(startPoint)
                #img = self.PointerMain.draw_section(startPoint,(0,255,0))
                lane, foundLane = self.adjacentPoints()
                
                if foundLane == True:
                    break
                
                
            _, reached_end = self.PointerMain.increment()
        return (lane,foundLane)
            #res = cv2.resize(curr_matrix,(40,40), interpolation = cv2.INTER_CUBIC)
        
            
    def adjacentPoints(self):
        """
        Spawn a new Pointer to the left of the initial Pointer and one line higher
        let it search in a new search box for an adjacent Point
        _____________________________
        |
        |
        |
        |   _________ 
        |   |       |New search field 
        |   |_______|
        |      x
        |___________________________
        
        
        """
        stepsize = self.PointerMain.get_stepsize()
        reachedLocalEnd = False
        
        while reachedLocalEnd == False:
            self.PointerLocal = PointerLocal(self.img,self.Points,stepsize)
            while reachedLocalEnd == False:
                
                #cv2.waitKey(0)
                value,reachedLocalEnd = self.PointerLocal.get_section_value(self.PointerLocal.get_Pos())
                if reachedLocalEnd == True:
                    break
                if value > self.t1:
                    #img = self.PointerMain.draw_section(self.PointerLocal.get_Pos(),(0,255,0))
#                    cv2.imshow('Window_OriginalPoint',img)
                    self.Points.add_Point(self.PointerLocal.get_Pos())
                    break
                _,reachedLocalEnd = self.PointerLocal.increment()
#                cv2.waitKey(0)
            if (len(self.Points.get_currPoints())>3) and reachedLocalEnd== True:
                break
            
        lanePoints = self.Points.get_currPoints()
        self.Points.flush_currPoints()
        self.Points.get_allPoints()
        if len(lanePoints)>3 :
            return lanePoints, True
        else:
           # print("Found no Lane here")
            return lanePoints, False
        #Pointer2.get_section_value()

class Pointer(object):
    
    def __init__(self,Points,x,y,img,stepsize = 6,isStartpoint = True):
        """
        Startpoint gets Initialized and stepsize
        """
        self.Points = Points
        self.x = x
        self.y = y
        self.stepsize = stepsize
        self.img_clean = np.copy(img)
        self.img_man  = cv2.cvtColor(self.img_clean,cv2.COLOR_GRAY2RGB)
        self.width = int(tuple(np.shape(img))[1])
        self.height = int(tuple(np.shape(img))[0])
        
        
    def get_section_matrix(self,Point):
        """
        Returns the Matrix of the current Section
        """
        #first collum - ,second row |
        x = int(Point[0])
        y = int(Point[1])
        matrix = self.img_clean[ y-self.stepsize:y ,x:x+self.stepsize]
        if np.shape(matrix)[0] != 6:
            return matrix,True

        return matrix,False
    
    def increment(self):
        reached_end = False
        if self.x + self.stepsize > self.width//2:
            self.y -= self.stepsize
            self.x = 0
        else:
            self.x += self.stepsize
        if self.y <= 0:
            reached_end = True
            
        if self.alreadyChecked((self.x,self.y)) == True:
            self.increment()
        return (self.x, self.y), reached_end
        
    def get_section_value(self,Point):

        x = int(Point[0])
        y = int(Point[1])
        try:
            part_img,reached_end = self.get_section_matrix(Point)
        #print(part_img,reached_end)
            eig_val = max(la.eigvals(part_img)[1:])
        #print(eig_val)
        except:
            reached_end = True
            eig_val = None
            
        return eig_val,reached_end
#        except:
#            return 0,reached_end
    
    def draw_section(self,point,color):
        """
        needs 1st top left
              2nd bottom right 
              corner
        as a tuple
        """
        x = point[0]
        y = point[1]
        top_left = (x,y-self.stepsize)
        bottom_right = (x+self.stepsize,y)
        cv2.rectangle(self.img_man,top_left,bottom_right,color,1)
        return self.img_man
    
    def get_Pos(self):
        #print("Called,",self.x,self.y)
        
        return (self.x,self.y)
    def get_stepsize(self):
        return self.stepsize
    
    def alreadyChecked(self,Point):
        
        if Point in self.Points.allPoints:
            return True
        else:
            return False
    
    
class PointerLocal(Pointer):
    
    def __init__(self,img,Points,stepsize):
        """
        IMPLEMENT SUPER 
        TODO!
        """
        self.Points = Points
        self.img_clean = np.copy(img)
        self.img_man  = cv2.cvtColor(self.img_clean,cv2.COLOR_GRAY2RGB)
        startpoint = self.Points.get_currPoints()[-1]
        self.searchStart = self.calcStart(startpoint,self.calcLineTrend(),stepsize)
        self.searchEnd = self.calcEnd(startpoint,self.calcLineTrend(),stepsize)
        self.x = self.searchStart[0]
        self.y = self.searchStart[1]
        self.stepsize =stepsize
        
    def calcLineTrend(self):
        """
        Takes in Points and returns "l" or "r" if Points >2
        else returns NONE
        """
        currPoints = self.Points.get_currPoints()
        if len(currPoints) > 2:
            alldiff = 0
            for Point in currPoints:
                try:
                    diff = Point[0] - prevPoint[0]
                    alldiff += diff
                    
                except NameError:
                    prevPoint = Point
            if alldiff > 0:
                return str("r")
            else:
                return str("l")
            
        else:
            return None
    
    def calcStart(self,Point,trend,stepsize):
        y = Point[1] - stepsize
        if trend != None:
            #if more than 3 Points have been calc line trend
            if trend == "l":
                #\
                x = Point[0]- 4* stepsize
                if x < 0:
                    x = 0
                return (x,y)            
            elif trend == "r":
                x = Point[0]- 2* stepsize
                if x < 0:
                    x = 0
                return (x,y)  
        else:
            x = Point[0]- 3* stepsize
            if x < 0:
                x = 0
            y = Point[1] - stepsize
            return (x,y)
    
    
    def calcEnd(self,Point,trend,stepsize):
        y = Point[1] - stepsize*3
        if trend != None:
            if trend == "l":
                #\
                x = Point[0]+ 2* stepsize
                if x > width:
                    x = width
                return (x,y) 
            
            elif trend == "r":
                x = Point[0]+ 4* stepsize
                if x > width:
                    x = width
                return (x,y)  
            
        x = Point[0]+3*stepsize
        return (x,y)    
        
    def increment(self):
        """
        First check how many points have already been checked
        If there have been found >3 then a line trend is obvious
        and the search field gets biased accordingly
        """
#        cv2.imshow("WINDOW MAN",self.img_man)
#        cv2.waitKey(0)
        if self.x != self.searchEnd[0]:
            self.x += self.stepsize
            reachedLocalEnd =False
        elif (self.x == self.searchEnd[0]) and (self.y != self.searchEnd[1]):
            self.x = self.searchStart[0]
            self.y -= self.stepsize
            reachedLocalEnd =False
        elif (self.x,self.y) == self.searchEnd:
            reachedLocalEnd = True
        if self.alreadyChecked((self.x,self.y)) == True:
            self.increment()
            
        #self.draw_section((self.x,self.y),(255,255,0))
#        cv2.waitKey(0)
        return (self.x,self.y),reachedLocalEnd
            
class Points(object):
    def __init__(self):
        self.currPoints = []
        self.allPoints = []
            
    def add_Point(self,Point):
        self.currPoints.append(Point)
        self.allPoints.append(Point)
    def flush_currPoints(self):
        self.currPoints = []
    def get_currPoints(self):
        return self.currPoints
    def get_allPoints(self):
        return self.allPoints
























