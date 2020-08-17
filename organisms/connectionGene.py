import random as rand


class connectionGene:
    '''
    a connectionGene between two nodes in a genome (neural network topology)
    '''

    def __init__(self, weight, inNode, outNode):
        # initialize
        self.weight = weight
        self.signal = None
        # assign this edge to nodes
        self.input = inNode
        self.output = outNode
        # NEAT's deactivation for addNodeMutation (and potentially random
        # deactivation pruning)
        self.disabled = False
        # declares a connection as recursive for ease of forward propagation
        self.loop = False
        self.innovation = 0

        # add connection references in node objects
        # Check for recurrency
        if inNode.nodeId == outNode.nodeId:
            inNode.addConnection(self)
        else:
            inNode.addConnection(self)
            outNode.addConnection(self)

    def remove(self):
        '''
        remove all references to this connection.

        *de-iterate references and call GC since each connection object exists only once in only one genome (no parallel edges)*
        '''
        if self.input.nodeId == self.output.nodeId:
            self.input.removeConnection(self)
        else:
            self.input.removeConnection(self)
            self.output.removeConnection(self)

    def splits(self, localNodes):
        '''
        get all nodes (parallel nodes) created from splitting this connection with an addNode operation.

        PARAMETER:
            localNodes: a list of nodes, used to check which nodes have been created from splitting this connection (addNode operations)
        RETURNS:
            splits: nodes that have resulted from splitting this connection
        '''
        splits = []
        for node in localNodes:
            primalInput = node.inConnections[0].input.nodeId
            primalOutput = node.outConnections[0].output.nodeId
            if self.input.nodeId == primalInput and \
                    self.output.nodeId == primalOutput:
                splits.append(node)
        return splits

    def exists(self, localConnections):
        '''
        comparator for checking if a connection already exists. used for innovation
        assignment in evaluation crossover.

        PARAMETERS:
            localConnections: connections to be checked against this, can include this
                              connection since discarded in comparison
        RETURNS:
            True if this connection is found in localConnections otherwise False
        '''
        for potentialConnection in [
                x for x in localConnections if x is not self]:
            if self.input.nodeId == potentialConnection.input.nodeId and \
                    self.output.nodeId == potentialConnection.output.nodeId:
                return True
        return False

    #NOTE: unimplemented
    def matches(self, potentialConnection):
        '''
        comparator for checking if a connection matches another connection.
        This is the singular case of exists.
        '''
        if self.input.nodeId == potentialConnection.input.nodeId and self.output.nodeId == potentialConnection.output.nodeId:
            return True
        return False
