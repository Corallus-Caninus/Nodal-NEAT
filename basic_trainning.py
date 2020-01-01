# USER DEFINED MODULES
from genome import genome as g  # TODO: fix directory structure
from evaluator import evaluator as e
# PLOTTING PACKAGES
import networkx as nx
import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx  # MAKE THIS ALL NETWORKX
# NATIVE PACKAGES
import sys

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

for _ in range(0, 1):
    target.addNodeMutation(.0001, evaluation.globalInnovations)
# target.addNodeMutation(.0001, evaluation.globalInnovations)
for _ in range(0, 30):
    # cons = target.outputNodes + target.inputNodes
    # cons = [x.inConnections for x in cons] + [x.outConnections for x in cons]
    # print('adding with connections: ', len(cons))
    print('with total globalInnovations: ', len(
        evaluation.globalInnovations.connections))
    target.addConnectionMutation(0.0001, evaluation.globalInnovations)

print('CONNECTION PRINTOUT')
connections = []
for node in target.hiddenNodes + target.outputNodes:
    for connection in node.outConnections + node.inConnections:
        if connection.exists(connections) == True:
            pass
        else:
            connections.append(connection)

connections = sorted(connections, key=lambda x: x.input.nodeId)
for connection in connections:
    #     for connection in list(set(node.outConnections + node.inConnections)):
    if connection.loop is True:
        print('THIS IS A RECURRENT CONNECTION')
    print(connection.input.nodeId, connection.output.nodeId)

outputs = target.forwardProp([1, 2, 3, 4])
print('\n\n', outputs)


# print(len(target.hiddenNodes), '\n')

# translate graph to networkx
# TODO: graph with different edges for disabled connections and color input and output nodes
myg = nx.DiGraph()
for node in target.hiddenNodes:
    # print(node.nodeId)
    for connection in node.inConnections:
        myg.add_edge(connection.input, connection.output)
    for connection in node.outConnections:
        myg.add_edge(connection.input, connection.output)
for node in target.inputNodes:
    # print(node.nodeId)
    for connection in node.outConnections:
        myg.add_edge(connection.input, connection.output)
for node in target.outputNodes:
    # print(node.nodeId)
    for connection in node.inConnections:
        myg.add_edge(connection.input, connection.output)

G = myg
pos = nx.drawing.layout.circular_layout(G)

node_sizes = [3 + 10 * i for i in range(len(G))]
M = G.number_of_edges()
edge_colors = range(2, M + 2)
edge_alphas = [(5 + i) / (M + 4) for i in range(M)]

nodes = nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='blue')
edges = nx.draw_networkx_edges(G, pos, node_size=node_sizes, arrowstyle='->',
                               arrowsize=10, edge_color=edge_colors,
                               width=2)
# set alpha value for each edge
for i in range(M):
    edges[i].set_alpha(edge_alphas[i])

pc = mpl.collections.PatchCollection(edges)
pc.set_array(edge_colors)
plt.colorbar(pc)

ax = plt.gca()
ax.set_axis_off()
plt.show()

sys.exit()
