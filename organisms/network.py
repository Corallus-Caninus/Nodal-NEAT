from graphviz import Digraph


# since this is about evolving deep direct NEAT networks, the slight simplification of
# the fitness landscape is not beneficial
# and will require more work for numpification (vectorization)


def graphvizNEAT(network, filename):  # was sequences
    f = Digraph('finite_state_machine', filename=str(filename))
    f.attr(rankdir='LR', size='8,5')

    f.attr('Node', shape='circle')

    for node in network.inputNodes:
        f.node(str(node.nodeId))
    for node in network.hiddenNodes:
        # was for Node in sequences
        f.node(str(node.nodeId))
    for node in network.outputNodes:
        f.node(str(node.nodeId))

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
                c.output.nodeId), label=str(c.loop) + ' ' + str(c.weight))

    f.view()
