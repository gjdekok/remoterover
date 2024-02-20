import pygame
import socket


pygame.init()
screen = pygame.display.set_mode((640, 480))

# Setting up the socket client
HOST = 'ev3dev.local'  
PORT = 12345  
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

def send_command(command):
    """Send commands to the EV3 brick."""
    s.sendall(command.encode())

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            key_name = pygame.key.name(event.key)
            key_action = 'down' if event.type == pygame.KEYDOWN else 'up'
            command = f"{key_name} {key_action}"
            send_command(command)
            print(f"Sent: {command}")

send_command("exit") 
pygame.quit()
s.close()
