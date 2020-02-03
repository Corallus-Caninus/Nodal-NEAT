from nodeGene import nodeGene as node
from connectionGene import connectionGene as connection
from network import getDepths, processSequences
import random as rand
from activationFunctions import softmax
import logging
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
# TODO: allow for reactivating connections in crossover (possibly in mutation as well)
# TODO: crossover should consider node topology for crossover THEN randomly add connections
#              based on excess or disjoints. this is more stable mathematically and biologically. K.stanley crossover
#              is either broken or sloppy. find a Genetics agreeable representation for this operation. distance is still
#               relevant so RoM will be possible.


class genome:
    # NOTE: graphs are defined by their Node objects not Connections. Node defined networks
    # allow for more interesting encapsulation and swappable implementations as well as make
    #  recurrent, energy based etc. networks easier to implement. Connection defined topologies are skipped
    #  in favor of a 'numpifier' which compiles the traced network down to a series of almost if not
    # entirely numpy operations. This network is not lightweight nor ideal for real time forward propagation
    #  but prefered  for ease of crossover, mutability etc. (relatively low frequency operations) and high level
    #  exploration of network topologies. The graph executor would preferably be written in the numpy C API
    #  and embedded or saved in a npy format but this development should be empirically justified.
    #
    # Use numpy recarray for compiling and slice
    #  matrix into forward prop numpy.array steps. create a masking matrix for gatekeeping/recurrence
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
        create a child genome without checking globalInnovation
        '''
        # self.inputNodes = inputNodes
        # self.outputNodes = outputNodes
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
        # prevents calculating after the fact and 'somewhat' less messy
        # return self

    @classmethod
    def initial(cls, inputSize, outputSize, globalInnovations):
        '''
        spawn initial genomes for genepool
        '''
        # TODO: this isnt the most flexible solution wrt globalConnections. remove globalConnections from here
        inputNodes = []
        outputNodes = []
        hiddenNodes = []
        # fitness = 0
        initNodeId = inputSize*outputSize

        globalInnovations.nodeId = initNodeId

        return cls(inputSize, outputSize, globalInnovations)

    def addNodeMutation(self, nodeMutationRate, globalInnovations):
        '''
        randomly adds a node, if successful returns the innovation adjustment for global innovation counter
        '''
        if rand.uniform(0, 1) > nodeMutationRate:
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
        # TODO: first order of refactor: move loop logic back into here
        replaceConnection.disabled = True
        # check splitDepth, the equivalent to checking localConnections
        # but parallel nodes are allowed as apposed to parallel connections
        splitDepth = replaceConnection.splits(self.hiddenNodes)
        # check global innovation of the two new connections
        newNode = globalInnovations.verifyNode(
            splitDepth, replaceConnection, replaceConnection.loop)

        logging.info('newNode {}'.format(newNode.nodeId))

        # keep extrema loop indicators pointing to extrema nodes
        if replaceConnection.loop is True:
            newNode.outConnections[0].loop = True
            newNode.inConnections[0].loop = True

        # add this genome
        self.hiddenNodes.append(newNode)

        # newly mutated genome is ready
        self.resetLoops()
        self.resetSignals()

    def addConnectionMutation(self, connectionMutationRate, globalInnovations):
        '''
        randomly adds a connection connections to input and from output nodes are allowed (circularity at all nodes)
        '''
        # NOTE: num nodes^2 is number of possible connections before depleted conventions.
        #             so long as self connections and recurrent connections (but no parallel connections)
        #             are allowed
        if rand.uniform(0, 1) > connectionMutationRate:
            # only allow certain node connection directions
            allInNodes = self.inputNodes + self.hiddenNodes
            allOutNodes = self.outputNodes + self.hiddenNodes
            newConnection = connection(
                rand.uniform(-1, 1), rand.choice(allInNodes), rand.choice(allOutNodes))
            self.addConnection(newConnection, globalInnovations)

    def addConnection(self, newConnection, globalInnovations):
        '''
        add a unique connection into the network attaching two nodes, self connections and recurrent connections are allowed

        Checks if a connection already exists locally (prevents parallel edges) or globally (innovation consistency).
        also checks if a connection creates a loop closure and marks it as recurrent.
        '''
        allNodes = self.hiddenNodes+self.outputNodes+self.inputNodes
        for checkNode in allNodes:
            # TODO: the sum of these lists ~doubles the search space with repeats make this a set or unique
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

    ###FORWARD PROPAGATION SPECIFIC OPERATIONS###

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
        # Can loops be detected an labelled within forwardProp?
        # 1. reset loops and signals on each graph change (addConnection addNode) and add back
        #     special case loops (intra-extrema connections and self loops)
        # 2. durng forward propagation, label all stuck connections as loops accordingly
        #     (first pass detection) NOTE: how can recurrence be attributed? need to set loop
        #      connections one at a time and only for first connection in unreadyConnections
        assert len(signals) == len(self.inputNodes)

        nextNodes = []
        nodeBuffer = []

        #NOTE: Overestimate
        nodeTimeout = {}
        # depths = buildChromosome(self)
        orders = processSequences(self)
        largestCircle = 2*(len(self.inputNodes) +
                           len(self.hiddenNodes) + len(self.outputNodes))
        currentLoopLength = largestCircle

        print('entering network..')
        print('ORDERS')
        for seq in orders:
            print(seq.nodeId, orders[seq])
        # print('ORDERS: ', orders)
        print([orders[x] for x in orders])

        for inode, sig in zip(self.inputNodes, signals):
            print('input node is: {}'.format(inode.nodeId))
            stepNodes = inode.activate(sig)
            # prevent reverb in forward prop
            for step in stepNodes:
                if step not in nodeBuffer and step not in self.inputNodes:
                    # let recurrent nodes get reappended and catch loop in activation condition
                    nodeBuffer.append(step)

        print('entering hidden layer..')
        while len(nodeBuffer) > 0:
            # unreadyNodes = [] #@DEPRECATED
            print('STEP FORWARD', [x.nodeId for x in nodeBuffer])
            for curNode in nodeBuffer:
                if curNode in self.outputNodes:
                    print('OUTPUT  node is: {}'.format(curNode.nodeId))
                    stepNodes = curNode.activate(False)
                    if curNode not in stepNodes and curNode in nextNodes:
                        nextNodes.remove(curNode)
                else:
                    print('HIDDEN node is: {}'.format(curNode.nodeId))
                    stepNodes = curNode.activate(None)
                    if curNode not in stepNodes and curNode in nextNodes:
                        nextNodes.remove(curNode)
                print('hidden node pushing to: {}'.format(
                    [x.nodeId for x in stepNodes]))

                # TODO: should probably use unreadyNodes to ensure timers tick at skip detection and not always
                # if stepNodes == [curNode]:
                #     unreadyNodes.append(curNode)
                # prevent same step reverb

                # TODO: stepNodes need to be hiddenNodes as outputNodes ad inputNodes are no longer considered for looping
                # for step in stepNodes:
                for step in [x for x in stepNodes if x in self.hiddenNodes]:
                    # TODO: had step check, can step be None in list stepNodes? I think not
                    if step not in nextNodes and step.activated is False:
                        nextNodes.append(step)
                        # start counting loop timer
                        # TODO: shouldnt need >0 check
                        if step in nodeTimeout and nodeTimeout[step] > 0:
                            print('tick @ node: {}'.format(step.nodeId))
                            nodeTimeout[step] -= 1
                        else:
                            nodeTimeout.update({step: largestCircle})
                            # reset counter on all deeper nodes to ensure
                            # skip connections wait for all other connections
                            # TODO: deepest sequence is usually attributed to recurrent connections
                            for stepNode in nodeTimeout:
                                # TODO: keyerror here
                                if orders[stepNode] > orders[step]:
                                    print('RESETING TIMER ON: ',
                                          stepNode.nodeId)
                                    print('since {} {} is less than {} {}'.format(
                                        step.nodeId, step, stepNode.nodeId, stepNode))
                                    # TODO: does this need to be larger than newly added step?
                                    #             since we are overestimating this is fine for now
                                    nodeTimeout.update(
                                        {stepNode: largestCircle+1})

            # trigger timeout or update timer tick
            for timer in nodeTimeout:
                if nodeTimeout[timer] == 0:
                    print('requesting blockage from node: {}'.format(timer.nodeId))
                    # TODO: need to get unreadyConnection with lowest sequence
                    # TODO: need sequence connections (depths is connection based but doesnt consider shorts)
                    #               legit attempts to retrieve unreadyConnection from unblocked node
                    unreadyConnections = timer.getUnreadyConnections()
                    # get the connection with the highest inConnection node sequence.
                    max([x for x in unreadyConnections],
                        key=lambda x: orders[x.input]).loop=True

                    nodeTimeout[timer] = largestCircle
                    break
                assert nodeTimeout[timer] >= 0, "node clocked largestLoop"

            nodeBuffer.clear()
            nodeBuffer = nextNodes.copy()
            nextNodes.clear()

        # TODO: can this be encapsulated in activate? return a different type is sloppy
        #               adding a non-connected outConnection is kludgey
        #               this is somewhat more readable as its a true edge case

        # harvest output signals
        outputs = []
        print('harvesting output signals..')
        for onode in self.outputNodes:
            activeSignal = 0
            for inc in [x for x in onode.inConnections if x.disabled is False]:
                # recursion case? should be forward propagated due to activating of output nodes
                # assert inc.signal is not None and inc.loop is False
                # assert inc.signal is not None
                if inc.loop is True and inc.signal is None:
                    continue
                else:
                    activeSignal += inc.signal*inc.weight
                    inc.signal = None
            activeSignal = softmax(activeSignal)
            outputs.append(activeSignal)

        self.resetNodes()
        print(outputs)
        return outputs
