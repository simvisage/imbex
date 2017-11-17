import numpy as np
import pylab as p
from scipy.signal import argrelextrema

x = np.linspace(0,2*np.pi,100)
y = np.sin(x) + np.random.random(100) * 0.8

def Smooth (y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

y_new = Smooth(y,40)

up_args = argrelextrema(y_new, np.greater)


p.plot(x, y, 'o')
p.plot(x, Smooth(y,3), 'r', lw=2)
p.plot(x, y_new , 'g', lw=2)
p.plot(x[up_args], y_new[up_args] , 'co', lw=2)


p.show()