# *-* coding: utf-8 *-*

from base import RGB_COLORS, RED, GREEN, BLUE
from border import SpaceBMPImage, L
from math import log, fabs, atan2, pi, degrees, radians, sqrt, cos, sin
from random import random

from util import get_LoG_element

import os
#import mahotas

class ComplexBMPImage(SpaceBMPImage):
    """ BMP format image that supports complex thresholding operations"""
    
    def otsu(self, histogram = None):
        if not histogram:
            histogram = self.histogram()
        
        #return mahotas.otsu(self)
        answer = {}
        for color in RGB_COLORS:
            hist = histogram[color]
            list_hist = [hist[value] for value in xrange(len(hist))]
            Ng = len(hist)
            
            suma = sum([hist[value] for value in xrange(Ng)])
            nB = [float(hist[value] + sum([hist[ivalue] for ivalue in xrange(value)])) for value in xrange(Ng)] # cumsum(hist)
            nO = [float(nB[-1]-nB[i]) for i in xrange(len(nB))] #nB[-1]-nB
            
            mu_B = float(0)
            weigthsum = [i for i in xrange(Ng)]
            for i in xrange(len(weigthsum)):
                weigthsum[i] = i * hist[i]
                
            mu_O = sum(weigthsum)/float(sum(list_hist))
            
            best = nB[0]*nO[0]*(mu_B-mu_O)*(mu_B-mu_O)
            bestT = 0
        
            for T in xrange(1, Ng):
                if nB[T] == 0:
                    continue
                if nO[T] == 0:
                    break
                mu_B = (mu_B*nB[T-1] + T*hist[T]) / float(nB[T])
                mu_O = (mu_O*nO[T-1] - T*hist[T]) / float(nO[T])
                sigma_between = nB[T]*nO[T]*(mu_B-mu_O)*(mu_B-mu_O)
                if sigma_between > best:
                    best = sigma_between
                    bestT = T
            answer[color] = bestT
        return answer
    
if __name__ == "__main__":
    
    megan = ComplexBMPImage(os.path.join("images", "LITTLE_MEGAN.BMP"))
    d = megan.otsu()
    print d
    thr = megan.thresholdizeRGB(d[0], d[1], d[2])
    thr.draw() 