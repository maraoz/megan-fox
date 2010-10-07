# *-* coding: utf-8 *-*

from math import log, sqrt, pi, cos, sin, exp
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


def EmptyMatrix(row_number, col_number):
    return [[None for col in col_number] for row in xrange(row_number)]

def Matrix(*rows):
    return [row for row in rows]

def median(values):
    theValues = sorted(values)
    count = len(theValues)
    if count % 2 == 1:
         return theValues[(count-1)/2]
    else:
        lower = theValues[count/2-1]
        upper = theValues[count/2]
        return (float(lower + upper)) / 2

def lorentzian(s):
    sigma = 100
    return 1.0 / ((s * s) / float(sigma) + 1.0)

def leclerquian(s):
    sigma = 100
    return exp(-(s*s)/float(sigma))

def get_LoG_element(x, y, sigma):
    a = - (1.0)/(sqrt(2*pi)*(sigma**3))
    b = 2.0 - (x**2 + y**2)/float(sigma**2)
    c = - (x**2+y**2)/float(2*(sigma**2))
    return a*b*exp(c)

if __name__ == "__main__":
    draw_histogram([rand_rayleigh(10) for _ in xrange(1000000)])
    # draw_histogram([rand_exponential(3) for _ in xrange(1000000)])
    # draw_histogram([rand_rayleigh(3) for _ in xrange(1000000)])
    # draw_histogram([rand_gaussian(mu = 100, sigma_squared = 10) for _ in xrange(1000000)])
