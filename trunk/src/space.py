# *-* coding: utf-8 *-*

from base import RGB_COLORS, RED, GREEN, BLUE
from point import PointBMPImage, L
from math import log
from random import random

from util import draw_histogram, rand_exponential, rand_rayleigh, rand_gaussian
from util import Matrix, EmptyMatrix, median
    



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

    def add_salt_and_pepper_noise(self, p0=0.10, p1=0.90):
        assert 0 <= p0 < p1 <= 1 
        def f(r, g, b):
            x = random()
            if x <= p0:
                return 0, 0, 0
            if p1 <= x:
                return L, L, L
        self._map_rgb(f)
        return self.normalize()

    def linear_filter(self, mask):
        m, n = len(mask), len(mask[0])
        a, b = m / 2, n / 2
        
        copy = self.copy()
        
        for x in xrange(self.width):
            for y in xrange(self.height):
                for color in RGB_COLORS:
                    total = 0
                    for s in xrange(-a, a + m % 2):
                        for t in xrange(-b, b + n % 2):
                            value = self.get_pixel(x + s, y + t, color)
                            weight = mask[s][t]
                            total += value * weight
                    copy.set_pixel(x, y, color, total)
        return copy
    
    def mean_filter(self, order):
        n = (2 * order + 1)
        m = [[1.0 / (n * n) for col in xrange(n)] for row in xrange(n)]
        return self.linear_filter(m)
    
    def lowpass_filter(self, order):
        n = (2 * order + 1)
        m = [[(0 if col == order and row == order else 1.0) / n * n \
              for col in xrange(n)] for row in xrange(n)]
        return self.linear_filter(m).normalize()
    def highpass_filter(self, order):
        n = (2 * order + 1)
        m = [[(n * n - 1 if col == order and row == order else - 1.0) \
              for col in xrange(n)] for row in xrange(n)]
        return self.linear_filter(m).normalize()
    
    def median_filter(self, order):
        a, b = order, order
        
        copy = self.copy()
        
        for x in xrange(self.width):
            for y in xrange(self.height):
                for color in RGB_COLORS:
                    group = [self.get_pixel(x + s, y + t, color) \
                             for s in xrange(-a, a + 1) \
                             for t in xrange(-b, b + 1) ]
                    m = median(group)
                    copy.set_pixel(x, y, color, m)
        return copy
    
    def detect_borders_roberts(self):
        one = self.linear_filter([[0, 0, 0], [0, 1, 0], [0, 0, -1]])
        two = self.linear_filter([[0, 0, 0], [0, 0, 1], [0, -1, 0]])
        bordered = one + two
        return bordered.normalize() 

    def detect_borders_prewitt(self):
        one = self.linear_filter([[-1, -1, -1], [0, 0, 0], [1, 1, 1]])
        two = self.linear_filter([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
        bordered = one + two
        return bordered.normalize() 

    def detect_borders_sobel(self):
        one = self.linear_filter([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
        two = self.linear_filter([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        bordered = one + two
        return bordered.normalize() 

if __name__ == "__main__":
    
    
    # load image from file
    megan = SpaceBMPImage("images/LITTLE_MEGAN.BMP")
    megan = megan.black_and_white()
    
    
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

    # apply mean filter with a 
    mean3 = megan.copy().mean_filter(5)
    mean3.save("mean.bmp")
    mean3.draw()
    
    # median filter of 7x7
    megan.copy().mean_filter(3).draw()
    
    # salt and peper noise reduced with median filter
    noisy = megan.add_salt_and_pepper_noise()
    noisy.save("snp.bmp")
    noisy.draw()
    noisy.median_filter(1).draw().save("snp_median.bmp")
    
    # highpass filter
    megan.highpass_filter(3).draw()
    
    # lowpass filter
    megan.lowpass_filter(5).draw()

    # roberts
    megan.detect_borders_roberts().thresholdize().draw()

    # prewitt
    megan.detect_borders_prewitt().thresholdize().draw()
    
    # sobel
    megan.detect_borders_sobel().thresholdize().draw()
