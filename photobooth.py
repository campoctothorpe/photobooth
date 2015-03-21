#!/usr/bin/env python
import sys
import subprocess
try:
    import pygame
except ImportError:
    print("Failed to import pygame. Maybe install it?")
    sys.exit(1)

## SETTINGS ##
# chdkptpbin = "libs/chdkptp/chdkptp"
# chdkptpenv = os.environ.copy()
# chdkptpenv['LUA_PATH'] = "/home/finn/gitshit/octothorpe-photobooth/libs/chdkptp/lua/?.lua"
photostorage = "Pictures/"
takephotocmd = "./take-photo-shim.sh"
fullscreen = True
bgcolor = 0, 0, 0
textcolor = 255, 255, 255


def takePhoto(countdown, background, filename):

    font = pygame.font.Font(None, 1000)
    text = font.render("", 1, textcolor)

    print("[tick] Countdown %s" % countdown)
    countdown = countdown - 1
    if countdown > 0:  # We're actually still counting
        text = font.render(str(countdown), 1, textcolor)
        if countdown == 2:
            subprocess.Popen([takephotocmd, filename])
    elif countdown == 0:  # We've reached the end of the countdown loop
        text = font.render("smile", 1, textcolor)
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


def displayWelcomeScreen(background):
    font = pygame.font.Font(None, 400)
    text = font.render("#photobooth", 1, textcolor)
    textpos = text.get_rect()
    textpos.centerx = background.get_rect().centerx
    textpos.centery = background.get_rect().centery
    background.blit(text, textpos)


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
    # print(chdkptp.communicate('connect'))chdkptp/

    picturenumber = -1
    countdown = -1
    displayTimeout = 1
    filename = "%s/%s.jpg" % (photostorage, picturenumber)

    while True:
        for event in pygame.event.get():
            print(event)
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == 32 and countdown < 0:  # spacebar
                    countdown = 4
                    picturenumber = picturenumber + 1
                    filename = "%s/%s.jpg" % (photostorage, picturenumber)
                elif event.key in [113, 27]:  # q, esc
                    sys.exit()
        print("[tick]")
        background.fill(bgcolor)
        if countdown >= 0:  # We're getting setup to take a picture or currently taking it
            countdown = takePhoto(countdown, background, filename)
        elif picturenumber >= 0:
            if displayTimeout > 0:  # We just took a picture and are showing it
                displayPhoto(background, filename)
                displayTimeout = displayTimeout - 1
            else:
                displayTimeout = 1
                picturenumber = picturenumber + 1
                countdown = 4

        else:  # We haven't taken a picture, nor are we displaying one
            displayWelcomeScreen(background)
        screen.blit(background, (0, 0))
        pygame.display.flip()
        c.tick(1)

if __name__ == "__main__":
    main()
