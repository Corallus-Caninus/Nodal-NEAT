from copy import copy

from genome import genome
import connectionGene
import nodeGene
import random as rand
# @DEPRECATED
import innovation


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


class Chromosome:
    #TODO: write unit test for this
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
        '''
        # TODO: need to add skeletonNodes not node with all connections
        hiddenNodes = targetGenome.hiddenNodes

        connectionBuffer = []
        curConnections = []
        depths = {}
        curDepth = 0
        for node in targetGenome.inputNodes:
            # add all initial topology connections
            depths.update({node: curDepth})
            for outc in node.outConnections[:len(targetGenome.outputNodes)]:
                curConnections.append(outc)

        while len(curConnections) > 0:
            curDepth += 1
            for connection in curConnections:
                splitNode = connection.splits(hiddenNodes)

                for node in splitNode:
                    for outConnection in node.outConnections:
                        connectionBuffer.append(outConnection)
                    for inConnection in node.inConnections:
                        connectionBuffer.append(inConnection)

                    depths.update({node: curDepth})

            curConnections.clear()
            curConnections = connectionBuffer.copy()
            connectionBuffer.clear()
        self.primalGenes.update({targetGenome: depths})

    def resetDepths(self):
        '''
        called once per crossover if using zero elitism crossover (the best for RoM)
        '''
        self.primalGenes.clear()

    def crossover(self, moreFitParent, lessFitParent, globalInnovations):
        # TODO: globalInnovations shouldnt need to be passed in
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
        assert moreFitParent.fitness >= lessFitParent, "less fit parent passed into the wrong positional parameter"
        childSkeleton = []
        # if fitness is equivalent treat moreFitParent as most fit still
        for depth in self.primalGenes[moreFitParent]:
            # since nodes are globally consistent we can compare with nodeId here
            # NOTE: {node: curDepth } are format of depths
            if depth in self.primalGenes[lessFitParent]:
                childSkeleton.append(depth)
            elif rand.uniform(a=0, b=1) > 0.5:
                childSkeleton.append(depth)

        child = genome(len(moreFitParent.inputNodes), len(
            moreFitParent.outputNodes), globalInnovations)

    # replay connection splits from skeleton topologies, disabling and adding nodes accordingly
    #distal alignment of loci (pedantic observation)
    # TODO: need to get skeleton topology in order of splits (should be natural ordering)
        for depth in childSkeleton:
            # get split that corresponds to this node
            allChildNodes = child.inputNodes + child.hiddenNodes + child.outputNodes
            for node in allChildNodes:
                for connection in node.outConnections + node.inConnections:
                    # this is the connection split that replays the skeleton node
                    if depth in connection.splits(allChildNodes):
                        child.addNode(connection, globalInnovations) #should match the depth node
                        continue
                #this can only happen due to ordering etc.
                assert "unable to find a split for depthNode {} in the connections".format(depth)
        allChildNodes = child.inputNodes + child.hiddenNodes + child.outputNodes

        # TODO: stochastically add connections based on available connections from child skeleton topology
        lessFitParentConnections = [x.outConnections for x in lessFitParent.inputNodes + lessFitParent.hiddenNodes + lessFitParent.outputNodes]
        lessFitParentConnections.extend([x.inConnections for x in lessFitParent.inputNodes + lessFitParent.hiddenNodes + lessFitParent.outputNodes])

        for node in moreFitParent.inputNodes + moreFitParent.hiddenNodes + moreFitParent.outputNodes:
            for connection in node.outConnections + node.inConnections:
                if connection.output.nodeId not in allChildNodes or connection.input.nodeId not in allChildNodes:
                    #connection is lost due to not being aligned in chromosomes
                    continue
                else:
                    if connection in lessFitParentConnections:
                        #get input node and output node of this connection from child and add connection to respective nodes
                        child.addConnection(connection, globalInnovations)
                    elif rand.uniform(0, 1) > 0.5:
                        child.addConnection(connection, globalInnovations)

        return child
            
