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
        evaluation = evaluator(inputs=2, outputs=2, population=1,
                               connectionMutationRate=0.5, nodeMutationRate=0.2)

        for _ in range(0, 40):
            for target in evaluation.genepool:
                target.addNodeMutation(.0001, evaluation.globalInnovations)
                target.addConnectionMutation(.0001,
                                             evaluation.globalInnovations)

        for target in evaluation.genepool:
            target.fitness = rand.randint(0, 5)
        # NOTE: everything above is a test fixture for most things

        graphvizNEAT(evaluation.genepool[0], 'originParent')

        evaluation.nuclei.readyPrimalGenes(evaluation.genepool[0])
        child = evaluation.nuclei.crossover(
            evaluation.genepool[0], evaluation.genepool[0], evaluation.globalInnovations)

        for par in evaluation.genepool[0].getAllConnections():
            if not par.exists(child.getAllConnections()):
                print('\n\n MISSING CONNECTION IN CLONE CHILD \n\n')

        print('number of nodes in child : {}'.format(
            len(child.hiddenNodes)))
        print('number of connections in child : {}'
              .format(len([x.outConnections for x in child.hiddenNodes]) +
                      len([x.inConnections for x in child.hiddenNodes])))

        print('number of nodes in clone : {}'.format(
            len(evaluation.genepool[0].hiddenNodes)))
        print('number of connections in clone : {}'
              .format(len([x.outConnections for x in evaluation.genepool[0].hiddenNodes]) +
                      len([x.inConnections for x in evaluation.genepool[0].hiddenNodes])))

        graphvizNEAT(child, 'child')


if __name__ == '__main__':
    unittest.main()
