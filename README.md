# Robot_Dancer
Hey there!

This Project is my first "big" Project, and its nowhere near finished, however a lot of the features already work.

Features are:
1. Client
2. Receiving Image Data from your RPi
3. Sending Move commands to your RPI
4. UV-Driving mode
5. early stages of lane detection

Still missing:
1. Full implementation of lane detection

This Project has a client and a server side. 

<b>1. Client:</b>
Currently uses Python 3.x.

<p>Non-standart modul needed: PIL,Numpy,GoPIGo and cv2</p>
You will also need a fully setup GoPiGo set.
Go to the start of the client file and edit HOST (= IP of RPI ) and (not necessarily) PORT.

<b>2.Server: </b>
Currently uses Python 2.x!!!

<p>Non-standart modul needed: PIL,Numpy and cv2 </p>
Go to main.py and edit HOST (=your standart Host, your Laptop or Pc that you want to use for remote control) and PORT (= same Port as client).

I would love some feedback!
