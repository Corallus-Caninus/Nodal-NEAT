import genome
from graphviz import Digraph
# @DEPRECATED
# import networkx as nx
# import matplotlib.pyplot as plt
# TODO: basic_trainning networkx operations should be extracted here

# NOTE: this contains utility functions for graph analysis and analysing/preparing topologies for genetic operations
#              it is understandably preferable to keep this all in genome.py as these methods operate on genome objects
#              but genome.py will be large to the point of unreadable.

# NOTE: adding depth information with nodeGene construction (encapsulating processSequence with nodeGene)
#              requires forward propagation afyter depth changes and fails with loops

# NOTE: Intra-extrema connections are no longer allowed due to complexity for very little simplification
#            (a network with intra-extrema connections always has an equivalent with hidden layer only recursion)
#           since this is about evolving deep direct NEAT networks, the slight simplification of the fitness landscape is not beneficial
#           and will require more work for numpification (vectorization)


def processSequences(targetGenome):
    '''
    gets all split depths of all nodes in the given topology then assign node sequence by checking node depths for shorting connections.
    PARAMETERS:
        targetGenome: the genome to be processed
    RETURNS:
        sequences: order of arrival for each node that will be found in forward propagation.
    '''
    sequences = {}
    connectionBuffer = []
    curConnections = []
    hiddenNodes = targetGenome.hiddenNodes

    # ACQUIRE SPLIT DEPTHS FOR HIDDEN NODES
    # TODO: extract splitDepths for crossover (chromosome alignment of skeleton/primal topologies)
    curDepth = 0
    for node in targetGenome.inputNodes:
        # add all initial topology connections
        sequences.update({node: curDepth})
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

                sequences.update({node: curDepth})

        curConnections.clear()
        curConnections = connectionBuffer.copy()
        connectionBuffer.clear()

    # SHORT ALL DEPTHS BY INCOMING CONNECTIONS
    for node in sequences:
        for inConnection in [x for x in node.inConnections if x.disabled is False]:
            # get incoming connection with lowest sequence/depth
            if sequences[inConnection.input] + 1 < sequences[node]:
                # update sequences
                sequences[node] = sequences[inConnection.input] + 1

    graphvizNEAT(targetGenome, sequences)
    # TODO: graph insight: can we say all connections with sequence[inConnection.output] < sequence[inConnection.input] are loops
    return sequences


def graphvizNEAT(network, sequences):
    f = Digraph('finite_state_machine', filename='graphvizSequences.svg')
    f.attr(rankdir='LR', size='8,5')

    f.attr('node', shape='doublecircle')

    for node in sequences:
        f.node(str(node.nodeId))
    for node in network.inputNodes:
        f.node(str(node.nodeId))
    for node in network.outputNodes:
        f.node(str(node.nodeId))

    f.attr('node', shape='circle')

    allConnects = []
    for n in network.hiddenNodes:
        allConnects.extend(
            [x for x in n.inConnections if x not in allConnects])
        allConnects.extend(
            [x for x in n.outConnections if x not in allConnects])
    for n in network.outputNodes:
        allConnects.extend(
            [x for x in n.inConnections if x not in allConnects])
        allConnects.extend(
            [x for x in n.outConnections if x not in allConnects])
    for n in network.inputNodes:
        allConnects.extend(
            [x for x in n.inConnections if x not in allConnects])
        allConnects.extend(
            [x for x in n.outConnections if x not in allConnects])

    for c in allConnects:
        if c.disabled is True:
            continue
        else:
            f.edge(str(c.input.nodeId), str(
                c.output.nodeId), label=str(c.loop))

    f.view()
