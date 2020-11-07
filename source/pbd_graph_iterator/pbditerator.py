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
        self.ITERATIONS = None
        self.CM = np.asarray([0, 0, 0])

    def __call__(self, iterations=1):
        self.ITERATIONS = iterations
        if iterations > 0:
            self.impose_boundary_conditions()
            self.iterator(iterations)

    def impose_boundary_conditions(self):
        for idx, node in self.graph.nodes.items():
            if not self.affiliation_list:
                self.affiliation_list = node.load_affiliation_list()
                self.parties = list(self.affiliation_list.keys())

            if node.party and node.party in self.affiliation_list:
                fv = self.affiliation_list[node.party][0]
                fv = np.asarray([fv['eco'], fv['img'], fv['cli']])
                node.set_feature_vector(fv/np.linalg.norm(fv))
            if not node.party:
                node.set_feature_vector([0, 0, 0])

    def feature_correction(self, node_i, connections, d=1.0):
        xi = np.asarray(node_i.feature_vector)
        wi = 1.0
        #if node_i.party:
        #    wi = 0.01

        v = np.asarray([0.0, 0.0, 0.0])
        w = wi
        for j in connections[node_i.screen_name]:
            node_j = self.graph.nodes[j]

            stiffness = 1.0 #self.graph.connections[node_j.id][node_i.id]
            xj = np.asarray(node_j.feature_vector)
            w += 1.0
            dx_ij = (xi - xj)

            if node_i.party and node_i.party in self.affiliation_list:
                pfeature = self.affiliation_list[node_i.party]
                dx_ij += 0.2*(xi - np.asarray([pfeature[0]['eco'], pfeature[0]['img'] , pfeature[0]['cli']]))

            #if not node_j.party and not node_i.party:
            #    stiffness = 0.01

            v += d*stiffness * dx_ij

        dxi = -wi/w * v
        dxi = dxi - self.CM

        new_feature_vector = node_i.feature_vector + 0.5*dxi
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
            for i in self.graph.connections:
                node_i = self.graph.nodes[i]
                self.feature_correction(node_i, self.graph.connections)

            for i in inverse_connections:
                node_i = self.graph.nodes[i]
                self.feature_correction(node_i, inverse_connections, d=0.4)

            self.CM = np.asarray([0.0, 0.0, 0.0])
            n = 0
            for node in self.graph.nodes.values():
                node.set_feature_vector(node.feature_vector / (np.linalg.norm(node.feature_vector) + 0.0000001))
                self.CM += np.asarray(node.feature_vector)
                n += 1

            self.CM = self.CM/n







