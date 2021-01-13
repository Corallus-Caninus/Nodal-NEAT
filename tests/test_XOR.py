import logging
import os
import random as rand
import re
import unittest
from math import sqrt

import matplotlib.pyplot as plt
from matplotlib import style
from organisms.Evaluator import Evaluator


def configLogfile():
    # TODO: call a separate logging file for unittests. this will make the code
    # easier to understand for first timers
    """
    configures logFile name and directory
    """
    biggestNum = 1
    for _, _, files in os.walk('logs'):
        fileNums = []
        if len(files) == 0:
            biggestNum = 1
        else:
            for name in files:
                chopFile = re.compile('[-,.]').split(name)
                fileNums.append(int(chopFile[1]))

            biggestNum = max(fileNums)

    logFile = 'logs/test-{}.log'.format(biggestNum + 1)
    logging.basicConfig(
        filename=logFile, level=logging.INFO)


def xor(solutionList):
    """
    0 0 | 0 1 | 1 0 | 1 1
     0   |   1  |   1  |  0

    """
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


# TODO: lru_cache here doesnt so anything really
#       but is a good idea in other fit funcs.
# @lru_cache(maxsize=None)
def myFunc(genome):
    """
    takes a Genome returns Genome with fitness associated
    """
    numTries = 50
    score = 0

    # needs to be random to prevent memorizing order of input
    for _ in range(0, numTries):
        entry1 = rand.randint(0, 1)
        entry2 = rand.randint(0, 1)

        output = genome.forwardProp([entry1, entry2])[0]
        solution = entry1 ^ entry2
        score += 1 - (sqrt((output - solution)**2))
        # TODO: dont round? apparantly this is linearly seperable
        #       because init topology gets >95 with numtries==50
        # if round(output) == entry1^entry2:
        #     score+=1

    score = score / numTries
    # return score
    genome.fitness = score
    return genome


class TestXOR(unittest.TestCase):
    """
    test crossover of an entire generation in a genepool.
    """

    def test_XOR(self):
        """
        trains a genepool to solve the XOR function.
        """
        generations = 500

        # Graph configuration
        style.use('fivethirtyeight')
        y = []
        yAvg = []
        nodes = []
        connections = []
        plt.ion()

        print('\nTESTING XOR EVALUATION:')
        # NOTE: this test if a Genome is crossed over with itself the same Genome is
        #       produced as offspring (diversity singularity)

        configLogfile()
        # configure Nodal-NEAT
        # NOTE: selectionPressure sets a betavariate distribution,
        #       the lower the value the more selection pressure
        evaluation = Evaluator(inputs=2, outputs=1, population=1000,
                               connectionMutationRate=0.02, nodeMutationRate=0.01,
                               weightMutationRate=0.1, weightPerturbRate=0.9,
                               selectionPressure=0.15)

        # evaluate
        evaluation.score(myFunc)
        for x in range(0, generations):
            print('GENERATION: {}'.format(x))
            evaluation.nextGeneration(myFunc)
            maxFit = evaluation.getMaxFitness()
            print('max fitness is: {}'.format(maxFit))

            # format matplotlib subplots
            y_avg = 0
            nodeAvg = 0
            connectionAvg = 0
            for g in evaluation.genepool:
                y_avg += g.fitness
                nodeAvg += len(g.hiddenNodes)
                for n in g.hiddenNodes:
                    connectionAvg += len(n.outConnections)
                    connectionAvg += len(n.inConnections)

            y_avg = y_avg / len(evaluation.genepool)
            connectionAvg = connectionAvg / len(evaluation.genepool)
            nodeAvg = nodeAvg / len(evaluation.genepool)

            yAvg.append(y_avg)
            connections.append(connectionAvg)
            nodes.append(nodeAvg)

            y.append(maxFit)

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


if __name__ == '__main__':
    unittest.main()
