# *-* coding: utf-8 *-*

from base import RGB_COLORS, RED, GREEN, BLUE
from space import SpaceBMPImage, L
from math import log, fabs, atan2, pi, degrees, radians
from random import random

from util import get_LoG_element

import os
    
FLATTENIZER = [
              (-1,-1,+1,+1), # pi/4,
              (0,+1,0,-1), # pi/2,
              (-1,+1,+1,-1), # 3*pi/4,
              (+1,0,-1,0), # 0
               ]



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
        one = self.linear_filter([[5, 5, 5], [-3, 0, -3], [-3, -3, -3]])
        two = self.linear_filter([[5, -3, -3], [5, 0, -3], [5, -3, -3]])
        three = self.linear_filter([[5, 5, -3], [5, 0, -3], [-3, -3, -3]])
        phawr = self.linear_filter([[-3, 5, 5], [-3, 0, 5], [-3, -3, -3]])
        bordered = one.abs() + two.abs() + three.abs() + phawr.abs()
        return bordered.normalize()
    
    def detect_borders_valley(self):
        one = self.linear_filter([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
        two = self.linear_filter([[1, 0, -1], [1, 0, -1], [1, 0, -1]])
        three = self.linear_filter([[1, 1, 0], [1, 0, -1], [0, -1, -1]])
        phawr = self.linear_filter([[0, 1, 1], [-1, 0, 1], [-1, -1, 0]])
        bordered = one.abs() + two.abs() + three.abs() + phawr.abs()
        return bordered.normalize()
    
    def detect_borders_valley2(self):
        one = self.linear_filter([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])
        two = self.linear_filter([[1, 0, -1], [2, 0, -2], [1, 0, -1]])
        three = self.linear_filter([[2, 1, 0], [1, 0, -1], [0, -1, -2]])
        phawr = self.linear_filter([[0, 1, 2], [-1, 0, 1], [-2, -1, 0]])
        bordered = one.abs() + two.abs() + three.abs() + phawr.abs()
        return bordered.normalize()
    
    def laplacian(self):
        one = self.linear_filter([[0, -1, 0], [-1, 4, -1], [0, -1, 0]])
        copy = one.__class__.blank(one.width, one.height, 0.0)
        for color in RGB_COLORS:
            for x in xrange(one.width):
                for y in xrange(one.height):
                    prev = one.get_pixel(x - 1, y, color)
                    value = one.get_pixel(x, y, color)
                    if prev * value < 0:
                        # sign change
                        copy.set_pixel(x, y, color, L - 1)
                    elif abs(prev * value) < 0.01:
                        # self of both is zero
                        if prev * one.get_pixel(x + 1, y, color) < 0:
                            # +,0,- or -,0,+ situation
                            copy.set_pixel(x, y, color, L - 1)
                        else:
                            # false sign change (+,0,+ or -,0,-)
                            copy.set_pixel(x, y, color, 0.0)
                    else:
                        # no sign change, +,+, -,-
                        copy.set_pixel(x, y, color, 0.0)
                        
        return copy
    
    def laplacian_variance(self, threshold=L / 2):
        one = self.linear_filter([[0, -1, 0], [-1, 4, -1], [0, -1, 0]])
        return one.crosses_through_zero(threshold)
    
    def marr_hildreth(self, order=3, sigma=1.0, threshold=L / 2):
        m = self.get_LoG_filter(order, sigma)
        one = self.linear_filter(m)
        return one.crosses_through_zero(threshold)
        
    def crosses_through_zero(self, threshold):
        copy = self.__class__.blank(self.width, self.height, 0.0)
        for color in RGB_COLORS:
            for x in xrange(self.width):
                for y in xrange(self.height):
                    prev = self.get_pixel(x - 1, y, color)
                    value = self.get_pixel(x, y, color)
                    if prev * value < 0:
                        # sign change
                        if abs(prev) + abs(value) > threshold:
                            copy.set_pixel(x, y, color, L - 1)
                    elif abs(prev * value) < 0.01:
                        # one of both is zero
                        next = self.get_pixel(x + 1, y, color)
                        if prev * next < 0:
                            # +,0,- or -,0,+ situation
                            if abs(prev) + abs(next) > threshold:
                                copy.set_pixel(x, y, color, L - 1)
                        else:
                            # false sign change (+,0,+ or -,0,-)
                            copy.set_pixel(x, y, color, 0.0)
                    else:
                        # no sign change, +,+, -,-
                        copy.set_pixel(x, y, color, 0.0)
        return copy

        
        
    
    def get_LoG_filter(self, order, sigma):
        n = (2 * order + 1)
        # x = col - order
        # y = row - order
        m = [[ get_LoG_element(col - order, row - order, sigma) \
              for col in xrange(n)] for row in xrange(n)]
        return m
    
    def gaussianate(self, sigma):
        self.isotropic_diffusion(int(sigma))
    
    def get_border_directions(self):
        gx = self.linear_filter([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        gy = self.linear_filter([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
        return gx, gy
    
    def gradient_angle(self, gx, gy):
        ret = self.__class__.blank(self.width, self.height, 0.0)
        for color in RGB_COLORS:
            for x in xrange(self.width):
                for y in xrange(self.height):
                    dx = gx.get_pixel(x, y, color)
                    dy = gy.get_pixel(x, y, color)
                    value = atan2(dy,dx)
                    ret.set_pixel(x, y, color, value)
        return ret

    def flattenize(self, phi):
        phi -= pi / 8.0
        if phi >= pi:
            phi -= pi
        if phi < 0:
            phi += pi
        z = int(phi / (pi/4.0))
        return FLATTENIZER[z]
        
    def no_max_supress(self, phi, epsilon):
        copy = self.copy()
        for color in RGB_COLORS:
            for x in xrange(self.width):
                for y in xrange(self.height):
                    value = self.get_pixel(x,y,color)
                    if value > epsilon:
                        phi_xy = phi.get_pixel(x,y,color)
                        dx1, dy1, dx2, dy2 = self.flattenize(phi_xy)
                        n1 = self.get_pixel(x+dx1, y+dy1, color)
                        n2 = self.get_pixel(x+dx2, y+dy2, color)
                        if value < n1 or value < n2:
                            copy.set_pixel(x,y,color, 0.0)
        return copy
    def histerical_umbralization(self, t1, t2):
        if t1 > t2:
            raise ValueError
        ret = self.__class__.blank(self.width, self.height, 0.0)
        for color in RGB_COLORS:
            for x in xrange(self.width):
                for y in xrange(self.height):
                    value = self.get_pixel(x,y,color)
                    if value > t2:
                        ret.set_pixel(x,y,color, L-1)
                    elif t1 < value <= t2:
                        if any((ret.get_pixel(x+dx,y+dy,color) == L-1 \
                                for (dx, dy) in [(0,1),(0,-1),(1,0),(-1,0)])):
                            ret.set_pixel(x,y,color, L-1)
                    else:
                        ret.set_pixel(x,y,color, 0.0)
        return ret
    
    def canny(self):
        self.gaussianate(1.0)
        print 1
        gx, gy = self.get_border_directions()
        print 2
        phi = self.gradient_angle(gx, gy)
        print 3
        
        start = gx.abs() + gy.abs()
        print 4
        nms = start.no_max_supress(phi, 0.1)
        print 5
        h = nms.histerical_umbralization(50,80)
        print 6
        return h
        
if __name__ == "__main__":
    
    
    # load image from file
    megan = BorderBMPImage(os.path.join("images", "LITTLE_MEGAN.BMP"))
    megan.black_and_white()
    
    megan.canny().draw()
