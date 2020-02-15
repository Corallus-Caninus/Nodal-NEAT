# define input, output and hidden nodes. define activation function.
# not many features will go here at first, but may be implemented further in future research so encapsulate
from activationFunctions import softmax
import logging


class nodeGene:
    '''
    handles activation gatekeeping and encapsulates activation propogation of signals
    '''
    # TODO: nodeGene can only be created with
    #              input and output connections should
    #              be included in constructor to enfore
    #             initialization of primal nodes in encapsulation
    #             (extract to here)
    # TODO: should override object comparison __rep__? method to compare nodeId instead of virtual addressing
    #             since nodeId is only every used and nodeGenes are frequently copied to new nodeGenes

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
        # TODO: testing nodeId comparison instead
        if self.nodeId is connectionGene.output.nodeId and self.nodeId is connectionGene.input.nodeId:
            self.inConnections.append(connectionGene)
            self.outConnections.append(connectionGene)
        elif self.nodeId is connectionGene.input.nodeId:
            self.outConnections.append(connectionGene)
        elif self.nodeId is connectionGene.output.nodeId:
            self.inConnections.append(connectionGene)
        else:  # default fallthrough error
            raise Exception('ERROR: cannot connect ',
                            connectionGene.input.nodeId, '->', connectionGene.output.nodeId, ' with ', self.nodeId)

    def removeConnection(self, connectionGene):
        '''
        removes an existing connection from this node
        '''
        # TODO: decide whether to use object comparison or nodeId/innovation.
        #              nodeId/innovation is de facto
        if self.nodeId is connectionGene.input.nodeId and self.nodeId is connectionGene.output.nodeId:
            self.outConnections.remove(connectionGene)
            self.inConnections.remove(connectionGene)
        elif self.nodeId is connectionGene.input.nodeId:
            self.outConnections.remove(connectionGene)
        elif self.nodeId is connectionGene.output.nodeId:
            self.inConnections.remove(connectionGene)
        else:  # default fallthrough error
            raise Exception('ERROR: cannot delete ',
                            connectionGene, ' from ', self)

    def alignNodeGene(self, connection):
        '''
        determines if the primal node representation of this node can be created by splitting the given connectionGene
        '''
        if self.outConnections[0].output.nodeId == connection.output.nodeId and \
                self.inConnections[0].input.nodeId == connection.input.nodeId:
            return True
        else:
            return False

    # @DEPRECATED
    # def comparePrimals(self, otherNodes):
    #     '''
    #     compares this primal node against all primal nodes in list, used for chromosome alignment operations.
    #     '''
    #     return any([self.comparePrimal(x) for x in otherNodes])

    # def comparePrimal(self, otherNode):
    #     '''
    #     compares primal representation of this node against another primal node representation, used for chromosome alignment operations.
    #     '''
    #     if self.outConnections[0].output.nodeId == otherNode.outConnections[0].output.nodeId and \
    #        self.inConnections[0].input.nodeId == otherNode.inConnections[0].input.nodeId:
    #         return True
    #     else:
    #         return False

    def getUnreadyConnections(self):
        incs = [x for x in self.inConnections if x.disabled is False]

        if any([x.signal is None and x.loop is False for x in incs]):
            blockages = [
                x for x in self.inConnections if x.signal is None and x.loop is False]
            return blockages
        else:
            assert "UNREADY NODE WITHOUT UNREADY CONNECTIONS!"

    def activate(self, signal):
        activeSignal = 0
        nextNodes = []
        assert self.activated is False, "@ node {}".format(self.nodeId)

        # INPUT NODE CASE
        if signal is not None and signal is not False:
            # passively accept loop signals to input
            for inc in self.inConnections:
                if inc.signal is not None and inc.disabled is False:
                    activeSignal += inc.signal
            activeSignal = softmax(activeSignal + signal)

            for outc in [x for x in self.outConnections if x.disabled is False]:
                outc.signal = activeSignal
                # dampen reverb
                if outc.output not in nextNodes and outc.output.activated is False:
                    nextNodes.append(outc.output)
            self.activated = True

        # OUTPUT NODE CASE
        elif signal is False:
            incs = [x for x in self.inConnections if x.disabled is False]
            if any([x.signal is None and x.loop is False for x in incs]):
                # persist this node to next step due to skip connection
                # for inc in incs:
                    # if inc.signal is None and inc.loop is False:
                        # print('awating a skip connection or stuck in recurrence.. {} -> {}'.format(
                        #     inc.input.nodeId, inc.output.nodeId))
                return [self]
            else:
                for inc in [x for x in incs if x.signal is not None]:
                    activeSignal += inc.signal*inc.weight
                    # inc.signal = None

                activeSignal = softmax(activeSignal)

                for outc in [x for x in self.outConnections if x.disabled is False]:
                    outc.signal = activeSignal
                self.activated = True
                # TODO: leaves hanging node connections that never get activated
                #              need to handle propagating but graph is functional

        # HIDDEN NODE CASE
        else:
            incs = [x for x in self.inConnections if x.disabled is False]
            if any([x.signal is None and x.loop is False for x in incs]):
                # persist this node to next step due to skip connection
                # for inc in incs:
                    # if inc.signal is None and inc.loop is False:
                        # print('awating a skip connection or stuck in recurrence.. {} -> {}'.format(
                        #     inc.input.nodeId, inc.output.nodeId))
                return [self]
            else:
                for inc in [x for x in incs if x.signal is not None]:
                    # assert inc.signal is not None and inc.loop is False, " @ node {}".format(self.nodeId)
                    # if inc.signal is None:
                    #     # unready recurrent connection
                    #     continue
                    activeSignal += inc.signal*inc.weight
                    inc.signal = None

                activeSignal = softmax(activeSignal)

                for outc in [x for x in self.outConnections if x.disabled is False]:
                    outc.signal = activeSignal
                    # dampen reverb
                    if outc.output not in nextNodes and outc.output.activated is False:
                        # if outc.output.activated:
                        #     outc.loop = True
                        nextNodes.append(outc.output)
                self.activated = True

        # TODO: trace this case (recurrence) could this also be x.loop is False?
        checkNodes = []
        for node in nextNodes:
            if node.activated is False:
                checkNodes.append(node)
        return checkNodes
        # return [x for x in nextNodes if x.activated is False]
