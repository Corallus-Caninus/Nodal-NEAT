import unittest
from copy import deepcopy

from organisms.Evaluator import Evaluator
#@DEPRECATED
#import uuid
#from organisms.network import graphvizNEAT


class TestDeepcopy(unittest.TestCase):
    def test_deepcopy(self):
        print('\n TESTING DEEPCOPY OPERATION PROPAGATION ')
        evaluation = Evaluator(inputs=2, outputs=2, population=100,
                               connectionMutationRate=0.3, nodeMutationRate=0.01, weightMutationRate=0.5,
                               weightPerturbRate=0.9, selectionPressure=3)
        test = evaluation.genepool[0]
        for _ in range(0, 20):
            test.addConnectionMutation(evaluation.connectionMutationRate,
                                       evaluation.globalInnovations)
            test.addNodeMutation(evaluation.connectionMutationRate,
                                 evaluation.globalInnovations)
            test.mutateConnectionWeights(evaluation.weightMutationRate,
                                         evaluation.weightPerturbRate)

        print('beginning forward propagation of original genome..')
        vals = [1, 2]
        lastOutputs = [0, 0]
        for x in range(0, 10):
            outputs = test.forwardProp(vals)
            print('{} Forward Prop of {} produced {} with d/dx {}'
                  .format(x, vals, outputs, [x - y for x, y in
                                             zip(outputs, lastOutputs)]))
            lastOutputs = outputs

        print('beginning forward propagation of deepcopy genome..')
        deepcopyTest = deepcopy(test)
        vals = [1, 2]
        lastOutputs = [0, 0]
        for x in range(0, 10):
            outputs = deepcopyTest.forwardProp(vals)
            print('{} Forward Prop of {} produced {} with d/dx {}'
                  .format(x, vals, outputs, [x - y for x, y in
                                             zip(outputs, lastOutputs)]))
            lastOutputs = outputs

        for x in test.getAllConnections():
            print(x)
        for x in test.hiddenNodes:
            print(x)

        #graphvizNEAT(test, 'test-Genome-{}'.format(uuid.uuid1()))


if __name__ == '__main__':
    unittest.main()
