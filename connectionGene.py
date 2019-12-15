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
        # assigned in globalConnections set to 0 to *hopefully* assign value not int object instance from globalInnovation
        self.innovation = 0
        # add connection references in node objects
        inNode.addConnection(self)
        outNode.addConnection(self)

    # @DEPRECATED all connectiongenes are checked
    @classmethod
    def copy_from(cls, connectionGene):
        '''
        copy all attributes of an existing connection to a new instance of connectionGene object
        '''
        return cls(weight=rand.uniform(-1, 1), inNode=connectionGene.input, outNode=connectionGene.output)

    def __del__(self):
        # cleanup connection references in node objects
        self.input.removeConnection(self)
        self.output.removeConnection(self)

    def connectionExists(self, potentialConnection):
        '''
        comparator for checking if a connection already exists. used for innovation assignment in evaluation crossover
        '''
        if self.input == potentialConnection.input and self.output == potentialConnection.output:
            return True
        else:
            return False
