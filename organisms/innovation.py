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


class globalInnovations:
    # TODO: refactor name since more than connections-- 'globalMaps'?
    '''
    keep a record of all connections and nodes that have been acquired by all genomes (global connections/nodes).
    '''

    def __init__(self):
        # all novel connections
        self.connections = []

        # used to keep track of node innovations splitConnection: (inConnection, outConnection)
        self.splitConnections = {}
        # innovation metric for connection novelty
        self.innovation = 0
        # innovation metric for node novelty
        self.nodeId = 0

    # called in addConnection
    def verifyConnection(self, verifyConnection):
        '''
        checks a connection to see if it has already been discovered.
        PARAMETERS:
            verifyConnection: a potentially novel connection
        RETURNS:
            verifyConnection with the proper innovation number associated.
        '''
        # TODO: find a way to lambda function transform list and search for max more efficiently than iteration

        # check all connections for matching input and output
        for connection in self.connections:
            # TODO: should be using connection.exists method
            if verifyConnection.input.nodeId == connection.input.nodeId and verifyConnection.output.nodeId == connection.output.nodeId:
                logging.info('INNOVATION: connection match {}'.format([
                    x.innovation for x in self.connections]))
                verifyConnection.innovation = copy(connection.innovation)
                return verifyConnection

        logging.info('INNOVATION: novel connection')
        self.innovation += 1
        verifyConnection.innovation = copy(self.innovation)
        self.connections.append(copy(verifyConnection))
        return verifyConnection

    def verifyNode(self, localParallelNodes, replaceConnection):
        '''
        check to see if a newly split connection has already occured
        PARAMETERS:
            localParallelNodes: all nodes local to the genome being compared that are created by splitting replaceConnection (parallel nodes).
            replaceConnection: the connection being split to create a new node.
        RETURNS:
            a newNode with proper innovation number associated (nodeId).
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
                break

        logging.info('INNOVATION: verifying node @ connection{} -> {} : localSplits {}   global matches {}'
                     .format(replaceConnection.input.nodeId, replaceConnection.output.nodeId,
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

            logging.info('INNOVATION: Global node found: {} -> {} -> {}'.format(
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

            logging.info('INNOVATION: Global node match exists: {} -> {} -> {}'.format(
                inConnection.input.nodeId, inConnection.output.nodeId, outConnection.output.nodeId))

            return newNode
