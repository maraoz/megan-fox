# *-* coding: utf-8 *-*

from base import RawImage, BMPImage, RGB_COLORS, RED, GREEN, BLUE
from math import log
    

class PointRawImage(RawImage):
    """ Raw image type that supports point operators"""
    pass


L = 256

class PointBMPImage(BMPImage):
    """ BMP format image that supports point operators"""
    
    def __add__(self, other):
        if self.width != other.width or \
            self.height != other.height:
            raise ValueError

        R = (L-1)*2     
        for y in xrange(self.width):
            for x in xrange(self.height):
                for color in RGB_COLORS:
                    value1 = self.get_pixel(x,y,color)
                    value2 = other.get_pixel(x,y,color) 
                    sum = value1+value2
                    self.set_pixel(x,y,color, sum)
        self.normalize(R)
        # TODO: should copy itself and return modified copy
        # this version affects left image in the sum (WRONG!)
    def __sub__(self, other):
        raise NotImplementedError
    
    def __rmul__(self, n):
        if type(n) is not int:
            raise ValueError
        R = n*(L-1)
        self._map(lambda r: n*r)
        self.normalize(R)
        # TODO: should copy itself and return modified copy
        # this version affects original image (WRONG!)
    
    def __iter__(self):
        for y in xrange(self.width):
            for x in xrange(self.height):
                for color in RGB_COLORS:
                    yield self.get_pixel(x,y, color)
    
    def _map(self, function):
        """ Evaluates a function for every pixel in the image,
        and if the function returns a value, it assigns this
        new value to the pixel in the image """
        for y in xrange(self.width):
            for x in xrange(self.height):
                for color in RGB_COLORS:
                    value = self.get_pixel(x,y, color)
                    modified = function(value)
                    if modified is not None:
                        self.set_pixel(x,y,color, modified)
    
    def _map_rgb(self, function):
        """ Same as _map, but evaluates the function over each
        3-tuple of r,g,b values instead of over each byte. """
        for y in xrange(self.width):
            for x in xrange(self.height):
                r, g, b = [self.get_pixel(x, y, c) for c in [RED, GREEN, BLUE]]
                t = function(r,g,b)
                if t is not None: 
                    r2, g2, b2 = t  
                    for color, v in [(RED, r2), (GREEN, g2), (BLUE, b2)]:
                        self.set_pixel(x, y, color, v)
    
    def negate(self):
        """ Negates every pixel in the image. """
        self._map(lambda r: L - 1 - r)
        
    def thresholdize(self, u):
        """ Takes each pixel to an extreme evaluating if it is below
        or over a certain threshold. """
        self._map(lambda r: 0 if r <= u else L - 1)
        
    def contrastize(self, r1, r2):
        """ Enhances contrast of image by making bright colors
        brighter and dark colors darker. r1 and r2 are the limits
        of what is considered a dark color or a bright color."""
        assert 0 <= r1 < r2 <= L -1
        t1 = L /4
        t2 = 3 * L / 4  
        def contrast(byte):
            if 0 <= byte <= r1:
                return byte * (t1 / r1)
            elif r1 < byte <= r2:
                m = ((t2-t1)/(r2-r1))
                b = t2 - m * r2
                return m * byte + b
            elif r2 < L -1:
                m = ((L - 1 -t2)/(L - 1 -r2))
                b = t2 - m * r2
                return m * byte + b
        self._map(contrast)
    
    def black_and_white(self):
        """ Turns a color image to black and white. """
        
        # mean transform
        #self._map_rgb(lambda r,g,b: ((r+g+b)/3, (r+g+b)/3, (r+g+b)/3))
        
        # luma transform
        def luma_transform(r,g,b):
            l = r * 299.0/1000 + g * 587.0/1000 + b * 114.0/1000
            return (l,l,l)
        self._map_rgb(luma_transform)
    
    
    def histogram(self):
        """ Returns the histogram of byte values in the image, 
        represented as a dictionary containing three dictionaries,
        one for each color in RGB. Each of these dictionaries 
        contains a mapping from byte value to occurrence number. """
        hist = {"r":{}, "g": {}, "b": {}}
        for color in hist:
            for i in xrange(L):
                hist[color][i] = 0
        
        def f(r,g,b):
            hist["r"][r] += 1
            hist["g"][g] += 1
            hist["b"][b] += 1
        
        self._map_rgb(f)
        return hist
    
    def normalize(self, R):
        """ Makes all image's pixels fall in the valid range [0, L-1].
        R is the maximum value it can take. """
        
        # logarithmic
        #c = (L-1) / log(1+R)
        #self._map(lambda r: c * log(1+r))
        
        # linear
        m = (L-1)/(R+0.0)
        self._map(lambda r: m*r)
    



if __name__ == "__main__":
    megan = PointBMPImage("images/MEGAN.BMP")
    megan.draw()
    megan.black_and_white()
    megan.draw()
