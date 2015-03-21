#!/usr/bin/env python
import pygame
import sys
import os
import subprocess

chdkptpbin = "libs/chdkptp/chdkptp"
chdkptpenv = os.environ.copy()
chdkptpenv['LUA_PATH'] = "/home/finn/gitshit/octothorpe-photobooth/libs/chdkptp/lua/?.lua"
photostorage = "Pictures/"

fullscreen = True

pygame.init()

displayinfo = pygame.display.Info()  # Find some info out about the display
if fullscreen:
    size = width, height = displayinfo.current_w, displayinfo.current_h
else:
    size = width, height = (displayinfo.current_w/2), (displayinfo.current_h/2)

speed = [2, 2]
bgcolor = 0, 0, 0


screen = pygame.display.set_mode(size)
if fullscreen:
    pygame.display.toggle_fullscreen()
c = pygame.time.Clock()


background = pygame.Surface(screen.get_size())
font = pygame.font.Font(None, 1000)
text = font.render("3", 1, (255, 255, 255))
textpos = text.get_rect()
textpos.centerx = background.get_rect().centerx
background.blit(text, textpos)

countdown = 4

# chdkptp = subprocess.Popen(chdkptpbin, env=chdkptpenv)
# print(chdkptp.communicate('connect'))

picturenumber = 0

filename = "%s/%s.jpg" % (photostorage, picturenumber)

while True:
    print("[tick] countdown=%s picturenumber=%s" % (countdown, picturenumber))
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
            sys.exit()

    if height < 1 or width < 1:
        sys.exit(0)

    background.fill(bgcolor)

    if countdown >= 0:  # If we're still in the countdown loop
        countdown = countdown - 1
        if countdown > 0:  # We're actually still counting
            text = font.render(str(countdown), 1, (255, 255, 255))
            if countdown == 2:
                subprocess.Popen(["./take-photo-shim.sh", filename])
        elif countdown == 0:  # We've reached the end of the countdown loop
            text = font.render("smile", 1, (255, 255, 255))
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        background.blit(text, textpos)
    else:  # We are not even counting anymore, the picture has been taken
        img = pygame.image.load(filename)
        imgposition = img.get_rect()
        imgposition.centerx = background.get_rect().centerx
        imgposition.centery = background.get_rect().centery
        background.blit(img, imgposition)
    screen.blit(background, (0, 0))
    pygame.display.flip()
    c.tick(1)
