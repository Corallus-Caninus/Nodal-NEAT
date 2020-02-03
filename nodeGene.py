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
    #              be included in constructor

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
    # @DEPRECATED
    # def getUnreadyConnection(self):
    #     # unreadys = []
    #     incs = [x for x in self.inConnections if x.disabled is False]
    #     if any([x.signal is None and x.loop is False for x in incs]):
    #         # persist this node to next step due to skip connection
    #         for inc in incs:
    #             if inc.signal is None and inc.loop is False:
    #                 firstBlockage = [
    #                     x for x in incs if x.loop is False and x.signal is None][0]
    #                 print('retrieving recurrent connection.. {} -> {}'.format(
    #                     inc.input.nodeId, inc.output.nodeId))
    #                 return firstBlockage
    #         #         unreadys.append(inc)
    #         # return unreadys
    #     else:
    #         assert "UNREADY NODE WITHOUT UNREADY CONNECTIONS!"

    def getUnreadyConnections(self):
        unreadys = []
        incs = [x for x in self.inConnections if x.disabled is False]
        if any([x.signal is None and x.loop is False for x in incs]):
            # persist this node to next step due to skip connection
            blockages = [
                x for x in self.inConnections if x.signal is None and x.loop is False]
            # for inc in incs:
            #     if inc.signal is None and inc.loop is False:
            #         blockages = [
            #             x for x in incs if x.loop is False and x.signal is None]
            #         print('retrieving recurrent connection.. {} -> {}'.format(
            #             inc.input.nodeId, inc.output.nodeId))
            #         # return firstBlockage
            #         unreadys.append(inc)
            return blockages
        else:
            assert "UNREADY NODE WITHOUT UNREADY CONNECTIONS!"

    def activate(self, signal):
        activeSignal = 0
        nextNodes = []
        assert self.activated is False, "@ node {}".format(self.nodeId)

        if signal is not None and signal is not False:  # INPUT NODE CASE
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

        elif signal is False:  # OUTPUT NODE CASE
            incs = [x for x in self.inConnections if x.disabled is False]
            if any([x.signal is None and x.loop is False for x in incs]):
                # persist this node to next step due to skip connection
                for inc in incs:
                    if inc.signal is None and inc.loop is False:
                        print('awating a skip connection or stuck in recurrence.. {} -> {}'.format(
                            inc.input.nodeId, inc.output.nodeId))
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
        else:  # HIDDEN NODE CASE
            incs = [x for x in self.inConnections if x.disabled is False]
            if any([x.signal is None and x.loop is False for x in incs]):
                # persist this node to next step due to skip connection
                for inc in incs:
                    if inc.signal is None and inc.loop is False:
                        print('awating a skip connection or stuck in recurrence.. {} -> {}'.format(
                            inc.input.nodeId, inc.output.nodeId))
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
