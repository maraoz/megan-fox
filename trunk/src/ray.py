# *-* coding: utf-8 *-*

from base import RGB_COLORS, RED, GREEN, BLUE
from border import BorderBMPImage, L
from math import log, fabs, atan2, pi, sqrt
from random import random

from util import get_LoG_element

import os


class Vector(object):
    def __init__(self, x, y, z):
        self.x, self.y, self.z = float(x), float(y), float(z)
    def norm(self):
        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
    
    def normalize(self):
        n = self.norm()
        self.x /= n
        self.y /= n
        self.z /= n
        return self
    
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def distance(self, other):
        diff = self - other
        return diff.norm()
    
    def __repr__(self):
        return "(%g, %g, %g)" % (self.x, self.y, self.z)
        
        

class Camera(object):
    def __init__(self, pos):
        self.pos = pos

class Sphere(object):
    def __init__(self, origin, radius):
        self.origin = origin
        self.radius = radius
    
    def contains(self, point):
        dist = self.origin.distance(point)
        return dist <= self.radius

class Ray(object):
    
    def __init__(self, origin, dir):
        self.origin = origin
        self.dir = dir
        self.ttl = 100
    
    def intersects(self, obj):
        pass
        


class Scene(object):
    
    def __init__(self, width, height, camera, objects):
        self.image = BorderBMPImage.blank(width, height, 0.0)
        self.camera = camera
        
        self.objects = objects
    
    def render(self):
        for xi in xrange(self.image.width):
            for yi in xrange(self.image.height):
                for color in RGB_COLORS:
                    x = xi - self.image.width / 2
                    y = yi - self.image.height / 2
                    origin = camera.pos
                    dir = origin - Vector(x,y,0)
                    dir = dir.normalize()
                    r = Ray(origin, dir)
                    for obj in self.objects:
                        value = r.intersects()
                        if value:
                            self.image.set_pixel(xi,yi,color, value)
        
    

        
if __name__ == "__main__":
    v = Vector(1, 1, 1)
    print v.normalize()
    
    p = Vector(1, 2, 0)
    s = Sphere(Vector(0, 200, 500), 100)
    print s.contains(p)
    
    cam = Camera(Vector(0,0,-500))
    
    
