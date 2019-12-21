import random as rand


class connectionGene:
    '''
    static class structure that holds connectionGene information. 
    Static because this concretely defines the graph (see k.stanley)
    '''

    def __init__(self, weight, inNode, outNode):
        # initialize
        self.weight = weight
        self.signal = 0
        # assign references
        self.input = inNode
        self.output = outNode
        # NEAT's deactivation for addNodeMutation (and potentially random deactivation pruning)
        self.disabled = False
        # NOTE: assigned in globalConnections set to 0 to *hopefully* assign value not int object instance from globalInnovation
        self.innovation = 0
        # add connection references in node objects
        inNode.addConnection(self)
        outNode.addConnection(self)

    # @DEPRECATED all connectiongenes are checked
    @classmethod
    def copy_from(cls, connectionGeneCopy):
        '''
        copy all attributes of an existing connection to a new instance of connectionGene object
        copy without disabled
        '''
        # TODO: ensure copying is done with local input and output nodes wrt Genome
        print('copy..')
        return cls(weight=rand.uniform(-1, 1), inNode=connectionGeneCopy.input, outNode=connectionGeneCopy.output)

    def __del__(self):
        # cleanup connection references in node objects
        # TODO: correct innovation fragmentation as well
        self.input.removeConnection(self)
        self.output.removeConnection(self)

    def exists(self, localConnections):
        '''
        comparator for checking if a connection already exists. used for innovation assignment in evaluation crossover
        '''
        if self in localConnections:  # case for genome constructor
            localConnections.remove(self)
        for potentialConnection in localConnections:
            if self.input.nodeId == potentialConnection.input.nodeId and self.output.nodeId == potentialConnection.output.nodeId:
                # print(self.input.nodeId, potentialConnection.input.nodeId,
                #       self.output.nodeId, potentialConnection.output.nodeId)
                return True
        return False
