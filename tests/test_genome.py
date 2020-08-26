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
        generations = 50
        tester = Evaluator(inputs=3, outputs=1,
                           population=10, connectionMutationRate=0.3,
                           nodeMutationRate=0.5, weightMutationRate=0.2,
                           weightPerturbRate=0.9, selectionPressure=2)

        for generation in range(generations):
            tester.nextGeneration(myFunc)

            candidate = tester.genepool[0]

            # uninitialize the topology
            candidate.resetSignals()
            candidate.resetNodes()
            candidate.resetLoops()
            candidate.forwardProp([0.5, 0.5, 0.5])

            # prepare loop check comparison
            first_loops = []
            for c in candidate.getAllConnections():
                if c.loop:
                    first_loops.append(c.innovation)

            first = candidate.processSequences()

            candidate.resetSignals()
            candidate.resetNodes()
            candidate.resetLoops()

            second = candidate.processSequences()

            # compare loops
            if len([x.loop for x in candidate.getAllConnections()]) != \
                    len(first_loops):
                raise Exception("non-deterministic loop detection!")

            for c in candidate.getAllConnections():
                if c.innovation not in first_loops:
                    raise Exception("non-deterministic loop detection!")

            print('testing sequencing @ generation {}..'.format(generation))
            assert all([first[x] in second.values() for x in first]), \
                'non-deterministic sequencing with key! (depth)'
            assert all([x in second.keys() for x in first]), \
                'non-deterministic sequencing with values! (primal connections)'

    # def test_phenome(self):
    #     """
    #     test the representation of this genome by comparing network
    #     attributes.
    #     """
    #     pass


if __name__ == '__main__':
    unittest.main()
