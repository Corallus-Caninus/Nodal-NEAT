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
    # TODO: recurring removal in start of evolution. need to debug this either just here or here and basic_trainning

    # def test_genepool(self):
    #     print('\nTESTING GENEPOOL:')
    #     configLogfile()
    #     evaluation = evaluator(inputs=2, outputs=2, population=3,
    #                            connectionMutationRate=0.5, nodeMutationRate=0.2)

    #     for _ in range(0, 100):
    #         for target in evaluation.genepool:
    #             target.addNodeMutation(.0001, evaluation.globalInnovations)
    #             target.addConnectionMutation(.0001,
    #                                          evaluation.globalInnovations)

    #     for target in evaluation.genepool:
    #         target.fitness = rand.randint(0, 5)
    #         print('number of nodes in initial genepool {} : {}'.format(
    #             target, len(target.hiddenNodes)))

    #     graphvizNEAT(evaluation.genepool[0], 'originParent1')
    #     graphvizNEAT(evaluation.genepool[1], 'originParent2')
    #     graphvizNEAT(evaluation.genepool[2], 'originParent3')

    #     # NOTE: everything above is a test fixture for most things

    #     # NOTE: advancing 10 generations
    #     for x in range(0, 1):
    #         curGenomes = evaluation.nextGeneration()
    #         for ge in curGenomes:
    #             print('number of nodes in generation {} genome {} : {}'.format(
    #                 x, ge, len(ge.hiddenNodes)))
    #         # curGenomes[0].forwardProp([1, 2])
    #         # curGenomes[0].forwardProp([1, 2])

    #     # TODO: child doesnt get added connections or nodes (just initialTopology)
    #     for child in curGenomes:
    #         graphvizNEAT(child, 'child ' + str(uuid.uuid1()))
    #         # print('nodes lost in child from superior parent: {}'.format(
    #         #     len(evaluation.genepool[0].hiddenNodes) - len(child.hiddenNodes)))
    #         # print('nodes lost in child from inferior parent: {}'.format(
    #         #     len(evaluation.genepool[1].hiddenNodes) - len(child.hiddenNodes)))

    # def test_cloneCrossover(self):
    #     '''
    #     test crossover between two identical genomes. should result a topology with all nodes, possibly lost connections.
    #     '''
    #     print('\nTESTING CLONE CROSSOVER:')
    #     # TODO: this test if a genome is crossed over with itself the same genome is produced as offspring (diversity singularity)
    #     configLogfile()
    #     evaluation = evaluator(inputs=2, outputs=2, population=1,
    #                            connectionMutationRate=0.5, nodeMutationRate=0.2)

    #     for _ in range(0, 20):
    #         for target in evaluation.genepool:
    #             target.addNodeMutation(.0001, evaluation.globalInnovations)
    #             target.addConnectionMutation(.0001,
    #                                          evaluation.globalInnovations)

    #     for target in evaluation.genepool:
    #         target.fitness = rand.randint(0, 5)
    #         print('number of nodes in initial genepool {} : {}'.format(
    #             target, len(target.hiddenNodes)))
    #     # NOTE: everything above is a test fixture for most things

    #     graphvizNEAT(evaluation.genepool[0], 'originParent')
    #     evaluation.genepool.append(deepcopy(evaluation.genepool[0]))
    #     graphvizNEAT(evaluation.genepool[0], 'cloneParent')

    #     evaluation.nuclei.readyPrimalGenes(evaluation.genepool[0])
    #     evaluation.nuclei.readyPrimalGenes(evaluation.genepool[1])
    #     # TODO: test confirms proper magnitude of edges BUG starts dropping nodes and connections
    #     #               with higher complexity. DE-BUG the edge case
    #     #               connections and nodes are misattributed. likely need chromosome rewrite
    #     print('number of nodes in primal backing of clone 1 : {}'.format(
    #         len(evaluation.genepool[0].hiddenNodes)))
    #     print('number of connections in clone 1 : {}'
    #           .format(len([x.outConnections for x in evaluation.genepool[0].hiddenNodes]) +
    #                   len([x.inConnections for x in evaluation.genepool[0].hiddenNodes])))

    #     print('number of nodes in primal backing of clone 2 : {}'.format(
    #         len(evaluation.genepool[1].hiddenNodes)))
    #     print('number of connections in clone 2 : {}'
    #           .format(len([x.outConnections for x in evaluation.genepool[1].hiddenNodes]) +
    #                   len([x.inConnections for x in evaluation.genepool[1].hiddenNodes])))
    #     # NOTE: not losing nodes in primal backings losing in child inheritance

    #     for x in range(0, 1):
    #         curGenomes = evaluation.nextGeneration()
    #         for ge in curGenomes:
    #             print('number of nodes in generation {} genome {} : {}'.format(
    #                 x, ge, len(ge.hiddenNodes)))
    #             print('number of connections in generation {} genome {} : {}'.format(
    #                 x, ge, len([x.outConnections for x in ge.hiddenNodes]) + len([x.inConnections for x in ge.hiddenNodes])))
    #         # curGenomes[0].forwardProp([1, 2])
    #         # curGenomes[0].forwardProp([1, 2])

    #     # TODO: child doesnt get added connections or nodes (just initialTopology)
    #     for child in curGenomes:
    #         graphvizNEAT(child, 'child ' + str(uuid.uuid1()))
    #         # print('nodes lost in child from superior parent: {}'.format(
    #         #     len(evaluation.genepool[0].hiddenNodes) - len(child.hiddenNodes)))
    #         # print('nodes lost in child from inferior parent: {}'.format(
    #         #     len(evaluation.genepool[1].hiddenNodes) - len(child.hiddenNodes)))

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
