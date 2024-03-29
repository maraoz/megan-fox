# *-* coding: utf-8 *-*

from base import RGB_COLORS, RED, GREEN, BLUE
from border import SpaceBMPImage, L
from math import log, fabs, atan2, pi, degrees, radians, sqrt, cos, sin
from random import random
from math import sqrt

from util import get_LoG_element

import os
#import mahotas

class ComplexBMPImage(SpaceBMPImage):
    """ BMP format image that supports complex thresholding operations"""
    
    def otsu(self, histogram=None):
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
            nO = [float(nB[-1] - nB[i]) for i in xrange(len(nB))] #nB[-1]-nB
            
            mu_B = float(0)
            weigthsum = [i for i in xrange(Ng)]
            for i in xrange(len(weigthsum)):
                weigthsum[i] = i * hist[i]
                
            mu_O = sum(weigthsum) / float(sum(list_hist))
            
            best = nB[0] * nO[0] * (mu_B - mu_O) * (mu_B - mu_O)
            bestT = 0
        
            for T in xrange(1, Ng):
                if nB[T] == 0:
                    continue
                if nO[T] == 0:
                    break
                mu_B = (mu_B * nB[T - 1] + T * hist[T]) / float(nB[T])
                mu_O = (mu_O * nO[T - 1] - T * hist[T]) / float(nO[T])
                sigma_between = nB[T] * nO[T] * (mu_B - mu_O) * (mu_B - mu_O)
                if sigma_between > best:
                    best = sigma_between
                    bestT = T
            answer[color] = bestT
        return answer
    
    def chang_thouin(self, otsu_values=None):
        if otsu_values == None:
            otsu_values = self.otsu()
        
        # 1
        tr, tg, tb = tuple([otsu_values[c] for c in otsu_values])
        
        # 2
        codewords = {}
        for x in xrange(self.width):
            for y in xrange(self.height):
                codeword = (self.get_pixel(x, y, RED) <= tr,
                self.get_pixel(x, y, GREEN) <= tg ,
                self.get_pixel(x, y, BLUE) <= tb)
                codewords[(x, y)] = codeword
        
        clusters = []
        for vr in [True, False]:
            for vg in [True, False]:
                for vb in [True, False]:
                    clusters.append(tuple([(vr, vg, vb)]))
                    
        cluster_means = {}
        within_cluster_variances = {}
        between_cluster_variances = {}
        
        while True:
            print str(len(clusters)) +" clusters."
            print clusters
            print cluster_means
            print within_cluster_variances
            print between_cluster_variances
            
            print "*" * 80
            # 3
            for cluster in clusters:
                if cluster not in cluster_means:
                    mean = self.get_cluster_mean(cluster, codewords)
                    cluster_means[cluster] = mean
            
            # 4        
            for cluster in clusters:
                if cluster not in within_cluster_variances:
                    mean_values = cluster_means[cluster]
                    sigma_k = self.get_within_cluster_variance(cluster, mean_values, codewords)
                    within_cluster_variances[cluster] = sigma_k
                
                for other_cluster in clusters:
                    if other_cluster == cluster:
                        continue
                    if (cluster, other_cluster) not in between_cluster_variances:
                        my_means = cluster_means[cluster]
                        other_means = cluster_means[other_cluster]
                        sigma_ij = self.get_between_cluster_variance(my_means, other_means)
                        between_cluster_variances[(cluster, other_cluster)] = sigma_ij
            
            
            # 5
            merged = False
            for cluster in clusters:
                if merged:
                    break
                for other_cluster in clusters:
                    if merged:
                        break
                    if other_cluster == cluster:
                        continue
                    pair = (cluster, other_cluster)
                    sigma_k = within_cluster_variances[cluster]
                    sigma_j = within_cluster_variances[other_cluster]
                    sigma_kj = between_cluster_variances[pair]
                    if sigma_k >= sigma_kj or \
                        sigma_j >= sigma_kj:
                        clusters.remove(cluster)
                        clusters.remove(other_cluster)
                        clusters.append(cluster + other_cluster)
                        merged = True
                    
                
            
            if not merged:
                # 7
                for x in xrange(self.width):
                    for y in xrange(self.height):
                        cwd = codewords[(x, y)]
                        for cluster in clusters:
                            if cwd in cluster:
                                mean_values = cluster_means[cluster]
                                for color in RGB_COLORS:
                                    self.set_pixel(x, y, color, mean_values[color])
                                break
                break
        print "Thresholdized with %d colors" % (len(clusters))
        return self
                                
                    
    def get_cluster_mean(self, cluster, codewords):
        count = {RED : 0, GREEN: 0, BLUE : 0}
        accum = {RED : 0, GREEN: 0, BLUE : 0}
        for x in xrange(self.width):
            for y in xrange(self.height):
                cwd = codewords[(x, y)]
                if cwd in cluster:
                    for color in RGB_COLORS:
                        value = self.get_pixel(x, y, color)
                        count[color] += 1
                        accum[color] += value
        mean_values = {}
        for color in RGB_COLORS:
            if count[color] == 0:
                mean_values[color] = L/2
                continue
            mean_values[color] = accum[color] / float(count[color])
        return tuple([mean_values[c] for c in RGB_COLORS])
        
    def get_within_cluster_variance(self, cluster, mean_values, codewords):
        suma = 0
        count = 0
        for x in xrange(self.width):
            for y in xrange(self.height):
                cwd = codewords[(x, y)]
                if cwd in cluster:
                    for color in RGB_COLORS:
                        diff = self.get_pixel(x, y, color) - mean_values[color]
                        suma += diff * diff
                    count += 1
        sigma_k = 0.0 
        if count != 0:
            sigma_k = sqrt(suma) / float(count)
        return sigma_k
         
    def get_between_cluster_variance(self, my_means, other_means):
        sum = 0
        for color in RGB_COLORS:
            diff = my_means[color] - other_means[color]
            sum += diff * diff
        return sqrt(sum)
        
        
    
if __name__ == "__main__":
    
    # COINS, MEGAN, SONIC, NOTICIA, HOMEBOY, TREE
    
    megan = ComplexBMPImage(os.path.join("images", "TREE.BMP"))
    megan.draw()
    #d = megan.otsu()
    
    #thr = megan.thresholdizeRGB(d[0], d[1], d[2])
    #thr.draw()
    
    megan.chang_thouin().draw()
