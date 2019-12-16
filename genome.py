# include operations such as crossover with another genome
# different methods of crossover and mutation are implemented here
# DEVNOTE: should recurrent connections be handled natively/on first iteration? yes
# optimize for mat-mul when networks show this is necessary
from nodeGene import nodeGene as node
from connectionGene import connectionGene as connection
import random as rand
from activationFunctions import softmax


class genome:
    '''
    a genome built with fully connected initial topology
    Parameters:
        inputSize: integer size of input nodes
        outputSize: integer size of output nodes
        globalConnections: list of all connections to keep things consistent
        nodeId: current highest nodeId counter for keeping globalConnections
    Constructs:
        a fully connected topology of given input and output dimensions with random initial weights
    '''

    def __init__(self, inputSize, outputSize, globalConnections):
        self.inputNodes = []
        self.outputNodes = []
        self.hiddenNodes = []
        self.fitness = 0
        nodeId = 0

        for newNode in range(0, inputSize):
            nodeId += 1
            self.inputNodes.append(node(nodeId))

        for outNode in range(0, outputSize):
            nodeId += 1
            self.outputNodes.append(node(nodeId))

        for inNode in self.inputNodes:
            for outNode in self.outputNodes:
                # ConnectionGene construtor automatically adds node connections
                globalConnections.verifyConnection(connection(
                    rand.uniform(-1, 1), inNode, outNode))
        # prevents calculating after the fact and 'somewhat' less messy
        globalConnections.nodeId = nodeId

    def addNodeMutation(self, nodeMutationRate, globalConnections):
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

            self.addNode(randConnection, globalConnections)

    def addConnectionMutation(self, connectionMutationRate, globalConnections):
        '''
        randomly adds a connection and adjusts innovation if novel in the genepool
        '''
        allNodes = self.hiddenNodes+self.outputNodes+self.inputNodes
        if rand.uniform(0, 1) > connectionMutationRate:
            globalConnections.verifyConnection(connection(rand.uniform(-1, 1), rand.choice(allNodes),
                                                          rand.choice(allNodes)))

    def addNode(self, replaceConnection, globalConnections):
        replaceConnection.disabled = True
        newNode = node(globalConnections.nodeId)
        # check if inConnection inNode and outConnection outNode already exist with a common node (must be this node)
        globalConnections.verifyNode(connection(
            rand.uniform(-1, 1), replaceConnection.input, newNode), connection(
            rand.uniform(-1, 1), newNode, replaceConnection.output))

        self.hiddenNodes.append(newNode)

    # TODO: check for deactivated connections as well (should be fixed verify)
    # TODO: 'numpyify' graph for fast forward prop
    #               batch out numpified functions and return fitness from evaluator pods
    #               can use a shared queue or manager that sends results back to a genepool pod and genomes (numpy array ops) to game pods
    # TODO: encapsulate the 3 states (input hidden output) to nodegene.activate to make code here a
    #              simple loop call, this will segue to parallelization better

    def forwardProp(self, signals):
        '''
        propagate a list of signals through the network.

        Throws an error if input matrix doesnt match input node matrix of network.
        Parameters:
            signals: a list of signals to be passed through of len inputNodes
        Returns:
            signals: a list of signals to be sent to outputs of len outputNodes
        '''
        assert len(signals) == len(self.inputNodes), "Mismatch input matrix Signals: {}, Input Nodes: {}".format(
            len(signals), len(self.inputNodes))

        unfiredNeurons = []
        nextNeurons = []
        outputs = []

        ###########INITIALIZE INPUT SIGNALS###########
        for sig, inputNode in zip(signals, self.inputNodes):
            for initialConnection in inputNode.outConnections:
                if initialConnection.disabled is True:
                    pass
                else:
                    initialConnection.signal = softmax(
                        sig)  # called statically for input
                    print('SIGTRACE (init): ', initialConnection.signal,
                          ' * ', initialConnection.weight)
                    # ensure its not an input to output connection
                    if len(initialConnection.output.outConnections) > 0:
                        unfiredNeurons.append(initialConnection.output)

        ###########PROCESS HIDDEN LAYER###########
        # begin forward passing:
        while True:
            print('DEBUG: Processing {} unfiredNeurons on deck: {}'.format(
                len(unfiredNeurons), unfiredNeurons))
            for processingNode in unfiredNeurons:
                print('DEBUG: type of processingNode is: ', processingNode)
                nextNeurons.extend(processingNode.activate())
            if len(nextNeurons) > 0:
                print(nextNeurons)
                unfiredNeurons = nextNeurons
                nextNeurons.clear()
            else:
                break

        ###########ACQUIRE OUTPUT SIGNALS###########
        # do something with output, have to activate manually just as with input
        for finalNode in self.outputNodes:
            finalSignal = 0
            for finalConnection in finalNode.inConnections:
                if finalConnection.disabled is True:
                    pass
                finalSignal += finalConnection.signal * finalConnection.weight
                if finalConnection.disabled:
                    print('Disabled SIGTRACE (final): ', finalConnection.signal,
                          ' * ', finalConnection.weight)
                else:
                    print('SIGTRACE (final): ', finalConnection.signal,
                          ' * ', finalConnection.weight)

                # print('SIGTRACE (final): ', softmax(finalSignal),
                #   ' * ', finalConnection.weight)
            outputs.append(softmax(finalSignal))
        return outputs
