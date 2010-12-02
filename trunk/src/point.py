# *-* coding: utf-8 *-*

from base import RawImage, BMPImage, RGB_COLORS, RED, GREEN, BLUE
from math import log
from util import draw_histogram

class PointRawImage(RawImage):
    """ Raw image type that supports point operators"""
    pass


L = 256

class PointBMPImage(BMPImage):
    """ BMP format image that supports point operators"""
    
    def __add__(self, other):
        """ Image sum """
        if self.width != other.width or \
            self.height != other.height:
            raise ValueError

        copy = self.copy()
        for x in xrange(copy.width):
            for y in xrange(copy.height):
                for color in RGB_COLORS:
                    value1 = copy.get_pixel(x, y, color)
                    value2 = other.get_pixel(x, y, color) 
                    sum = value1 + value2
                    copy.set_pixel(x, y, color, sum)
        R = (L - 1) * 2     
        copy.normalize(0, max(copy.data))
        return copy
    
    def __sub__(self, other):
        """ Image difference"""
        if self.width != other.width or \
            self.height != other.height:
            raise ValueError
        copy = self.copy()
        for x in xrange(copy.width):
            for y in xrange(copy.height):
                for color in RGB_COLORS:
                    value1 = copy.get_pixel(x, y, color)
                    value2 = other.get_pixel(x, y, color) 
                    diff = value1 - value2
                    copy.set_pixel(x, y, color, diff)
        copy.normalize()
        return copy
    
    def __mul__(self, other):
        """ Image product (pixel-by-pixel)"""
        if self.width != other.width or \
            self.height != other.height:
            raise ValueError
        
        copy = self.copy()
        for x in xrange(copy.width):
            for y in xrange(copy.height):
                for color in RGB_COLORS:
                    value1 = copy.get_pixel(x, y, color)
                    value2 = other.get_pixel(x, y, color) 
                    prod = value1 * value2
                    copy.set_pixel(x, y, color, prod)
        copy.normalize(0, max(copy.data))
        return copy
    
    def __rmul__(self, n):
        """Scalar product of an image """
        if type(n) not in [int, float]:
            raise ValueError
        
        copy = self.copy()
        copy._map(lambda r: n * r)
        
        copy.normalize()
        return copy
    
    def __iter__(self):
        for x in xrange(self.width):
            for y in xrange(self.height):
                for color in RGB_COLORS:
                    yield self.get_pixel(x, y, color)
    
    def _map(self, function):
        """ Evaluates a function for every pixel in the image,
        and if the function returns a value, it assigns this
        new value to the pixel in the image """
        for x in xrange(self.width):
            for y in xrange(self.height):
                for color in RGB_COLORS:
                    value = self.get_pixel(x, y, color)
                    modified = function(value)
                    if modified is not None:
                        self.set_pixel(x, y, color, modified)
    
    def _map_rgb(self, function):
        """ Same as _map, but evaluates the function over each
        3-tuple of r,g,b values instead of over each byte. """
        for x in xrange(self.width):
            for y in xrange(self.height):
                r, g, b = [self.get_pixel(x, y, c) for c in [RED, GREEN, BLUE]]
                t = function(r, g, b)
                if t is not None: 
                    r2, g2, b2 = t  
                    for color, v in [(RED, r2), (GREEN, g2), (BLUE, b2)]:
                        self.set_pixel(x, y, color, v)
    
    def negate(self):
        """ Negates every pixel in the image. """
        self._map(lambda r: L - 1 - r)
        return self
        
    def thresholdize(self, u=None):
        """ Takes each pixel to an extreme evaluating if it is below
        or over a certain threshold. """
        if not u:
            u = self.mean_pixel()
        self._map(lambda r: 0 if r <= u else L - 1)
        return self
    
    def thresholdizeRGB(self, tr, tg, tb):
        """ Takes each pixel to an extreme evaluating if it is below
        or over a certain threshold, for each color channel. """
        self._map_rgb(lambda r, g, b: 
                (0 if r <= tr else L - 1, 
                0 if g <= tg else L - 1, 
                0 if b <= tb else L - 1))
        return self
        
    def contrastize(self, r1, r2):
        """ Enhances contrast of image by making bright colors
        brighter and dark colors darker. r1 and r2 are the limits
        of what is considered a dark color or a bright color."""
        assert 0 <= r1 < r2 <= L - 1
        t1 = L / 4
        t2 = 3 * L / 4  
        def contrast(byte):
            if 0 <= byte <= r1:
                return byte * (t1 / r1)
            elif r1 < byte <= r2:
                m = ((t2 - t1) / (r2 - r1))
                b = t2 - m * r2
                return m * byte + b
            elif r2 < L - 1:
                m = ((L - 1 - t2) / (L - 1 - r2))
                b = t2 - m * r2
                return m * byte + b
        self._map(contrast)
        return self
    
    def black_and_white(self):
        """ Turns a color image to black and white. """
        
        # mean transform
        #self._map_rgb(lambda r,g,b: ((r+g+b)/3, (r+g+b)/3, (r+g+b)/3))
        
        # luma transform
        def luma_transform(r, g, b):
            l = r * 299.0 / 1000 + g * 587.0 / 1000 + b * 114.0 / 1000
            return (l, l, l)
        self._map_rgb(luma_transform)
        return self
    
    
    def histogram(self):
        """ Returns the histogram of byte values in the image, 
        represented as a dictionary containing three dictionaries,
        one for each color in RGB. Each of these dictionaries 
        contains a mapping from byte value to occurrence number. """
        hist = {RED:{}, GREEN: {}, BLUE: {}}
        for color in hist:
            for i in xrange(L):
                hist[color][i] = 0
        
        def f(r, g, b):
            hist[RED][int(r)] += 1
            hist[GREEN][int(g)] += 1
            hist[BLUE][int(b)] += 1
        
        self._map_rgb(f)
        return hist

    def draw_histogram(self):
        """ Paint the image histogram in a new image and draw it."""
        h = self.histogram()
        im = PointBMPImage.blank(256 + 40, 100 + 40)
        maxim = max([max(hc.values()) for hc in h.values()])
        for color in h:
            hc = h[color]
            for index in hc:
                height = (hc[index] * 100) / maxim
                for col in xrange(height):
                    im.set_pixel(index + 20, 140 - (col + 20), color, 255)
        im.draw()
    
    def mean_pixel(self, histogram=None):
        """ Get the mean value of all pixels.
        If histogram is provided, it is used, as it is faster
        to obtain analyzing it than analyzing the whole image. """
    
        if histogram:
            # faster version using histogram
            upper = 0.0
            lower = 0.0
            for color in RGB_COLORS:
                for r in xrange(L):
                    value = histogram[color][r]
                    upper += value * r
                    lower += value
            
            return upper / lower
        # slower, histogramless version
        d = {"sum" : 0.0}
        def f(r):
            d["sum"] += r
        self._map(f)
        return d["sum"] / (self.width * self.height * 3)
    
    def autocontrastize(self, histogram):
        """ Adjust contrast automatically analyzing the 
        image's histogram. It takes the contrast function with
        the weighted mean of the pixel values as the limit
        for enhancement or reduction of brightness"""
        mean = self.mean_pixel(histogram)
        self.contrastize(mean - 32, mean + 32)
        return self
    
    def equalize(self, histogram):
        """ Equalize histogram so that the probability
        distribution function becomes uniform (Fx(X) = X) """
        n = self.width * self.height
        def t(r, g, b):
            R, G, B = 0.0, 0.0, 0.0
            for j in xrange(int(r)):
                nj = float(histogram[RED][j])
                R += nj / n
            for j in xrange(int(g)):
                nj = float(histogram[GREEN][j])
                G += nj / n
            for j in xrange(int(b)):
                nj = float(histogram[BLUE][j])
                B += nj / n
            return R, G, B
        
        self._map_rgb(t)
        
        smin = min(self.data)
        self._map(lambda r: int((r - smin) * (L - 1) / (1 - smin) + 0.5))
        
        return self
    
    def normalize(self, Q=None, R=None):
        """ Makes all image's pixels fall in the valid range [0, L-1].
        R is the maximum value it can take. """
        
        if not Q:
            Q = min(self.data)
        if not R:
            R = max(self.data)
        
        # logarithmic
        #c = (L-1) / log(1+R)
        #self._map(lambda r: c * log(1+r))
        
        # linear
        if R == Q:
            return self
                
        m = (L - 1) / (R - Q)
        b = -m * Q
        self._map(lambda r: m * r + b)
        return self
    



if __name__ == "__main__":
    # loading images from files
    megan = PointBMPImage("images/MEGAN.BMP")
    robot = PointBMPImage("images/MARS.BMP")
    draw_histogram(megan.data)
    
    # image sum
    sum = megan + robot
    sum.draw()
    
    #image product
    prod = megan * robot
    prod.draw()
    
    # scalar product of an image
    scalar = 5 * megan
    scalar.draw()
    
    # difference between images
    diff = megan - robot
    diff.draw()
    
    # negative of an image
    negative = megan.copy().negate()
    negative.draw()
    
    # histogram
    print megan.histogram()
    
    # autocontrast with histogram
    lc = PointBMPImage("images/low_contrast.bmp")
    
    lc.draw()
    lc.save("1a.bmp")
    lc.autocontrastize(lc.histogram())
    lc.autocontrastize(lc.histogram())
    lc.save("1b.bmp")
    lc.draw()
    
    # threshold at L/2
    thr = megan.copy().black_and_white().thresholdize(L / 2)
    thr.draw()
    
   
