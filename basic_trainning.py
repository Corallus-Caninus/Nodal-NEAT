from genome import genome as g  # TODO: fix directory structure
from evaluator import evaluator as e
import sys
import networkx as nx
import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx

########### THIS IS TEST CODE ###########
evaluation = e(inputs=1, outputs=2, population=1,
               connectionMutationRate=0.5, nodeMutationRate=0.2)
print(len(evaluation.globalInnovations.connections),
      evaluation.globalInnovations.nodeId)
target = evaluation.genepool[0]
# target.addNodeMutation(.0001, evaluation.globalInnovations)
# target.addNodeMutation(.0001, evaluation.globalInnovations)
# target.addNodeMutation(.0001, evaluation.globalInnovations)
# target.addNodeMutation(.0001, evaluation.globalInnovations)
for _ in range(0, 10000000):
    cons = target.outputNodes + target.inputNodes
    cons = [x.inConnections for x in cons] + [x.outConnections for x in cons]
    print(len(cons))
    print(len(evaluation.globalInnovations.connections))
    target.addConnectionMutation(0.0001, evaluation.globalInnovations)

print(len(target.hiddenNodes), '\n')

# translate graph to networkx
myg = nx.DiGraph()
for node in target.hiddenNodes:
    print(node.nodeId)
    for connection in node.inConnections:
        myg.add_edge(connection.input, connection.output)
    for connection in node.outConnections:
        myg.add_edge(connection.input, connection.output)
for node in target.inputNodes:
    print(node.nodeId)
    for connection in node.outConnections:
        myg.add_edge(connection.input, connection.output)
for node in target.outputNodes:
    print(node.nodeId)
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

# outputs = target.forwardProp([1, 2, 3, 4])
# print('\n\n', outputs)

sys.exit()
