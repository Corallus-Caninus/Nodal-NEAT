import random as rand


class connectionGene:
    '''
    static class structure that holds connectionGene information. 
    Static because this concretely defines the graph (see k.stanley)
    '''

    def __init__(self, weight, inNode, outNode):
        # initialize
        self.weight = weight
        self.signal = None
        # assign references
        self.input = inNode
        self.output = outNode
        # NEAT's deactivation for addNodeMutation (and potentially random deactivation pruning)
        self.disabled = False
        # declares a connection as recursive for ease of forward propagation
        self.loop = False
        # NOTE: assigned in globalConnections set to 0 to *hopefully* assign value not int object instance from globalInnovation
        self.innovation = 0

        # add connection references in node objects
        # Check for recurrency
        if inNode.nodeId == outNode.nodeId:
            inNode.addConnection(self)
        else:
            inNode.addConnection(self)
            outNode.addConnection(self)

    def remove(self):
        if self.input.nodeId == self.output.nodeId:
            self.input.removeConnection(self)
        else:
            self.input.removeConnection(self)
            self.output.removeConnection(self)

    def exists(self, localConnections):
        '''
        comparator for checking if a connection already exists. used for innovation assignment in evaluation crossover
        '''
        for potentialConnection in [x for x in localConnections if x is not self]:
            if self.input.nodeId == potentialConnection.input.nodeId and self.output.nodeId == potentialConnection.output.nodeId:
                return True
        return False

    # TODO: BELOW IS UNUSED
    def splits(self, localNodes):
        '''
        static method for getting all nodes created from splitting this connection and creating parallel nodes
        '''
        splits = []
        for node in localNodes:
            primalInput = node.inConnections[0].input.nodeId
            primalOutput = node.outConnections[0].output.nodeId
            if self.input.nodeId == primalInput and self.output.nodeId == primalOutput:
                splits.append(node)
        return splits

    def matches(self, potentialConnection):
        '''
        comparator for checking if a connection matches another connection. This is the singular case of exists.
        '''
        if self.input.nodeId == potentialConnection.input.nodeId and self.output.nodeId == potentialConnection.output.nodeId:
            return True
        return False
