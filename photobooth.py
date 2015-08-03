#!/usr/bin/env python3
import pygame
import subprocess
import logging
import os
import configparser
import sys
import time
from PIL import Image
import calendar

logging.basicConfig(level=logging.DEBUG)

BEAGLE = False
try:
    from Adafruit_BBIO import GPIO
    BEAGLE = True
except ImportError:
    logging.info("Adafruit_BBIO.GPIO not available, assuming not a beagle")

config = {
    "photostorage": "Pictures",
    "chdkptp": "chdkptp",
    "fullscreen": "-w" not in sys.argv,  # -w for windowed
    "bgcolor": (0, 0, 0),
    "textcolor": (255, 255, 255),
    "displayPhotoFor": 5,
    "photosPerSet": 4,
    "countdown": 4,
    "countdownSpeed": 1,
    "framesize": 100,
    "padding": 100,
    "bottomframesize": 800,
    "bottom": "bottom.png",
    "pin": "P8_12"
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
    logging.debug("Configured")


def waitForInput(stream, waitFor=">"):
    char = stream.read(1).decode('utf-8')
    line = char
    while char != waitFor:
        char = stream.read(1).decode('utf-8')
        line += char
    logging.debug(line)


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


def renderText(textstr, game, fontSize=1000, top=None):
    logging.info("Rendering text %s", textstr)
    font = pygame.font.Font(None, fontSize)
    lines = wrapline(textstr, font, game['size'][0]-100)
    height = font.size(lines[0])[1]
    totalTextHeight = height * len(lines)
    if top is None:
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


def makeSet(prefix, mode="RGB", color="white"):
    logging.info("Rendering a set of images starting with %s", prefix)
    images = []
    frame = config['framesize']
    bottomframe = config['bottomframesize']
    for i in range(0, config['photosPerSet']):
        images.append(Image.open("%s-%s.jpg" % (prefix, i)))
    width = (images[0].size[0] * 2) + (frame * 2) + config['padding']
    height = (images[0].size[1] * 2) + frame + bottomframe + config['padding']
    image = Image.new(mode, (width, height), color)

    left, upper = frame, frame
    for img in images:
        image.paste(img, (left, upper))
        if left == frame:
            left += img.size[0] + config['padding']
        else:
            left = frame
            upper += img.size[1] + config['padding']

    bottom = Image.open(config['bottom'])
    bottomposition = (0, (images[0].size[1] * 2) + frame + config['padding'])
    image.paste(bottom, bottomposition, bottom)
    outputName = "%s-set.jpg" % prefix
    image.save(outputName, "JPEG", quality=90, optimize=True)
    return outputName


def takePhotoSet(chdkptp, game):
    stripnumber = calendar.timegm(time.gmtime())
    filename = "%s/%s" % (config['photostorage'], stripnumber)
    # Enter rsint mode
    chdkptp.stdin.write(("rsint %s-last\n" % filename).encode())
    waitForInput(chdkptp.stdout)
    photonumber = 0
    while photonumber < config['photosPerSet']:
        logging.debug('Doing countdown for picture %s', photonumber)
        doCountdown(game)
        logging.debug('Taking photo')
        takePhoto(chdkptp)
        logging.debug('Renaming from %s-last.jpg to %s-%s.jpg', filename, filename, photonumber)
        os.rename("%s-last.jpg" % filename, "%s-%s.jpg" % (filename, photonumber))
        if photonumber != config['photosPerSet']-1:
            logging.debug('Displaying!')
            # Don't display the last picture because we're going to show it in the strip
            displayPhoto("%s-%s.jpg" % (filename, photonumber), game, sleep=20)
        photonumber += 1
    chdkptp.stdin.write(b"q\n")
    photoset = makeSet(filename)
    logging.info('Displaying set')
    displayPhoto(photoset, game)
    logging.info('Returning to idle state')
    waitForInput(chdkptp.stdout)


def doCountdown(game):
    countdown = config['countdown']
    while countdown >= 0:
        game['background'].fill(config['bgcolor'])
        if countdown > 0:
            renderText(str(countdown), game, fontSize=1500, top=-75)
        elif countdown == 0:
            renderText("smile!", game, fontSize=500)
        countdown -= 1
        time.sleep(config['countdownSpeed'])


def takePhoto(chdkptp):
    chdkptp.stdin.write(b"s\n")
    waitForInput(chdkptp.stdout)


def displayPhoto(filename, game, sleep=None, size=None):
    logging.info("Displaying %s", filename)
    if sleep is None:
        sleep = config['displayPhotoFor']

    # Blank the screen
    game['background'].fill(config['bgcolor'])

    img = pygame.image.load(filename)

    if size is None:
        imgsize = img.get_rect().size
        bgsize = game['background'].get_rect()
        logging.debug(bgsize)
        logging.debug(imgsize)
        scale = imgsize[0]/bgsize[2]
        if imgsize[0] < imgsize[1]:
            scale = imgsize[1]/bgsize[3]
        size = (int(imgsize[0]/scale), int(imgsize[1]/scale))
        logging.debug(size)

    img = pygame.transform.scale(img, size)
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
    text = "Press the space bar to begin"
    if BEAGLE:
        text = "Press the #BigRedButton to begin"
    renderText(text, game, fontSize=200)
    while not triggered:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == 32:  # spacebar
                    logging.debug("Spacebar pressed!")
                    triggered = True
                elif event.key in [113, 27]:  # q, esc
                    sys.exit()
        if BEAGLE:
            if GPIO.input(config['pin']) == 1:
                logging.debug("GPIO Pin %s triggered!", config['pin'])
                triggered = True
        time.sleep(0.05)
    logging.debug("triggered!!")


def main():
    configure()

    if BEAGLE:
        logging.debug("Configuring GPIO pin %s", config['pin'])
        GPIO.setup(config['pin'], GPIO.IN)

    pygame.init()
    pygame.mouse.set_visible(False)
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
    logging.debug("Connecting to camera....")
    waitForInput(chdkptp.stdout)
    chdkptp.stdin.write(b"rec\n")
    logging.debug("Entering shooting mode...")
    waitForInput(chdkptp.stdout)
    logging.debug("Annnd into the loop we go!")

    game = {
        "screen": screen,
        "background": background,
        "clock": c,
        "size": size
    }

    game['background'].fill(config['bgcolor'])
    while True:
        waitForTrigger(game)
        takePhotoSet(chdkptp, game)


if __name__ == "__main__":
    main()
