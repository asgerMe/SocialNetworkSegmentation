import os
from pathlib import Path
import pickle
import numpy as np
import re

class PbdGraphIterator:
    def __init__(self, graph):
        self.graph = graph
        self.affiliation_list = None
        self.parties = None

    def __call__(self, iterations=1):
        if iterations > 0:
            self.impose_boundary_conditions()
            self.iterator(iterations)

    def impose_boundary_conditions(self):
        for idx, node in self.graph.nodes.items():
            if not self.affiliation_list:
                self.affiliation_list = node.load_affiliation_list()
                self.parties = list(self.affiliation_list.keys())
            if node.party:
                fv = self.affiliation_list[node.party][0]
                fv = np.asarray([fv['eco'], fv['img'], fv['cli']])
                node.set_feature_vector(fv/np.linalg.norm(fv))
            if not node.party:
                node.set_feature_vector([0, 0, 0])

    def feature_correction(self, node_i, inverse_connections, t):
        xi = np.asarray(node_i.feature_vector)
        wi = 1.0
        v = np.asarray([0.0, 0.0, 0.0])

        if node_i.party:
            wi = 1.0

        w = wi
        for j in inverse_connections[node_i.id]:
            node_j = self.graph.nodes[j]
            stiffness = 1.0 #self.graph.connections[node_j.id][node_i.id]
            xj = np.asarray(node_j.feature_vector)
            w += 1.0
            v += stiffness*(xi - xj)

        dxi = -wi/w * v
        new_feature_vector = node_i.feature_vector + 0.5*dxi
        feature_length = np.linalg.norm(node_i.feature_vector)
        if feature_length != 0:
            node_i.set_feature_vector(node_i.feature_vector / np.linalg.norm(feature_length))
        else:
            node_i.set_feature_vector(new_feature_vector)

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
                self.feature_correction(node_i, inverse_connections, t)






