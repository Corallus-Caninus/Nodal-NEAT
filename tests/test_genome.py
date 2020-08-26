import unittest

from organisms.Evaluator import Evaluator


class TestGenome(unittest.TestCase):
    def test_sequencing(self):
        """
        check layer detection and ensure it is deterministic.
        """
        # TODO: call forwardPropagation with processSequences and
        #       check if same result from a given genome. Scale Genomes
        #       sufficiently to ensure all edge cases (parallel nodes with
        #       recurrence etc.)
        generations = 50
        tester = Evaluator(inputs=3, outputs=1,
                           population=10, connectionMutationRate=0.3,
                           nodeMutationRate=0.5, weightMutationRate=0.2,
                           weightPerturbRate=0.9, selectionPressure=2)

        for generation in range(generations):
            tester.nextGeneration(lambda x: 2)

            candidate = tester.genepool[0]

            # uninitialize the topology
            candidate.resetSignals()
            candidate.resetNodes()
            candidate.resetLoops()

            first = candidate.processSequences()

            candidate.resetSignals()
            candidate.resetNodes()
            candidate.resetLoops()

            second = candidate.processSequences()

            print('testing sequencing @ generation {}..'.format(generation))
            assert all([x.key in second.keys for x in first]), \
                'non-deterministic sequencing with key! (depth)'
            assert all([x.value in second.values for x in first]), \
                'non-deterministic sequencing with values! (primal connections)'

    # def test_phenome(self):
    #     """
    #     test the representation of this genome by comparing network
    #     attributes.
    #     """
    #     pass


if __name__ == '__main__':
    unittest.main()
