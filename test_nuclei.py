from nuclei import nuclei
from genome import genome
from evaluator import evaluator
import unittest
import logging
from network import graphvizNEAT
import uuid
import sys
import random as rand


class TestPrimalAlignment(unittest.TestCase):
    '''
    unittest for chromosome's crossover and supporting methods. Essentially a manual generation step.
    '''
    # TODO: recurring connectionGene removal BUG in start of evolution. need to debug this either just here or here and basic_trainning
    #               this is likely to be during split of loop connection trace from globalInnovations. bug has occured long enough it could be a deep
    #               feature

    def test_primalOperations(self):
        evaluation = evaluator(inputs=2, outputs=2, population=3,
                               connectionMutationRate=0.5, nodeMutationRate=0.2)

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
            rfit = rand.uniform(0, len(evaluation.genepool))
            ge.fitness = rfit

        # NOTE: everything above is a test fixture for most things

        chromosomes = nuclei()
        for ge in evaluation.genepool:
            chromosomes.readyPrimalGenes(ge)

        nextGeneration = []
        for _ in range(0, 5):
            p1 = rand.randint(0, len(evaluation.genepool)-1)
            p2 = rand.randint(0, len(evaluation.genepool)-1)
            if evaluation.genepool[p1].fitness >= evaluation.genepool[p2].fitness:
                child = chromosomes.crossover(
                    evaluation.genepool[p1], evaluation.genepool[p2], evaluation.globalInnovations)
            else:
                child = chromosomes.crossover(
                    evaluation.genepool[p2], evaluation.genepool[p1], evaluation.globalInnovations)

            nextGeneration.append(child)

        print(nextGeneration)
        nextGeneration[0].forwardProp([1, 2])
        nextGeneration[0].forwardProp([1, 2])

        for child in nextGeneration:
            graphvizNEAT(child, 'child ' + str(uuid.uuid1()))
        for parent in evaluation.genepool:
            graphvizNEAT(parent, 'parent' + str(uuid.uuid1()))


if __name__ == '__main__':
    unittest.main()
