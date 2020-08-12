import logging
import matplotlib.pyplot as plt
import matplotlib.animation as anim
from matplotlib import style
import unittest
import uuid
import random as rand
import os
import re
from copy import deepcopy
from functools import lru_cache

import numpy as np

from organisms.nuclei import nuclei
from organisms.genome import genome
from organisms.evaluator import evaluator
from organisms.network import graphvizNEAT

def configLogfile():
    # TODO: call a seperate logging file foru unittests. this will make the code easier to understand for first timers
    '''
    configures logFile name and directory
    '''
    for _, _, files in os.walk('logs'):
        fileNums = []
        if len(files) == 0:
            biggestNum = 1
        else:
            for name in files:
                chopFile = re.compile('[-,.]').split(name)
                fileNums.append(int(chopFile[1]))

            biggestNum = max(fileNums)

    logFile = 'logs/test-{}.log'.format(biggestNum+1)
    logging.basicConfig(
        filename=logFile, level=logging.INFO)


def xor(solutionList):
    '''
    0 0 | 0 1 | 1 0 | 1 1
     0   |   1  |   1  |  0

    '''
    if solutionList is [0, 0]:
        return 0
    elif solutionList is [0, 1]:
        return 1
    elif solutionList is [1, 0]:
        return 0
    elif solutionList is [1, 1]:
        return 1
    else:
        raise Exception("wrong values sent to xor")

#TODO: lru_cache here doesnt so anything really
#       but is a good idea in other fit funcs.
#@lru_cache(maxsize=None)
def myFunc(genome):
    '''
    takes a genome returns genome with fitness associated
    '''
    numTries = 50
    score = 0

    # needs to be random to prevent memorizing order of input
    for _ in range(0, numTries):
        entry1 = rand.randint(0, 1)
        entry2 = rand.randint(0, 1)

        output = genome.forwardProp([entry1, entry2])[0]

        if output >= 0.5:
            if entry1 == 1 or entry2 == 1:
                # one
                if entry1 != 1 and entry2 != 1:
                    score += 1
        elif output < 0.5 and entry1 == 1 and entry2 == 1:
            score += 1
        elif output < 0.5 and entry1 == 0 and entry2 == 0:
            score += 1

    score = score/numTries
    # return score
    genome.fitness = score
    return genome


class TestGenepool(unittest.TestCase):
    '''
    test crossover of an entire generation in a genepool.
    '''
    def test_XOR(self):
        '''
        trains a genepool to solve the XOR function.
        '''
        generations = 10000

        #Graph configuration
        style.use('fivethirtyeight')
        y = []
        yAvg = []
        nodes = []
        connections = []
        plt.ion()
        
        print('\nTESTING XOR EVALUATION:')
        # NOTE: this test if a genome is crossed over with itself the same genome is produced as offspring (diversity singularity)

        configLogfile()
        # configure Nodal-NEAT
        evaluation = evaluator(inputs=2, outputs=1, population=800,
                               connectionMutationRate=0.002, nodeMutationRate=0.0001,
                               weightMutationRate=0.06, weightPerturbRate=0.9, selectionPressure=3)

        # evaluate 200 generations
        evaluation.score(myFunc, 1)
        #TODO: simple matplotlib real time graph
        for x in range(0, generations):
            print('GENERATION: {}'.format(x))
            evaluation.nextGeneration(myFunc, 1)
            maxFit = evaluation.getMaxFitness()
            print('max fitness is: {}'.format(maxFit))
           
            y_avg = 0
            nodeAvg = 0
            connectionAvg = 0
            for g in evaluation.genepool:
                y_avg += g.fitness
                nodeAvg += len(g.hiddenNodes)
                for n in g.hiddenNodes:
                    connectionAvg += len(n.outConnections)
                    connectionAvg += len(n.inConnections)

            y_avg = y_avg/len(evaluation.genepool)
            connectionAvg = connectionAvg/len(evaluation.genepool)
            nodeAvg = nodeAvg/len(evaluation.genepool)

            yAvg.append(y_avg)
            connections.append(connectionAvg)
            nodes.append(nodeAvg)

            y.append(maxFit)
            #TODO: average fitness graph line
            plt.clf()

            plt.subplot(221)
            plt.title('max fitness')
            plt.plot(y, 'b', linewidth=0.5)

            plt.subplot(222)
            plt.title('average fitness')
            plt.plot(yAvg, 'black', linewidth=0.5)

            plt.subplot(223)
            plt.title('average connections in genepool')
            plt.plot(connections, 'black', linewidth=1)

            plt.subplot(224)
            plt.title('average nodes in genepool')
            plt.plot(nodes, 'r', linewidth=1)

            plt.draw()
            plt.pause(0.001)
        plt.savefig('test_XOR')

        # sortPool = sorted([x for x in evaluation.genepool],
        #                   key=lambda x: x.fitness, reverse=True)
        #for c in evaluation.genepool[:10]:
            #graphvizNEAT(c, 'sample-genome-'+str(uuid.uuid1()))


if __name__ == '__main__':
    unittest.main()
