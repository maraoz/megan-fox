# *-* coding: utf-8 *-*

import Image
import pygame
from array import array
pygame.init()





class MemoryImage(object):
    """ Represents a image stored in memory. Base type for all images"""
    
    def __init__(self, filename, format = None):
        # TODO: constructor loads image from file, should be able
        # to create an image independently from a file 
        self.filename = filename
        if not format:
            format = filename.split(".")[-1]
            
        self.type = format.lower()
    
    def draw(self):
        """ Draws the image on screen using pygame.
        Delegates format-specific details to subclass
        method implementation in _do_draw() """
        size = (self.width, self.height)
        screen = pygame.display.set_mode(size)
        pygame.display.set_caption("image, "+str(size))
        surface = pygame.Surface(size)
        pixel_array = pygame.PixelArray(surface)
        pygame.display.flip()
        
        self._do_draw(pixel_array)
        
        del pixel_array
        screen.blit (surface, (0, 0))
        pygame.display.flip()
        
        # display image until window clicked
        while 1:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                break
            if event.type == pygame.MOUSEBUTTONDOWN:
                break
    def _do_draw(self, pixel_array):
        raise NotImplementedError
    

class RawImage(MemoryImage):
    """ Raw image type """
    def __init__(self, width, height, *args, **kwargs):
        MemoryImage.__init__(self, *args, **kwargs)
        if self.type == "raw":
            fin = open(self.filename)
            self.data = array('B', fin.read())
            self.width, self.height = width, height
        else:
            raise ValueError("Invalid format for raw image")
        
    def _do_draw(self, pixel_array):
        for x in xrange(self.height):
            for y in xrange(self.width):
                value = self.get_pixel(x,y)
                pixel_array[y, x] = (value, value, value)
        
    def get_pixel(self, x, y):
        return self.data[x*self.width+y]
    
    def set_pixel(self, x, y, value):
        self.data[x*self.width+y] = value
    
    def save(self, filename):
        fout = open(filename, "w")
        fout.write(self.data.tostring())
        fout.close()
    
    def crop(self, x, y, width, height):
        pass
        
        
class FormatImage(MemoryImage):
    def __init__(self, *args, **kwargs):
        MemoryImage.__init__(self, *args, **kwargs)

        im = Image.open(self.filename)
        
        self.data = array('B', im.tostring())
        self.width, self.height = im.size

RGB_COLORS = RED, GREEN, BLUE = range(3)

class BMPImage(FormatImage):
    def _do_draw(self, pixel_array):
        for x in xrange(self.height):
            for y in xrange(self.width):
                r = self.get_pixel(x, y, RED)
                g = self.get_pixel(x, y, GREEN)
                b = self.get_pixel(x, y, BLUE)
                pixel_array[y, x] = (r,g,b)
    
    def get_pixel(self, x, y, color):
        return self.data[(x*self.width+y)*3 + color]
    
    def set_pixel(self, x, y, color, value):
        self.data[(x*self.width+y)*3 + color] = value
    
    def save(self, filename):
        new_image = Image.fromstring('RGB', (self.width, self.height), self.data.tostring())
        new_image.save(filename, "BMP")
    
    def crop(self, x, y, width, height):
        pass



if __name__ == "__main__":
    
    RawImage(290,207,"images/BARCO.RAW").draw()
    RawImage(200,200,"images/FRACTAL.RAW").draw()
    RawImage(389,164,"images/GIRL.RAW").draw()
    RawImage(256,256,"images/LENA.RAW").draw()
    RawImage(256,256,"images/LENAX.RAW").draw()
    RawImage(256,256,"images/GIRL2.RAW").draw()
    BMPImage("images/MEGAN.BMP").draw()
    
    
    i = RawImage(256,256,"images/GIRL2.RAW")
    for x in xrange(10,50):
        for y in xrange(10,50):
            i.set_pixel(x,y,0)
    i.draw()
    i.save("images/new.raw")