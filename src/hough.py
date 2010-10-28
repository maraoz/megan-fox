'''
Created on Oct 28, 2010

@author: maraoz
'''


from ga import CrossoverGeneticAlgorithm
from random import randint, random, choice
from math import sqrt, sin, cos, pi
import pygame

from base import RGB_COLORS, RED, GREEN, BLUE
from border import BorderBMPImage, L
from math import log, fabs, atan2, pi, degrees, radians, sqrt, cos, sin
from random import random
import os

from border import SUSAN_PERCENTAGE_EPSILON, SUSAN_PIXEL_EPSILON
from border import SUSAN_CORNER_RATIO, SUSAN_BORDER_RATIO, HOUGH_LINEAR_EPSILON
from border import HOUGH_MAX_PERCENTAGE, HOUGH_MAX_AMMOUNT, HOUGH_CIRCULAR_EPSILON
        






if __name__ == "__main__":
    
    image = BorderBMPImage(os.path.join("images", "3POINTS.BMP"))
    D = max([image.width, image.height]) * sqrt(2)
    class LineSpace(dict):
        def contains(self, parameters, x, y):
            rho, phi = parameters[0], parameters[1]
            pcos = cos(phi)
            psin = sin(phi)     
            return fabs(rho - x * pcos - y * psin) < HOUGH_LINEAR_EPSILON
        
    parameter_space = LineSpace()
    
    def fitness_function(line):
        sum = 0
        for x in xrange(image.width):
            for y in xrange(image.height):
                value = image.get_pixel(x, y, GREEN)
                if value == float(L - 1) and \
                parameter_space.contains(line, x, y):
                    sum+=1
                    
        return sum
    def random_chromosome_function():
        d = random()*360.0
        phi = d*2*pi/360.0
        rho = random() * D
        return (rho,phi)
    def mating_function(father, mother):
        #r = random()
        #if r < CROSSOVER_P:
        #    crossover_point = randint(0, len(father.swaps) - 1)
        #    new_genes = father.swaps[:crossover_point] + mother.swaps[crossover_point:]
        #    return Tour(new_genes)
        if random() < 0.2:
            return (father[0], mother[1])
        return choice([father, mother])
    def mutation_function(line):
        if random() < 0.05:
            line = (line[0]+random()*50, line[1])
        if random() < 0.05:
            line = (line[0], line[1]+random()*pi)
        return line
    d = {'gen': 1}
    def generation_callback(lines):
        
        i = 0
        done = []
        
        
        ret = BorderBMPImage.blank(image.width, image.height, 0.0)
        for line in lines:
            if line not in done:
                print line
                done.append(line)
                ret.draw_guess(parameter_space, line)
                i+=1
                if i >= 3:
                    break
        s = ret + image
        s.save("ga/"+str(d['gen'])+".bmp")
        d['gen']+= 1
    
    
    
    algo = CrossoverGeneticAlgorithm(fitness_function, random_chromosome_function,
                 mating_function, mutation_function, generation_callback, max_generations=100000,
                 population_size=100)
    t, f =  algo.run()
        
    
    print "Done!"
    print t, f
    raw_input("Press enter to terminate.")