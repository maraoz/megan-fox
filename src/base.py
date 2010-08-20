# *-* coding: utf-8 *-*

import Image
from array import array

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

    @classmethod
    def blank(cls, width, height):
        obj = cls()
        obj.width, obj.height = width, height
        obj.data = array('d', cls._blank(width, height))
        return obj

    @classmethod
    def rectangle(cls, width, height, x0, y0, w, h):
        # TODO: fix, this is not working
        obj = cls()
        obj.width, obj.height = width, height
        obj.data = array('d', cls._rectangle(width, height, x0, y0, w, h))
        return obj
    
    
    @classmethod
    def _blank(cls, width, height):
        raise NotImplementedError
    
    @classmethod
    def _rectangle(cls, width, height, x0, y0, w, h):
        raise NotImplementedError
    
    def _do_draw(self, pixel_array):
        raise NotImplementedError

class EasyLoadImage(MemoryImage):
    """ Image which can be loaded using Python Image Library. """
    def __init__(self, filename=None):

        if filename:
            im = Image.open(filename)
            self.data = array('d', [float(ord(c)) for c in im.tostring()])
            self.width, self.height = im.size

class GrayscaleImage(MemoryImage):
    """ Abstract 8-bit per pixel grayscale image type """
        
    def _do_draw(self):
        color_list = []
        coord_list = []
        for x in xrange(self.height):
            for y in xrange(self.width):
                coord_list.append(y)
                coord_list.append(self.height - x)
                for t in RGB_COLORS:
                    color_list.append(int(self.get_pixel(x, y)))
        pyglet.graphics.draw(self.width * self.height, pyglet.gl.GL_POINTS,
            ('v2i', tuple(coord_list)),
            ('c3B', tuple(color_list))
        )
        
    def get_pixel(self, x, y):
        return self.data[x * self.width + y]
    
    def set_pixel(self, x, y, value):
        self.data[x * self.width + y] = value
    
    @classmethod
    def _blank(cls, width, height):
        return [255.0 for c in xrange(width * height)]
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
        for x in xrange(self.height):
            for y in xrange(self.width):
                coord_list.append(y)
                coord_list.append(self.height - x)
                for c in RGB_COLORS:
                    color_list.append(int(self.get_pixel(x, y, c)))
        pyglet.graphics.draw(self.width * self.height, pyglet.gl.GL_POINTS,
            ('v2i', tuple(coord_list)),
            ('c3B', tuple(color_list))
        )
    
    def get_pixel(self, x, y, color):
        return self.data[(x * self.width + y) * 3 + color]
    
    def set_pixel(self, x, y, color, value):
        self.data[(x * self.width + y) * 3 + color] = value
    
    @classmethod
    def _blank(cls, width, height):
        return [255.0 for c in xrange(width * height * 3)]
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
    
    def crop(self, x, y, width, height):
        pass
        
        
            



class PGMImage(EasyLoadImage, GrayscaleImage):
    """ PGM Image Format"""

class PPMImage(EasyLoadImage, ColorImage):
    """ PPM Image Format"""

class BMPImage(EasyLoadImage, ColorImage):
    
    def save(self, filename):
        new_image = Image.fromstring('RGB', (self.width, self.height), \
                    "".join([chr(int(c)) for c in self.data]))
        new_image.save(filename, "BMP")
    
    def crop(self, x, y, width, height):
        pass



if __name__ == "__main__":

    PGMImage("images/TEST.PGM").draw()
    PPMImage("images/WEST.PPM").draw()
    RawImage(290, 207, "images/BARCO.RAW").draw()
    BMPImage("images/MEGAN.BMP").draw()
    
    width = height = 200
    PGMImage.blank(width, height).draw()
    PPMImage.blank(width, height).draw()
    RawImage.blank(width, height).draw()
    BMPImage.blank(width, height).draw()
    
    PPMImage("images/WEST.PPM").draw()
    RawImage(290, 207, "images/BARCO.RAW").draw()
    BMPImage("images/MEGAN.BMP").draw()
    

    RawImage(200, 200, "images/FRACTAL.RAW").draw()
    RawImage(389, 164, "images/GIRL.RAW").draw()
    RawImage(256, 256, "images/LENA.RAW").draw()
    RawImage(256, 256, "images/LENAX.RAW").draw()
    RawImage(256, 256, "images/GIRL2.RAW").draw()
    
    
    i = RawImage(256, 256, "images/GIRL2.RAW")
    for x in xrange(10, 50):
        for y in xrange(10, 50):
            i.set_pixel(x, y, 0)
    i.draw()
    i.save("images/new.raw")

