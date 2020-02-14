from genome import genome
from innovation import globalConnections
from nuclei import nuclei
import random as rand
import logging


def fitnessFunction():
    # TODO: make this functional
    '''
    define fitness function. This must be done first for every application implementing
    this algorithm.
    '''

    # DEFAULT FITNESS FUNCTION:
    # evaluate xor.. for debugging, dont let this turn into ROM/POM, build at least 2-3 test cases asap before feature addition
    return 0

    # TODO: make a seperate NEAT package that is called in PoM/RoM. this allows seperate versioning :)
    # TODO: branch this off into a NEAT algorithm and PoM/RoM so PoM/RoM can be selectively merged with NEAT updates
    # TODO: how to make this safe for parallelism (e.g.: a connection is discovered in two seperate genomes concurrently.)
    #               how can this be interrupt handled post-generation?
    # TODO: Dask
    # TODO: add verbosity levels with logging for tracing at each level of encapsulation
    # TODO: can networkx be used for forward propagation given associative matrix?
    # TODO: implement this in Cython


class evaluator:
    # TODO: pass in inheritance rates (addNodeFitParent, addNodeLesserParent, (and possibly: addConnectionFitParent, addConnectionLesserParent))
    def __init__(self, inputs, outputs, population, connectionMutationRate, nodeMutationRate):
        self.connectionMutationRate = connectionMutationRate
        self.nodeMutationRate = nodeMutationRate

        # mutate self.innovation and self.nodeId in innovation.globalConnections
        self.globalInnovations = globalConnections()
        self.nuclei = nuclei()

        genepool = []
        for entry in range(0, population):
            logging.info('EVALUATOR: building a genome in genepool')
            genepool.append(
                genome.initial(inputs, outputs, self.globalInnovations))
        self.genepool = genepool
        logging.info('EVALUATOR: done constructing evaluator')

    def nextGeneration(self):
        '''
        Step forward one generation. Crosses over members of current genome, selecting parents
        biased to fitness.
        '''
        # TODO: ensure all genomes have been evaluated and assigned fitness
        # assert all([x.fitness is not None for x in genepool])
        nextPool = []

        while len(nextPool) < len(self.genepool):
            # TODO: add proper fitness bias with something real (logit, gamma, poisson etc. reading to be done)
            biasFitnessSelect = sorted(
                [x for x in self.genepool], key=lambda x: x.fitness, reverse=True)
            # TODO: does this effect globalInnovations? new list but should be shallow copy
            # TODO: do we need to reset primalGenes in the loop? extract this to a setup operation
            self.nuclei.resetPrimalGenes()
            for ge in biasFitnessSelect:
                self.nuclei.readyPrimalGenes(ge)

            firstParent = biasFitnessSelect[rand.randint(
                0, int(len(self.genepool)/2))]
            secondParent = biasFitnessSelect[rand.randint(
                0, len(self.genepool)-1)]

            if firstParent.fitness > secondParent.fitness:
                nextPool.append(self.nuclei.crossover(
                    firstParent, secondParent, self.globalInnovations))
            else:
                nextPool.append(self.nuclei.crossover(
                    secondParent, firstParent, self.globalInnovations))
        self.genepool.clear()
        self.genepool = nextPool.copy()
        print('new genepool with {} members'.format(len(self.genepool)))
        nextPool.clear()

        return self.genepool
