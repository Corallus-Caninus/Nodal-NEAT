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


def myFunc(genome):
    '''
    example function for evaluation. always takes a genome and returns a float.
    '''
    # TODO: use python type enforcement since functional
    # (not necessarily ctypes but cython is a goal unless jax/numpy is sufficient)
    return rand.uniform(0, 1)


class TestGenepool(unittest.TestCase):
    '''
    test crossover of an entire generation in a genepool.
    '''

    def test_clone(self):
        '''
        test crossover between two identical genomes. should result a topology with all nodes, possibly lost connections.
        '''
        print('\nTESTING CLONE CROSSOVER:')
        # NOTE: this test if a genome is crossed over with itself the same genome is produced as offspring (diversity singularity)

        configLogfile()
        evaluation = evaluator(inputs=2, outputs=2, population=5,
                               connectionMutationRate=0.5, nodeMutationRate=0.2)

        # evaluate 50 generations
        for _ in range(0, 50):
            evaluation.evaluate(myFunc)
            evaluation.nextGeneration()
        for c in evaluation.genepool:
            graphvizNEAT(c, 'sample-genome' + uuid.uuid1)


if __name__ == '__main__':
    unittest.main()
