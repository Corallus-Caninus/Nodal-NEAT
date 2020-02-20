from nuclei import nuclei
from genome import genome
from evaluator import evaluator
import unittest
import logging
from network import graphvizNEAT
import uuid
import random as rand
import os
import re
from copy import deepcopy

# TODO: REALLY NEED TO DEBUG CONNECTION INNOVATION MATCH REMOVAL


def configLogfile():
    # TODO: call a seperate logging file for each object. this will make the code easier to understand for first timers
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
    0 0 | 0 1 | 1 0 | 11
     0   |   1  |   1  |   0

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


def myFunc(genome):
    '''
    takes a genome returns genome with fitness associated
    '''
    numTries = 20
    score = 0

    # needs to be random to prevent memorizing order of input
    for _ in range(0, numTries):
        entry1 = rand.randint(0, 1)
        entry2 = rand.randint(0, 1)

        output = genome.forwardProp([entry1, entry2])[0]

        if output >= 0.05:
            if entry1 == 1 or entry2 == 1:
                # one
                if not entry1 == 1 and entry2 == 1:
                    score += 1
        elif output < 0.05 and entry1 == 1 and entry2 == 1:
            score += 1
        elif output < 0.05 and entry1 == 0 and entry2 == 0:
            score += 1

    score = score/numTries
    # return score
    genome.fitness = score
    return genome


class TestGenepool(unittest.TestCase):
    '''
    test crossover of an entire generation in a genepool.
    '''

    def test_clone(self):
        '''
        test crossover between two identical genomes. should result a topology with all nodes, possibly lost connections.
        '''
        print('\nTESTING XOR EVALUATION:')
        # NOTE: this test if a genome is crossed over with itself the same genome is produced as offspring (diversity singularity)

        configLogfile()
        # configure Nodal-NEAT
        evaluation = evaluator(inputs=2, outputs=1, population=100000,
                               connectionMutationRate=0.1, nodeMutationRate=0.09,
                               weightMutationRate=0.9, weightPerturbRate=0.6, selectionPressure=3)

        # evaluate 50 generations
        for _ in range(0, 1000):
            evaluation.nextGeneration(myFunc)

        sortPool = sorted([x for x in evaluation.genepool],
                          key=lambda x: x.fitness, reverse=True)
        for c in sortPool[:10]:
            graphvizNEAT(c, 'sample-genome_fitness-'+str(uuid.uuid1()))


if __name__ == '__main__':
    unittest.main()
