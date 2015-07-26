# photobooth
Code to power a simple photobooth.

# Install
First go get [chdkptp](https://www.assembla.com/spaces/chdkptp/wiki) and either put it in your `$PATH`
or specify it's location in the config (see [configuring](#configuring)). Then
`pip install -r requirements.txt` and run `photobooth.py`. For debugging purposes, passing the -w
flag on the command line causes it to start up in windowed mode. Otherwise it will be full screen.

# Configuring
The program will attempt to read a file called `photobooth.cfg` in this current directory, as well
as `.photobooth.cfg` in your home directory. See photobooth.example.cfg for an example. This allows
you to change configuration options. Below is an attempt to document every available option, but
the most up to date list of options is in the code of `photobooth.py`, near the top where all the
defaults are defined.

## photostorage
Defines the folder that photos are stored in

## chdkptp
Defines the command to execute to get a chdkptp CLI interface. This should be the full path to
`chdkptp-sample.sh`, unless it's in your `$PATH`.

## bgcolor
Three comma separated values between 0 and 255 to define the background color.

## textcolor
Three comma separated values between 0 and 255 to define the text color

## displayPhotoFor
The length of time, in seconds, to display the photo for after taking it

## photosPerSet
The number of photos per separated

## countdown
The length of the countdown

## countdownSpeed
The number of seconds (decimals accepted) to wait on each number in the countdown
