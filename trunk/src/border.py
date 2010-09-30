# *-* coding: utf-8 *-*

from base import RGB_COLORS, RED, GREEN, BLUE
from space import SpaceBMPImage, L
from math import log, fabs
from random import random

from util import draw_histogram, rand_exponential, rand_rayleigh, rand_gaussian
from util import Matrix, EmptyMatrix, median
from util import lorentzian, leclerquian 

import os
    



class BorderBMPImage(SpaceBMPImage):
    """ BMP format image that supports spatial, point operators and border detection"""
    
    def detect_borders_saddle(self):
        one = self.linear_filter([[1, 1, 1], [1, -2, 1], [-1, -1, -1]])
        two = self.linear_filter([[1, 1, 1], [1, -2, -1], [1, -1, -1]])
        three = self.linear_filter([[-1, 1, 1], [-1, -2, 1], [-1, 1, 1]])
        phawr = self.linear_filter([[1, 1, 1], [-1, -2, 1], [-1, -1, 1]])
        bordered = one.abs() + two.abs() + three.abs() + phawr.abs()
        return bordered.normalize()
    
    def detect_borders_kirsh(self):
        one = self.linear_filter([[5, 5, 5], [-3, 0,-3], [-3, -3,-3]])
        two = self.linear_filter([[5, -3, -3], [5, 0,-3], [5, -3,-3]])
        three = self.linear_filter([[5, 5, -3], [5, 0,-3], [-3, -3,-3]])
        phawr = self.linear_filter([[-3, 5, 5], [-3, 0,5], [-3, -3,-3]])
        bordered = one.abs() + two.abs() + three.abs() + phawr.abs()
        return bordered.normalize()
    
    def detect_borders_valley(self):
        one = self.linear_filter([[1,1,1], [0,0,0], [-1,-1,-1]])
        two = self.linear_filter([[1,0,-1], [1,0,-1], [1,0,-1]])
        three = self.linear_filter([[1,1,0], [1,0,-1], [0,-1,-1]])
        phawr = self.linear_filter([[0,1,1], [-1,0,1], [-1,-1,0]])
        bordered = one.abs() + two.abs() + three.abs() + phawr.abs()
        return bordered.normalize()
    
    def detect_borders_valley2(self):
        one = self.linear_filter([[1,2,1], [0,0,0], [-1,-2,-1]])
        two = self.linear_filter([[1,0,-1], [2,0,-2], [1,0,-1]])
        three = self.linear_filter([[2,1,0], [1,0,-1], [0,-1,-2]])
        phawr = self.linear_filter([[0,1,2], [-1,0,1], [-2,-1,0]])
        bordered = one.abs() + two.abs() + three.abs() + phawr.abs()
        return bordered.normalize()

if __name__ == "__main__":
    
    
    # load image from file
    megan = BorderBMPImage(os.path.join("images","LITTLE_MEGAN.BMP"))
    megan.black_and_white()
    megan.detect_borders_valley2().draw()
