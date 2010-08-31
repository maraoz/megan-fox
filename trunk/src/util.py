# *-* coding: utf-8 *-*

from math import log, sqrt, pi, cos, sin
from random import random

def draw_histogram(x):
    import matplotlib.pyplot

    fig = matplotlib.pyplot.figure()
    ax = fig.add_subplot(111)
    n, bins, patches = ax.hist(x, 200, normed=1, facecolor='green', alpha=0.75)
    
    ax.set_xlabel('Value Range')
    ax.set_ylabel('Frecuency')
    ax.set_title(r'$\mathrm{Histogram:}\ \alpha \beta \pi$')
    ax.grid(True)
    
    matplotlib.pyplot.show()

def rand_exponential(lam):
    x = random()
    return - (1.0 / lam) * log(x)

def rand_rayleigh(xi):
    x = random()
    return xi * sqrt(-2 * log(1 - x))

def rand_gaussian(mu = 0, sigma_squared = 1):
    x1 = random()
    x2 = random()
    y = sqrt(-2 * log(x1)) * cos(2 * pi * x2) 
    return mu + sigma_squared*y





if __name__ == "__main__":
    
    # draw_histogram([rand_exponential(3) for _ in xrange(1000000)])
    # draw_histogram([rand_rayleigh(3) for _ in xrange(1000000)])
    draw_histogram([rand_gaussian(mu = 100, sigma = 10) for _ in xrange(1000000)])
