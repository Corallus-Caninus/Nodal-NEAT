from genome import genome
from innovation import globalConnections


def fitnessFunction():
    # TODO: make this functional
    '''
    define fitness function. This must be done first for every application implementing
    this algorithm.
    '''

    # DEFAULT FITNESS FUNCTION:
    # evaluate xor.. for debugging, dont let this turn into ROM/POM, build at least 2-3 test cases asap before feature addition
    return 0

# TODO: verify proper copys are used unless reference is being passed
# TODO: matplotlib for debugging. make a gui to test code further


class evaluator:
    # TODO: how to make this safe for parallelism (e.g.: a connection is discovered in two seperate genomes concurrently.)
    #               how can this be interrupt handled post-generation?
    # TODO: Dask
    # TODO: add verbosity levels with logging for tracing at each level of encapsulation
    def __init__(self, inputs, outputs, population, connectionMutationRate, nodeMutationRate):
        self.connectionMutationRate = connectionMutationRate
        self.nodeMutationRate = nodeMutationRate

        # mutate self.innovation and self.nodeId in innovation.globalConnections
        self.globalInnovations = globalConnections()

        genepool = []
        for entry in range(0, population):
            genepool.append(
                genome(inputs, outputs, self.globalInnovations))
        self.genepool = genepool

    def crossover(self, firstGenome, secondGenome):
        # TODO: implement nodeId and globalConnections
        #               NOTE: nodeId needs to be updated accordingly unless a better solution can be found
        if firstGenome.fitness > secondGenome.fitness:
            child = firstGenome  # TODO: crossover operation
        else:
            child = secondGenome  # TODO: crossover opreration with fitness bias of parent
        # Add mutation modifiers
        # allConnections = map(lambda x: x.connections, self.genepool)

        # if rand.uniform(0,1) > nodeMutationRate:
        #   self.innovation += child.addNodeMutation(
        #   self.nodeMutationRate, self.innovation)
        # if rand.uniform(0, 1) > connectionMutationRate:
        #   self.innovation += child.addConnectionMutation(
        #   self.innovation)
