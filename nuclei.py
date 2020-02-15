from copy import copy
from genome import genome
# import connectionGene
from connectionGene import connectionGene
from nodeGene import nodeGene
import random as rand


class nuclei:
    # TODO: handle connection reactivation
    #               CORR: this isnt necessarily necessary for functional equivalence, skip connections still exist and a
    #                           weight of 1 in a parallelNodes inConnection can make a node split essentially a skip connection
    #               how does reactivation assist in traversing error manifold?

    '''
    nucleus class for crossover, stores skeleton topologies of genomes to allow quick
    crossover after processing of each genome.
    '''

    def __init__(self):
        self.primalGenes = {}  # dictionary of {genomes: skeleton topologies}
    # TODO: need to perform object data storage for split depths on construction
    #               instead of object data inference processesing at crossover time
    #               (readyPrimalGenes is inefficient)

    def readyPrimalGenes(self, targetGenome):
        '''
        takes a genome and breaks it down to its 'split depth' representation, describing in what order nodes have
        been added from the initial fully connected topology.
        '''
        # NOTE: now using list of lists to denote each depth in splits
        # these nodes contain all connections but may not have the supporting nodes.
        # this needs to be resolved in crossover
        # NOTE fun fact: initial topology is analogous to the equator of centromeres
        connectionBuffer = []
        curConnections = []
        curDepth = []
        self.primalGenes.update({targetGenome: []})

        for inode in targetGenome.inputNodes:
            for outc in inode.outConnections[:len(targetGenome.outputNodes)]:
                if outc not in curConnections:
                    curConnections.append(outc)

        while len(curConnections) > 0:
            for connect in curConnections:
                splitNodes = connect.splits(targetGenome.hiddenNodes)
                # TODO: extend should keep list for order of splits performed
                curDepth.extend(splitNodes)

                # TODO: this code requires connections to be added while rebuilding from primalGenes
                for split in splitNodes:
                    for outc in split.outConnections:
                        if outc not in connectionBuffer:
                            connectionBuffer.append(outc)
                    for inc in split.inConnections:
                        if inc not in connectionBuffer:
                            connectionBuffer.append(inc)

            self.primalGenes[targetGenome].append(curDepth.copy())
            curDepth.clear()
            curConnections.clear()
            curConnections = connectionBuffer.copy()
            connectionBuffer.clear()

        # acquiredGenes = []
        # # TODO: may be unecessary since playing back the operations into the child genome
        # # @DEPRECATED
        # for prime in reversed(self.primalGenes[targetGenome]):
        #     for gene in prime:
        #         if gene.nodeId in [x.nodeId for x in acquiredGenes]:
        #             # flag for removal
        #             prime.remove(gene)
        #         else:
        #             acquiredGenes.append(gene)

    def resetPrimalGenes(self):
        '''
        called once per crossover if using zero elitism crossover (the best for RoM)
        '''
        self.primalGenes.clear()

    #   NOTE: relatively large chance to miss shallow node splits here, in which subsequent splits will be missed.
    #   should use exponential/logistic decay to reduce chance of adding based on depth
    #   this is analogous to chromosome alignment given the spatial factor of combination
    #   from the length of attachment (read more on this, however it is only abstractly pertinent)
    # this is more based in reduction division

    def crossover(self, moreFitParent, lessFitParent, globalInnovations):
        '''
        align chromosomes of two genomes based on their primalGene representation and produce
        a child genome with inherited genes (both nodeGenes and connectionGenes).
        '''
        assert moreFitParent in self.primalGenes and lessFitParent in self.primalGenes, \
            "genomes have not been preprocessed in nuclei for chromosome alignment"
        assert moreFitParent.fitness >= lessFitParent.fitness, \
            "less fit parent passed into the wrong positional parameter"

        connectionBuffer = []
        curConnections = []

        moreFitGenes = self.primalGenes[moreFitParent].copy()
        lessFitGenes = self.primalGenes[lessFitParent].copy()
        # configure excess gene orientation in chromosome alignment
        alignmentOffset = len(moreFitGenes) - len(lessFitGenes)

        child = genome(len(moreFitParent.inputNodes), len(
            moreFitParent.outputNodes), globalInnovations)

        # TODO: add node and connection probability hyperparameters

        for inode in child.inputNodes:
            for outc in inode.outConnections[:len(child.outputNodes)]:
                if outc not in curConnections:
                    curConnections.append(outc)

        # handle disjoint node genes first then excess
        while len(curConnections) > 0:
            if len(lessFitGenes) == 0 and alignmentOffset > 0:
                # handle moreFit excess nodeGenes
                curGenes = moreFitGenes.pop(0)
                for primal in curGenes:
                    for connect in curConnections:
                        if primal.alignNodeGene(connect):
                            newNode = child.addNode(connect, globalInnovations)
                            self.inheritExcessConnections(
                                newNode, child, moreFitParent, globalInnovations)

                            for outc in newNode.outConnections:
                                if outc not in connectionBuffer:
                                    connectionBuffer.append(outc)
                            for inc in newNode.inConnections:
                                if inc not in connectionBuffer:
                                    connectionBuffer.append(inc)
                            break

            elif len(moreFitGenes) == 0 and alignmentOffset < 0:
                # handle lessFit excess nodeGenes
                curGenes = lessFitGenes.pop(0)
                for primal in curGenes:
                    for connect in curConnections:
                        if primal.alignNodeGene(connect):
                            newNode = child.addNode(connect, globalInnovations)
                            self.inheritExcessConnections(
                                newNode, child, lessFitParent, globalInnovations)

                            for outc in newNode.outConnections:
                                if outc not in connectionBuffer:
                                    connectionBuffer.append(outc)
                            for inc in newNode.inConnections:
                                if inc not in connectionBuffer:
                                    connectionBuffer.append(inc)
                            break
            elif len(moreFitGenes) == 0 and len(lessFitGenes) == 0:
                # Done with alignment TODO: last pass of connections?
                curConnections.clear()
                break
            else:
                # handle matching/disjoint nodeGenes
                curGenes = []
                # get all nodes between parents (if not already in to prevent duplicate additions across parents)
                for gene in moreFitGenes.pop(0) + lessFitGenes.pop(0):
                    if gene.nodeId not in [x.nodeId for x in curGenes]:
                        curGenes.append(gene)
            for primal in curGenes:
                for connect in curConnections:
                    # TODO: is splitting node when already exists and found at a deeper depth desired? ensure this doesnt happen
                    #               ensured with if gene.nodeId not in [x.nodeId for x in curGenes]
                    #              (local alignment (last part of metaphase with alignNodeGene))
                    #              this doesnt distinguish local excess genes (if len(moreFitGenes.pop() > len(lessFitGenes.pop())))
                    #               not really important, most import excess/disjoint metric is depth of split (which promotes deeper networks)

                    if primal.alignNodeGene(connect):
                        newNode = child.addNode(connect, globalInnovations)

                        self.inheritDisjointConnections(
                            newNode, child, moreFitParent, lessFitParent, globalInnovations)

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

    def inheritConnection(self, child, connect, outConnection, targetNode, globalInnovations):
        if outConnection is True:
            nodeMatch = child.getNode(connect.output.nodeId)
        else:
            nodeMatch = child.getNode(connect.input.nodeId)
        if nodeMatch is not None:
            if outConnection is True:
                newConnection = connectionGene(
                    copy(connect.weight), targetNode, nodeMatch)
            else:
                newConnection = connectionGene(
                    copy(connect.weight), nodeMatch, targetNode)
            if newConnection.exists(targetNode.outConnections + targetNode.inConnections):
                newConnection.remove()
            else:
                print('connecting node {} to node {}'.format(
                    targetNode.nodeId, nodeMatch.nodeId))
                child.addConnection(
                    newConnection, globalInnovations)

    def inheritDisjointConnections(self, targetNode, child, moreFitParent, lessFitParent, globalInnovations):
        # TODO: inherit from lesserFitParent when not in moreFitParent (true disjoint not matching and moreFit)
        '''
        inherit connections from disjoint nodeGenes (occuring in a primalGene depth represented in both parents).
        '''
        print('\n\nDISJOINT: inheriting into targetNode.nodeId {}'.format(
            targetNode.nodeId))

        moreFitNode = moreFitParent.getNode(targetNode.nodeId)
        lessFitNode = lessFitParent.getNode(targetNode.nodeId)

        inheritOuts = []
        inheritIns = []
        # determines if this node is in both parents or lesser/more fit parent
        fitDisjoint = None

        assert targetNode in child.hiddenNodes
        if moreFitNode is None and lessFitNode is None:
            # TODO: this should be assertion
            return
        # assert moreFitNode is not None and lessFitNode is not None, "missing node in child from parents"

        print(moreFitNode, lessFitNode)
        # orient parent's disjoint nodeGene
        if moreFitNode is None:
            inheritIns = lessFitNode.inConnections
            inheritOuts = lessFitNode.outConnections
            fitDisjoint = True
        elif lessFitNode is None:
            inheritIns = moreFitNode.inConnections
            inheritOuts = moreFitNode.outConnections
            fitDisjoint = False
        else:
            for outc in moreFitNode.outConnections + lessFitNode.outConnections:
                if outc not in inheritOuts:
                    inheritOuts.append(outc)
            for inc in moreFitNode.outConnections + lessFitNode.outConnections:
                if inc not in inheritIns:
                    inheritIns.append(inc)

        # inherit outConnetions
        for outc in inheritOuts:
            if fitDisjoint is True:
                if rand.uniform(0, 1) > 0.01:
                    self.inheritConnection(
                        child, outc, True, targetNode, globalInnovations)
            elif fitDisjoint is False:
                if rand.uniform(0, 1) > 0.01:
                    self.inheritConnection(
                        child, outc, True, targetNode, globalInnovations)
            else:
                self.inheritConnection(
                    child, outc, True, targetNode, globalInnovations)

        # inherit inConnections
        for inc in inheritIns:
            if fitDisjoint is True:
                if rand.uniform(0, 1) > 0.01:
                    self.inheritConnection(
                        child, inc, False, targetNode, globalInnovations)
            elif fitDisjoint is False:
                if rand.uniform(0, 1) > 0.01:
                    self.inheritConnection(
                        child, inc, False, targetNode, globalInnovations)
            else:
                self.inheritConnection(
                    child, inc, False, targetNode, globalInnovations)

    def inheritExcessConnections(self, targetNode, child, excessParent, globalInnovations):
        '''
        inherit connections from excess nodeGenes (occuring in a depth only represented by one parent).
        '''
        assert targetNode in child.hiddenNodes
        print('\n\n\n\nEXCESS: inheriting into targetNode.nodeId {} \n\n\n'.format(
            targetNode.nodeId))
        excessParentNode = excessParent.getNode(targetNode.nodeId)

        if excessParentNode is None:
            return

        print('targeting outConnection excess inheritence')
        for outc in excessParentNode.outConnections:
            self.inheritConnection(
                child, outc, True, targetNode, globalInnovations)

        print('targeting inConnection excess inheritence')
        for inc in excessParentNode.inConnections:
            self.inheritConnection(
                child, inc, False, targetNode, globalInnovations)

    def test_rebuildPrimalGenes(self, targetGenome, globalInnovations):
        # TODO: extract to test code
        '''
        test code to rebuild a genome from a primalGenes (split depth genome representation) data structure.
        '''

        assert targetGenome in self.primalGenes, "genome has not been preprocessed in nuclei for chromosome alignment"
        connectionBuffer = []
        curConnections = []
        primalGenes = self.primalGenes[targetGenome].copy()

        child = genome(len(targetGenome.inputNodes), len(
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
                    #               DE-BUG innovation but still getting novel nodes
                    if primal.alignNodeGene(connect):
                        newNode = child.addNode(connect, globalInnovations)

                        self.inheritDisjointConnections(
                            newNode, child, targetGenome, targetGenome, globalInnovations)

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
