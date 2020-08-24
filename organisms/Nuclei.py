import random as rand
from copy import copy

from organisms.ConnectionGene import ConnectionGene
from organisms.Genome import Genome


def inheritConnection(
        child,
        connect,
        outConnection,
        targetNode,
        globalInnovations):
    """
    add a Connection to targetNode
    """
    if outConnection is True:
        nodeMatch = child.getNode(connect.output.nodeId)
    else:
        nodeMatch = child.getNode(connect.input.nodeId)
    if nodeMatch is not None:
        if outConnection is True:
            newConnection = ConnectionGene(
                copy(connect.weight), targetNode, nodeMatch)
            child.addConnection(newConnection, globalInnovations)
        else:
            newConnection = ConnectionGene(
                copy(connect.weight), nodeMatch, targetNode)
            child.addConnection(newConnection, globalInnovations)


def inheritDisjointConnections(
        targetNode,
        child,
        moreFitParent,
        lessFitParent,
        globalInnovations):
    # TODO: inherit from lesserFitParent when not in moreFitParent (true disjoint not matching and moreFit)
    # TODO: rewrite this. need to review zip method for when connections in one Node are greater.
    #      also need to attempt true Nodal crossover (random chance for moreFit or lessFit connections
    #      but not a mixing of both)
    """
    inherit connections from disjoint nodeGenes (occurring in a primalGene depth represented in both parents).
    Obeys K.Stanley's random disjoint gene inheritance
    """
    # NOTE: this allows for discovering new expressions of a Node as parent connections may not be added
    #      later if not inherited. follows the pruning motif of Nodal_NEAT
    # print('\n\nDISJOINT: inheriting into targetNode.nodeId {}'.format(
    #     targetNode.nodeId))

    moreFitNode = moreFitParent.getNode(targetNode.nodeId)
    lessFitNode = lessFitParent.getNode(targetNode.nodeId)

    inheritOuts = []
    inheritIns = []
    # determines if this Node is in both parents or lesser/more fit parent
    # fitDisjoint = None

    assert targetNode in child.hiddenNodes
    if moreFitNode is None and lessFitNode is None:
        # TODO: this should be assertion
        return

    # orient parent's disjoint NodeGene
    if moreFitNode is None:
        return
        # inheritIns = lessFitNode.inConnections
        # inheritOuts = lessFitNode.outConnections
        # fitDisjoint = False
    elif lessFitNode is None:
        inheritIns = moreFitNode.inConnections
        inheritOuts = moreFitNode.outConnections
        # fitDisjoint = True
    else:
        # inherit matching genes
        # TODO: inherit all connections of a Node instead. trying to search for modular solutions
        #      instead of connections. This may lead to multiple inheritance (add a Node multiple times
        # at a split depth, generating 'layers' from a successful Node
        # solution)
        if rand.uniform(0, 1) > 0.5:
            inheritOuts = moreFitNode.outConnections
            inheritIns = moreFitNode.inConnections
        else:
            inheritOuts = lessFitNode.outConnections
            inheritIns = lessFitNode.inConnections


    # inherit outConnections
    for outc in inheritOuts:
        inheritConnection(
            child, outc, True, targetNode, globalInnovations)

    # inherit inConnections
    for inc in inheritIns:
        inheritConnection(
            child, inc, False, targetNode, globalInnovations)


def inheritExcessConnections(
        targetNode,
        child,
        excessParent,
        globalInnovations):
    """
    inherit connections from excess nodeGenes (occurring in a depth only represented by one parent).
    """
    assert targetNode in child.hiddenNodes
    # print('\n\nEXCESS: inheriting into targetNode.nodeId {}'.format(
    #     targetNode.nodeId))
    excessParentNode = excessParent.getNode(targetNode.nodeId)

    if excessParentNode is None:
        return

    # print('targeting outConnection excess inheritance')
    for outc in excessParentNode.outConnections:
        inheritConnection(
            child, outc, True, targetNode, globalInnovations)

    # print('targeting inConnection excess inheritance')
    for inc in excessParentNode.inConnections:
        inheritConnection(
            child, inc, False, targetNode, globalInnovations)


