# *-* coding: utf-8 *-*

import Image
from array import array
from random import randint

import pyglet 

RGB_COLORS = RED, GREEN, BLUE = range(3)

class MemoryImage(object):
    """ Represents a image stored in memory. Base type for all images"""
    
    def draw(self):
        """ Draws the image on screen using pygame.
        Delegates format-specific details to subclass
        method implementation in _do_draw() """
        size = (self.width, self.height)
        window = pyglet.window.Window(*size)
        window.set_location(0, 0)
        window.set_caption("(%d, %d)" % (self.width, self.height))
        window.manu_drawn = False
        
        @window.event
        def on_draw():
            if not window.manu_drawn:
                self._do_draw()
                window.manu_drawn = True
        @window.event
        def on_mouse_press(x, y, button, modifiers):
            window.close()
        
        pyglet.app.run()
        return self


    def copy(self):
        c = self.__class__()
        c.width = self.width
        c.height = self.height
        c.data = self.data[:]
        
        return c
        

    @classmethod
    def blank(cls, width, height, color = 0.0):
        obj = cls()
        obj.width, obj.height = width, height
        obj.data = array('d', cls._blank(width, height, color))
        return obj

    @classmethod
    def rectangle(cls, width, height, x0, y0, w, h):
        # TODO: fix, this is not working
        obj = cls()
        obj.width, obj.height = width, height
        obj.data = array('d', cls._rectangle(width, height, x0, y0, w, h))
        return obj
    
    
    @classmethod
    def _blank(cls, width, height, color=0.0):
        raise NotImplementedError
    
    @classmethod
    def _rectangle(cls, width, height, x0, y0, w, h):
        raise NotImplementedError

    def _do_draw(self, pixel_array):
        raise NotImplementedError

class EasyLoadImage(MemoryImage):
    """ Image which can be loaded using Python Image Library. """
    def __init__(self, filename=None):
        
        self.filename = filename

        if filename:
            im = Image.open(filename)
            self.data = array('d', [float(ord(c)) for c in im.tostring()])
            self.width, self.height = im.size

class GrayscaleImage(MemoryImage):
    """ Abstract 8-bit per pixel grayscale image type """
        
    def _do_draw(self):
        color_list = []
        coord_list = []
        for x in xrange(self.width):
            for y in xrange(self.height):
                coord_list.append(x)
                coord_list.append(y)
                for t in RGB_COLORS:
                    color_list.append(int(self.get_pixel(x, self.height - 1 - y)))
        pyglet.graphics.draw(self.width * self.height, pyglet.gl.GL_POINTS,
            ('v2i', tuple(coord_list)),
            ('c3B', tuple(color_list))
        )
        
    def get_pixel(self, x, y):
        return self.data[y * self.width + x]
    
    def set_pixel(self, x, y, value):
        self.data[y * self.width + x] = value
    
    def crop(self, x, y, width, height):
        new = GrayscaleImage.blank(width, height)
        for xp in xrange(width):
            for yp in xrange(height):
                value = self.get_pixel(xp + x, yp + y)
                new.set_pixel(xp, yp, value)
        return new
    
    @classmethod
    def _blank(cls, width, height, color=0.0):
        return [color for c in xrange(width * height)]
    @classmethod
    def _rectangle(cls, width, height, x0, y0, w, h):
        l = []
        for x in xrange(width):
            for y in xrange(height):
                if (x0 <= x <= x0 + w) and (y0 <= y <= y0 + h):
                    l.append(255.0)
                else:
                    l.append(0.0)
        return l


class ColorImage(MemoryImage):
    """ Abstract 8-bit per color image. """
    def _do_draw(self):
        color_list = []
        coord_list = []
        for x in xrange(self.width):
            for y in xrange(self.height):
                coord_list.append(x)
                coord_list.append(y)
                for c in RGB_COLORS:
                    color_list.append(int(self.get_pixel(x, self.height - 1 - y, c)))
        pyglet.graphics.draw(self.width * self.height, pyglet.gl.GL_POINTS,
            ('v2i', tuple(coord_list)),
            ('c3B', tuple(color_list))
        )
    
    def get_pixel(self, x, y, color):
        try:
            return self.data[(y * self.width + x) * 3 + color]
        except IndexError:
            return 0 
    
    def set_pixel(self, x, y, color, value):
        self.data[(y * self.width + x) * 3 + color] = value
    
    def crop(self, x, y, width, height):
        new = ColorImage.blank(width, height)
        for xp in xrange(width):
            for yp in xrange(height):
                for c in RGB_COLORS:
                    value = self.get_pixel(xp + x, yp + y, c)
                    new.set_pixel(xp, yp, c, value)
        return new
    
    
    @classmethod
    def _blank(cls, width, height, color=0.0):
        return [color for c in xrange(width * height * 3)]
    @classmethod
    def _rectangle(cls, width, height, x0, y0, w, h):
        l = []
        for x in xrange(width):
            for y in xrange(height):
                for c in xrange(3):
                    if (x0 <= x <= x0 + w) and (y0 <= y <= y0 + h):
                        l.append(255.0)
                    else:
                        l.append(0.0)
        return l
    






