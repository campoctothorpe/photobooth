#!/usr/bin/env python3
import pygame
import subprocess
import os
import configparser
import sys
import time
import calendar

config = {
    "photostorage": "Pictures",
    "chdkptp": "chdkptp",
    "fullscreen": "-w" not in sys.argv,  # -w for windowed
    "bgcolor": (0, 0, 0),
    "textcolor": (255, 255, 255),
    "displayPhotoFor": 5,
    "photosPerSet": 4,
    "countdown": 4,
    "countdownSpeed": 1
}


def configure():
    cf = configparser.SafeConfigParser()
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


def waitForInput(stream, waitFor=">"):
    char = stream.read(1).decode('utf-8')
    while char != waitFor:
        print(char, end="")
        sys.stdout.flush()
        char = stream.read(1).decode('utf-8')
    print(char)


## The following code was stolen from http://www.pygame.org/wiki/TextWrapping
def truncline(text, font, maxwidth):
    real = len(text)
    stext = text
    l = font.size(text)[0]
    cut = 0
    a = 0
    done = 1
    while l > maxwidth:
        a = a+1
        n = text.rsplit(None, a)[0]
        if stext == n:
            cut += 1
            stext = n[:-cut]
        else:
            stext = n
        l = font.size(stext)[0]
        real = len(stext)
        done = 0
    return real, done, stext


def wrapline(text, font, maxwidth):
    done = 0
    wrapped = []

    while not done:
        nl, done, stext = truncline(text, font, maxwidth)
        wrapped.append(stext.strip())
        text = text[nl:]
    return wrapped


def renderText(textstr, game, fontSize=1000):
    font = pygame.font.Font(None, fontSize)
    lines = wrapline(textstr, font, game['size'][0]-100)
    height = font.size(lines[0])[1]
    totalTextHeight = height * len(lines)
    top = game['background'].get_rect().centery - (totalTextHeight/2)
    for line in range(0, len(lines)):
        text = font.render(lines[line], 1, config['textcolor'])
        textpos = text.get_rect()
        textpos.centerx = game['background'].get_rect().centerx
        textpos.top = top + height*line
        game['background'].blit(text, textpos)
        game['screen'].blit(game['background'], (0, 0))
    pygame.display.flip()
    game['clock'].tick()


def takePhotoSet(chdkptp, game):
    stripnumber = calendar.timegm(time.gmtime())
    filename = "%s/%s" % (config['photostorage'], stripnumber)
    # Enter rsint mode
    chdkptp.stdin.write(("rsint %s-last\n" % filename).encode())
    waitForInput(chdkptp.stdout)
    photonumber = 0
    while photonumber < config['photosPerSet']:
        doCountdown(game)
        takePhoto(chdkptp)
        os.rename("%s-last.jpg" % filename, "%s-%s.jpg" % (filename, photonumber))
        displayPhoto("%s-%s.jpg" % (filename, photonumber), game)
        photonumber += 1
    chdkptp.stdin.write(b"q\n")
    waitForInput(chdkptp.stdout)


def doCountdown(game):
    countdown = config['countdown']
    while countdown >= 0:
        game['background'].fill(config['bgcolor'])
        if countdown > 0:
            renderText(str(countdown), game, fontSize=1500)
        elif countdown == 0:
            renderText("smile!", game, fontSize=500)
        countdown -= 1
        time.sleep(config['countdownSpeed'])


def takePhoto(chdkptp):
    chdkptp.stdin.write(b"s\n")
    waitForInput(chdkptp.stdout)


def displayPhoto(filename, game):
    img = pygame.image.load(filename)
    imgposition = img.get_rect()
    imgposition.centerx = game['background'].get_rect().centerx
    imgposition.centery = game['background'].get_rect().centery
    game['background'].blit(img, imgposition)
    game['screen'].blit(game['background'], (0, 0))
    pygame.display.flip()
    game['clock'].tick()
    time.sleep(config['displayPhotoFor'])


def waitForTrigger(game):
    triggered = False
    game['background'].fill(config['bgcolor'])
    renderText("Press the #BigRedButton to begin", game, fontSize=200)
    while not triggered:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == 32:  # spacebar
                    triggered = True
                elif event.key in [113, 27]:  # q, esc
                    sys.exit()
        time.sleep(0.05)
    print("triggered!!")


def main():
    configure()

    pygame.init()

    displayinfo = pygame.display.Info()  # Find some info out about the display
    if config['fullscreen']:
        size = displayinfo.current_w, displayinfo.current_h
    else:
        size = 1800, 800

    screen = pygame.display.set_mode(size)

    if config['fullscreen']:
        pygame.display.toggle_fullscreen()
    c = pygame.time.Clock()

    background = pygame.Surface(screen.get_size())

    chdkptp = subprocess.Popen(config['chdkptp'],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               bufsize=0)
    waitForInput(chdkptp.stdout)
    chdkptp.stdin.write(b"c\n")
    print("Connecting to camera....")
    waitForInput(chdkptp.stdout)
    chdkptp.stdin.write(b"rec\n")
    print("Entering shooting mode...")
    waitForInput(chdkptp.stdout)
    print("Annnd into the loop we go!")

    game = {
        "screen": screen,
        "background": background,
        "clock": c,
        "size": size
    }

    while True:
        waitForTrigger(game)
        takePhotoSet(chdkptp, game)


if __name__ == "__main__":
    main()