class Nuclei:
    # TODO: losing too many connections (SOLVED with proper Node inheritance)
    # TODO: if innovation discovery doesnt happen this can occur in parallel
    # TODO: This needs to occur in parallel
    # TODO: need to cleanup this class (lots of refactoring)

    # TODO: handle Connection reactivation
    #               CORR: this isn't necessarily necessary for functional
    #               equivalence, skip connections still exist and a
    #                           weight of 1 in a parallelNodes inConnection can
    #                           make a Node split essentially a skip Connection
    #               how does reactivation assist in traversing error manifold?

    """
    nucleus class for crossover, stores skeleton topologies of genomes to allow quick
    crossover after processing of each Genome.
    """

    def __init__(self):
        self.primalGenes = {}  # dictionary of {genomes: skeleton topologies}

    # TODO: need to perform object data storage for split depths on construction
    #               instead of object data inference processing at crossover time
    #               (readyPrimalGenes is inefficient). Inherently memory constrained so
    #               this is debatable.

    def readyPrimalGenes(self, targetGenome):
        """
        takes a Genome and breaks it down to its 'split depth' representation, describing in what order nodes have
        been added from the initial fully connected topology.
        """
        # NOTE: now using list of lists to denote each depth in splits
        # these nodes contain all connections but may not have the supporting
        # nodes.
        connectionBuffer = []
        curConnections = []
        curDepth = []
        self.primalGenes.update({targetGenome: []})

        # get initial topology connections
        for inode in targetGenome.inputNodes:
            for outc in inode.outConnections[:len(targetGenome.outputNodes)]:
                if outc not in curConnections:
                    curConnections.append(outc)

        while len(curConnections) > 0:
            for connect in curConnections:
                splitNodes = connect.splits(targetGenome.hiddenNodes)
                # TODO: extend should keep list for order of splits performed
                curDepth.extend(splitNodes)

                # TODO: this code requires connections to be added while
                # rebuilding from primalGenes
                for split in splitNodes:
                    # TODO: I feel like this should be a connectionBuffer.extend(returnedBuffer)
                    #      instead of pass in mutating
                    for outc1 in split.outConnections:
                        if outc1 not in connectionBuffer:
                            connectionBuffer.append(outc1)
                    for inc in split.inConnections:
                        if inc not in connectionBuffer:
                            connectionBuffer.append(inc)

            self.primalGenes[targetGenome].append(curDepth.copy())
            curDepth.clear()
            curConnections.clear()
            curConnections = connectionBuffer.copy()
            connectionBuffer.clear()

    def resetPrimalGenes(self):
        """
        called once per crossover if using zero elitism crossover (the best for RoM)
        """
        self.primalGenes.clear()

    def crossover(self, parent1, parent2, globalInnovations):
        # NOTE: crossover should also be performed with some amount of similarity metric
        #       otherwise 'unstable' destructive crossover will occur
        #       (return to common ancestor may result in oversimplification). this is solved
        #       with speciation.
        # TODO: ensure disjoint and excess is implemented exactly as k.stanley for now
        #       and investigate further
        #               NOTE: K.Stanley has a builtin chance for disjoint gene inheritance.
        #                           Currently testing hyperparameter inheritance next 
        #                           is k.stanley analogy
        # TODO: remove GlobalInnovations passthrough here, shouldnt be necessary. need
        #       another method for addind connections here.
        """
        align chromosomes of two genomes based on their primalGene representation and
        produce a child Genome with inherited genes (both nodeGenes and ConnectionGenes).
        """

        if parent1.fitness >= parent2.fitness:
            moreFitParent = parent1
            lessFitParent = parent2
        else:
            moreFitParent = parent2
            lessFitParent = parent1

        connectionBuffer = []
        curConnections = []
        if moreFitParent not in self.primalGenes:
            self.readyPrimalGenes(moreFitParent)
        if lessFitParent not in self.primalGenes:
            self.readyPrimalGenes(lessFitParent)

        moreFitGenes = self.primalGenes[moreFitParent].copy()
        lessFitGenes = self.primalGenes[lessFitParent].copy()
        # configure excess gene orientation in chromosome alignment
        alignmentOffset = len(moreFitGenes) - len(lessFitGenes)

        child = Genome(len(moreFitParent.inputNodes), len(
            moreFitParent.outputNodes), globalInnovations)

        # get initial topology connections
        for inode in child.inputNodes:
            for initOutc in inode.outConnections[:len(child.outputNodes)]:
                if initOutc not in curConnections:
                    curConnections.append(initOutc)

        # handle disjoint Node genes first then excess
        while len(curConnections) > 0:
            # done with alignment
            # TODO: extract this into while condition
            if len(moreFitGenes) == 0 and len(lessFitGenes) == 0:
                # Done with alignment TODO: last pass of connections? yes. (frontier connections)
                curConnections.clear()
                break
            elif len(lessFitGenes) == 0 and alignmentOffset > 0:
                # handle moreFit excess nodeGenes
                curGenes = moreFitGenes.pop(0)
                for primal in curGenes:
                    for connect in curConnections:
                        if primal.alignNodeGene(connect):
                            newNode = child.addNode(connect, globalInnovations)

                            inheritExcessConnections(
                                newNode, child, moreFitParent, globalInnovations)

                            for outc in newNode.outConnections:
                                if outc not in connectionBuffer:
                                    connectionBuffer.append(outc)
                            for inc in newNode.inConnections:
                                if inc not in connectionBuffer:
                                    connectionBuffer.append(inc)
                            break
            # TODO: check with K.Stanley but these should be thrown out
            else:
                # handle matching/disjoint nodeGenes
                curGenes = []
                # get all nodes between parents (if not already in to prevent
                # duplicate additions across parents)
                for gene in moreFitGenes.pop(0) + lessFitGenes.pop(0):
                    if gene.nodeId not in [x.nodeId for x in curGenes]:
                        curGenes.append(gene)

                for primal in curGenes:
                    for connect in curConnections:
                        # TODO: verify novel nodes arent discovered in
                        #  crossover or obey the algorithm
                        if primal.alignNodeGene(connect):
                            newNode = child.addNode(connect, globalInnovations)

                            inheritDisjointConnections(
                                newNode, child, moreFitParent, lessFitParent, globalInnovations)

                            # TODO: I feel like this should be a connectionBuffer.extend(returnedBuffer)
                            #      instead of append
                            for outc in newNode.outConnections:
                                if outc not in connectionBuffer:
                                    connectionBuffer.append(outc)
                            for inc in newNode.inConnections:
                                if inc not in connectionBuffer:
                                    connectionBuffer.append(inc)
                            break

            curConnections.clear()
            curConnections = connectionBuffer.copy()
            connectionBuffer.clear()

        return child

    def test_rebuildPrimalGenes(self, targetGenome, globalInnovations):
        # TODO: extract to test code
        """
        test code to rebuild a Genome from a primalGenes (split depth Genome representation) data structure.
        """

        assert targetGenome in self.primalGenes, "Genome has not been preprocessed in Nuclei for chromosome alignment"
        connectionBuffer = []
        curConnections = []
        primalGenes = self.primalGenes[targetGenome].copy()

        child = Genome(len(targetGenome.inputNodes), len(
            targetGenome.outputNodes), globalInnovations)

        for inode in child.inputNodes:
            for outc in inode.outConnections[:len(child.outputNodes)]:
                if outc not in curConnections:
                    curConnections.append(outc)

        while len(curConnections) > 0:
            if len(primalGenes) == 0:
                curConnections.clear()
                break
            else:
                curGenes = primalGenes.pop(0)
            for primal in curGenes:
                for connect in curConnections:
                    # TODO: finding novel nodes. BUG in innovation return to here after
                    # DE-BUG innovation but still getting novel nodes
                    if primal.alignNodeGene(connect):
                        newNode = child.addNode(connect, globalInnovations)

                        inheritDisjointConnections(
                            newNode, child, targetGenome, targetGenome, globalInnovations)

                        # TODO: I feel like this should be a connectionBuffer.extend(returnedBuffer)
                        #      instead of pass in mutating
                        for outc1 in newNode.outConnections:
                            if outc1 not in connectionBuffer:
                                connectionBuffer.append(outc1)
                        for inc in newNode.inConnections:
                            if inc not in connectionBuffer:
                                connectionBuffer.append(inc)
                        break

            curConnections.clear()
            curConnections = connectionBuffer.copy()
            connectionBuffer.clear()

        return child
