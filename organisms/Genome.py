import logging
import random as rand
from math import sqrt

from organisms.ConnectionGene import ConnectionGene as Connection
from organisms.NodeGene import NodeGene as Node
from organisms.activationFunctions import softmax


# from organisms.network import processSequences


# NOTE: doesnt support extrema connections. (connections between inputs and outputs)
#       this simplifies the implementation but should be changed when numpified or
#       low level genome changes.

class Genome:
    # TODO: Use numpy recarray (consider jax for scalability not necessary for awhile).
    #  create matrix from forward prop numpy.array steps. create a masking matrix
    #  for recurrence and two float matrices for signal and weights (perform matrix-wise
    #  activation of the mat-mul result matrix) trace FSM manually before scripting attempt.
    #       dont be a chicken. implement all genetic ops and crossover with numpy array.
    """
    a Genome built with fully connected initial topology

    Parameters:
        inputSize: integer size of input nodes
        outputSize: integer size of output nodes
        globalInnovations: list of all connections to keep things consistent
    Constructs:
        a fully connected topology of given input and output dimensions with random
        initial weights
    """

    def __init__(self, inputSize, outputSize, globalInnovations):
        # TODO: I don't like spawn's overloading for initialization. rewrite.
        # this is all due to initialization of nodeId in globalInnovation
        """
        create a child Genome without checking nodeId globalInnovation
        """
        self.inputNodes = []
        self.outputNodes = []
        self.hiddenNodes = []
        self.fitness = 0
        initNodeId = 0

        for newNode in range(0, inputSize):
            initNodeId += 1
            self.inputNodes.append(Node(initNodeId))

        for outNode in range(0, outputSize):
            initNodeId += 1
            self.outputNodes.append(Node(initNodeId))

        for inNode in self.inputNodes:
            for outNode in self.outputNodes:
                globalInnovations.verifyConnection(Connection(
                    rand.uniform(-1, 1), inNode, outNode))

    # TODO: I dont like this.. think of a way to clean this up a little.
    #       This breaks passed in globalInnovation
    @classmethod
    def initial(cls, inputSize, outputSize, globalInnovations):
        """
        spawn initial genomes for genepool (sets nodeId based on initial topology)
        """
        # TODO: this isn't the most flexible solution wrt GlobalInnovations.
        #       remove GlobalInnovations from here

        # TODO: this is a hack and needs to be reworked. when reworked just cleanup
        #       as mentioned in above TODO
        if globalInnovations.nodeId == 0:
            initNodeId = inputSize + outputSize
            globalInnovations.nodeId = initNodeId

        return cls(inputSize, outputSize, globalInnovations)

    def getNode(self, nodeId):
        """
        return the Node object that has the given nodeId
        """
        allNodes = self.inputNodes + self.hiddenNodes + self.outputNodes
        for n in allNodes:
            if n.nodeId == nodeId:
                return n

    def getAllConnections(self):
        """
        get all connections in this topology without repeats
        """
        allConnections = []
        for snode in self.inputNodes + self.hiddenNodes + self.outputNodes:
            for outc in snode.outConnections:
                if outc not in allConnections:
                    allConnections.append(outc)
            for inc in snode.outConnections:
                if inc not in allConnections:
                    allConnections.append(inc)

        return allConnections

    # TODO: no. Technically yes but no.
    def geneticPosition(self):
        """
        returns the position of this Genome
        *(used for hamming distance in speciation and location in PointsOfMutation)*
        """
        connections = self.getAllConnections()
        innovations = [x.innovation for x in connections]

        return innovations

    # TODO: searches such as this dont scale. need to store this information
    #       with more geneticPosition features during construction to
    #       simply subtract two genomes e.g.:
    #       distance = first.geneticPosition() - second.geneticPosition()
    # TODO: I've always had a problem with connection checksum as a weight position.
    #       connections are vectors, magnitude is a lossy representation in terms of position.
    def geneticDistance(self, otherGenome, c1, c2, c3):
        """
        compute K.Stanley's distance metric traditionally used for speciation
        PARAMETERS:
            otherGenome: the Genome this will be compared against
            c1: coefficient for weighting excess genes
            c2: coefficient for weighting disjoint genes
            c3: coefficient for weighting average weight differences of matching genes
        RETURNS:
            the genomic distance from this Genome to otherGenome
        """

        thisMaxGene = max(self.geneticPosition())
        otherMaxGene = max(self.geneticPosition())

        if thisMaxGene >= otherMaxGene:
            # self has more genes than otherGenome
            matchingGenes = [
                x for x in otherGenome.geneticPosition() if x in self.geneticPosition()]

            disjointGenes = [x for x in self.geneticPosition()
                             if x not in otherGenome.geneticPosition()]

            excessGenes = [x for x in self.geneticPosition()
                           if x > otherMaxGene]

            genomeSize = len(self.geneticPosition())
        else:
            # otherGenome has more genes than self
            matchingGenes = [
                x for x in otherGenome.geneticPosition() if x in self.geneticPosition()]

            disjointGenes = [x for x in self.geneticPosition()
                             if x not in otherGenome.geneticPosition()]

            excessGenes = [x for x in self.geneticPosition()
                           if x > otherMaxGene]

            genomeSize = len(otherGenome.geneticPosition())

        # return matchingGenes, disjointGenes, excessGenes
        excessTerm = c1 * len(disjointGenes) / genomeSize
        disjointTerm = c2 * len(excessGenes) / genomeSize

        thisMatchWeights = [
            x.weight for x in self.getAllConnections() if x.innovation in matchingGenes]
        otherMatchWeights = [
            x.weight for x in otherGenome.getAllConnections() if
            x.innovation in matchingGenes]
        differences = [x - y for x,
                                 y in zip(thisMatchWeights, otherMatchWeights)]

        averageWeightTerm = sum(differences) / len(matchingGenes)
        averageWeightTerm = c3 * averageWeightTerm

        return sqrt(excessTerm ** 2 + disjointTerm ** 2 + averageWeightTerm ** 2)

    def mutateConnectionWeights(self, weightMutationRate, weightPerturbRate):
        """
        randomly changes weights of connections
        """
        if rand.uniform(0, 1) < weightPerturbRate:
            for con in self.getAllConnections():
                if rand.uniform(0, 1) < weightMutationRate:
                    con.weight = rand.uniform(-1, 1)

    def addConnectionMutation(self, connectionMutationRate, globalInnovations):
        """
        randomly adds a Connection
        PARAMETERS:
            connectionMutationRate: chance to add a Connection
            globalInnovations: innovation book keeping class for genes that
                               have been discovered in all genomes
        RETURNS:
            adds a Connection to this topology
        """
        # NOTE: num nodes^2 is number of possible connections before depleted conventions.
        #             so long as self connections and recurrent connections
        #             (but no parallel connections) are allowed
        if rand.uniform(0, 1) < connectionMutationRate:
            # only allow certain Node Connection directions
            allInNodes = self.inputNodes + self.hiddenNodes
            allOutNodes = self.outputNodes + self.hiddenNodes
            # TODO: should check before creating the object to prevent sudden
            #       initialization and removal
            newConnection = Connection(
                rand.uniform(-1, 1), rand.choice(allInNodes), rand.choice(allOutNodes))
            self.addConnection(newConnection, globalInnovations)

    def addNodeMutation(self, nodeMutationRate, globalInnovations):
        """
        randomly adds a Node
        PARAMETERS:
            nodeMutationRate: chance to add a Node
            globalInnovations: innovation book keeping class for genes that have
                               been discovered in all genomes
        RETURNS:
            adds a Node to this Genome topology
        """
        if rand.uniform(0, 1) < nodeMutationRate:
            randNode = rand.choice(
                self.hiddenNodes + self.outputNodes + self.inputNodes)
            if randNode in self.hiddenNodes:
                if rand.uniform(0, 1) > 0.5:
                    randConnection = rand.choice(randNode.outConnections)
                else:
                    randConnection = rand.choice(randNode.inConnections)
            elif randNode in self.outputNodes:
                randConnection = rand.choice(randNode.inConnections)
            elif randNode in self.inputNodes:
                randConnection = rand.choice(randNode.outConnections)

            self.addNode(randConnection, globalInnovations)

    def addNode(self, replaceConnection, globalInnovations):
        """
        adds a Node into the network by splitting a Connection into two connections
        adjoined by the new Node
        """
        # TODO: this is a little lopsided, addConnection contains loop logic and
        #       object creation
        # whereas addNode sends these operations to GlobalInnovations

        replaceConnection.disabled = True

        # check splitDepth, the equivalent to checking localConnections
        # but parallel nodes are allowed as apposed to parallel connections
        splitDepth = replaceConnection.splits(self.hiddenNodes)
        # check global innovation of the two new connections
        newNode = globalInnovations.verifyNode(
            splitDepth, replaceConnection)

        logging.info('newNode {}'.format(newNode.nodeId))

        # add this Genome
        self.hiddenNodes.append(newNode)

        # newly mutated Genome is ready
        self.resetLoops()
        self.resetSignals()
        return newNode

    def addConnection(self, newConnection, globalInnovations):
        """
        add a unique Connection into the network attaching two nodes, self connections
        and recurrent connections are allowed

        Checks if a Connection already exists locally (prevents parallel edges) or
        globally (innovation consistency).
        also checks if a Connection creates a loop closure and marks it as recurrent.
        """
        allNodes = self.hiddenNodes + self.outputNodes + self.inputNodes
        for checkNode in allNodes:
            if newConnection.exists(checkNode.outConnections +
                                    checkNode.inConnections):
                # TODO: this clips mutation rates probability distribution
                # for cases:
                #              connectionMutationRate>>nodeMutationRate and
                # very small, sparse networks
                #               instead check if numConnections = allNodes**2
                #               NEAT must be robust for further development
                #               wrt prob distribution in both
                #               latent and environment sampling
                logging.info('mutation Failed: already in this Genome')
                logging.info('{} {}'.format(newConnection.input.nodeId,
                                            newConnection.output.nodeId))
                newConnection.remove()
                return

        newConnection = globalInnovations.verifyConnection(newConnection)
        logging.info('new Connection acquired')
        logging.info('{} {}'.format(newConnection.input.nodeId,
                                    newConnection.output.nodeId))

        # newly mutated Genome is ready
        self.resetLoops()
        self.resetSignals()

    # FORWARD PROPAGATION SPECIFIC OPERATIONS  #
    def resetLoops(self):
        """
        resets all connections in this Genome to Connection.loop = False
        unless obvious recursion (input is output)
        """
        # reset all loops from previous topology
        for node in self.inputNodes + self.outputNodes + self.hiddenNodes:
            for connect in node.inConnections + node.outConnections:
                if connect.input is connect.output:
                    connect.loop = True
                else:
                    connect.loop = False

    def resetSignals(self):
        """
        resets all Connection signals in this Genome including recurrent.
        """
        for node in self.inputNodes + self.outputNodes + self.hiddenNodes:
            for outc in node.outConnections:
                outc.signal = None
            for inc in node.inConnections:
                inc.signal = None

    def resetNodes(self):
        """
        reset all activated nodes in this Genome. used once forward propagation
        completes a cycle
        """
        for activeNode in self.inputNodes + self.outputNodes + self.hiddenNodes:
            activeNode.activated = False

    def forwardProp(self, signals):
        assert len(signals) == len(
            self.inputNodes), 'mismatch input tensor size'

        nextNodes = []
        nodeBuffer = []  # TODO: this is a sloppy set

        # TODO: extract loop detection to a separate method?
        # TODO: is Node timeout deprecated?
        # nodeTimeout = {}
        orders = self.processSequences()  # TODO: BUBBLES!!!!

        # NOTE: Overestimate
        # TODO: DEPRECATED
        # largestCircle = len(self.inputNodes) + \
        # len(self.hiddenNodes) + len(self.outputNodes)

        for inode, sig in zip(self.inputNodes, signals):
            # print('input Node is: {}'.format(inode.nodeId))
            stepNodes = inode.activate(sig)
            # prevent reverb in forward prop
            for step in stepNodes:
                if step not in nodeBuffer and step not in self.inputNodes:
                    # let recurrent nodes get reappended and catch loop in
                    # activation condition
                    nodeBuffer.append(step)

        # print('entering hidden layer..')
        while len(nodeBuffer) > 0:
            # print('STEP FORWARD', [x.nodeId for x in nodeBuffer])
            for curNode in nodeBuffer:

                stepNodes = curNode.activate(None)

                if curNode not in stepNodes and curNode in nextNodes:
                    nextNodes.remove(curNode)

                for step in [x for x in stepNodes if x in self.hiddenNodes]:
                    # TODO: activated condition should be redundant with
                    # NodeGene.activate method
                    if step not in nextNodes and step.activated is False:
                        nextNodes.append(step)

            # loop detection routine
            if nodeBuffer == nextNodes:
                # TODO need to check if orders is appropriate
                unreadyConnections = [x.getUnreadyConnections() for
                                      x in nodeBuffer]
                unreadyConnections = [x for y in unreadyConnections for x in y]
                # add loop attribute to oldest unreadyConnection
                min([x for x in unreadyConnections],
                    key=lambda x: orders[x.input] if x.input in
                                                     self.hiddenNodes else float('inf')).loop = True
            nodeBuffer.clear()
            nodeBuffer = nextNodes.copy()
            nextNodes.clear()

        # harvest output signals
        outputs = []
        # print('harvesting output signals..')
        for onode in self.outputNodes:
            activeSignal = 0
            for inc in [x for x in onode.inConnections if x.disabled is False]:
                if inc.loop is True and inc.signal is None:
                    continue
                else:
                    activeSignal += inc.signal * inc.weight
                    # inc.signal = None
            activeSignal = softmax(activeSignal)
            outputs.append(activeSignal)

        self.resetNodes()
        # hacky resetSignals that keep recurrence
        for x in self.getAllConnections():
            if x.loop is False:
                x.signal = None

        return outputs

    def processSequences(self):
        # TODO: trace this out. if this worked there would never be unnecessary loop
        #       detection (minimal number of loop connections to forward prop topo)
        #
        # TODO: lots of operations but simple way is to set sequence based on depth
        #       and everytime a Connection is added set
        #             Connection.output.depth to Connection.input.depth + 1 if
        #             Connection.output.depth <= Connection.input.depth and repeat for
        #             all connections
        #             until loop closure or no outnodes
        """
        gets all split depths of all nodes in the given topology then assign Node sequence
        by checking Node depths for shorting connections. Essentially assigns layers.
        PARAMETERS:
            self: the Genome to be processed
        RETURNS:
            sequences: order of arrival for each Node that will be found in forward propagation.
        """
        sequences = {}
        connectionBuffer = []
        curConnections = []
        hiddenNodes = self.hiddenNodes

        # ACQUIRE SPLIT DEPTHS FOR HIDDEN NODES
        # TODO: extract splitDepths for crossover (chromosome alignment of skeleton/primal
        #       topologies)
        curDepth = 0
        for node in self.inputNodes:
            # add all initial topology connections
            sequences.update({node: curDepth})
            for outc in node.outConnections[:len(self.outputNodes)]:
                curConnections.append(outc)

        while len(curConnections) > 0:
            curDepth += 1
            for connection in curConnections:
                splitNode = connection.splits(hiddenNodes)

                for node in splitNode:
                    for outConnection in node.outConnections:
                        connectionBuffer.append(outConnection)
                    for inConnection in node.inConnections:
                        connectionBuffer.append(inConnection)

                    # TODO: does this cause duplicate entries for a Node
                    sequences.update({node: curDepth})

            curConnections.clear()
            curConnections = connectionBuffer.copy()
            connectionBuffer.clear()

        # SHORT ALL DEPTHS BY INCOMING CONNECTIONS
        for node in sequences:
            for inConnection in [
                x for x in node.inConnections if x.disabled is False]:
                # get incoming Connection with lowest sequence/depth
                if sequences[inConnection.input] + 1 < sequences[node]:
                    # update sequences
                    sequences[node] = sequences[inConnection.input] + 1

        # TODO: graph insight: can we say all connections with
        # sequence[inConnection.output] < sequence[inConnection.input] are loops
        return sequences
