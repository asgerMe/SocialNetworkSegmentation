import os
from pathlib import Path
import pickle
import numpy as np
import re

class PbdGraphIterator:
    def __init__(self, graph, iterations=0):
        self.graph = graph
        self.iterator(iterations)

    def feature_correction(self, node_i, inverse_connections):
        xi = np.asarray(node_i.feature_vector)
        wi = 1.0
        w = wi
        v = np.asarray([0.0, 0.0, 0.0])


        if node_i.party and node_i.format_word(node_i.screen_name)[:5] == node_i.format_word(node_i.party)[:5]:
            wi = 0.0

        for j in inverse_connections[node_i.id]:
            node_j = self.graph.nodes[j]
            wj = 1.0
            stiffness = 1.0 #self.graph.connections[node_j.id][node_i.id]
            xj = np.asarray(node_j.feature_vector)
            w += wj

            if node_j.party:
                stiffness += 35

            v += stiffness/2*(xi - xj)
        dxi = -wi/w * v
        node_i.set_feature_vector(node_i.feature_vector + 0.1*dxi)

    def invert_connections(self):
        inverse = {}
        for i in self.graph.connections:
            for j in self.graph.connections[i]:
                if not j in inverse:
                    inverse[j] = []
                inverse[j].append(i)

        return inverse

    def iterator(self, iterations):
        inverse_connections = self.invert_connections()

        for t in range(iterations):
            for i in inverse_connections:
                node_i = self.graph.nodes[i]
                self.feature_correction(node_i, inverse_connections)


