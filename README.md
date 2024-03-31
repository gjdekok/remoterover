# EV3 Remote Controlled Rover

This is a remote controlled LEGO EV3 (Mindstorms) rover, implemented using MicroPython and PyBricks 2.0. It uses a socket connection to communicate between the client (a laptop in my case) and the server (the EV3 brick). The rover will refuse to run into walls (or at least try to). The client script is implemented using a PyGame event loop.

## Implementation details
The program for the brick is written using the excellent [PyBricks 2.0](https://pybricks.com/ev3-micropython/) library which runs on [ev3dev](https://www.ev3dev.org/). This platform (MicroPython on the EV3) is not thread-safe, so I cannot use the threading module. To continuously read the IR sensor while also checking for user commands, I use cooperative multitasking (coroutines that yield control to a scheduler). The socket library is employed for direct communication between the server and client. Both must be visible to each other to establish a connection

On the client side, the implementation uses PyGame to continuously check for user commands and send these to the rover using the socket connection. 

## To do?
Should I have some time, here's a small feature wish list:
* A client-side dashboard using PyGame, which includes sensor readings
* A self-driving function
* A follow-the-remote-control function
* Adding more sensors to the rover
* Rover audio

Oh, and I like to make my rover design more flexible to allow for optional track wheels (so it is finally able to climb our rug).
