#!/usr/bin/env python
import pygame
import sys
import subprocess


## SETTINGS ##
# chdkptpbin = "libs/chdkptp/chdkptp"
# chdkptpenv = os.environ.copy()
# chdkptpenv['LUA_PATH'] = "/home/finn/gitshit/octothorpe-photobooth/libs/chdkptp/lua/?.lua"
photostorage = "Pictures/"
takephotocmd = "./take-photo-shim.sh"
fullscreen = False
bgcolor = 0, 0, 0
textcolor = 255, 255, 255


def takePhoto(countdown, background, filename):

    font = pygame.font.Font(None, 1000)
    text = font.render("", 1, (255, 255, 255))

    print("[tick] Countdown %s" % countdown)
    countdown = countdown - 1
    if countdown > 0:  # We're actually still counting
        text = font.render(str(countdown), 1, textcolor)
        if countdown == 2:
            subprocess.Popen([takephotocmd, filename])
    elif countdown == 0:  # We've reached the end of the countdown loop
        text = font.render("smile", 1, (255, 255, 255))
    textpos = text.get_rect()
    textpos.centerx = background.get_rect().centerx
    background.blit(text, textpos)
    return countdown


def displayPhoto(background, filename):
    img = pygame.image.load(filename)
    imgposition = img.get_rect()
    imgposition.centerx = background.get_rect().centerx
    imgposition.centery = background.get_rect().centery
    background.blit(img, imgposition)


def main():
    pygame.init()

    displayinfo = pygame.display.Info()  # Find some info out about the display
    if fullscreen:
        size = displayinfo.current_w, displayinfo.current_h
    else:
        size = (displayinfo.current_w/2), (displayinfo.current_h/2)

    screen = pygame.display.set_mode(size)
    if fullscreen:
        pygame.display.toggle_fullscreen()
    c = pygame.time.Clock()

    background = pygame.Surface(screen.get_size())

    # chdkptp = subprocess.Popen(chdkptpbin, env=chdkptpenv)
    # print(chdkptp.communicate('connect'))

    picturenumber = 0

    filename = "%s/%s.jpg" % (photostorage, picturenumber)

    countdown = 4

    while True:
        for event in pygame.event.get():
            print(event)
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                sys.exit()
        print("[tick]")
        background.fill(bgcolor)
        if countdown >= 0:
            countdown = takePhoto(countdown, background, filename)
        else:
            displayPhoto(background, filename)
        screen.blit(background, (0, 0))
        pygame.display.flip()
        c.tick(1)

if __name__ == "__main__":
    main()
