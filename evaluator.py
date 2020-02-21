from multiprocessing import Pool
from functools import partial
import logging
import random as rand
from genome import genome
from innovation import globalConnections
from nuclei import nuclei
from copy import deepcopy

# DEFAULT FITNESS FUNCTION:
# evaluate xor.. for debugging, dont let this turn into ROM/POM, build at least 2-3 test cases asap before feature addition

# TODO: make a seperate NEAT package that is called in PoM/RoM. this allows seperate versioning :)
# TODO: branch this off into a NEAT algorithm and PoM/RoM so PoM/RoM can be selectively merged with NEAT updates
# TODO: how to make this safe for parallelism (e.g.: a connection is discovered in two seperate genomes concurrently.)
#               how can this be interrupt handled post-generation?
# TODO: Dask
# TODO: add verbosity levels with logging for tracing at each level of encapsulation
# TODO: can networkx be used for forward propagation given associative matrix?
# TODO: implement this in Cython


# def massSpawn(inputs, outputs, globalInnovations, count):
# return genome.initial(inputs, outputs, globalInnovations)
def massSpawn(genome, count):
    return deepcopy(genome)


class evaluator:
    # TODO: pass in inheritance rates (addNodeFitParent, addNodeLesserParent, (and possibly: addConnectionFitParent, addConnectionLesserParent))
    # TODO: this is just inherit more/less connection since missing a connection prevents all subsequent splits
    # TODO: !DOCSTRING!
    # TODO: parallelize everything!
    def __init__(self, inputs, outputs, population,
                 connectionMutationRate, nodeMutationRate, weightMutationRate,
                 weightPerturbRate, selectionPressure):
        # hyperparameters
        self.connectionMutationRate = connectionMutationRate
        self.nodeMutationRate = nodeMutationRate
        self.weightMutationRate = weightMutationRate
        self.weightPerturbRate = weightPerturbRate
        self.selectionPressure = selectionPressure

        # mutate self.innovation and self.nodeId in innovation.globalConnections
        self.globalInnovations = globalConnections()
        self.nuclei = nuclei()

        # TODO: cleanup initial method
        seed = genome.initial(inputs, outputs, self.globalInnovations)
        massSpawner = partial(massSpawn, seed)

        with Pool() as divers:
            self.genepool = divers.map(massSpawner, range(population))

    def nextGeneration(self, fitnessFunction, fitnessObjective):
        '''
        step forward one generation. Processes each genome with the given 
        fitnessFunction and crosses over members of current genome, selecting parents
        biased to fitness.

        PARAMETERS:
            fitnessFunction: a function that takes a genome as a parameter and returns the genome 
                                      with a fitness float local variable associated
        RETURNS:
            None, sets self.genepool to next generation offspring (no elitism crossover)
        '''
        # TODO: consider fitnessFunctions as an abstract base class for inheritance with prototype methods.
        #              generates data and yields outputs as well as triggering fitness score return.

        # TODO: continuously evaluate fitness
        # TODO: evaluate genepool for fitness at end of generation

        nextPool = []
        globalCrossover = partial(self.nuclei.crossover,
                                  globalInnovations=self.globalInnovations)

        with Pool() as swimmers:
            # TODO: need to ensure all genepools are operating on
            #             fitnessFunction for swarm/multiagent environment optimization
            self.genepool = swimmers.map(fitnessFunction, self.genepool)

        # print(max([x.fitness for x in self.genepool]))
        if any([x.fitness == fitnessObjective for x in self.genepool]):
            print('SOLVED')

        assert all([x.fitness is not None for x in self.genepool]), \
            "missed fitness assignment in evaluator"

        self.nuclei.resetPrimalGenes()
        # @DEPRECATED
        # biasFitnessSelect = sorted(
        #     [x for x in self.genepool], key=lambda x: x.fitness, reverse=True)
        # for ge in biasFitnessSelect:
        #     self.nuclei.readyPrimalGenes(ge)

        # TODO: consider making crossover consistent to not have to loop.
        while len(nextPool) < len(self.genepool):
            parent1, parent2 = [], []

            for x in range(0, len(self.genepool) - len(nextPool)):
                parent1.append(
                    self.genepool[self.selectBiasFitness(self.selectionPressure)])
                # NOTE: crosses over with self
                parent2.append(
                    self.genepool[self.selectBiasFitness(self.selectionPressure)])

            with Pool() as sinkers:
                rawNextPool = sinkers.starmap(
                    globalCrossover, zip(parent1, parent2))

            for x in rawNextPool:
                if len(nextPool) == len(self.genepool):
                    break
                else:
                    nextPool.append(x)

            print('mutating..')
            for child in nextPool:
                self.mutations(child)

        self.genepool.clear()
        self.genepool = nextPool.copy()
        print('new genepool with {} members'.format(len(self.genepool)))
        nextPool.clear()

    def mutations(self, child):
        '''
        sequentially add mutations to a genome due to globalInnovation's current data structure.

        PARAMETERS:
            child: child genome to inherit mutations
        RETURNS:
            alters the genome stochastically adding a node, connection and changing weights of connections
            in the genome
        '''
        child.addNodeMutation(
            self.nodeMutationRate, self.globalInnovations)
        child.addConnectionMutation(
            self.connectionMutationRate, self.globalInnovations)
        child.mutateConnectionWeights(
            self.weightMutationRate, self.weightPerturbRate)

    def selectBiasFitness(self, bias):
        '''
        get a genome selection index.

        PARAMETERS:
            bias: an integer for the level of bias for selecting genomes based on fitness
        RETURNS:
            selection: an index in genepool list
        '''
        # TODO: very small chance of collision
        selection = rand.randint(0, len(self.genepool))

        for _ in range(0, bias):
            selection = selection - rand.randint(0, selection)
        return selection
