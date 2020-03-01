from nodeGene import nodeGene as node
from connectionGene import connectionGene as connection
from network import processSequences
import random as rand
from activationFunctions import softmax
import logging
from math import sqrt
# import numpy as np

# TODO: write unittests for forwardProp and loop detection (re-organize)


class genome:
    # TODO: rename to nodal-neat to emphasis chromosome alignment operation.
    #              (pruning of dissimalar topologies to refine genepool error vector)
    # NOTE: graphs are defined by their Node objects not Connections. Node defined networks
    # allow for more interesting encapsulation and swappable implementations as well as make
    #  recurrent, energy based etc. networks easier to implement. Connection defined topologies are skipped
    #  in favor of a 'numpifier' which compiles the traced network down to a series of almost if not
    #  entirely numpy operations. This network is not lightweight nor ideal for real time forward propagation
    #  but prefered  for ease of crossover, mutability etc. (relatively low frequency operations) and high level
    #  exploration of network topologies. The graph executor would preferably be written in the numpy C API
    #  and embedded or saved in a npy format but this development should be empirically justified.
    #
    # even though this is node based, connection innovation numbers can be used for genetic positioning (and therefore distance)
    # considering nodeGenes allows for complete complexification considerations in crossover, allowing each generation to sample
    # a spread of much more complex to much simpler topologies instead of just more complex. a configurable sliding window of complexity
    # helps to create definite and more robust fitness manifold vectors.
    #
    # Use numpy recarray for compiling and slice. consider jax
    #
    #  create matrix from forward prop numpy.array steps. create a masking matrix for gatekeeping/recurrence
    #  and two float matrices for signal and weights (perform matrix-wise activation of the mat-mul result matrix)
    #   trace FSM manually before scripting attempt.
    '''
    a genome built with fully connected initial topology

    Parameters:
        inputSize: integer size of input nodes
        outputSize: integer size of output nodes
        globalInnovations: list of all connections to keep things consistent
        nodeId: current highest nodeId counter for keeping globalInnovations
    Constructs:
        a fully connected topology of given input and output dimensions with random initial weights
    '''

    def __init__(self, inputSize, outputSize, globalInnovations):
        # TODO: I dont like spawn's overloading for initialization. rewrite.
        #              this is all due to initialization of nodeId in globalInnovation
        '''
        create a child genome without checking nodeId globalInnovation
        '''
        self.inputNodes = []
        self.outputNodes = []
        self.hiddenNodes = []
        self.fitness = 0
        initNodeId = 0

        for newNode in range(0, inputSize):
            initNodeId += 1
            self.inputNodes.append(node(initNodeId))

        for outNode in range(0, outputSize):
            initNodeId += 1
            self.outputNodes.append(node(initNodeId))

        for inNode in self.inputNodes:
            for outNode in self.outputNodes:
                globalInnovations.verifyConnection(connection(
                    rand.uniform(-1, 1), inNode, outNode))

    @classmethod
    # TODO: get rid of this. currently cant because of crossover starting from new genome object
    def initial(cls, inputSize, outputSize, globalInnovations):
        '''
        spawn initial genomes for genepool (sets nodeId based on initial topology)
        '''
        # TODO: this isnt the most flexible solution wrt globalInnovations. remove globalInnovations from here

        initNodeId = inputSize+outputSize
        globalInnovations.nodeId = initNodeId

        return cls(inputSize, outputSize, globalInnovations)

    def getNode(self, nodeId):
        '''
        return the node object that has the given nodeId
        '''
        allNodes = self.inputNodes + self.hiddenNodes + self.outputNodes
        for n in allNodes:
            if n.nodeId == nodeId:
                return n

    def getAllConnections(self):
        '''
        get all connections in this topology without repeats
        '''
        allConnections = []
        for snode in self.inputNodes + self.hiddenNodes + self.outputNodes:
            for outc in snode.outConnections:
                if outc not in allConnections:
                    allConnections.append(outc)
            for inc in snode.outConnections:
                if inc not in allConnections:
                    allConnections.append(inc)

        return allConnections

    def geneticLocation(self):
        '''
        returns the position of this genome
        *(used for hamming distance in speciation and location in PointsOfMutation)*
        '''
        connections = self.getAllConnections()
        innovations = [x.innovation for x in connections]

        return innovations

    def geneticDistance(self, otherGenome, c1, c2, c3):
        '''
        compute K.Stanley's distance metric traditionally used for speciation
        PARAMETERS:
            otherGenome: the genome this will be compared against
            c1: coefficient for weighting excess genes
            c2: coefficient for weighting disjoint genes
            c3: coefficient for weighting average weight differences of matching genes
        RETURNS:
            the genomic distance from this genome to otherGenome
        '''

        thisMaxGene = max(self.geneticLocation())
        otherMaxGene = max(self.geneticLocation())

        if thisMaxGene >= otherMaxGene:
            # self has more genes than otherGenome
            matchingGenes = [
                x for x in otherGenome.geneticLocation() if x in self.geneticLocation()]

            disjointGenes = [x for x in self.geneticLocation()
                             if x not in otherGenome.geneticLocation()]

            excessGenes = [x for x in self.geneticLocation()
                           if x > otherMaxGene]

            genomeSize = len(self.geneticLocation())
        else:
            # otherGenome has more genes than self
            matchingGenes = [
                x for x in otherGenome.geneticLocation() if x in self.geneticLocation()]

            disjointGenes = [x for x in self.geneticLocation()
                             if x not in otherGenome.geneticLocation()]

            excessGenes = [x for x in self.geneticLocation()
                           if x > otherMaxGene]

            genomeSize = len(otherGenome.geneticLocation())

        # return matchingGenes, disjointGenes, excessGenes
        excessTerm = c1*len(disjointGenes)/genomeSize
        disjointTerm = c2*len(excessGenes)/genomeSize

        thisMatchWeights = [
            x.weight for x in self.getAllConnections() if x.innovation in matchingGenes]
        otherMatchWeights = [
            x.weight for x in otherGenome.getAllConnections() if x.innovation in matchingGenes]
        differences = [x-y for x,
                       y in zip(thisMatchWeights, otherMatchWeights)]

        averageWeightTerm = sum(differences)/len(matchingGenes)
        averageWeightTerm = c3*averageWeightTerm

        return sqrt(excessTerm**2 + disjointTerm**2 + averageWeightTerm**2)

    def mutateConnectionWeights(self, weightMutationRate, weightPerturbRate):
        '''
        randomly changes weights of connections
        '''
        if rand.uniform(0, 1) < weightPerturbRate:
            for conect in self.getAllConnections():
                if rand.uniform(0, 1) < weightMutationRate:
                    conect.weight = rand.uniform(-1, 1)

    def addConnectionMutation(self, connectionMutationRate, globalInnovations):
        '''
        randomly adds a connection 
        PARAMETERS:
            connectionMutationRate: chance to add a connection
            globalInnovations: innovation book keeping class for genes that have been discovered in all genomes
        RETURNS:
            adds a connection to this topology
        '''
        # NOTE: num nodes^2 is number of possible connections before depleted conventions.
        #             so long as self connections and recurrent connections (but no parallel connections)
        #             are allowed
        if rand.uniform(0, 1) < connectionMutationRate:
            # only allow certain node connection directions
            allInNodes = self.inputNodes + self.hiddenNodes
            allOutNodes = self.outputNodes + self.hiddenNodes
            # TODO: should check before creating the object to prevent sudden initialization and removal
            newConnection = connection(
                rand.uniform(-1, 1), rand.choice(allInNodes), rand.choice(allOutNodes))
            self.addConnection(newConnection, globalInnovations)

    def addNodeMutation(self, nodeMutationRate, globalInnovations):
        '''
        randomly adds a node
        PARAMETERS:
            nodeMutationRate: chance to add a node
            globalInnovations: innovation book keeping class for genes that have been discovered in all genomes
        RETURNS:
            adds a node to this genome topology
        '''
        if rand.uniform(0, 1) < nodeMutationRate:
            randNode = rand.choice(
                self.hiddenNodes + self.outputNodes+self.inputNodes)
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
        '''
        adds a node into the network by splitting a connection into two connections adjoined by the new node
        '''
        # TODO: this is a little lopsided, addConnection contains loop logic and object creation
        #              whereas addNode sends these operations to globalInnovations

        replaceConnection.disabled = True

        # check splitDepth, the equivalent to checking localConnections
        # but parallel nodes are allowed as apposed to parallel connections
        splitDepth = replaceConnection.splits(self.hiddenNodes)
        # check global innovation of the two new connections
        newNode = globalInnovations.verifyNode(
            splitDepth, replaceConnection)

        logging.info('newNode {}'.format(newNode.nodeId))

        # add this genome
        self.hiddenNodes.append(newNode)

        # newly mutated genome is ready
        self.resetLoops()
        self.resetSignals()
        return newNode

    def addConnection(self, newConnection, globalInnovations):
        '''
        add a unique connection into the network attaching two nodes, self connections and recurrent connections are allowed

        Checks if a connection already exists locally (prevents parallel edges) or globally (innovation consistency).
        also checks if a connection creates a loop closure and marks it as recurrent.
        '''
        allNodes = self.hiddenNodes+self.outputNodes+self.inputNodes
        for checkNode in allNodes:
            if newConnection.exists(checkNode.outConnections + checkNode.inConnections) == True:
                    # TODO: this clips mutation rates probability distribution for cases:
                    #              connectionMutationRate>>nodeMutationRate and very small, sparse networks
                    #               instead check if numConnections = allNodes**2
                    #               NEAT must be robust for further development wrt prob distribution in both
                    #               latent and environment sampling
                logging.info('mutation Failed: already in this genome')
                logging.info('{} {}'.format(newConnection.input.nodeId,
                                            newConnection.output.nodeId))
                newConnection.remove()
                return

        newConnection = globalInnovations.verifyConnection(newConnection)
        logging.info('new connection acquired')
        logging.info('{} {}'.format(newConnection.input.nodeId,
                                    newConnection.output.nodeId))

        # newly mutated Genome is ready
        self.resetLoops()
        self.resetSignals()

    ###FORWARD PROPAGATION SPECIFIC OPERATIONS###
    def resetLoops(self):
        '''
        resets all connections in this genome to connection.loop = False
        unless obvious recursion (input is output)
        '''
        # reset all loops from previous topology
        for node in self.inputNodes + self.outputNodes + self.hiddenNodes:
            for connect in node.inConnections + node.outConnections:
                if connect.input is connect.output:
                    connect.loop = True
                else:
                    connect.loop = False

    def resetSignals(self):
        '''
        resets all connection signals in this genome (even recurrent)
        '''
        for node in self.inputNodes + self.outputNodes + self.hiddenNodes:
            for outc in node.outConnections:
                outc.signal = None
            for inc in node.inConnections:
                inc.signal = None

    def resetNodes(self):
        '''
        reset all activated nodes in this genome. used once forward propagation completes a cycle
        '''
        for activeNode in self.inputNodes + self.outputNodes + self.hiddenNodes:
            activeNode.activated = False

    def forwardProp(self, signals):
        assert len(signals) == len(self.inputNodes)

        nextNodes = []
        nodeBuffer = []

        nodeTimeout = {}
        orders = processSequences(self)  # TODO: BUBBLES!!!!

        # NOTE: Overestimate
        largestCircle = len(self.inputNodes) + \
            len(self.hiddenNodes) + len(self.outputNodes)

        for inode, sig in zip(self.inputNodes, signals):
            # print('input node is: {}'.format(inode.nodeId))
            stepNodes = inode.activate(sig)
            # prevent reverb in forward prop
            for step in stepNodes:
                if step not in nodeBuffer and step not in self.inputNodes:
                    # let recurrent nodes get reappended and catch loop in activation condition
                    nodeBuffer.append(step)

        # print('entering hidden layer..')
        while len(nodeBuffer) > 0:
            # print('STEP FORWARD', [x.nodeId for x in nodeBuffer])
            for curNode in nodeBuffer:

                stepNodes = curNode.activate(None)

                if curNode not in stepNodes and curNode in nextNodes:
                    nextNodes.remove(curNode)

                for step in [x for x in stepNodes if x in self.hiddenNodes]:
                    #TODO: activated condition should be redundant with nodeGene.activate method
                    if step not in nextNodes and step.activated is False:
                        nextNodes.append(step)
                        
            if nodeBuffer == nextNodes:
                #TODO need to check if orders is appropriate
                unreadyConnections = [x.getUnreadyConnections() for x in nodeBuffer]
                unreadyConnections = [x for y in unreadyConnections for x in y]
                min([x for x in unreadyConnections],
                        key=lambda x: orders[x.input] if x.input in self.hiddenNodes else float('inf')).loop=True
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
                    activeSignal += inc.signal*inc.weight
                    # inc.signal = None
            activeSignal = softmax(activeSignal)
            outputs.append(activeSignal)

        self.resetNodes()
        # hacky resetSignals that keep recurrence
        for x in self.getAllConnections():
            if x.loop is False:
                x.signal = None

        return outputs
