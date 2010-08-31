# *-* coding: utf-8 *-*

from base import RGB_COLORS, RED, GREEN, BLUE
from point import PointBMPImage, L
from math import log
from random import random

from util import draw_histogram, rand_exponential, rand_rayleigh, rand_gaussian
    



class SpaceBMPImage(PointBMPImage):
    """ BMP format image that supports spatial and point operators"""
    
    def add_gaussian_noise(self, sigma_squared):
        self._map(lambda r: r + rand_gaussian(0, sigma_squared))
        self.normalize()
        return self
    
    def add_rayleigh_noise(self, xi):
        self._map(lambda r: r * rand_rayleigh(xi))
        self.normalize()
        return self

    def add_exponential_noise(self, lam):
        self._map(lambda r: r * rand_exponential(lam))
        self.normalize()
        return self

    def add_salt_and_pepper_noise(self, p0 = 0.10, p1 = 0.90):
        assert 0 <= p0 < p1 <= 1 
        def f(r,g,b):
            x = random()
            if x <= p0:
                return 0,0,0
            if p1 <= x:
                return L,L,L
        self._map_rgb(f)
        self.normalize()
        return self

if __name__ == "__main__":
    
    # load image from file
    megan = SpaceBMPImage("images/MEGAN.BMP")
    gaussian = megan.copy().add_gaussian_noise(15)
    gaussian.draw()
    gaussian.save("gaussian.bmp")
    
    rayleigh = megan.copy().add_rayleigh_noise(0.001)
    rayleigh.draw()
    rayleigh.save("rayleigh.bmp")
    
    exponential = megan.copy().add_exponential_noise(1)
    exponential.draw()
    exponential.save("exponential.bmp")
    
    snp = megan.black_and_white().add_salt_and_pepper_noise()
    snp.draw()
    snp.save("salt&pepper.bmp")


