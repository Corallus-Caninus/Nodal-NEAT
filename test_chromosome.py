from chromosome import chromosome
from genome import genome
from evaluator import evaluator
import unittest
import logging
from network import graphvizNEAT
import uuid


class TestPrimalAlignment(unittest.TestCase):
    '''
    unittest for chromosome's crossover method and supporting methods
    '''
    # TODO: recurring removal in start of evolution. need to debug this either just here or here and basic_trainning

    def test_primalOperations(self):
        evaluation = evaluator(inputs=2, outputs=2, population=2,
                               connectionMutationRate=0.5, nodeMutationRate=0.2)

        for _ in range(0, 20):
            for target in evaluation.genepool:
                target.addNodeMutation(.0001, evaluation.globalInnovations)
                target.addConnectionMutation(.0001,
                                             evaluation.globalInnovations)

        evaluation.genepool[0].fitness = 4
        evaluation.genepool[1].fitness = 1
        # NOTE: everything above is a test fixture for most things

        chromosomes = chromosome()

        chromosomes.readyPrimalGenes(evaluation.genepool[0])
        chromosomes.readyPrimalGenes(evaluation.genepool[1])

        # NOTE: primalGenes are assembled seemingly correctly
        for x in chromosomes.primalGenes:
            for i in chromosomes.primalGenes[x]:
                print(i)

        nextGeneration = []
        for _ in range(0, 5):
            child = chromosomes.crossover(
                evaluation.genepool[0], evaluation.genepool[1], evaluation.globalInnovations)
            nextGeneration.append(child)

        print(nextGeneration)
        nextGeneration[0].forwardProp([1, 2])
        nextGeneration[0].forwardProp([1, 2])
        # TODO: child doesnt get added connections or nodes (just initialTopology)
        for child in nextGeneration:
            graphvizNEAT(child, 'child ' + str(uuid.uuid1()))
            print('nodes lost in child from superior parent: {}'.format(
                len(evaluation.genepool[0].hiddenNodes) - len(child.hiddenNodes)))
            print('nodes lost in child from inferior parent: {}'.format(
                len(evaluation.genepool[1].hiddenNodes) - len(child.hiddenNodes)))
        # NOTE: graphically confirmed levels of complexification is functioning.
        #             need to add logistic probability of adding node to prevent too much pruning
        #              otherwise risk losing innovations faster than mutation rate.
        #              (also forces crossover to follow a path as a genepool so this is interesting)
        #               ready for unittest of fitness function xor to examine behaviour in pressure.
        graphvizNEAT(evaluation.genepool[0], 'superior')
        graphvizNEAT(evaluation.genepool[1], 'inferior')


if __name__ == '__main__':
    unittest.main()