class RawImage(GrayscaleImage):
    """ Raw image type """
    def __init__(self, width=None, height=None, filename=None):
        if filename and width and height:
            fin = open(filename)
            self.data = array('d', [float(ord(c)) for c in fin.read()])
            self.width, self.height = width, height
        
    def save(self, filename):
        fout = open(filename, "w")
        fout.write(self.data.tostring())
        fout.close()
        return self
    
    
        
class PGMImage(EasyLoadImage, GrayscaleImage):
    """ PGM Image Format"""
    def save(self, filename):
        new_image = Image.fromstring('L', (self.width, self.height), \
                    "".join([chr(int(c)) for c in self.data]))
        # PGM not supported, saving in PNG format
        new_image.save(filename.lower().replace("pgm", "png"), "PNG")

class PPMImage(EasyLoadImage, ColorImage):
    """ PPM Image Format"""
    def save(self, filename):
        new_image = Image.fromstring('RGB', (self.width, self.height), \
                    "".join([chr(int(c)) for c in self.data]))
        new_image.save(filename, "PPM")

class BMPImage(EasyLoadImage, ColorImage):
    
    def save(self, filename):
        new_image = Image.fromstring('RGB', (self.width, self.height), \
                    "".join([chr(int(c)) for c in self.data]))
        new_image.save(filename, "BMP")
        
    def to_raw(self, i):

        n = RawImage.blank(self.width, self.height, 0)
        fout = open('out/'+str(i)+".raw", "w")
        print 'out/'+self.filename.split("/")[-1]+".raw"
        #fout.write("[ ");
        for y in xrange(self.height):
            for x in xrange(self.width):
                if y % 20 == 0:
                    fout.write(str(int(255.0))+" ")#(", " if x != self.width-1 else ""))
                else:
                    fout.write(str(int(self.get_pixel(x, y, GREEN)))+" ")#(", " if x != self.width-1 else ""))
            fout.write("\n")
            #fout.write(";\n" if y != self.height -1 else "\n")
        #fout.write("]")
        fout.close()
        return n



def display_greyscale_gradient():
    image = GrayscaleImage.blank(255, 255)
    for x in xrange(image.width):
        for y in xrange(image.height):
            image.set_pixel(x, y, x)
    image.draw()

def display_color_gradient():
    image = ColorImage.blank(256, 256)
    for x in xrange(image.width):
        for y in xrange(image.height):
            image.set_pixel(x, y, BLUE, x)
            image.set_pixel(x, y, GREEN, y)
            image.set_pixel(x, y, RED, 128)
    image.draw()

def display_grayscale_random():
    image = GrayscaleImage.blank(256, 256)
    for x in xrange(image.width):
        for y in xrange(image.height):
            image.set_pixel(x, y, randint(0, 255))
    image.draw()

def display_color_random():
    image = ColorImage.blank(256, 256)
    for x in xrange(image.width):
        for y in xrange(image.height):
            for c in RGB_COLORS:
                image.set_pixel(x, y, c, randint(0, 255))
    image.draw()


if __name__ == "__main__":
    
    

    fin = open("nombre.txt")
    i = 1
    for line in fin:
        bmp = BMPImage(line.strip())
        
        raw = bmp.to_raw(i)
        i+=1
    exit(0)



    # loading and drawing images of all 4 types
    PGMImage("images/TEST.PGM").draw()
    PPMImage("images/WEST.PPM").draw()
    barco = RawImage(290, 207, "images/BARCO.RAW").draw()
    megan = BMPImage("images/MEGAN.BMP").draw()
    
    # creating a blank image file
    width = height = 200
    pgm = PGMImage.blank(width, height).draw()
    ppm = PPMImage.blank(width, height).draw()
    raw = RawImage.blank(width, height).draw()
    bmp = BMPImage.blank(width, height).draw()
    
    # pixel-wise edition of an image
    for x in xrange(10, 50):
        for y in xrange(10, 50):
            pgm.set_pixel(x, y, 0)
    for x in xrange(10, 50):
        for y in xrange(10, 50):
            for c in RGB_COLORS:
                ppm.set_pixel(x, y, c, 0)
    for x in xrange(10, 50):
        for y in xrange(10, 50):
            raw.set_pixel(x, y, 0)
    for x in xrange(10, 50):
        for y in xrange(10, 50):
            for c in RGB_COLORS:
                bmp.set_pixel(x, y, c, 0)
    
    
    # saving all 4 image types
    pgm.save("blank.pgm")
    ppm.save("blank.ppm")
    raw.save("blank.raw")
    bmp.save("blank.bmp")
    
    # display grayscale gradient
    display_greyscale_gradient()
    # display color gradient
    display_color_gradient()

    # display random color image
    display_color_random()
    # display random grayscale image
    display_grayscale_random()
    
    
    # cropping images
    megan.crop(200,100,200,200).draw()
    barco.crop(100,100,100,100).draw()
    

    # displaying all remaining raw images
    RawImage(200, 200, "images/FRACTAL.RAW").draw()
    RawImage(389, 164, "images/GIRL.RAW").draw()
    RawImage(256, 256, "images/LENA.RAW").draw()
    RawImage(256, 256, "images/LENAX.RAW").draw()
    RawImage(256, 256, "images/GIRL2.RAW").draw()
    
