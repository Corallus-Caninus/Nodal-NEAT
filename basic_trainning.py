# USER DEFINED MODULES
from genome import genome as g  # TODO: fix directory structure
from evaluator import evaluator as e
# PLOTTING PACKAGES
import networkx as nx
import matplotlib as mp
import matplotlib.pyplot as plt
# NATIVE PACKAGES
import sys
import logging
import os
import re
# NOTE: if this ever goes to linux use graphviz for graphics


def graphNEAT(network, name):
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

    logging.info('BASIC TRAINNING (Graph): {}'.format(allConnects))
    for c in allConnects:
        myg.add_edge(c.input, c.output)

    G = myg
    pos = nx.drawing.layout.circular_layout(G)
    # TODO: redundant declaration by node for painting
    # SET COLORS BASED ON NODE TYPE:
    # input, output, hidden
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
        G, pos, nodelist=ins, label='Input', node_size=44, node_color='green')
    nx.draw_networkx_nodes(
        G, pos, nodelist=outs, label='output', node_size=44, node_color='red')
    nx.draw_networkx_nodes(
        G, pos, nodelist=hids, label='hidden', node_size=44, node_color='black')

    # SET COLORS BASED ON CONNECTION TYPE
    # loop, disabled, normal
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

    # TODO: redundant node_size declaration
    nx.draw_networkx_edges(G, pos, edgelist=dis, node_size=44, arrowstyle='- >',
                           arrowsize=10, edge_color='yellow',
                           width=2)
    nx.draw_networkx_edges(G, pos, edgelist=loops, node_size=44, arrowstyle='->',
                           arrowsize=10, edge_color='blue',
                           width=2)
    nx.draw_networkx_edges(G, pos, edgelist=norms, node_size=44, arrowstyle='->',
                           arrowsize=10, edge_color='black',
                           width=2)

    nx.draw_networkx_labels(G, pos, labels=labels, fontsize=5)

    ax = plt.gca()
    ax.set_axis_off()
    # plt.show()
    # TODO: log svg with logfile based on number
    with open(name + '.svg', 'wb') as c:
        plt.savefig(c, format='svg')


def configLogfile():
    # TODO: call a seperate logging file for each object. this will make the code easier to understand for first timers
    '''
    configures logFile name and directory
    '''
    for _, _, files in os.walk('logs'):
        fileNums = []
        if len(files) == 0:
            biggestNum = 1
        else:
            for name in files:
                chopFile = re.compile('[-,.]').split(name)
                fileNums.append(int(chopFile[1]))

            biggestNum = max(fileNums)

    logFile = 'logs/test-{}.log'.format(biggestNum+1)
    logging.basicConfig(
        filename=logFile, level=logging.INFO)


if __name__ == '__main__':
    # NOTE: Currently this is the top level API for NEAT.
    # Evaluator with fitness function will be the final API for NEAT and RoM
    # when moving to evaluator, need to move logger configuration
    '''
    A test ground for the NEAT algorithm.

    This is a scratch space that will not be consistent
    with feature additions and is only commited to Git
    for aligning test code at a given revision
    '''
    configLogfile()

    logging.info('begin trainning..')
    ########### THIS IS TEST CODE ###########
    evaluation = e(inputs=2, outputs=2, population=2,
                   connectionMutationRate=0.5, nodeMutationRate=0.2)
    logging.info('{} {}'.format(len(evaluation.globalInnovations.connections),
                                evaluation.globalInnovations.nodeId))

    i = 0
    for target in evaluation.genepool:
        logging.info('BEGIN {} GENOME'.format(i))
        i += 1
        for _ in range(0, 5):
            print(' TOP O\' THE LOOP TO YA\n\n\n\n')
            logging.info('with total globalInnovations: {}'.format(len(
                evaluation.globalInnovations.connections)))
            target.addNodeMutation(.0001, evaluation.globalInnovations)
            # split a specific connection multiple times TODO: call this many times for genome one then for genome 2 to ensure splitDepth
            #  is preserved when genome 2 catches up
            target.addConnectionMutation(.0001, evaluation.globalInnovations)

    # TODO: possibly getting connections across genomes
    # graphNEAT(evaluation.genepool[1], 'secFig')
    graphNEAT(evaluation.genepool[0], 'firFig')

    print('\n\nBEGIN FORWARD PROPAGATION: \n\n')
    outputs = evaluation.genepool[0].forwardProp([1, 2])
    logging.info('\n\n {}'.format(outputs))
    graphNEAT(evaluation.genepool[0], 'firFig')
    # NOTE: second propagation bugs due to improper loop detection
    outputs = evaluation.genepool[0].forwardProp([1, 2])
    logging.info('\n\n {}'.format(outputs))
    logging.info('End of Test')
