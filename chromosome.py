from copy import copy

from genome import genome
# import connectionGene
from connectionGene import connectionGene
from nodeGene import nodeGene
import random as rand
from copy import deepcopy

# TODO: consider renaming this to nuclei or something more appropriate as this contains many chromosomes


class chromosome:
    # TODO: write unit test for this. scale this unittest out to the point of removing basic_trainning.
    #              (next step is making basic_trainning a unittest)

    # TODO: handle connection reactivation
    #               CORR: this isnt necessarily necessary for functional equivalence, skip connections still exist and a
    #                           weight of 1 in a parallelNodes inConnection can make a node split essentially a skip connection

    '''
    Chromosome class for crossover, stores skeleton topologies of genomes to allow quick
    crossover after processing of each genome.
    '''

    def __init__(self):
        self.primalGenes = {}  # dictionary of {genomes: skeleton topologies}

    def readyPrimalGenes(self, targetGenome):
        '''
        acquire all split depths for a genome (topology with minimal connections) aka 'skeleton topology'
        for chromosome alignment. This helps to speed up crossover considering most fit genomes are selected more frequently.
        PARAMETERS:
            targetGenome: genome which will be processed for primal representation (skeleton topology of minimally connected nodes).
        RETURNS:
            primalGenes: stores primalGenes 'skeleton topology' representation for crossover alignment between two Genomes.
        '''
        # TODO: this can be called with crossover unless some parallelization during crossover operations is desired
        #               (if not in self.primalGenes self.readyPrimalGenes)
        # TODO: may be more fitting to use two for loops and have a [[]] s.t. [[depth1 nodes], [depth2 nodes], ...]
        #               and iterate with two for loops

        hiddenNodes = targetGenome.hiddenNodes

        connectionBuffer = []
        curConnections = []
        curDepth = 0
        self.primalGenes.update({targetGenome: []})

        for node in targetGenome.inputNodes:
            # add all initial topology connections
            for outc in node.outConnections[:len(targetGenome.outputNodes)]:
                assert outc.output in targetGenome.outputNodes and outc.input in targetGenome.inputNodes, \
                    "reached out from initial topology in assembling split depths"
                curConnections.append(outc)

        while len(curConnections) > 0:
            curDepth += 1
            for connection in curConnections:
                splitNodes = connection.splits(hiddenNodes)

                for node in splitNodes:
                    for outConnection in node.outConnections:
                        connectionBuffer.append(outConnection)
                    for inConnection in node.inConnections:
                        connectionBuffer.append(inConnection)

                    # TODO: how does this create duplicate split depths?
                    # instead of using node objects, should we store tuples of output.node.Id and input.node.id?
                    primalNode = deepcopy(node)
                    primalNode.outConnections.clear()
                    primalNode.inConnections.clear()
                    # TODO: shouldnt have any deeper objects
                    primalNode.outConnections = deepcopy(
                        [node.outConnections[0]])
                    primalNode.inConnections = deepcopy(
                        [node.inConnections[0]])
                    # TODO: deepcopy always returns a new object so duplicates appear to never have been added
                    #              needs a trace
                    if primalNode not in self.primalGenes[targetGenome]:
                        self.primalGenes[targetGenome].append(primalNode)
            curConnections.clear()
            curConnections = connectionBuffer.copy()
            connectionBuffer.clear()

    def resetDepths(self):
        '''
        called once per crossover if using zero elitism crossover (the best for RoM)
        '''
        self.primalGenes.clear()

    #   NOTE: relatively large chance to miss shallow node splits here, in which subsequent splits will be missed.
    #   should use exponential/logistic decay to reduce chance of adding based on depth
    #   this is analogous to chromosome alignment given the spatial factor of combination
    #   from the length of attachment (read more on this, however it is only abstractly pertinent)

    def crossover(self, moreFitParent, lessFitParent, globalInnovations):
        # TODO: robust to depth but needs a trace!
        # TODO: pass in probabilities
        # NOTE: remember to only compare nodeId and innovation number for nodes and connections respectively.
        #              NOT virtual object addresses. only exception is addConnection and addNode methods should
        #              handle comparison with passed object internally.
        '''
        performs crossover between to genomes producing a child genome.
        1. align chromosome
        2. stochastically acquire nodes for child from aligned chromosome
        3. stochastically add connections based on available nodes in aligned chromosome
        3. return child genome
        '''
        assert moreFitParent in self.primalGenes and lessFitParent in self.primalGenes, "depths have not been processed and cannot be aligned"
        assert moreFitParent.fitness >= lessFitParent.fitness, "less fit parent passed into the wrong positional parameter"
        childSkeleton = []

        # add fit parent nodes
        for depth in self.primalGenes[moreFitParent]:
            # TODO: fix nodeId comparisons. remove all bugs that cause novel nodes in child topologies
            # TODO: it is believed novel nodes occur when nodes are added deeper than a split that was missed.
            #               can either write a condition in chromosome alignment (add node) or
            #               make tree based rule here forcing fully connected tree.
            if any([x.comparePrimal(depth) for x in self.primalGenes[lessFitParent]]):
                # TODO: how do multiple connections occur?
                if depth.nodeId not in [x.nodeId for x in childSkeleton]:
                    print('in both parents')
                    childSkeleton.append(depth)
            elif rand.uniform(a=0, b=1) < 0.90:
                if depth.nodeId not in [x.nodeId for x in childSkeleton]:
                    childSkeleton.append(depth)

        # add less fit parent nodes
        for depth in self.primalGenes[lessFitParent]:
            if rand.uniform(a=0, b=1) < 0.25:
                if depth.nodeId not in [x.nodeId for x in childSkeleton]:
                    childSkeleton.append(depth)

        child = genome(len(moreFitParent.inputNodes), len(
            moreFitParent.outputNodes), globalInnovations)

        # ADDING NODES
        # NOTE: we are expecting node to occur in order of depth.
        # TODO: Trace out where depths are lost and where connections cant be added.
        #               innovation should still never occur here
        # TODO: this causes multiple connections with parallel splits this is normal
        while(any([x.comparePrimals(child.hiddenNodes) for x in childSkeleton])):
            for node in childSkeleton:
                allNodes = child.outputNodes + child.inputNodes + child.hiddenNodes
                allConnections = []
                for cnode in allNodes:
                    for outc in cnode.outConnections:
                        if outc not in allConnections:
                            allConnections.append(outc)
                    for inc in cnode.inConnections:
                        if inc not in allConnections:
                            allConnections.append(inc)

                for connection in allConnections:
                    if node.outConnections[0].output.nodeId == connection.output.nodeId and \
                            node.inConnections[0].input.nodeId == connection.input.nodeId:
                        # this is the split

                        # TODO: need to force this to not innovate no nodes are novel
                        #               could globalInnovations be broke?
                        #               why are some working and others not?
                        #
                        # SOLUTION: something from depth 5 added to a
                        #                      network that only has depth 3.
                        # #TODO: need to stop split search if node isnt added.
                        #                could this also be from splitting out of order?
                        # OR is innovation here okay, combining different orders of nodes from different topologies
                        # can cause new splits NEEDS A TRACE
                        child.addNode(connection, globalInnovations)
                        break

        # ADDING CONNECTIONS
        # NOTE: this seems to be working appropriately.
        # TODO: add stochastics based on more AND less fit parent

        # TODO: dont verifyConnection
        allChildNodes = child.outputNodes + child.inputNodes + child.hiddenNodes
        for node in allChildNodes:
            print('adding from moreFitParent')
            addParentConnections(node, moreFitParent,
                                 child, globalInnovations, 1)
            print('adding from lessFitParent')
            addParentConnections(node, lessFitParent,
                                 child, globalInnovations, 0.5)
            # get node in moreFitParent topology

            # now iterate over connections in less fit topology with random chance to add
        return child


