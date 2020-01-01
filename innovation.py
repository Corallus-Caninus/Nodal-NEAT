from connectionGene import connectionGene
from nodeGene import nodeGene
import random as rand
# TODO: this is so inherent to creating connections it should be in the connectionGene constructor!
#               ConnectionGene construction is becoming spaghetti in higher order objects. Fix this.
# TODO: is it simpler to just pass in list of all existing connections to connectionGene and check in constructor?


class globalConnections:
    # TODO: refactor name since more than connections 'globalMaps'?
    '''
    keep a record of all global variables that define the fitness landscape mapping
    '''

    def __init__(self):
        # TODO: ensure these are consistent with PointsOfMutation and RiverOfMutation
        #               need to be isolated from evaluator and genepool. currently connection objects
        #               are stored only for inNode and outNode id lookup. this should only need to be
        #               shared across PointsOfMutation

        # connection objects refered to in various genomes in the genepool
        self.connections = []
        # innovation metric for novelty
        self.innovation = 0
        # node metric for innovation and cross-genome similarity
        self.nodeId = 0  # This should be held here since global variable

    #called in addConnection
    def verifyConnection(self, verifyConnection):
        '''
        checks a connection to see if it already exists
        '''
        # check all connections for matching input and output
        # TODO: find a way to lambda function transform list and search for max more efficiently than iteration

        for connection in self.connections:
            if verifyConnection.input.nodeId == connection.input.nodeId and verifyConnection.output.nodeId == connection.output.nodeId:
                verifyConnection.innovation = connection.innovation
                return verifyConnection

        self.connections.append(verifyConnection)
        self.innovation += 1
        verifyConnection.innovation = self.innovation
        return verifyConnection

    def verifyNode(self, inputNode, outputNode, isLoop):
        '''
        check to see if a newly split connection has already occured
        '''
        for firstConnection in self.connections:
            if firstConnection.input.nodeId == inputNode.nodeId:
                # iterate over all other connections searching for a matching connection between an isolated node
                for secondConnection in [x for x in self.connections if x is not firstConnection]:
                    if secondConnection.output.nodeId == outputNode.nodeId:
                        if secondConnection.input.nodeId == firstConnection.output.nodeId:
                            # a match is found
                            # create a copy of the node for the new Genome locally
                            newNode = nodeGene(firstConnection.output.nodeId)
                            inConnection = connectionGene(
                                rand.uniform(-1, 1), inputNode, newNode)
                            inConnection.innovation = firstConnection.innovation

                            outConnection = connectionGene(
                                rand.uniform(-1, 1), newNode, outputNode)
                            outConnection.innovation = secondConnection.innovation

                            if isLoop is True:
                                outConnection.loop = True

                            return newNode

        # a novel node has been acquired, update innovations
        self.nodeId += 1
        newNode = nodeGene(self.nodeId)
        self.innovation += 1
        inConnection = connectionGene(
            rand.uniform(-1, 1), inputNode, newNode)
        inConnection.innovation = self.innovation

        self.innovation += 1
        outConnection = connectionGene(
            rand.uniform(-1, 1), newNode, outputNode)
        outConnection.innovation = self.innovation

        if isLoop is True:
            outConnection.loop = True

        return newNode
