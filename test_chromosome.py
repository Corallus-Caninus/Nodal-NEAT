from chromosome import chromosome
from genome import genome
from evaluator import evaluator
import unittest
import logging
from network import graphvizNEAT


class TestPrimalAlignment(unittest.TestCase):
    '''
    unittest for chromosome's crossover method and supporting methods
    '''

    def test_primalOperations(self):
        evaluation = evaluator(inputs=2, outputs=2, population=2,
                               connectionMutationRate=0.5, nodeMutationRate=0.2)
        i = 0
        for target in evaluation.genepool:
            # TODO: implement logging
            # TODO: change order of mutations to test globalInnovations
            # logging.info('BEGIN {} GENOME'.format(i))
            i += 1
            for _ in range(0, 25):
                # print(' TOP O\' THE LOOP TO YA\n\n\n\n')
                # logging.info('with total globalInnovations: {}'.format(len(
                # evaluation.globalInnovations.connections)))
                target.addNodeMutation(.0001, evaluation.globalInnovations)
                # split a specific connection multiple times TODO: call this many times for genome one then for genome 2 to ensure splitDepth
                #  is preserved when genome 2 catches up.
                target.addConnectionMutation(.0001,
                                             evaluation.globalInnovations)
            evaluation.genepool[0].fitness = 4
            evaluation.genepool[1].fitness = 1

        chromosomes = chromosome()

        chromosomes.readyPrimalGenes(evaluation.genepool[0])
        chromosomes.readyPrimalGenes(evaluation.genepool[1])

        # NOTE: primalGenes are assembled seemingly correctly
        for x in chromosomes.primalGenes:
            for i in chromosomes.primalGenes[x]:
                print(i)

        child = chromosomes.crossover(
            evaluation.genepool[0], evaluation.genepool[1], evaluation.globalInnovations)

        print(child)
        # TODO: child doesnt get added connections or nodes (just initialTopology)
        graphvizNEAT(child, 'child')
        graphvizNEAT(evaluation.genepool[0], 'superior')
        graphvizNEAT(evaluation.genepool[1], 'inferior')


if __name__ == '__main__':
    unittest.main()
