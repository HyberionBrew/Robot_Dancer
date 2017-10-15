# -*- coding: utf-8 -*-
"""
Created on Thu May  4 11:50:43 2017

@author: Fabian
"""
import socket
import sys
import io
import struct
import picamera
import queue
from PIL import Image
import numpy as np
import cv2
from skimage.draw import line_aa

class dataQueue(object):
    """
    This queue ist used to temporarily store the next command
    
    """
    def __init__(self):
        self.queue = queue.Queue(maxsize = 2)

    def write_temp(self,data,data_type):
        """
        writes to the queue
        """
        msg = (data,data_type)
        self.queue.put(msg)

    def read_temp(self):
        """
        reads from the queue
        """
        msg = self.queue.get()
        return msg
    def get_qsize(self):
        """
        reurns queue size
        """
        return self.queue.qsize()

class lineQueue(object):
    """
    This queue ist used to temporarily store the next command
    
    """
    def __init__(self):
        self.queue = queue.Queue(maxsize = 2)

    def write_temp(self,data):
        """
        writes to the queue
        """
        msg = data
        self.queue.put(msg)

    def read_temp(self):
        """
        reads from the queue
        """
        msg = self.queue.get()
        return msg
    def get_qsize(self):
        """
        reurns queue size
        """
        return self.queue.qsize()
    
    
class PointQueue(lineQueue):
    """
    This queue ist used to temporarily store the next command
    
    """
    def __init__(self):
        self.queue = queue.Queue(maxsize = 2)
        
class connection(object):
    
    def __init__(self,HOST,PORT):
        """
        Creates the class connection, takes in HOST and PORT
        """
        self.HOST = HOST
        self.PORT = PORT
        self.dataQ = dataQueue()
        self.receive_send = receiving_sending_value()
        self.lineQueue = lineQueue()
        self.PointQueue = PointQueue()
    def connection_start(self): ##
        '''
        Takes in HOST and PORT as possible Arguments, predefined AS STR AND INT
        returns Socket Connection as SOCKET
        Server Side Connection with IPv4! IPv6 won't work! (possible fix later)
        THIS IS PYTHON 2.7! not up to date!
        '''

        try:
            HOST = self.HOST
            PORT = self.PORT
            self.s = socket.socket()
            self.s.connect((HOST, PORT))
            print ('Socket created')
            return self.s
        except:
            print("Couldnt create socket, no connection to client")
    
    def receive(self):
        '''
        Takes in socket (called vb)!##
        returns Data from client currently AS INT
        return is quiet redundant because self.forward gets changed globaly
        
        Data is send and received in this form 0,255: motor1(int),motor2(int)
        '''
        try:
            while True:
                data = self.s.recv(1024)
                x = repr(data)
                #split in data and data_type
                x = x[1:-1]
                x_list = x.split("|")
                data = (x_list[0])
                data_type = str(x_list[1])
                self.data_type = data_type
                self.dataQ.write_temp(data,data_type)
        except:
            print(sys.exc_info())
        finally:
            print("Returned from receive")
            return 0
    def draw_lines(self,frame):
#        try:
        """
        Format that gets taken in:
        [[[x[1],y[2],x[3],y[4]]],[[x[1],y[2],x[3],y[4]]],[[...]]...]
        for one: [[[x,y,x2,y2]]]
        """
        if self.lineQueue.get_qsize() != 0:
            lines = self.lineQueue.read_temp()
            if lines == None:
                lines = [[[0,0,0,0]]]
            else:
                lines = lines
                
            for line in lines:
                coords = line[0]
                cv2.line(frame, (int(coords[0]), int(coords[1])), (int(coords[2]), int(coords[3])), [250,250,60], 3)

        return frame
    
    def drawPoints(self,frame):
        steps = 6
        if self.PointQueue.get_qsize() != 0:
            PointsAll = self.PointQueue.read_temp()
            for PointsData in PointsAll:
                Points,Color = PointsData
                if Points == None:
                    Points = [(0,0)]
                else:
                    Points = Points
                    
                for Point in Points:
                    x = Point[0]
                    y = Point[1]
                    top_left = (x,y-steps)
                    bottom_right = (x+steps,y)
                    cv2.rectangle(frame,top_left,bottom_right,Color,1)

        return frame
#        except:
#            print("Couldnt draw lines",sys.exc_info())
#            return frame
    
    def send_stream(self):
        """
        Sends the stream and provides get_frame with the current frame
        """
        try:
        # Make a file-like object out of the connection self.s
            self.connection_file = self.s.makefile('wb')
            print("Started sending image data")
            with picamera.PiCamera() as camera:
                camera.resolution = (240, 200)
                #camera.color_effects = (128,128)
                # temporarily (we could write it directly to connection but in this
                # case we want to find out the size of each capture first to keep
                # our protocol simple)
                self.stream = io.BytesIO()
                for foo in camera.capture_continuous(self.stream, 'jpeg'):
                    #self.s.close()
                    # Write the length of the capture to the stream and flush to
                    # ensure it actually gets send
                    len_stream = self.stream.tell()
                    
                    self.stream.seek(0)
        #                
                    data = self.stream.read(len_stream)
                    image_stream = io.BytesIO()
                    image_stream.write(data)
                    image = Image.open(image_stream) 
                    self.frame = np.array(image)
                    self.clean_frame = self.frame.copy()
                   # self.frame = self.draw_lines(self.frame)
                    self.frame = self.drawPoints(self.frame)
                    
                    #cv2.line(self.frame, (int(100), int(200)), (int(0), int(300)), [200,20,20], 3)
                    img = Image.fromarray(self.frame, 'RGB')
                    imgByteArr = io.BytesIO()
                    img.save(imgByteArr, format='JPEG')
                    x = imgByteArr.tell()
                    self.connection_file.write(struct.pack('<L',x))
                    self.connection_file.flush()
                    self.connection_file.write(imgByteArr.getvalue())
                    # Reset the stream for the next capture
                    self.stream.seek(0)
                    imgByteArr.seek(0)
                    self.stream.truncate()

#            # Write a length of zero to the stream to signal we're done
#            self.connection_file.write(struct.pack('<L', 0))
        except:
            print("Unexpected error:", sys.exc_info())
        finally:
            print("Returned from stream")
            return 0
        
    def send_lines(self):
        """
        TODO implement
        sends lines from server to client
        """
        pass
    
    def get_frame(self):
        """
        Returns current camera frame
        """
        return self.clean_frame
    
    def get_current_data_type(self):
        """
        Returns current data_type, defined in receive
        """
        return self.data_type
    
    
class receiving_sending_value(object):
    """
    TODO implement 
    Used to terminate all Threads open after End is pressed
    """
    def __init__(self):
        self.receiving = True
        self.sending = True

    def change_sending(self):
        if self.sending == True:
            self.sending = False
        else:
            self.sendning = True
    
    def change_receiving(self):
        if self.receiving == True:
            self.receiving = False
        else:
            self.receiving = True
                
    def get_sending(self):
        return self.sending
    
    def get_receiving(self):
        return self.receiving
    
    
if __name__ == "__main__" :
    connection = connection()
    connection.connection_start()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    