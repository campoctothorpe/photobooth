#!/bin/bash
 avconv -f video4linux2 -s 640x480 -i /dev/video0 -ss 0:0:2 -frames 1 $1 &> /dev/null
