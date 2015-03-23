#!/usr/bin/env python
import sys
import subprocess
import time
import calendar
import ConfigParser
import os
try:
    import pygame
except ImportError:
    print("Failed to import pygame. Maybe install it?")
    sys.exit(1)

## DEFAULTS ##
# chdkptpbin = "libs/chdkptp/chdkptp"
# chdkptpenv = os.environ.copy()
# chdkptpenv['LUA_PATH'] = "/home/finn/gitshit/octothorpe-photobooth/libs/chdkptp/lua/?.lua"
config = {
    "photostorage": "Pictures/",
    "takephotocmd": "./take-photo-shim.sh",
    "fullscreen": "-w" not in sys.argv,  # -w for windowed
    "bgcolor": (0, 0, 0),
    "textcolor": (255, 255, 255),
    "displayTimeout": 1
}


def configure():
    cf = ConfigParser.SafeConfigParser()
    cf.read(['photobooth.cfg', os.path.expanduser('~/.photobooth.cfg')])
    if cf.has_section('photobooth'):
        for key in config:
            if cf.has_option('photobooth', key):
                if type(config[key]) == int:
                    config[key] = cf.getint('photobooth', key)
                else:
                    config[key] = cf.get('photobooth', key)
                    if key in ["bgcolor", "textcolor"]:
                        config[key] = config[key].split(",")
                        for color in range(len(config[key])):
                            config[key][color] = int(config[key][color].strip())
                        config[key] = tuple(config[key])
    print(config)


def takePhoto(countdown, background, filename):

    font = pygame.font.Font(None, 1000)
    text = font.render("", 1, config['textcolor'])

    print("[tick] Countdown %s" % countdown)
    countdown = countdown - 1
    if countdown > 0:  # We're actually still counting
        text = font.render(str(countdown), 1, config['textcolor'])
        if countdown == 2:
            subprocess.Popen([config['takephotocmd'], filename])
    elif countdown == 0:  # We've reached the end of the countdown loop
        text = font.render("smile", 1, config['textcolor'])
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
    text = font.render("#photobooth", 1, config['textcolor'])
    textpos = text.get_rect()
    textpos.centerx = background.get_rect().centerx
    textpos.centery = background.get_rect().centery
    background.blit(text, textpos)


def main():
    configure()

    pygame.init()

    displayinfo = pygame.display.Info()  # Find some info out about the display
    if config['fullscreen']:
        size = displayinfo.current_w, displayinfo.current_h
    else:
        size = (displayinfo.current_w/2), (displayinfo.current_h/2)

    screen = pygame.display.set_mode(size)
    if config['fullscreen']:
        pygame.display.toggle_fullscreen()
    c = pygame.time.Clock()

    background = pygame.Surface(screen.get_size())

    # chdkptp = subprocess.Popen(chdkptpbin, env=chdkptpenv)
    # print(chdkptp.communicate('connect'))chdkptp/

    picturenumber = -1
    countdown = -1
    displayTimeout = config['displayTimeout']
    stripnumber = calendar.timegm(time.gmtime())
    filename = "%s/%s-%s.jpg" % (config['photostorage'], stripnumber, picturenumber)

    while True:
        print("[tick] countdown = %s stripnumber = %s picturenumber = %s displayTimeout = %s" % (countdown, stripnumber, picturenumber, displayTimeout))
        for event in pygame.event.get():
            print(event)
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == 32 and countdown < 0:  # spacebar
                    countdown = 4
                    picturenumber = 0
                    stripnumber = calendar.timegm(time.gmtime())
                    filename = "%s/%s-%s.jpg" % (config['photostorage'], stripnumber, picturenumber)
                elif event.key in [113, 27]:  # q, esc
                    sys.exit()
        print("[tick]")
        background.fill(config['bgcolor'])
        if countdown >= 0:  # We're getting setup to take a picture or currently taking it
            countdown = takePhoto(countdown, background, filename)
        elif picturenumber >= 0:
            if displayTimeout > 0:  # We just took a picture and are showing it
                displayPhoto(background, filename)
                displayTimeout = displayTimeout - 1
            elif picturenumber < 3:
                displayTimeout = 1
                picturenumber = picturenumber + 1
                countdown = 4
                filename = "%s/%s-%s.jpg" % (config['photostorage'], stripnumber, picturenumber)
            else:
                picturenumber = -1
        else:  # We haven't taken a picture, nor are we displaying one
            displayWelcomeScreen(background)
        screen.blit(background, (0, 0))
        pygame.display.flip()
        c.tick(1)

if __name__ == "__main__":
    main()
