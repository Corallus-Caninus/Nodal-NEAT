# define input, output and hidden nodes. define activation function.
# not many features will go here at first, but may be implemented further in future research so encapsulate
from activationFunctions import softmax


class nodeGene:
    '''
    handles activation gatekeeping and encapsulates activation propogation of signals
    '''

    def __init__(self, identifier):
        self.inConnections = []
        self.outConnections = []
        self.nodeId = identifier
        self.activated = False

    def addConnection(self, connectionGene):
        '''
        add a connection reference to this node and orients the edge based on input or output direction.
        '''
        # check if connection exists first
        # TODO: Really ought to clean up the self loop case here..
        if self is connectionGene.output and self is connectionGene.input:
            self.inConnections.append(connectionGene)
            self.outConnections.append(connectionGene)
        elif self is connectionGene.input:
            self.outConnections.append(connectionGene)
        elif self is connectionGene.output:
            self.inConnections.append(connectionGene)
        else:  # default fallthrough error
            raise Exception('ERROR: cannot connect ',
                            connectionGene, ' with ', self)

    def removeConnection(self, connectionGene):
        '''
        removes an existing connection from this node
        '''
        if self is connectionGene.input and self is connectionGene.output:
            self.outConnections.remove(connectionGene)
            self.inConnections.remove(connectionGene)
        elif self is connectionGene.input:
            self.outConnections.remove(connectionGene)
        elif self is connectionGene.output:
            self.inConnections.remove(connectionGene)
        else:  # default fallthrough error
            raise Exception('ERROR: cannot delete ',
                            connectionGene, ' from ', self)

    # TODO: implement this in cython
    def activate(self):
        '''
        activate the given node, returns all nodes outputted from 
        this process that havent been activated 
        (propogate signals by node so encapsulation can make changing graph easily e.g.: recurrent nodes, dif eq nodes etc.)
        recurrent connections are just circularity where level of recursion is the size of sequential loops
        '''
        outputSignal = 0
        nextNodes = []

        for availableConnection in self.inConnections:
            if availableConnection.signal is None and availableConnection.loop is False:
                print('SIGTRACE (hidden): unready connection {} at node {}'.format(
                    availableConnection, self))
                return self
        # TODO: ENSURE THIS DOESNT PREMATURELY ACTIVATE

        # ignore first pass with recurrency unavailable
        readyConnections = \
            [connection for connection in self.inConnections if connection.signal is not None]

        # TODO: merge this condition with readyConnection filter should be gaurunteed from genome forwardPropagation
        for connection in readyConnections:
            if connection.disabled is True:
                pass
            else:
                outputSignal += connection.signal * connection.weight
                connection.signal = None
                # TODO: ..unless recurrent? this should reset current recurrent signals (T-1)
                #              for incoming recurrent signal.
                # handles general circularity but not recurrence from node A to node A.
        outputSignal = softmax(outputSignal)
        print('SIGTRACE (hidden): ', outputSignal)

        # output nodes have no outConnections
        if(len(self.outConnections) > 0):
            for connection in self.outConnections:
                if self.activated is False and connection.disabled is False:
                    connection.signal = outputSignal
                    nextNodes.append(connection.output)
                else:
                    # TODO: can test with this using a list collecting nodes here to verify no hanging nodes
                    pass

            # used for recurrency activation gatekeeping
            self.activated = True
            return nextNodes

        assert "ERROR: FAILED NEURON"
