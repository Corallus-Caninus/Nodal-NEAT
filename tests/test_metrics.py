import logging
import os
import random as rand
import re
import unittest

from organisms.Evaluator import Evaluator


# @DEPRECATED
# import uuid
# from organisms.network import graphvizNEAT


def configLogfile():
    # TODO: call a separate logging file for unittests. this will make the code easier to understand for first timers
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


def myFunc(genome):
    """
    takes a Genome returns Genome with fitness associated
    """
    numTries = 20
    score = 0

    # needs to be random to prevent memorizing order of input
    for _ in range(0, numTries):
        entry1 = rand.randint(0, 1)
        entry2 = rand.randint(0, 1)

        output = genome.forwardProp([entry1, entry2])[0]

        if output >= 0.05:
            if entry1 == 1 or entry2 == 1:
                # one
                if not entry1 == 1 and entry2 == 1:
                    score += 1
        elif output < 0.05 and entry1 == 1 and entry2 == 1:
            score += 1
        elif output < 0.05 and entry1 == 0 and entry2 == 0:
            score += 1

    score = score / numTries
    # return score
    genome.fitness = score
    return genome


class TestMetrics(unittest.TestCase):
    """
    test genetic metrics.
    """

    def test_distance(self):
        # TODO: repeated in test_nuclei. rework this unittest.
        # NOTE: this tests if a Genome is crossed over with itself the same Genome
        # is produced as offspring (diversity singularity)

        configLogfile()
        # configure Nodal-NEAT
        evaluation = Evaluator(inputs=2, outputs=1, population=100,
                               connectionMutationRate=0.5, nodeMutationRate=0.2,
                               weightMutationRate=0.9, weightPerturbRate=0.3, selectionPressure=3)

        # evaluate 50 generations
        evaluation.score(myFunc)
        for x in range(0, 10):
            print('GENERATION: {}'.format(x))
            evaluation.nextGeneration(myFunc)
            print('Distance between first two genomes is: {}'.format(
                evaluation.genepool[0].geneticDistance(
                    evaluation.genepool[1], 1, 1, 1)))
            # Ensure distance is 0 else some novelty occurred (self crossover doesnt produce replication)
            assert evaluation.genepool[0].geneticDistance(evaluation.genepool[1], 1, 1, 1) == 0, \
                'novelty from crossover!'

        # sortPool = sorted([x for x in evaluation.genepool],
        # key=lambda s: s.fitness, reverse=True)
        # for c in sortPool[:10]:
        # graphvizNEAT(c, 'sample-genome_fitness-' + str(uuid.uuid1()))


if __name__ == '__main__':
    unittest.main()
