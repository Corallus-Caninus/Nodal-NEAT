# USER DEFINED MODULES
from genome import genome as g  # TODO: fix directory structure
from evaluator import evaluator as e
# PLOTTING PACKAGES
import networkx as nx
import matplotlib as mp
import matplotlib.pyplot as plt
# NATIVE PACKAGES
import sys
from multiprocessing import Process
# NOTE: if this ever goes to linux use graphviz for graphics


def graphNEAT(network):

    # translate graph to networkx
    # TODO: this feature will make debuging much faster (with painting) and code more understandable (with animations)
    myg = nx.DiGraph()
    # TODO: are edge directions correct?
    # Translate from node based network to connection based networkx graph
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

    print('BASIC TRAINNING (Graph): ', allConnects)
    for c in allConnects:
        myg.add_edge(c.input, c.output)

    G = myg
    pos = nx.drawing.layout.circular_layout(G)

    # SET COLORS BASED ON NODE TYPE:
    #input, output, hidden
    ins, outs, hids = [], [], []
    labels = {}
    for node in G.nodes:
        if node in network.inputNodes:
            ins.append(node)
        elif node in network.hiddenNodes:
            hids.append(node)
        elif node in network.outputNodes:
            outs.append(node)
        labels.update({node: node.nodeId})

    nx.draw_networkx_nodes(
        G, pos, nodelist=ins, label='Input', node_size=22, node_color='green')
    nx.draw_networkx_nodes(
        G, pos, nodelist=outs, label='output', node_size=22, node_color='red')
    nx.draw_networkx_nodes(
        G, pos, nodelist=hids, label='hidden', node_size=22, node_color='black')

    # SET COLORS BASED ON CONNECTION TYPE
    #loop, disabled, normal
    loops, dis, norms = [], [], []
    for connection in G.edges:
        # get inNode in connection-node tuple
        for check in connection[0].outConnections:
            if check.input == connection[0] and check.output == connection[1]:
                if check.disabled == True:
                    dis.append(connection)
                elif check.loop == True:
                    loops.append(connection)
                else:
                    norms.append(connection)
            else:
                assert "ERROR: NETWORK CONNECTION NOT ASSOCIATED WITH GENOME"

    nx.draw_networkx_edges(G, pos, edgelist=dis, node_size=22, arrowstyle='- >',
                           arrowsize=10, edge_color='yellow',
                           width=2)
    nx.draw_networkx_edges(G, pos, edgelist=loops, node_size=22, arrowstyle='->',
                           arrowsize=10, edge_color='blue',
                           width=2)
    nx.draw_networkx_edges(G, pos, edgelist=norms, node_size=22, arrowstyle='->',
                           arrowsize=10, edge_color='black',
                           width=2)

    nx.draw_networkx_labels(G, pos, labels=labels, fontsize=5)

    ax = plt.gca()
    ax.set_axis_off()
    # plt.show()
    with open('curFig.svg', 'wb') as c:
        plt.savefig(c, format='svg')


if __name__ == '__main__':
    '''
    A test ground for the NEAT algorithm.

    This is a scratch space that will not be consistent
    with feature additions and is only commited to Git
    for aligning test code at a given revision
    '''
    print('begin trainning..')
    ########### THIS IS TEST CODE ###########
    evaluation = e(inputs=4, outputs=2, population=1,
                   connectionMutationRate=0.5, nodeMutationRate=0.2)
    print(len(evaluation.globalInnovations.connections),
          evaluation.globalInnovations.nodeId)
    target = evaluation.genepool[0]

    for _ in range(0, 11):
        target.addNodeMutation(.0001, evaluation.globalInnovations)

    for _ in range(0, 100):
        print('with total globalInnovations: ', len(
            evaluation.globalInnovations.connections))
        target.addConnectionMutation(0.0001, evaluation.globalInnovations)

    # print('CONNECTION PRINTOUT')
    # connections = []
    # for node in target.hiddenNodes + target.outputNodes + target.inputNodes:
    #     for connection in node.outConnections + node.inConnections:
    #         if connection.exists(connections) == True:
    #             pass
    #         else:
    #             connections.append(connection)
    # connections = sorted(connections, key=lambda x: x.input.nodeId)
    # for connection in connections:
    #     #     for connection in list(set(node.outConnections + node.inConnections)):
    #     if connection.loop is True:
    #         print('THIS IS A RECURRENT CONNECTION')
    #     print(connection.input.nodeId, connection.output.nodeId)

    graphNEAT(target)

    outputs = target.forwardProp([1, 2, 3, 4])
    print('\n\n', outputs)
