# -*- coding: utf-8 -*-
"""
Created on Thu May 11 16:35:09 2017

@author: Fabian
"""
import socket
import tkinter as tk
from tkinter import *
import cv2
from PIL import Image, ImageTk
import time
import numpy as np
import struct
import io
import threading
import queue


HOST = '192.168.0.12'    # The remote host
PORT = 8889              # The same port as used by the server
cam = "http://192.168.0.12:8080/?action=stream"

class client():
    
    def __init__(self,create_stream):
        """
        Starts Running the Client as a Thread
        """
        self.create_stream = create_stream
#        threading.Thread.__init__(self)
        self.previous_img = Image.open("Error.png")
        self.previous_img = np.array(self.previous_img )
        self.starttime = 0 #is getting used in update_img to check if connection timed out
#        self.start()
        
    def ende(self,window):    
        try:
            self.send([0,0],"close")
        finally:
            print("Called")
            self.create_stream.close_stream()
#            try:
#                create_stream.close_connection()
#            except:
#                print("No connection was established")
            print("did it")
            window.destroy()
            return 0

    def callback(self):
        """
        For quiting the window used in run() 
        not used right now use the end button to end !!!
        """
        self.ende()
        
    def run(self):
        """
        creates all the buttons and packs them in the seperate function self.pack
        USING GRID not PACK 
        a .pack() will not be accepted // self.pack() is a own function
        not to be confused with the tkinter pack()!!!!! (yeah bad naming)
        """
        
        #initizallizing the Window
        #print("ru")
        window = tk.Tk()
        #self.window.protocol("WM_DELETE_WINDOW", self.callback)
        window.wm_title("Client 1.0")
        #initizalizing the grid
        self.imageFrame = tk.Frame(window, width=800, height=500)
        self.imageFrame.grid(row=0, column=0, padx=10, pady=2)
        #creates the 2 main scrollbars
        self.scrollbars(window)
        #create Buttons
        self.submit = tk.Button(window, text = "Submit", width = 10, command =lambda:self.send(window,[self.scvwert.get(),self.scvwert2.get()],"remote_control"))
        self.stopbutton = tk.Button(window, text = "Stop", width = 10, command =lambda:self.send(window,[0,0],"remote_control"))
        self.UV = tk.Button(window, text = "UV", width = 10, command =lambda:self.send(window,[0,0],"UV_control"))
        self.visual_1 = tk.Button(window, text = "Visual_1", width = 10, command=lambda:self.send(window,[0,0],"image_control_1"))
        self.visual_2 = tk.Button(window, text = "Visual_2", width = 10, command=lambda:self.send(window,[0,0],"image_control_2"))
        self.close = tk.Button(window, text = "End", width = 10, command=lambda:self.ende(window))

        self.last_command(window,"None")
        self.display = tk.Label(self.imageFrame)
        self.display.grid(row=1, column=0, padx=10, pady=2)
        self.update_img(window)
        
        self.pack(window)
        window.mainloop()
        
    def scrollbars(self,window):
        """
        Creates 2 scrollbars and saves the current value of them in self.scv and self.scv2
        """
        self.lb = tk.Label(window, text = "Geschwindigkeit: 0", width= 25)
        
        
        self.scvwert = tk.IntVar() 
        self.scvwert.set(0)
        self.scvwert2 = tk.IntVar()
        self.scvwert2.set(0)

        self.scv = tk.Scale(window, width = 20, length = 255,
                        orient="vertical", from_= 0, to =255,
                        resolution = 5, tickinterval = 20,
                        command = self.anzeigen, variable= self.scvwert)

        self.scv2 = tk.Scale(window, width = 20, length = 255,
                        orient="vertical", from_= 0, to =255,
                        resolution = 5, tickinterval = 20,
                        command = self.anzeigen, variable= self.scvwert2)
        
    def anzeigen(self,window):
        """
        Gets used by scorllbars
        """
        self.lb["text"] = "Geschwindigkeit:" \
        + str(self.scvwert.get()) 
        
    def last_command(self,window, data_datatype):
        """
        Creates a label that shows the last executed programm
        It gets called at the end of the send programm
        """
        self.lastcommandlb = tk.Label(window, text = "Last Command: {}".format(data_datatype), width= 50)
        self.lastcommandlb.grid(column=2, row=0,sticky = S,pady = 90)
            
    def update_img(self,window):
        """
        looks @ the queue of the class currentQueue 
        unques the last one and updates the image shown every 30 ms
        """
        
        try:
            
            img = cQ.read_temp()
            self.starttime = time.time()
            cQ.queue.task_done()
        except:
            #print("ex")
            if self.starttime == 0:
                img = Image.open("Error.png")
                img = np.array(img)
            else:    
                if (time.time() - self.starttime) < 1 :
                    img = self.previous_img
                
                else:
                    img = Image.open("Error.png")
                    img = np.array(img)
                
            
        self.previous_img = img   
        #print(type(img))
        img = cv2.resize(img,(640, 480), interpolation = cv2.INTER_CUBIC)
        #print(np.shape(img))
        img = Image.fromarray(img)
        
        imgtk = ImageTk.PhotoImage(image=img)
        self.display.imgtk = imgtk #Shows frame for display 1

        self.display.configure(image=imgtk)
        window.after(500, self.update_img, window)

        
    def pack(self,window):
        
        self.scv.grid(column=1, row=0,sticky = N,pady = 20, padx = 20)
        self.scv2.grid(column=2, row=0,sticky = N,pady = 20, padx = 20)
        self.lastcommandlb.grid(column=2, row=0,sticky = S,pady = 90)
        self.submit.grid(column=1, row=0,sticky = S,pady = 150)
        self.UV.grid(column=1, row=0,sticky = S,pady = 120)
        self.visual_1.grid(column=1, row=0,sticky = S,pady = 90)
        self.visual_2.grid(column=1, row=0,sticky = S,pady = 60)
        self.stopbutton.grid(column=2, row=0,sticky = S,pady = 150)
        self.close.grid(column=2, row=0,sticky = S,pady = 120)          


    def send(self,window,data,datatype):
        try:
            connection = create_stream.get_connection()
        except:
            print("No connection yet")
        #.format(self.scwert.get(),self.scwert2.get())
        data_datatype = "{}|{}".format(data,datatype)
        print(type(connection))
        connection.send(bytes(data_datatype,'utf-8'))
        print("Send {} to Robot.".format(data_datatype))
        self.last_command(window,data_datatype)

        
            

            
