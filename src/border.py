# *-* coding: utf-8 *-*

from base import RGB_COLORS, RED, GREEN, BLUE
from space import SpaceBMPImage, L
from math import log, fabs, atan2, pi, degrees, radians, sqrt, cos, sin
from random import random

from util import get_LoG_element

import os
    
FLATTENIZER = [
              (-1, -1, +1, +1), # pi/4,
              (0, +1, 0, -1), # pi/2,
              (-1, +1, +1, -1), # 3*pi/4,
              (+1, 0, -1, 0), # 0
               ]

SUSAN_MASK = [    [1, 1, 1],
               [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
               [1, 1, 1, 1, 1],
                  [1, 1, 1]
            ]

SUSAN_PERCENTAGE_EPSILON = 0.12
SUSAN_PIXEL_EPSILON = 15
SUSAN_CORNER_RATIO = 0.75
SUSAN_BORDER_RATIO = 0.50

HOUGH_LINEAR_EPSILON =1.1#1.1
HOUGH_MAX_PERCENTAGE = 0.6
HOUGH_MAX_AMMOUNT = 10
HOUGH_CIRCULAR_EPSILON = 20

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
                    value = atan2(dy, dx)
                    ret.set_pixel(x, y, color, value)
        return ret

    def flattenize(self, phi):
        phi -= pi / 8.0
        if phi >= pi:
            phi -= pi
        if phi < 0:
            phi += pi
        z = int(phi / (pi / 4.0))
        return FLATTENIZER[z]
        
    def no_max_supress(self, phi, epsilon):
        copy = self.copy()
        for color in RGB_COLORS:
            for x in xrange(self.width):
                for y in xrange(self.height):
                    value = self.get_pixel(x, y, color)
                    if value > epsilon:
                        phi_xy = phi.get_pixel(x, y, color)
                        dx1, dy1, dx2, dy2 = self.flattenize(phi_xy)
                        n1 = self.get_pixel(x + dx1, y + dy1, color)
                        n2 = self.get_pixel(x + dx2, y + dy2, color)
                        if value < n1 or value < n2:
                            copy.set_pixel(x, y, color, 0.0)
        return copy
    def histerical_umbralization(self, t1, t2):
        if t1 > t2:
            raise ValueError
        ret = self.__class__.blank(self.width, self.height, 0.0)
        for color in RGB_COLORS:
            for x in xrange(self.width):
                for y in xrange(self.height):
                    value = self.get_pixel(x, y, color)
                    if value > t2:
                        ret.set_pixel(x, y, color, L - 1)
                    elif t1 < value <= t2:
                        if any((ret.get_pixel(x + dx, y + dy, color) == L - 1 \
                                for (dx, dy) in [(0, 1), (0, -1), (1, 0), (-1, 0)])):
                            ret.set_pixel(x, y, color, L - 1)
                    else:
                        ret.set_pixel(x, y, color, 0.0)
        ret.clean_borders()
        return ret
    
    def clean_borders(self):
        for x in xrange(self.width):
            for color in RGB_COLORS:
                self.set_pixel(x,0,color, 0.0)
                self.set_pixel(x,self.height-1,color, 0.0)
        for y in xrange(self.height):
            for color in RGB_COLORS:
                self.set_pixel(0,y,color, 0.0)
                self.set_pixel(self.width-1,y,color, 0.0)
        return self
    
    def canny(self, verbose=False, stop_at_no_max = False):
        if verbose: print "1: apply gaussian convolution"
        self.gaussianate(1.0)
        if verbose: print "2: obtain border directions"
        gx, gy = self.get_border_directions()
        if verbose: print "3: calculate gradient angle"
        phi = self.gradient_angle(gx, gy)
        
        start = gx.abs() + gy.abs()
        if verbose: print "4: supress no maximums"
        nms = start.no_max_supress(phi, 0.1)
        if stop_at_no_max:
            return nms.clean_borders()
        if verbose: print "5: apply histerical umbralization"
        h = nms.histerical_umbralization(50, 75)
        if verbose: print "6: Done!"
        return h
    
    
    def susan_corner_detector(self):
        def response(ratio):
            if fabs(ratio - SUSAN_CORNER_RATIO) < SUSAN_PERCENTAGE_EPSILON:
                return L - 1
            return 0.0

        return self.circular_filter(SUSAN_MASK, SUSAN_PIXEL_EPSILON, response)
    
    def susan_border_detector(self):
        def response(ratio):
            if fabs(ratio - SUSAN_BORDER_RATIO) < SUSAN_PERCENTAGE_EPSILON:
                return L - 1
            return 0.0
        return self.circular_filter(SUSAN_MASK, SUSAN_PIXEL_EPSILON, response)
    
    def circular_filter(self, mask, threshold=10, get_susan_response=None):
        n = len(mask)
        b = n / 2
        
        if get_susan_response is None:
            raise ValueError
        
        count = 0
        for row in mask:
            for e in row:
                count += 1
        
        copy = self.copy()
        
        for x in xrange(self.width):
            for y in xrange(self.height):
                for color in RGB_COLORS:
                    total = 0
                    center_value = self.get_pixel(x, y, color)
                    for t in xrange(-b, b + n % 2):
                        m = len(mask[t + b])
                        a = m / 2
                        for s in xrange(-a, a + m % 2): 
                            value = self.get_pixel(x + s, y + t, color)
                            if fabs(center_value - value) < threshold:
                                total += 1
                    ratio = 1.0 - total / float(count)
                    response = get_susan_response(ratio)
                    copy.set_pixel(x, y, color, response)
        copy.clean_borders()
        return copy
    
    
    def hough_line_detector(self, n=20, detect_borders=False):
        image = self
        class LineSpace(dict):
            def initialize(self):
                D = max([image.width, image.height]) * sqrt(2)
        
                for i in xrange(n + 1):
                    for j in xrange(n + 1):
                        d = i*360.0/n
                        phi = d*2*pi/360.0
                        r = j * D / float(n)
                        self[(r, phi)] = 0
                print self
            def contains(self, parameters, x, y):
                rho, phi = parameters[0], parameters[1]
                pcos = cos(phi)
                psin = sin(phi)     
                return fabs(rho - x * pcos - y * psin) < HOUGH_LINEAR_EPSILON
            def get_parameters_votes(self):
                return self.values()
            def increment(self, parameters):
                self[parameters] += 1
            def __str__(self):
                pairs = [(self[k], k) for k in self.keys()]
                pairs.sort(reverse=False)
                ret = ""
                for value, key in pairs:
                    ret += str(key) + ": "+str(value)+"\n"
                return ret
        parameter_space = LineSpace()
        return self.hough_detector(n, detect_borders, parameter_space)
    
    def hough_circle_detector(self, n=20, detect_borders=False):
        image = self
        class CircleSpace(dict):
            def initialize(self):
                D = min([image.width, image.height]) * sqrt(2) / 2
                for i in xrange(n + 1):
                    for j in xrange(n + 1):
                        for k in xrange(n + 1):
                            self[(30 + k * D / float(n), 0 + i * image.width / float(n), 0 + j * image.height / float(n))] = 0
            def contains(self, parameters, x, y):
                r, x0, y0 = parameters[0], parameters[1], parameters[2]
                xd, yd = x - x0, y - y0
                return fabs(r * r - xd * xd - yd * yd) < HOUGH_CIRCULAR_EPSILON
            def get_parameters_votes(self):
                return self.values()
            def increment(self, parameters):
                self[parameters] += 1
        parameter_space = CircleSpace()
        return self.hough_detector(n, detect_borders, parameter_space)
                
    
    def hough_detector(self, n=20, detect_borders=False, parameter_space=None, fixed_ammount = True):
        if parameter_space is None:
            raise ValueError

        if detect_borders:
            self = self.susan_border_detector().draw()
            
        parameter_space.initialize()
        
        size = len(parameter_space)
        i = 0
        
        for parameters in parameter_space:
            i +=1 
            print i, "de", size
            for x in xrange(self.width):
                for y in xrange(self.height):
                    value = self.get_pixel(x, y, GREEN)
                    if value == float(L - 1) and \
                    parameter_space.contains(parameters, x, y):
                        parameter_space.increment(parameters)
                
        mx = max(parameter_space.get_parameters_votes())
        print "*"*70
        print parameter_space
        ret = self.__class__.blank(self.width, self.height, 0.0)
        
        #fixed_ammount = False
        if not fixed_ammount:
            print "in case 1, guess max ammount"
            threshold = mx#HOUGH_MAX_PERCENTAGE * mx
            
            for parameters in parameter_space:
                s = parameter_space[parameters]
                if s >= threshold:
                    ret.draw_guess(parameter_space, parameters)
        else:
            print "in case 2, fixed ammount of maxes"
            
            pairs = [(parameter_space[k], k) for k in parameter_space.keys()]
            pairs.sort(reverse=True)
            for i in xrange(HOUGH_MAX_AMMOUNT):
                print i
                value, key = pairs[i]
                print key, value
                ret.draw_guess(parameter_space, key)
            #for parameters in parameter_space.keys():
            #    if 0 < parameters[1] < pi:
            #        ret.draw_guess(parameter_space, parameters)
            #for i in xrange(5):
            #    for r in xrange(0,100,20):
            #        d = 90+80+i*10/5.0
            #        angle = d*2*pi/360
            #        ret.draw_guess(parameter_space, (r,angle))
                                    
        return ret
    
    def draw_guess(self, parameter_space, parameters):
        for x in xrange(self.width):
            for y in xrange(self.height):
                for color in RGB_COLORS:
                    if parameter_space.contains(parameters, x, y):
                        self.set_pixel(x, y, color, L - 1)
        
        
if __name__ == "__main__":
    
    
    
    p = BorderBMPImage(os.path.join("images", "3POINTS.BMP"))
    p.draw()
    h = p.hough_line_detector(30, detect_borders = False)
    h.draw()
    s = p+h
    s.draw()
    
    exit(0)
    
    c = BorderBMPImage(os.path.join("images", "3CIRCLES.BMP"))
    c.draw()
    h = c.hough_circle_detector(15, detect_borders = False)
    h.draw()
    s = c+h
    s.draw()
    
    
    
    # load image from file
    megan = BorderBMPImage(os.path.join("images", "LITTLE_MEGAN.BMP"))
    megan.black_and_white()
    megan.draw()
    
    print "punto 1"
    megan.detect_borders_saddle().draw()
    megan.detect_borders_kirsh().draw()
    megan.detect_borders_valley().draw()
    megan.detect_borders_valley2().draw()
    
    print "punto 2"
    megan.laplacian().draw()
    megan.laplacian_variance(80).draw()
    megan.marr_hildreth(3, 1.0, 50).draw()
    
    
    print "punto 3"
    megan.canny(verbose = True, stop_at_no_max = True).draw()
    
    
    print "puntos 4 y 5"
    megan.canny(verbose = True).draw()
    
    print "punto 6"

    test = BorderBMPImage(os.path.join("images", "TEST.BMP"))
    lena = BorderBMPImage(os.path.join("images", "LENA.BMP"))
    test_noisy = test.copy().add_gaussian_noise(10)
    lena_noisy = lena.copy().add_gaussian_noise(10)
    
    test.draw()
    lena.draw()
    test_noisy.draw()
    lena_noisy.draw()
    
    for image in [test, test_noisy]:
        image.susan_corner_detector().draw()
        image.susan_border_detector().draw()
    
    
    print "punto 7"
    
    for image in [test, test_noisy]:
        post = image.copy().hough_line_detector(20, detect_borders = True)
        s = post + test
        s.draw()
        
    
    print "punto 8"
    canned = BorderBMPImage(os.path.join("images", "LITTLE_COIN.BMP"))
    canned.draw()
    canned.black_and_white()
    canned.hough_circle_detector(10, True).draw()
    
    
    
    
    
    
    print "fin de la practica"
    canned = BorderBMPImage(os.path.join("images", "WDG3_MINI.BMP"))
    canned = canned.autocontrastize(canned.histogram())
    susaned = canned.susan_border_detector()
    houghed = susaned.hough_line_detector(20)
    d = canned + houghed
    d.draw() 
    
    #test = BorderBMPImage(os.path.join("images", "TEST.BMP"))
    #h = test.hough_line_detector(50, detect_borders = True).draw()
    #s = test + h
    #s.draw()
    
