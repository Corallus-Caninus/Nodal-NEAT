import random as rand
from copy import deepcopy
from functools import partial
from multiprocessing import Pool

from organisms.Genome import Genome
from organisms.Nuclei import Nuclei
from organisms.innovation import GlobalInnovations


# DEFAULT FITNESS FUNCTION:
# evaluate xor.. for debugging, don't let this turn into ROM/POM, build at
# least 2-3 test cases asap before feature addition

# TODO: how to make this safe for parallelism (e.g.: a Connection is discovered in two separate genomes concurrently.)
#               how can this be interrupt handled post-generation?
# TODO: Dask or paxos if scaled up sufficiently.
# TODO: add verbosity levels with logging for tracing at each level of encapsulation
# NOTE: optimization considerations:
# TODO: Numpy/Scipy for low level representation and methods. networkx for creating initial adjacency matrix?
# TODO: implement this in Cython

# @DEPRECATED
# def massSpawn(inputs, outputs, GlobalInnovations, count):
# return Genome.initial(inputs, outputs, GlobalInnovations)

def massSpawn(target_genome, count):
    """
    used for parallel mapping to spawn a Genome. count is ignored.
    """
    return deepcopy(target_genome)


class Evaluator:
    """
    create a genepool for evolution of a given fitness function. This is the main
    class for NEAT.
    """

    def __init__(self, inputs, outputs, population,
                 connectionMutationRate, nodeMutationRate, weightMutationRate,
                 weightPerturbRate, selectionPressure):
        # hyperparameters
        self.connectionMutationRate = connectionMutationRate
        self.nodeMutationRate = nodeMutationRate
        self.weightMutationRate = weightMutationRate
        # some kind of gradient descent might not be crazy here..
        self.weightPerturbRate = weightPerturbRate
        self.selectionPressure = selectionPressure

        # mutate self.innovation and self.nodeId in
        # innovation.GlobalInnovations
        self.globalInnovations = GlobalInnovations()
        self.nuclei = Nuclei()
        self.standing = Pool()

        seed = Genome.initial(inputs, outputs, self.globalInnovations)
        massSpawner = partial(massSpawn, seed)

        # with Pool() as divers:
        # self.genepool = divers.map(massSpawner, range(population))
        self.genepool = self.standing.map(massSpawner, range(population))

    def score(self, fitnessFunction):
        """
        score genepool for initialization

        PARAMETERS:
            fitnessFunction: a function that takes a Genome as a parameter and returns
                             the Genome with a fitness float local variable associated
        RETURNS:
            None, sets fitness on all members of genepool
        """
        # with Pool() as swimmers:
        # self.genepool = swimmers.map(fitnessFunction, self.genepool)
        self.genepool = self.standing.map(fitnessFunction, self.genepool)

    def nextGeneration(self, fitnessFunction):
        """
        step forward one generation. Processes each Genome with the given
        fitnessFunction and crosses over members of current Genome, selecting parents
        biased to fitness.

        PARAMETERS:
            fitnessFunction: a function that takes a Genome as a parameter and returns
            the Genome with a fitness float local variable associated
        RETURNS:
            None, sets self.genepool to next generation offspring (no elitism crossover)
        """
        # TODO: test this then @DEPRECATED
        # assert all([x.fitness is not 0 for x in self.genepool]), \
        # "need to initialize genepool scoring with a call to Evaluator.score() \
        # before iterating generations"

        nextPool = []
        globalCrossover = partial(self.nuclei.crossover,
                                  globalInnovations=self.globalInnovations)

        # @DEPRECATED
        # if any([x.fitness >= fitnessObjective for x in self.genepool]):
        #     print('SOLVED {}'.format(max([x.fitness for x in self.genepool])))
        # print('max fitness in genepool: {}'.format(max([x.fitness for x in
        #       self.genepool])))
        # print('average fitness in genepool: {}'.format(sum([x.fitness for x in
        #       self.genepool])/len(self.genepool)))

        assert all([x.fitness is not None for x in self.genepool]), \
            "missed fitness assignment in Evaluator"

        self.nuclei.resetPrimalGenes()

        # TODO: keep thread pools standing as long as possible to prevent resource
        #       acquisition issues. create local pool that is up for the lifetime of this Evaluator.
        # TODO: consider making crossover consistent to not have to loop.
        while len(nextPool) < len(self.genepool):
            parent1, parent2 = [], []
            self.genepool = sorted(
                self.genepool, key=lambda x: x.fitness, reverse=True)
            for x in range(0, len(self.genepool) - len(nextPool)):
                parent1.append(
                    self.genepool[self.selectBiasFitness(self.selectionPressure)])
                # parent1.append(self.selectBiasFitness(self.selectionPressure))
                # NOTE: crosses over with self
                parent2.append(
                    self.genepool[self.selectBiasFitness(self.selectionPressure)])
                # parent2.append(self.selectBiasFitness(self.selectionPressure))

                # with Pool() as sinkers:
                rawNextPool = self.standing.starmap(
                    globalCrossover, zip(parent1, parent2))

            for x in rawNextPool:
                if len(nextPool) == len(self.genepool):
                    break
                else:
                    nextPool.append(x)

            print('mutating..')
            # TODO: put this in parallel
            #      (requires: innovation novelty parallelism)
            for child in nextPool:
                self.mutations(child)

            # evaluate fitness
            # with Pool() as swimmers:
            # self.genepool = swimmers.map(fitnessFunction, nextPool)
            self.genepool = self.standing.map(fitnessFunction, nextPool)

    def mutations(self, child):
        """
        sequentially add mutations to a Genome due to globalInnovation's current
        data structure.

        PARAMETERS:
            child: child Genome to inherit mutations
        RETURNS:
            alters the Genome stochastically adding a Node, Connection and changing
            weights of connections in the Genome
        """
        child.addNodeMutation(
            self.nodeMutationRate, self.globalInnovations)
        child.addConnectionMutation(
            self.connectionMutationRate, self.globalInnovations)
        child.mutateConnectionWeights(
            self.weightMutationRate, self.weightPerturbRate)

    def selectBiasFitness(self, selectionPressure):
        """
        get a Genome selection index.
        RETURNS:
            selection: an index in genepool list
        """
        # TODO: implement many different selection pressure methods
        #       investigate the tournament selection method.
        #           (probably not noteworthy #NFL)
        # cull bottom nth of genepool
        bias = len(self.genepool) // selectionPressure
        totalFitness = sum([x.fitness for x in self.genepool[:bias]])
        curFit = 0
        targetFit = rand.uniform(0, 1) * totalFitness
        for ge in self.genepool[:bias]:
            curFit += ge.fitness
            if curFit > targetFit:
                return self.genepool.index(ge)
        return rand.randint(0, len(self.genepool) - 1)

    def getMaxFitness(self):
        return max([x.fitness for x in self.genepool])
