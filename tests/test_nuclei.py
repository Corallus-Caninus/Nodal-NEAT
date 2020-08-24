import logging
import os
import random as rand
import re
import unittest

from organisms.Evaluator import Evaluator
# from organisms.network import graphvizNEAT
from organisms.Nuclei import Nuclei


# import uuid


def configLogfile():
    # TODO: no logging in unittests only in algorithm
    """
    configures logFile name and directory
    """
    biggestNum = 0
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


class TestCrossover(unittest.TestCase):
    """
    unittest for chromosome's crossover and supporting methods. Essentially a manual generation step.
    """

    def test_crossover(self):
        evaluation = Evaluator(inputs=2, outputs=1, population=3,
                               connectionMutationRate=0.1, nodeMutationRate=0.09,
                               weightMutationRate=0.9, weightPerturbRate=0.6, selectionPressure=3)

        for _ in range(0, 100):
            for target in evaluation.genepool:
                target.addNodeMutation(0.8, evaluation.globalInnovations)
                target.addConnectionMutation(0.9,
                                             evaluation.globalInnovations)

        for _ in range(0, 100):
            evaluation.genepool[0].addNodeMutation(
                0.9, evaluation.globalInnovations)
            evaluation.genepool[0].addConnectionMutation(
                0.01, evaluation.globalInnovations)

            evaluation.genepool[1].addNodeMutation(
                0.9, evaluation.globalInnovations)
            evaluation.genepool[1].addConnectionMutation(
                0.01, evaluation.globalInnovations)

        for ge in evaluation.genepool:
            ge.fitness = rand.uniform(0, len(evaluation.genepool))

        # NOTE: everything above is a test fixture for most things

        chromosomes = Nuclei()
        for ge in evaluation.genepool:
            chromosomes.readyPrimalGenes(ge)

        nextGeneration = []
        for _ in range(0, 5):
            p1 = rand.randint(0, len(evaluation.genepool) - 1)
            p2 = rand.randint(0, len(evaluation.genepool) - 1)
            if evaluation.genepool[p1].fitness >= evaluation.genepool[p2].fitness:
                child = chromosomes.crossover(
                    evaluation.genepool[p1], evaluation.genepool[p2], evaluation.globalInnovations)
            else:
                child = chromosomes.crossover(
                    evaluation.genepool[p2], evaluation.genepool[p1], evaluation.globalInnovations)

            nextGeneration.append(child)

        nextGeneration[0].forwardProp([1, 2])
        nextGeneration[0].forwardProp([1, 2])

        # for child in nextGeneration:
        #     graphvizNEAT(child, 'child ' + str(uuid.uuid1()))
        # for parent in evaluation.genepool:
        #     graphvizNEAT(parent, 'parent' + str(uuid.uuid1()))

    def test_clone(self):
        """
        test crossover between two identical genomes. should result a topology with
        all nodes, possibly lost connections.
        """
        print('\nTESTING CLONE CROSSOVER:')
        # NOTE: this test if a Genome is crossed over with itself the same Genome is produced
        #       as offspring (diversity singularity)

        configLogfile()
        evaluation = Evaluator(inputs=2, outputs=1, population=1,
                               connectionMutationRate=0.1, nodeMutationRate=0.09,
                               weightMutationRate=0.9, weightPerturbRate=0.6, selectionPressure=3)

        for _ in range(0, 40):
            for target in evaluation.genepool:
                target.addNodeMutation(0.99, evaluation.globalInnovations)
                target.addConnectionMutation(0.99,
                                             evaluation.globalInnovations)

        for target in evaluation.genepool:
            target.fitness = rand.randint(0, 5)
        # NOTE: everything above is a test fixture for most things

        # graphvizNEAT(evaluation.genepool[0], 'originParent')

        evaluation.nuclei.readyPrimalGenes(evaluation.genepool[0])
        child = evaluation.nuclei.crossover(
            evaluation.genepool[0], evaluation.genepool[0], evaluation.globalInnovations)

        assert child.geneticDistance(evaluation.genepool[0]) == 0, 'innovation changed during crossover!'

        for par in evaluation.genepool[0].getAllConnections():
            if not par.exists(child.getAllConnections()):
                raise Exception("ERROR: MISSING CONNECTION IN CLONE CHILD")

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

        # graphvizNEAT(child, 'child')


if __name__ == '__main__':
    unittest.main()
