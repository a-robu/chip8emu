import pygame
from pygame.locals import *

import math
import numpy

# I introduced this scaling factor because the beep used to be very loud.
# I hand-picked this quantity which is not too loud while it can still be
# heard clearly.
AMPLITUDE = 0.15

size = (1366, 720)

bits = 16
#the number of channels specified here is NOT 
#the channels talked about here http://www.pygame.org/docs/ref/mixer.html#pygame.mixer.get_num_channels

pygame.mixer.pre_init(44100, -bits, 2)
pygame.init()
#_display_surf = pygame.display.set_mode(size, pygame.HWSURFACE | pygame.DOUBLEBUF)


duration = 0.05         # in seconds
#freqency for the left speaker
frequency_l = 440
#frequency for the right speaker
frequency_r = 440

#this sounds totally different coming out of a laptop versus coming out of headphones

sample_rate = 44100

n_samples = int(round(duration*sample_rate))

#setup our numpy array to handle 16 bit ints, which is what we set our mixer to expect with "bits" up above
buf = numpy.zeros((n_samples, 2), dtype = numpy.int16)
max_sample = 2**(bits - 1) - 1

for s in range(n_samples):
    t = float(s)/sample_rate    # time in seconds

    #grab the x-coordinate of the sine wave at a given time, while constraining the sample to what our mixer is set to with "bits"
    buf[s][0] = int(round(max_sample*math.sin(2*math.pi*frequency_l*t) * AMPLITUDE))        # left
    buf[s][1] = int(round(max_sample*0.5*math.sin(2*math.pi*frequency_r*t) * AMPLITUDE))    # right

sound = pygame.sndarray.make_sound(buf)
#play once, then loop forever

def start():
    sound.play(loops = -1)

def stop():
    sound.stop()

