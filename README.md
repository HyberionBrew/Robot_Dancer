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


<h1>1. Client:</h1>

Currently uses Python 3.x.

<p>Non-standart moduls needed: PIL,Numpy,GoPIGo and cv2</p>
Go to the start of the <b>client1_4.py</b> file in the client folder and edit HOST (= IP of RPI ) and (not necessarily) PORT.


<h1>2. Server: </h1>

Currently uses Python 2.x!!!

<p>Non-standart moduls needed: PIL,Numpy and cv2 </p>
<p>You will also need a fully setup GoPiGo set.+ Im using Raspbian but other linux dist should be fine</p>
Go to <b>main.py</b> in the server folder and edit HOST (=your standart Host, your Laptop or Pc that you want to use for remote control) and PORT (= same Port as client).


<h1>3. Start</h1>

<p>To start the connection type <b>sudo python main.py</b> in the path of the server files</p>
<p>To start the client open it in your IDE and Run it, everything else <b>should</b> happen automaticaly!



<p> PLEASE REMEMBER THIS IS WORK IN PROGRESS SOME DOCUMENTATION IS MISSING AND SOME MIGHT BE EVEN WRONG<p>
<b>I would love some feedback!<b>
