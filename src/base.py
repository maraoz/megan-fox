# *-* coding: utf-8 *-*

import Image
import pygame
from array import array
pygame.init()

def draw(image):
    size = (image.width, image.height)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("image")
    surface = pygame.Surface(size)
    ar = pygame.PixelArray(surface)
    pygame.display.flip()
    
    if image.type == "raw":
        draw_raw(image, ar)
    elif image.type == "bmp":
        draw_bmp(image, ar)
    else:
        raise NotImplementedError
    
    del ar
    screen.blit (surface, (0, 0))
    pygame.display.flip()
    while 1:
        event = pygame.event.wait ()
        if event.type == pygame.QUIT:
            break
        if event.type == pygame.MOUSEBUTTONDOWN:
            break

def draw_raw(image, ar):
    
    for x in xrange(image.height):
        for y in xrange(image.width):
            value = image.get_pixel(x,y)
            ar[y, x] = (value, value, value)

def draw_bmp(image, ar):
    
    for x in xrange(image.height):
        for y in xrange(image.width):
            r = image.data[(x*image.width+y)*3]
            g = image.data[(x*image.width+y)*3+1]
            b = image.data[(x*image.width+y)*3+2]
            ar[y, x] = (r,g,b)

class MemoryImage(object):
    
    def __init__(self, filename, format = None):
        self.filename = filename
        if not format:
            format = filename.split(".")[-1]
            
        self.type = format.lower()
    

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




if __name__ == "__main__":
    
    draw(RawImage(290,207,"images/BARCO.RAW"))
    draw(RawImage(200,200,"images/FRACTAL.RAW"))
    draw(RawImage(389,164,"images/GIRL.RAW"))
    draw(RawImage(256,256,"images/LENA.RAW"))
    draw(RawImage(256,256,"images/LENAX.RAW"))
    draw(RawImage(256,256,"images/GIRL2.RAW"))
    draw(RawImage(256,256,"images/new.raw"))
    draw(FormatImage("images/MEGAN.BMP"))
    
    
    i = RawImage(256,256,"images/GIRL2.RAW")
    for x in xrange(10,20):
        for y in xrange(10,20):
            i.set_pixel(x,y,0)
    i.save("images/new.raw")