from copy import copy
from genome import genome
# import connectionGene
from connectionGene import connectionGene
from nodeGene import nodeGene
import random as rand
from copy import deepcopy
from itertools import zip_longest


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
        been added to the topology.
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

        acquiredGenes = []
        # TODO: may be unecessary
        for prime in reversed(self.primalGenes[targetGenome]):
            for gene in prime:
                if gene.nodeId in [x.nodeId for x in acquiredGenes]:
                    # flag for removal
                    prime.remove(gene)
                else:
                    acquiredGenes.append(gene)

    def resetPrimalGenes(self):
        '''
        called once per crossover if using zero elitism crossover (the best for RoM)
        '''
        self.primalGenes.clear()

    #   NOTE: relatively large chance to miss shallow node splits here, in which subsequent splits will be missed.
    #   should use exponential/logistic decay to reduce chance of adding based on depth
    #   this is analogous to chromosome alignment given the spatial factor of combination
    #   from the length of attachment (read more on this, however it is only abstractly pertinent)

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

        for inode in child.inputNodes:
            for outc in inode.outConnections[:len(child.outputNodes)]:
                if outc not in curConnections:
                    curConnections.append(outc)

        while len(curConnections) > 0:
            # handle disjoint genes first then excess
            if len(lessFitGenes) == 0 and alignmentOffset > 0:
                # handle moreFit excess genes
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
                # handle lessFit excess genes
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
            # elif len(moreFitGenes) == 0 and alignmentOffset == 0:
            # Done with alignment
            elif len(moreFitGenes) == 0 and len(lessFitGenes) == 0:
                curConnections.clear()
                break
            else:
                # handle disjoint genes
                curGenes = []
                # get all nodes between parents (if not already in to prevent duplicate additions across parents)
                for gene in moreFitGenes.pop(0) + lessFitGenes.pop(0):
                    if gene.nodeId not in [x.nodeId for x in curGenes]:
                        curGenes.append(gene)

                # curGenes = moreFitGenes.pop(0) + lessFitGenes.pop(0)
            for primal in curGenes:
                for connect in curConnections:
                    # TODO: is splitting node when already exists and found at a deeper depth desired?
                    #               it can be argued that a deeper node has different meaning even if its the result of
                    #               a split in the other genome
                    #              this diverges innovation counting used in connectionGene
                    #              can also prune duplicates in both parent genes
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

    def inheritDisjointConnections(self, targetNode, child, moreFitParent, lessFitParent, globalInnovations):
        # TODO: inherit from lesserFitParent when not in moreFitParent
        '''
        inherit connections from disjoint nodeGenes (occuring in a primalGene depth represented in both parents).
        '''
        print('\n\nDISJOINT: inheriting into targetNode.nodeId {}'.format(
            targetNode.nodeId))
        moreFitNode = moreFitParent.getNode(targetNode.nodeId)
        lessFitNode = lessFitParent.getNode(targetNode.nodeId)

        if moreFitNode is None or lessFitNode is None:
            # TODO: raise assertion
            return
        # TODO: nodes might be missing in more or less fit parent with next feature addition
        # assert moreFitNode is not None and lessFitNode is not None
        # assert moreFitNode.nodeId == lessFitNode.nodeId == targetNode.nodeId
        assert targetNode in child.hiddenNodes

        # TODO: break to prevent repeat connections
        print('DISJOINT: targeting outConnection excess inheritence')
        for outc in moreFitNode.outConnections:
            # compare innovation numbers since looking across genomes
            if outc.output.nodeId in [x.output.nodeId for x in lessFitNode.outConnections]:
                # add newConnection if output node exists already in child topology
                # (will add later if splits havent occured to reveal this node)
                nodeMatch = child.getNode(outc.output.nodeId)
                if nodeMatch is not None:
                    print('DISJOINT: in both parents: connecting node {} to node {}'.format(
                        targetNode.nodeId, nodeMatch.nodeId))
                    newConnection = connectionGene(
                        copy(outc.weight), targetNode, nodeMatch)
                    # if newConnection.exists(child.getAllConnections()):
                    if newConnection.exists(targetNode.outConnections + targetNode.inConnections):
                        # have to ALWAYS do this since constructing connectionGene associates tree nodes
                        newConnection.remove()
                    else:
                        child.addConnection(
                            newConnection, globalInnovations)
            # else:
            # TODO: add probability of adding connection if only in more or less fit genome
            #               now need to encapsulate common addConnections
            elif rand.uniform(0, 1) > 0.5:
                nodeMatch = child.getNode(outc.output.nodeId)
                if nodeMatch is not None:
                    print('DISJOINT: in fit parent: connecting node {} to node {}'.format(
                        targetNode.nodeId, nodeMatch.nodeId))
                    newConnection = connectionGene(
                        copy(outc.weight), targetNode, nodeMatch)
                    # if newConnection.exists(child.getAllConnections()):
                    if newConnection.exists(targetNode.outConnections + targetNode.inConnections):
                        # have to ALWAYS do this since constructing connectionGene associates tree nodes
                        newConnection.remove()
                    else:
                        child.addConnection(
                            newConnection, globalInnovations)

        print('DISJOINT: targeting inConnection excess inheritence')
        for inc in moreFitNode.inConnections:
            # compare innovation numbers since looking across genomes
            if inc.input.nodeId in [x.input.nodeId for x in lessFitNode.inConnections]:
                # add newConnection if output node exists already in child topology
                # (will add later if splits havent occured to reveal this node)
                nodeMatch = child.getNode(inc.input.nodeId)
                if nodeMatch is not None:
                    print('DISJOINT: in both parents: connecting node {} to node {}'.format(
                        nodeMatch.nodeId, targetNode.nodeId))
                    newConnection = connectionGene(
                        copy(inc.weight), nodeMatch, targetNode)
                    # if newConnection.exists(child.getAllConnections()):
                    if newConnection.exists(targetNode.outConnections + targetNode.inConnections):
                        newConnection.remove()
                    else:
                        child.addConnection(
                            newConnection, globalInnovations)

            # else:
            elif rand.uniform(0, 1) > 0.5:
                nodeMatch = child.getNode(inc.output.nodeId)
                if nodeMatch is not None:
                    print('DISJOINT: in fit parent: connecting node {} to node {}'.format(
                        targetNode.nodeId, nodeMatch.nodeId))
                    newConnection = connectionGene(
                        copy(inc.weight), nodeMatch, targetNode)
                    # if newConnection.exists(child.getAllConnections()):
                    if newConnection.exists(targetNode.outConnections + targetNode.inConnections):
                        # have to ALWAYS do this since constructing connectionGene associates tree nodes
                        newConnection.remove()
                    else:
                        child.addConnection(
                            newConnection, globalInnovations)
            #     # TODO: add probability of adding connection if only in more or less fit genome
            #     pass

    def inheritExcessConnections(self, targetNode, child, excessParent, globalInnovations):
        '''
        inherit connections from excess nodeGenes (occuring in a depth only represented by one parent).
        '''
        print('\n\nEXCESS: inheriting into targetNode.nodeId {}'.format(
            targetNode.nodeId))
        excessParentNode = excessParent.getNode(targetNode.nodeId)

        if excessParentNode is None:
            return

        # assert moreFitNode is not None and lessFitNode is not None
        # assert moreFitNode.nodeId == lessFitNode.nodeId == targetNode.nodeId
        assert targetNode in child.hiddenNodes

        # TODO: break to prevent repeat connections
        print('targeting outConnection excess inheritence')
        for outc in excessParentNode.outConnections:
            # compare innovation numbers since looking across genomes
            # if outc.output.nodeId in [x.output.nodeId for x in lessFitNode.outConnections]:

                # add newConnection if output node exists already in child topology
                # (will add later if splits havent occured to reveal this node)
            nodeMatch = child.getNode(outc.output.nodeId)
            if nodeMatch is not None:
                print('EXCESS: connecting node {} to node {}'.format(
                    targetNode.nodeId, nodeMatch.nodeId))
                newConnection = connectionGene(
                    copy(outc.weight), targetNode, nodeMatch)
                # if newConnection.exists(child.getAllConnections()):
                if newConnection.exists(targetNode.outConnections + targetNode.inConnections):
                        # have to ALWAYS do this since constructing connectionGene associates tree nodes
                    newConnection.remove()
                else:
                    child.addConnection(
                        newConnection, globalInnovations)
            # else:
            #     # TODO: add probability of adding connection if only in more or less fit genome
            #     pass

        print('targeting inConnection excess inheritence')
        for inc in excessParentNode.inConnections:
            # compare innovation numbers since looking across genomes
            # if inc.input.nodeId in [x.input.nodeId for x in lessFitNode.inConnections]:
            # add newConnection if output node exists already in child topology
            # (will add later if splits havent occured to reveal this node)
            nodeMatch = child.getNode(inc.input.nodeId)
            if nodeMatch is not None:
                print('EXCESS: connecting node {} to node {}'.format(
                    nodeMatch.nodeId, targetNode.nodeId))
                newConnection = connectionGene(
                    copy(inc.weight), nodeMatch, targetNode)
                # if newConnection.exists(child.getAllConnections()):
                if newConnection.exists(targetNode.outConnections + targetNode.inConnections):
                    newConnection.remove()
                else:
                    child.addConnection(
                        newConnection, globalInnovations)
            # else:
            #     # TODO: add probability of adding connection if only in more or less fit genome
            #     pass

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
