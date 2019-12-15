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
        # TODO: may be too many instances of connection diagram. connections should be encapsulated in one object. optimize this later..
        # check if connection exists first
        if self is connectionGene.input:
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
        if self is connectionGene.input:
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
        '''
        outputSignal = 0
        nextConnections = []  # should be next node

        # this doesnt handle recurrency?
        for connection in self.inConnections:
            if connection.disabled is True:
                pass
            outputSignal += connection.signal * connection.weight
        outputSignal = softmax(outputSignal)
        print('SIGTRACE (hidden): ', outputSignal)

        # output nodes have no outConnections
        if(len(self.outConnections) > 0):
            for connection in self.outConnections:
                if self.activated is False and connection.disabled is False:
                    connection.signal = outputSignal
                    nextConnections.append(connection)
                else:
                    pass

            # used for recurrency activation gatekeeping
            self.activated = True
            return nextConnections

        self.activated = True
        return None

    def deactivate(self):
        '''
        called after forwardProp and outputs are received
        '''
        self.activated = False
