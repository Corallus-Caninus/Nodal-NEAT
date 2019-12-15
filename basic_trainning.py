import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from genome import genome as g  # TODO: fix directory structure
from evaluator import evaluator as e
import sys

########### THIS IS TEST CODE ###########
# TODO: use networkx to create visualization and call test methods?
#              no write matplotlib instead (better) custom if necessary.
#               GUI application for interfacing with visualizations may be fun

evaluation = e(inputs=4, outputs=3, population=5,
               connectionMutationRate=0.5, nodeMutationRate=0.2)
print(len(evaluation.globalInnovations.connections),
      evaluation.globalInnovations.nodeId)
target = evaluation.genepool[0]
for i in range(0, 10):
    target.addNodeMutation(
        0.2, evaluation.globalInnovations)
    target.addConnectionMutation(0.1, evaluation.globalInnovations)
print(len(evaluation.globalInnovations.connections),
      evaluation.globalInnovations.nodeId)
target.forwardProp([1, 2, 3, 4])
# myG = g(3, 3)
# print('walking the network..')
# print(myG.forwardProp([1, 2, 3]))
sys.exit()
########### EXAMPLE ###########
# libraries

# Build a dataframe with 4 connections
# df = pd.DataFrame({'from': edgeIns, 'to': edgeOuts})
# TODO: define using edges and nodes with networkx

# Build your graph
graph = nx.DiGraph()
for node in myG.inputNodes+myG.outputNodes+myG.hiddenNodes:
    graph.add_node(node)
    graph.add_node(node)

# for connection in myG.connections:
#     graph.add_edge(connection.input, connection.output)

nx.draw(graph)  # , pos
# G = nx.from_pandas_edgelist(df, 'from', 'to').to_directed()

# Plot it
# nx.draw(G, with_labels=True)
plt.show()
#################################
