# *-* coding: utf-8 *-*

from base import RGB_COLORS, RED, GREEN, BLUE
from point import PointBMPImage, L
from math import log
from random import random

from util import draw_histogram, rand_exponential, rand_rayleigh, rand_gaussian
from util import Matrix, EmptyMatrix
    



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

    def linear_mask(self, mask):
        m, n = len(mask), len(mask[0])
        if m % 2 != 1 or n % 2 != 1:
            raise ValueError("Mask must have odd number of rows and columns")
        a, b = (m-1)/2, (n-1)/2
        
        copy = self.copy()
        
        for x in xrange(self.width):
            for y in xrange(self.height):
                for color in RGB_COLORS:
                    total = 0
                    for s in xrange(-a,a+1):
                        for t in xrange(-b, b+1):
                            value = self.get_pixel(x+s, y+t, color)
                            weight = mask[s][t]
                            total += value * weight
                    copy.set_pixel(x, y, color, total)
        return copy
    
    def mean_mask(self, order):
        n = (2*order+1)
        m = [[1.0/(n*n) for col in xrange(n)] for row in xrange(n)]
        return self.linear_mask(m)

if __name__ == "__main__":
    
    # load image from file
    megan = SpaceBMPImage("images/MEGAN.BMP")
    mean1 = megan.mean_mask(5)
    mean1.save("mean.bmp")
    mean1.draw()
    exit(0)
    # add gaussian noise
    gaussian = megan.copy().add_gaussian_noise(15)
    gaussian.draw()
    gaussian.save("gaussian.bmp")
    
    # add rayleigh noise
    rayleigh = megan.copy().add_rayleigh_noise(0.001)
    rayleigh.draw()
    rayleigh.save("rayleigh.bmp")
    
    # add exponential noise
    exponential = megan.copy().add_exponential_noise(1)
    exponential.draw()
    exponential.save("exponential.bmp")
    
    # add sant and pepper noise
    snp = megan.black_and_white().add_salt_and_pepper_noise()
    snp.draw()
    snp.save("salt&pepper.bmp")


