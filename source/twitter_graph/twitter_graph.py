class Graph:
    def __init__(self):
        self.nodes = dict()
        self.connections = dict()

    def __add__(self, other):
        for val in other.nodes.values():
            self.nodes[val.id] = val

    def add_connection(self, idx, idy):
        self.connections[idx] = idy

    def add_user(self, user):
        self.nodes[user.id] = user



