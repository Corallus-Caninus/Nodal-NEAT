from chromosome import chromosome
from genome import genome
from evaluator import evaluator
import unittest
import logging
from network import graphvizNEAT
import uuid
import random as rand
import os
import re

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
    unittest for chromosome's crossover method and supporting methods
    '''
    # TODO: recurring removal in start of evolution. need to debug this either just here or here and basic_trainning

    def test_genepool(self):
        configLogfile()
        evaluation = evaluator(inputs=2, outputs=2, population=10,
                               connectionMutationRate=0.5, nodeMutationRate=0.2)

        for _ in range(0, 20):
            for target in evaluation.genepool:
                target.addNodeMutation(.0001, evaluation.globalInnovations)
                target.addConnectionMutation(.0001,
                                             evaluation.globalInnovations)

        for target in evaluation.genepool:
            target.fitness = rand.randint(0, 5)

        graphvizNEAT(evaluation.genepool[0], 'fitParent')
        graphvizNEAT(evaluation.genepool[1], 'lesserParent')

        # NOTE: everything above is a test fixture for most things

        # NOTE: advancing 10 generations
        for _ in range(0, 10):
            curGenomes = evaluation.nextGeneration()

            print(curGenomes)
            curGenomes[0].forwardProp([1, 2])
            curGenomes[0].forwardProp([1, 2])

        # TODO: child doesnt get added connections or nodes (just initialTopology)
        for child in curGenomes:
            graphvizNEAT(child, 'child ' + str(uuid.uuid1()))
            # print('nodes lost in child from superior parent: {}'.format(
            #     len(evaluation.genepool[0].hiddenNodes) - len(child.hiddenNodes)))
            # print('nodes lost in child from inferior parent: {}'.format(
            #     len(evaluation.genepool[1].hiddenNodes) - len(child.hiddenNodes)))
        # NOTE: graphically confirmed levels of complexification is functioning.
        #             need to add logistic probability of adding node to prevent too much pruning
        #              otherwise risk losing innovations faster than mutation rate.
        #              (also forces crossover to follow a path as a genepool so this is interesting)
        #               ready for unittest of fitness function xor to examine behaviour in pressure.
        # graphvizNEAT(evaluation.genepool[0], 'superior')
        # graphvizNEAT(evaluation.genepool[1], 'inferior')


if __name__ == '__main__':
    unittest.main()
