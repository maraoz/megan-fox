#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on Feb 16, 2010

@author: maraoz
'''


from random import random, choice

class GeneticAlgorithm(object):
    """ Generic class for genetic algorithm """
    
    def __init__(self, fitness_function, random_chromosome_function,
                 mating_function, mutation_function, generation_callback,
                 max_generations=2000, population_size=100):
        
        self.fitness = fitness_function
        self.random_chromosome = random_chromosome_function
        self.combine = mating_function
        self.mutate = mutation_function
        self.generation_callback = generation_callback

        self.max_generations = max_generations
        self.population_size = population_size
        
        
    def get_best_individual(self):
        return max(self.population, key=lambda c: c['fitness'])
        

    def evaluate_fitness(self):
        for individual in self.population:
            chrm = individual['genes']
            # if 0 set fitness to a small number
            individual['fitness'] = self.fitness(chrm) or 0.1
    def sort_by_fitness(self):
        cmp_function = lambda c, d: cmp(d['fitness'], c['fitness'])
        self.population.sort(cmp=cmp_function)
        
    def next_generation(self):
        self.generation += 1

    def initialize_population(self):
        self.population = []
        self.generation = 0
        for _ in xrange(self.population_size):
            chromosome = self.random_chromosome()
            individual = {'genes' : chromosome, 'fitness' : 0}
            self.population.append(individual)

    def mutation(self, offspring):
        new_o = []
        for child in offspring:
            new_o.append({'genes' : self.mutate(child['genes']),
                          'fitness' : 0})
        return new_o

    def get_offspring(self):
        raise NotImplementedError
        
    def introduce(self, offspring):
        raise NotImplementedError

    def termination_condition(self):
        # default is no termination
        return False

    def best_callback(self):
        best = self.get_best_individual()
        self.generation_callback(best['genes'], best['fitness'])
        
    def run(self):
        
        self.initialize_population()    
        while not self.termination_condition() and \
              self.generation < self.max_generations:
            print "Generation", self.generation
            self.evaluate_fitness()
            self.best_callback()
            offspring = self.get_offspring()
            mutated_offspring = self.mutation(offspring)
            self.introduce(mutated_offspring)
            self.next_generation()

        best = self.get_best_individual()
        
        return best['genes'], best['fitness']


class ElitistGeneticAlgorithm(GeneticAlgorithm):
    """This class englobes the genetic algorithms which use elitism,
        that is, that a (usually small) percentage of each population
        is preserved alive and intact to the next generation. This are
        the best individuals based on fitness"""

    def __init__(self, *args, **kwargs):

    
        GeneticAlgorithm.__init__(self, *args, **kwargs)

        # we calculate how many offspring to generate based on the
        # ammount of individuals that will survive to next generation
        elite = 0.1
        self.elite_ammount = int(elite * self.population_size)
        self.offspring_ammount = self.population_size - self.elite_ammount


    def introduce(self, offspring):
        assert len(self.population) == self.population_size
        self.population = self.population[:self.elite_ammount] + offspring


class KnownOptimaGeneticAlgorithm(GeneticAlgorithm):
    """This is a special case of Genetic Algorithms where the objective
    fitness is known, and the algorithm can halt when that fitness is 
    reached"""
    def __init__(self, max_fitness, *args, **kwargs):
        self.max_fitness = max_fitness
    
        GeneticAlgorithm.__init__(self, *args, **kwargs)
    
    def termination_condition(self):
        return self.population[0]['fitness'] == self.max_fitness


class AsexualGeneticAlgorithm(GeneticAlgorithm):
    """In this simple version, the offspring we generate are
        exact copies of the fittest individuals in the population.
        Then mutation will be applied, so this algorithm simulates
        asexual reproduction"""


    def get_offspring(self):
        self.sort_by_fitness()
        return self.population[:self.offspring_ammount]

class CrossoverGeneticAlgorithm(ElitistGeneticAlgorithm):
    """In this more complex version, the offspring we generate are
        combination of two parents from previous population. The parents
        are chosen for mating using a linear roulette wheel based on
        fitness."""

    def roulette_wheel(self, total):
        """ total: total population fitness """
        if total == 0:
            return choice(self.population)
        r = random() * total
        s = 0
        for ind in self.population:
            s += ind['fitness']
            if s > r:
                return ind
        #shouldn't reach this point
        raise TypeError, "random number r=%f derived from total=%f \
            shouldn't be greater than sum s=%f." % (r, total, s)

    def get_offspring(self):
        self.sort_by_fitness()
        pop_fitness = sum(i['fitness'] for i in self.population)
        offspring = []
        for i in xrange(self.offspring_ammount):
            father = self.roulette_wheel(pop_fitness)
            mother = self.roulette_wheel(pop_fitness)

            combined_genes = self.combine(father['genes'], mother['genes'])
            offspring.append({'genes' : combined_genes, 'fitness' : 0})

        return offspring

class FreeForAllGeneticAlgorithm(CrossoverGeneticAlgorithm):
    """This algorithms assumes that fitness of an individual depends
    on its performance in relatin to others. In this case, the fitness function
    must receive the whole population to be evauated, and should return a list
    of all fitnesses."""
    def evaluate_fitness(self):
        fitnesses = self.fitness([ind['genes'] for ind in self.population])
        for index, individual in enumerate(self.population):
            individual['fitness'] = fitnesses[index] or 0.1

def main():
    pass
    

if __name__ == "__main__":
    main()
