from connectionGene import connectionGene
from nodeGene import nodeGene
import random as rand
import logging
# TODO: this is so inherent to creating connections it should be in the connectionGene constructor! maybe not..
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

        # TODO: easier to keep track of split connections and count how many times a connection has been split for local match
        # self.nodes = []
        # used to keep track of node innovations splitConnection: (inConnection, outConnection)
        self.splitConnections = {}
        # innovation metric for novelty
        self.innovation = 0
        # node metric for innovation and cross-genome similarity
        self.nodeId = 0  # This should be held here since global variable

    # called in addConnection
    def verifyConnection(self, verifyConnection):
        '''
        checks a connection to see if it already exists
        '''
        # check all connections for matching input and output
        # TODO: find a way to lambda function transform list and search for max more efficiently than iteration

        for connection in self.connections:
            # TODO: should be using connection.exists method
            if verifyConnection.input.nodeId == connection.input.nodeId and verifyConnection.output.nodeId == connection.output.nodeId:
                verifyConnection.innovation = connection.innovation
                return verifyConnection

        self.connections.append(verifyConnection)
        self.innovation += 1
        verifyConnection.innovation = self.innovation
        return verifyConnection

    def verifyNode(self, localParallelNodes, replaceConnection, isLoop):
        '''
        check to see if a newly split connection has already occured
        PARAMETERS:
            localParallelNodes: all nodes that appear locally from splitting replaceConnection.
            replaceConnection: the connection being split to create a new node.
            isLoop: if the replaceConnection is a loop, the outputConnection from newly formed node must also indicated a loop
        RETURNS:
            a newNode with proper global innovation backing.
        '''
        # TODO: TRACE THIS. probability of connection split collision without RoM and pressurized crossover is exponential decay
        inputNode = replaceConnection.input
        outputNode = replaceConnection.output
        globalMatches = []
        localSplits = len(localParallelNodes)
        # check first inConnection and outConnection in node since other connections are always appended.
        # NOTE: this only works if connections are never deleted from node once added.
        #             Crossover can break this if done via k.stanley method.
        #             Crossover needs to consider exactly whole nodes and accessory connections as genes

        for split in self.splitConnections:
            if split.input.nodeId == inputNode.nodeId and split.output.nodeId == outputNode.nodeId:
                    # TODO: collect all matches (maybe a filter operation?) and subtract against local node. if difference ==1 create new node
                globalMatches.append(split)
        logging.info('localSplits {}   global matches {}'.format(
            localSplits, globalMatches))

        if localSplits - len(globalMatches) >= 0:
            # NOVEL
            # TODO: would rather move the node creation stuff to genome.addNode method. lots of jumping around
            self.nodeId += 1
            newNode = nodeGene(self.nodeId)
            # dont create split from global pool as will connect across genepool

            self.innovation += 1
            inConnection = connectionGene(
                rand.uniform(-1, 1), inputNode, newNode)
            inConnection.innovation = self.innovation

            self.innovation += 1
            outConnection = connectionGene(
                replaceConnection.weight, newNode, outputNode)
            outConnection.innovation = self.innovation

            if isLoop is True:
                outConnection.loop = True

            logging.info('Global Innovation: Global node found: {} -> {} -> {}'.format(
                inConnection.input.nodeId, inConnection.output.nodeId, outConnection.output.nodeId))

            self.splitConnections.update(
                {replaceConnection: (inConnection, outConnection)})

            return newNode

        elif localSplits - len(globalMatches) < 0:
            # NOT NOVEL
            # TODO: would rather move the node creation stuff to genome.addNode method

            # thisSplit = globalMatches[localSplits-1]
            # TODO: could this also be [0]? if novel nodes are only introduced sequentially (no parallel crossover or mutations)
            #              shouldnt make a difference but should be noted
            thisSplit = [
                x for x in globalMatches if self.splitConnections[x][0].output not in localParallelNodes].pop()

            match = self.splitConnections[thisSplit]

            newNode = nodeGene(match[0].output.nodeId)

            inConnection = connectionGene(
                rand.uniform(-1, 1), inputNode, newNode)
            inConnection.innovation = match[0].innovation

            outConnection = connectionGene(
                replaceConnection.weight, newNode, outputNode)
            outConnection.innovation = match[1].innovation

            if isLoop is True:
                outConnection.loop = True

            logging.info('Global Innovation: Global node match exists: {} -> {} -> {}'.format(
                inConnection.input.nodeId, inConnection.output.nodeId, outConnection.output.nodeId))

            return newNode
        else:
            # TODO: impossible state
            assert "Unidentified node creation missed in verifyNode!"