def addParentConnections(targetNode, parent, child, globalInnovations, addConnectionProbability):
    # TODO: remove globalInnovations.
    # TODO: possibly dont need addConnectionProbability since nodes have already been selected and
    #              reduce probability significantly
    '''
    randomly add connections to a target node from a given parents possible connections. Checks to ensure that child has nodes available
    to support connections in parent genome.
    PARAMETERS: 
            targetNode: node to inherit connections from parent
            parent: parent scanned for connectionGenes at given shared node
            child: child genome which the given node belongs to
            globalInnovations: globalInnovations for adding connections (SHOULD NOT BE NOVEL)
            addConnectionProbability: chance to inherit a connectionGene from parent to child topology
        RETURNS:
            None. just alters the given node
    '''
    allChildNodes = child.outputNodes + child.inputNodes + child.hiddenNodes
    # TODO: extract to parent method
    for parentNode in parent.hiddenNodes:
        if parentNode.nodeId == targetNode.nodeId:
            for outc in parentNode.outConnections:
                if outc.output.nodeId in [x.nodeId for x in allChildNodes]:
                    # TODO: add probability OR keep all connections from moreFitParent
                    # get corresponding node in child topology
                    for onode in allChildNodes:
                        if onode.nodeId == outc.output.nodeId:
                            # add output connection
                            child.addConnection(connectionGene(weight=copy(
                                outc.weight), inNode=targetNode, outNode=onode), globalInnovations)

            for inc in parentNode.inConnections:
                if inc.input.nodeId in [x.nodeId for x in allChildNodes]:
                    # TODO: add probability
                    # add input connection
                    for inode in allChildNodes:
                        if inode.nodeId == inc.input.nodeId:
                            child.addConnection(connectionGene(
                                weight=copy(inc.weight), inNode=inode, outNode=targetNode), globalInnovations)
