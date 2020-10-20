import numpy as np

class GraphIterator:
    def __init__(self, node_generator, seed_names=None):

        self.nodes = dict()
        self.connections = dict()
        self.seed_names = seed_names
        self.__node_generator = node_generator
        self.init_graph()
        self.previous_node = None

    def init_graph(self):
        for name in self.seed_names:
            self.expand_graph(name)

    def expand_graph(self, name):
        node = self.__node_generator.new(name)
        self.add_user(node)
        liked_users = self.get_stashed_likes(node.id)
        if not liked_users:
            liked_users = node.get_connections(node.id)
        for user in liked_users:
            if isinstance(user, dict):
                node_connect = self.__node_generator.new(user)
            else:
                node_connect = user

            self.add_user(node_connect)
            self.add_connection(node.id, node_connect.id)

    def next(self, leaf_cutoff=0):
        followers_list = []
        id_list = []
        for node in self.nodes.values():
            if node.followers > leaf_cutoff:
                followers_list.append(node.followers)
                id_list.append(node.id)

        self.expand_graph(self.multinomial_pick(followers_list, id_list))

    def multinomial_pick(self, followers, index_list):
        followers = np.asarray(np.log(followers))
        index_list = np.asarray(index_list)

        sorted_idx = np.argsort(followers)
        followers = followers[sorted_idx]/np.max(followers)
        index_list = index_list[sorted_idx]

        r = np.random.rand()
        chosen_index = index_list[followers > r][0]

        if chosen_index == self.previous_node:
            pick_seed_name = self.seed_names[np.random.randint(0, len(self.seed_names))]
            seed_node = self.__node_generator.new(pick_seed_name)
            print('Resetting: ', pick_seed_name, '-', seed_node.id)
            return seed_node.id

        self.previous_node = chosen_index

        return chosen_index

    def add_connection(self, idx, idy):
        if idx in self.connections and idy in self.connections[idx]:
            self.connections[idx][idy] += 1
        elif idx in self.connections:
            self.connections[idx][idy] = 1
        else:
            self.connections[idx] = {}
            self.connections[idx][idy] = 1

    def get_stashed_likes(self, idx):
        if idx in self.connections:
            objects = []
            for node in self.connections[idx].keys():
                objects.append(self.nodes[node])
            return objects
        else:
            return False

    def add_user(self, user):
        self.nodes[user.id] = user

    def convert_to_dense_matrix(self):
        index = self.get_index()
        matrix = np.zeros([len(index), len(index)])
        for idx, i in enumerate(index):
            for idj, j in enumerate(index):
                if i in self.connections and j in self.connections[i]:
                    matrix[idx, idj] = self.connections[i][j]
        return index, matrix

    def get_index(self):
        index = []
        for i in self.connections.keys():
            index.append(i)
            for j in self.connections[i].keys():
                index.append(j)
        index = set(index)
        return index