class currentQueue(client):
    
    def __init__(self):
        self.queue = queue.Queue(maxsize = 2)

    def write_temp(self,img):
        self.queue.put(img)

    def read_temp(self):
        msg = self.queue.get(False)
        return msg
        
class create_stream(threading.Thread):
   
    def  __init__(self):
       threading.Thread.__init__(self)
       
       self.server_socket = socket.socket()
       self.server_socket.bind(('0.0.0.0', 8889))
       self.terminate = False
       self.start()
       
       
    def run(self):
            # Accept a single connection and make a file-like object out of it
        print("stream running")
        self.server_socket.listen(0)
        try:
            self.con,addr = self.server_socket.accept()
            self.connection = self.con.makefile('rb')
            print("Stream Working")
            while self.terminate == False:
                # Read the length of the image as a 32-bit unsigned int. If the
                # length is zero, quit the loop
                #print("receiving")
#                try:
                image_len = struct.unpack('<L', self.connection.read(4))[0]
#                except struct.error:
#                    #this is/should be thrown if connection is endet by client
#                    self.connection.close()
#                    time.sleep(0.2)
#                    self.__init__()
#                    self.run()
#                    return 0
                # Construct a stream to hold the image data and read the image
                # data from the connection
               #print(self.connection.read(image_len))
                image_stream = io.BytesIO()
#                
                image_stream.write(self.connection.read(image_len))
#                # Rewind the stream, open it as an image with PIL and do some
#                # processing on it
#                print("HI")
                image_stream.seek(0)
                try:
                    image = Image.open(image_stream)
                except:
                    image = Image.open("error.png")
                open_cv_image = np.array(image) 
#                cv2.imshow('Window_Original',open_cv_image)
                cQ.write_temp(open_cv_image)
                image.verify()
                
#                if cv2.waitKey(1) & 0xFF == ord('q'):
#                    break
            return 0
        
        except ConnectionRefusedError:
            print("Couldnt get Camera data")
        except:
            print("No more Camera data")
            cQ.write_temp("Nothing")
            
        finally:
            self.close_stream()
        
    def get_connection(self):
        return self.con
    
    def close_connection(self):
        try:
            self.con.close()
        except:
            print("No connection was open")
            return 0
    
    def close_stream(self):
        print("called close stream()")
        self.terminate = True
        print("joined")
        self.server_socket.close()
        self.close_connection()
#        cv2.destroyAllWindows()
        print("Closed connection")
        return 0
    
    
if __name__ == "__main__" :
        
    cQ = currentQueue()
    create_stream = create_stream()
    client = client(create_stream)
    client.run()
#    client = client()




