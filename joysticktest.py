import pygame
pygame.init()
joysticks = []
for i in range(0, pygame.joystick.get_count()):
    # create an Joystick object in our list
    joysticks.append(pygame.joystick.Joystick(i))
    joysticks[-1].init()
    print(("Detected joystick "),joysticks[-1].get_name(),"'")

while True:
    for event in pygame.event.get():
        print(event)

