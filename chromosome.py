from copy import copy

from genome import genome
import connectionGene
from nodeGene import nodeGene
import random as rand
from copy import deepcopy

# TODO: consider renaming this to nuclei or something more appropriate as this contains many chromosomes


class chromosome:
    # TODO: write unit test for this. scale this unittest out to the point of removing basic_trainning.
    #              (next step is making basic_trainning a unittest)

    # TODO: handle connection reactivation

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
                    primalNode = deepcopy(node)
                    primalNode.outConnections.clear()
                    primalNode.inConnections.clear()
                    # TODO: shouldnt have any deeper objects
                    primalNode.outConnections = deepcopy(
                        [node.outConnections[0]])
                    primalNode.inConnections = deepcopy(
                        [node.inConnections[0]])
                    # TODO: ensure we can still perform proper comparisons in crossover
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
        # TODO: globalInnovations shouldnt need to be passed in, consider implementing chromosome from evaluator
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
        for depth in self.primalGenes[moreFitParent]:
            # TODO: should also consider less fit parent, this is purely pruning
            # since nodes are globally consistent we can compare with nodeId here
            # does this comparison really work?
            if any([x.comparePrimal(depth) for x in self.primalGenes[lessFitParent]]):
                if depth not in childSkeleton:
                    print('in both parents')
                    childSkeleton.append(depth)
            elif rand.uniform(a=0, b=1) > 0.5:
                if depth not in childSkeleton:
                    childSkeleton.append(depth)

        child = genome(len(moreFitParent.inputNodes), len(
            moreFitParent.outputNodes), globalInnovations)

        # ADDING NODES
        # NOTE: we are expecting node to occur in order of depth.
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
                    child.addNode(connection, globalInnovations)

        # TODO: stochastically add connections based on available connections from child skeleton topology
        # ADDING CONNECTIONS
        allChildNodes = child.outputNodes + child.inputNodes + child.hiddenNodes

        lessFitParentConnections = [
            x.outConnections for x in lessFitParent.inputNodes + lessFitParent.hiddenNodes + lessFitParent.outputNodes]
        lessFitParentConnections.extend(
            [x.inConnections for x in lessFitParent.inputNodes + lessFitParent.hiddenNodes + lessFitParent.outputNodes])

        for node in moreFitParent.inputNodes + moreFitParent.hiddenNodes + moreFitParent.outputNodes:
            for connection in node.outConnections + node.inConnections:
                if connection.output.nodeId not in allChildNodes or connection.input.nodeId not in allChildNodes:
                    # connection is lost due to not being aligned in chromosomes
                    continue
                else:
                    if connection in lessFitParentConnections:
                        # get input node and output node of this connection from child and add connection to respective nodes
                        child.addConnection(connection, globalInnovations)
                    elif rand.uniform(0, 1) > 0.5:
                        child.addConnection(connection, globalInnovations)

        return child


# @DEPRECATED
class node:
    def __init__(self, parent, node):
        self.parent = parent  # edge
        self.node = node
        self.children = []  # edges

    def addEdge(self, children):
        '''
        assign children to this node
        '''
        # force iterable
        if type(children) is not list:
            children = [children]
        for child in children:
            self.children.append(node(self, child))

    def walkTree(self, depth):
        '''
        walks the tree formed from this node down to a given depth
        '''
        nextNodes = []
        nodeBuffer = []
        for _ in range(depth):
            for child in nextNodes:
                nodeBuffer.extend(child.children)
            nextNodes.clear()
            nextNodes.extend(nodeBuffer)
            nodeBuffer.clear()
        return nextNodes

    def getNode(self, target):
        '''
        walks the tree starting from this node looking for a given target node
        '''
        curNodes = [self]
        nextNodes = []
        while len([curNode.children for curNode in curNodes]) > 0:
            for node in curNodes:
                if node == target:
                    return node
                else:
                    nextNodes.extend(node.children)
            print('current nodes: ', curNodes)
            curNodes = copy(nextNodes)
            print('next nodes: ', curNodes)
            nextNodes.clear()
            print('copy check: ', curNodes)
        return None
