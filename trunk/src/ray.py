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
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __rmul__(self, other):
        return Vector(self.x * other, self.y * other, self.z * other)
    
    def distance(self, other):
        diff = self - other
        return diff.norm()
    
    def __repr__(self):
        return "(%g, %g, %g)" % (self.x, self.y, self.z)
        
        

class Camera(object):
    def __init__(self, pos):
        self.pos = pos


class Sphere(object):
    def __init__(self, origin, radius, color):
        self.origin = origin
        self.radius = radius
        self.color = color
    
    def contains(self, point):
        dist = self.origin.distance(point)
        return dist <= self.radius
    
    def get_tone(self, color):
        if self.color == color:
            return 255
        else:
            return 0

class Ray(object):
    
    def __init__(self, origin, dir):
        self.origin = origin
        self.dir = dir
        self.ttl = 200
    
    def intersects(self, obj):
        if self.ttl == 0:
            return False
        if obj.contains(self.origin):
            return True
        self.origin = self.origin + 10* self.dir
        self.ttl -= 1
        #print self.ttl, self.origin
        return self.intersects(obj)
        


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
                    origin = self.camera.pos
                    dir = Vector(x,y,0) - origin
                    dir = dir.normalize()
                    for obj in self.objects:
                        r = Ray(origin, dir)
                        value = r.intersects(obj)
                        if value:
                            tone = obj.get_tone(color)
                            self.image.set_pixel(xi,yi,color, tone)
        
    

        
if __name__ == "__main__":
    v = Vector(1, 1, 1)
    
    p = Vector(1, 2, 0)
    sp = Sphere(Vector(0, 0, 550), 20, RED)
    sp2 = Sphere(Vector(0, 10, 500), 20, GREEN)
    for i in xrange(-500,-300,20):
        c =  (i+300) /-20
        print i,c
        cam = Camera(Vector(c,c,i))
        s = Scene(50, 50, cam, [sp, sp2])
        s.render()
        s.image.save("arch"+str(-1*i)+".bmp")
    
