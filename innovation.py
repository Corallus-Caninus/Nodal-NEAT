from connectionGene import connectionGene
from nodeGene import nodeGene
import random as rand
import logging
from copy import copy
# TODO: this is so inherent to creating connections it should be in the connectionGene constructor! maybe not..
#               ConnectionGene construction is becoming spaghetti in higher order objects. Fix this.
# TODO: is it simpler to just pass in list of all existing connections to connectionGene and check in constructor?

# TODO: Ensure copy is used properly.. ugh.. python.
# TODO: write unittests for comparing innovation after simple mutations against expected returns

# NOTE: copying objects increases reference count and allows equivalence comparison in reflection


class globalConnections:
    # TODO: refactor name since more than connections-- 'globalMaps'?
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
                logging.info('INNOVATION: connection match! {}'.format([
                    x.innovation for x in self.connections]))
                verifyConnection.innovation = copy(connection.innovation)
                return verifyConnection

        logging.info('INNOVATION: novel connection')
        self.innovation += 1
        verifyConnection.innovation = copy(self.innovation)
        self.connections.append(copy(verifyConnection))
        return verifyConnection

    def verifyNode(self, localParallelNodes, replaceConnection):
        # TODO: seemingly patched run more tests
        '''
        check to see if a newly split connection has already occured
        PARAMETERS:
            localParallelNodes: all nodes that appear locally from splitting replaceConnection.
            replaceConnection: the connection being split to create a new node.
            isLoop: if the replaceConnection is a loop, the outputConnection from newly formed node must also indicated a loop
        RETURNS:
            a newNode with proper global innovation backing.
        '''
        inputNode = replaceConnection.input
        outputNode = replaceConnection.output
        globalMatches = []
        localSplits = len(localParallelNodes)
        # TODO: constructed nodeGene object should be passed in here for verification just as connectionGene or
        #             these two methods need to be extracted to nodeGene and connectionGene constructors, leaving innovation.py
        #             as a class based data structure (not terrible since segues into RoM PoM paradigm but bloats gene classes)

        for split in self.splitConnections:
            if split == replaceConnection.innovation:
                globalMatches = self.splitConnections[split]
                # NOTE: Unique because dictionary so done here
                break
        logging.info('localSplits {}   global matches {}'.format(
            localSplits, len(globalMatches)))

        if localSplits - len(globalMatches) >= 0:
            # NOVEL
            # TODO: would rather move the node creation stuff to genome.addNode method. lots of jumping around
            self.nodeId += 1
            newNode = nodeGene(copy(self.nodeId))
            # dont create split from global pool as will connect across genepool

            # TODO: could be error when splitting loop connection
            self.innovation += 1
            inConnection = connectionGene(
                rand.uniform(-1, 1), inputNode, newNode)
            inConnection.innovation = copy(self.innovation)

            self.innovation += 1
            outConnection = connectionGene(
                copy(replaceConnection.weight), newNode, outputNode)
            outConnection.innovation = copy(self.innovation)

            logging.info('Global Innovation: Global node found: {} -> {} -> {}'.format(
                inConnection.input.nodeId, inConnection.output.nodeId, outConnection.output.nodeId))

            if replaceConnection.innovation in self.splitConnections:
                self.splitConnections[replaceConnection.innovation].append(
                    # TODO: dont need inConnection and outConnection here, split connection innovation is sufficient
                    (inConnection, outConnection))
            else:
                self.splitConnections[replaceConnection.innovation] = [
                    (inConnection, outConnection)]

            return newNode

        elif localSplits - len(globalMatches) < 0:
            # NOT NOVEL
            # TODO: would rather move the node creation stuff to genome.addNode method

            for m in globalMatches:
                if m[0].output.nodeId not in [x.nodeId for x in localParallelNodes]:
                    match = m
                    # TODO: should be first match to keep iteration of parallel splits across genomes

            newNode = nodeGene(copy(match[0].output.nodeId))
            logging.info('INNOVATION: node match {}'.format(
                match[0].output.nodeId))

            inConnection = connectionGene(
                rand.uniform(-1, 1), inputNode, newNode)
            inConnection.innovation = copy(match[0].innovation)

            outConnection = connectionGene(
                copy(replaceConnection.weight), newNode, outputNode)
            outConnection.innovation = copy(match[1].innovation)

            logging.info('Global Innovation: Global node match exists: {} -> {} -> {}'.format(
                inConnection.input.nodeId, inConnection.output.nodeId, outConnection.output.nodeId))

            return newNode
