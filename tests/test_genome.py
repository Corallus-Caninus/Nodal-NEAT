import unittest

from organisms.Evaluator import Evaluator


def myFunc(x):
    x.fitness = 0.999999
    return x


class TestGenome(unittest.TestCase):
    def test_sequencing(self):
        """
        check layer detection and ensure it is deterministic.
        """
        # TODO: call forwardPropagation with processSequences and
        #       check if same connection loop attribute result from a
        #       given genome. Scale Genomes sufficiently to ensure all
        #       edge cases (parallel nodes with recurrence etc.)
        print('\n TESTING SEQUENCING AND LOOP DETECTION')
        generations = 50
        tester = Evaluator(inputs=3, outputs=1,
                           population=10, connectionMutationRate=0.3,
                           nodeMutationRate=0.5, weightMutationRate=0.2,
                           weightPerturbRate=0.9, selectionPressure=2)

        for generation in range(generations):
            tester.nextGeneration(myFunc)

            candidate = tester.genepool[0]
            print('new generation.. sampled node_count: {} sampled connection_count: {}'
                  .format(len(candidate.getAllConnections()), len(candidate.hiddenNodes)))

            # uninitialize the topology
            candidate.resetSignals()
            candidate.resetNodes()
            candidate.resetLoops()
            candidate.forwardProp([0.5, 0.5, 0.5])

            first = candidate.processSequences()
            first_loops = [x.loop for x in candidate.getAllConnections()].copy()

            candidate.resetSignals()
            candidate.resetNodes()
            candidate.resetLoops()

            second = candidate.processSequences()
            second_loops = [x.loop for x in candidate.getAllConnections()]

            print('testing loop detection @ generation {}..'.format(generation))
            # compare loops
            if len(second_loops) != \
                    len(first_loops):
                raise Exception("non-deterministic loop detection! \n first_loops: {} \n second_loops: {}"
                                .format(first_loops, second_loops))
            for c in second_loops:
                if c not in first_loops:
                    raise Exception("non-deterministic loop detection! \n first_loops: {} \n second_loops: {}"
                                    .format(first_loops, second_loops))

            print('testing sequencing @ generation {}..'.format(generation))
            assert all([first[x] in second.values() for x in first]), \
                'non-deterministic sequencing with key! (depth) first_sequence: {} second_sequence: {}' \
                    .format(first, second)
            assert all([x in second.keys() for x in first]), \
                'non-deterministic sequencing with values! (primal connections) first_sequence: {} second_sequence: {}' \
                    .format(first, second)

    # def test_phenome(self):
    #     """
    #     test the representation of this genome by comparing network
    #     attributes.
    #     """
    #     pass


if __name__ == '__main__':
    unittest.main()
