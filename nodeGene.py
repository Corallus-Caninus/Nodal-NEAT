# define input, output and hidden nodes. define activation function.
# not many features will go here at first, but may be implemented further in future research so encapsulate
from activationFunctions import softmax
import logging


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

    def activate(self):
        '''
        activate the given node, returns all nodes in output connections
        recurrent connections are just circularity where level of recursion is the size of sequential loops
        '''
        outputSignal = 0
        nextNodes = []
        for availableConnection in self.inConnections:
            if availableConnection.signal is None and availableConnection.loop is False and availableConnection.disabled is False:
                logging.info('SIGTRACE (hidden): unready connection {}->{} at node {}'.format(
                    availableConnection.input.nodeId, availableConnection.output.nodeId, self.nodeId))
                return self

        # ignore first pass with recurrency unavailable
        readyConnections = \
            [connection for connection in self.inConnections if connection.signal is not None]

        for connection in readyConnections:
            #TODO: REDUNDANT
            if connection.disabled is True:
                pass
            else:
                outputSignal += connection.signal * connection.weight
                connection.signal = None
                logging.info('SIGTRACE (hidden) Received: {} {} {} -> {}'.format(self.nodeId, outputSignal, connection.input.nodeId,
                                                                                 connection.output.nodeId))
        outputSignal = softmax(outputSignal)

        # output nodes have no outConnections
        if(len(self.outConnections) > 0):
            for connection in self.outConnections:
                logging.info('SIGTRACE (hidden) Sending: {} {} \t\t {} -> {}'.format(
                    self.nodeId, outputSignal, connection.input.nodeId, connection.output.nodeId))
                if connection.disabled is False:
                    connection.signal = outputSignal
                    if connection.loop is False:
                        nextNodes.append(connection.output)
                else:
                    # TODO: trace and remove
                    assert 'SIGTRACE (hidden): BAD STATE!!'

            # used for recurrency activation gatekeeping
            self.activated = True
            return nextNodes

        assert "ERROR: FAILED NEURON"
