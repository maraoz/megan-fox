# *-* coding: utf-8 *-*

import Image
import pygame
from array import array
pygame.init()





class MemoryImage(object):
    
    def __init__(self, filename, format = None):
        self.filename = filename
        if not format:
            format = filename.split(".")[-1]
            
        self.type = format.lower()
    
    def draw(self):
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
        while 1:
            event = pygame.event.wait ()
            if event.type == pygame.QUIT:
                break
            if event.type == pygame.MOUSEBUTTONDOWN:
                break
    

class RawImage(MemoryImage):
    def __init__(self, width, height, *args, **kwargs):
        MemoryImage.__init__(self, *args, **kwargs)
        if self.type == "raw":
            fin = open(self.filename)
            self.data = array('B', fin.read())
            self.width, self.height = width, height
        else:
            raise ValueError("Invalid format for raw image")
        
    @classmethod
    def create(cls):
        pass
    
    
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
        
class BMPImage(FormatImage):
    def _do_draw(self, pixel_array):
        for x in xrange(self.height):
            for y in xrange(self.width):
                r = self.data[(x*self.width+y)*3]
                g = self.data[(x*self.width+y)*3+1]
                b = self.data[(x*self.width+y)*3+2]
                pixel_array[y, x] = (r,g,b)




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